import logging
from typing import Union, Any
from datetime import datetime, timezone
from pathlib import Path
from os import getuid, getgid, environ
from grp import getgrnam
import docker
from docker.types import DeviceRequest
from docker.models.containers import Container
from docker.errors import DockerException, APIError
from proceed.run_recorder import RunRecorder
from proceed.model import Pipeline, ExecutionRecord, Step, StepResult, Timing
from proceed.file_matching import count_matches, match_patterns_in_dirs


def run_pipeline(
    original: Pipeline,
    execution_path: Path,
    run_recorder: RunRecorder,
    args: dict[str, str] = {},
    force_rerun: bool = False,
    step_names: list[str] = None,
    client_kwargs: dict[str, Any] = {}
) -> ExecutionRecord:
    """
    Run steps of a pipeline and return results.

    :param original: a Pipeline, as read from an input YAML spec
    :return: a summary of Pipeline execution results.

    """

    logging.info("Starting pipeline run.")

    start = datetime.now(timezone.utc)
    start_iso = start.isoformat(sep="T")

    amended = original._with_args_applied(args)._with_prototype_applied()
    step_results = []
    try:
        for step in amended.steps:
            if step_names and not step.name in step_names:
                logging.info(f"Ignoring step '{step.name}', not in list of steps to run: {step_names}")
                continue

            # Choose the log file for this step.
            log_stem = step.name.replace(" ", "_")
            log_path = Path(execution_path, f"{log_stem}.log")

            # Write out the execution so far, including previous steps and a placeholder for this step.
            # This way, if we interrupt the runner or crash horribly, we still have a partial execution record.
            partial_result = StepResult(
                name=step.name,
                log_file=log_path.as_posix(),
                timing=Timing(start_iso)
            )
            step_results.append(partial_result)
            partial_record = ExecutionRecord(
                original=original,
                amended=amended,
                step_results=step_results,
                timing=Timing(start_iso)
            )
            run_recorder.write(partial_record)

            # Run this step and update the results with a complete step record.
            step_result = run_step(step, log_path, force_rerun, client_kwargs)
            step_results[-1] = step_result

            if step_result.exit_code:
                logging.error("Stopping pipeline run after error.")
                break

    finally:
        finish = datetime.now(timezone.utc)
        finish_iso = finish.isoformat(sep="T")
        duration = finish - start

        logging.info("Finished pipeline run.")

        # Write out a complete execution record.
        execution_record = ExecutionRecord(
            original=original,
            amended=amended,
            step_results=step_results,
            timing=Timing(start_iso, finish_iso, duration.total_seconds())
        )
        run_recorder.write(execution_record)

    return execution_record


def apply_step_X11(
    step: Step,
) -> Step:
    """Set up the step as an X11 gui client with DISPLAY access.

    This is implemented here in the docker_runner and not in the model
    because the intended behavior depends on the runtime system and environment.
    """

    if not step.X11:
        return

    if "DISPLAY" not in step.environment:
        display = environ.get("DISPLAY")
        logging.info(f"Step '{step.name}': using X11 DISPLAY: {display}")
        step.environment["DISPLAY"] = display

    local_socket_dir = Path("/tmp/.X11-unix").as_posix()
    if local_socket_dir not in step.volumes:
        logging.info(f"Step '{step.name}': using X11 local socket dir: {local_socket_dir}")
        step.volumes[local_socket_dir] = local_socket_dir

    if step.network_mode is None:
        logging.info(f"Step '{step.name}': using network_mode host for X11 support")
        step.network_mode = "host"

    default_xauthority = Path("~", ".Xauthority").as_posix()
    xauthority = environ.get("XAUTHORITY", default_xauthority)
    xauthorith_path = Path(xauthority).expanduser().absolute()
    logging.info(f"Step '{step.name}': looking for .Xauthority cookie file at {xauthority} AKA {xauthorith_path}")
    if xauthorith_path.exists():
        xauthority_host = xauthorith_path.as_posix()
        logging.info(f"Step '{step.name}': found .Xauthority cookie file on host at {xauthority_host}")

        xauthority_container = "/var/.Xauthority"
        if xauthority_host not in step.volumes:
            logging.info(f"Step '{step.name}': adding .Xauthority cookie file to container at {xauthority_container}")
            step.volumes[xauthority_host] = xauthority_container

        if "XAUTHORITY" not in step.environment:
            logging.info(f"Step '{step.name}': setting XAUTHORITY env var in container to {xauthority_container}")
            step.environment["XAUTHORITY"] = xauthority_container

    return step


def run_step(
    step: Step,
    log_path: Path,
    force_rerun: bool = False,
    client_kwargs: dict[str, Any] = {}
) -> StepResult:
    logging.info(f"Step '{step.name}': starting.")

    apply_step_X11(step)

    start = datetime.now(timezone.utc)
    start_iso = start.isoformat(sep="T")

    # Create volume dirs on the host as the current user.
    # This is nicer than having dockerd create them as root!
    volume_dirs = step.volumes.keys()
    for volume_dir in volume_dirs:
        volume_path = Path(volume_dir)
        if not volume_path.exists():
            logging.info(f"Step '{step.name}': creating host directory: {volume_path}")
            volume_path.mkdir(parents=True, exist_ok=True)

    if step.progress_file is not None:
        progress_done_file = Path(step.progress_file + ".done")
        if progress_done_file.exists():
            logging.info(f"Step '{step.name}': found progress .done file {progress_done_file}.")
            if force_rerun:
                logging.info(f"Step '{step.name}': executing despite .done file because force_rerun is {force_rerun}.")
            else:
                logging.info(f"Step '{step.name}': skipping execution because .done file found {progress_done_file}.")
                return StepResult(
                    name=step.name,
                    skipped=True,
                    progress_done_file=progress_done_file.as_posix(),
                    timing=Timing(start_iso)
                )

    files_done = match_patterns_in_dirs(volume_dirs, step.match_done)
    if files_done:
        logging.info(f"Step '{step.name}': found {count_matches(files_done)} done files.")

        if force_rerun:
            logging.info(f"Step '{step.name}': executing despite done files because force_rerun is {force_rerun}.")
        else:
            logging.info(f"Step '{step.name}': skipping execution because done files were found.")
            return StepResult(
                name=step.name,
                skipped=True,
                files_done=files_done,
                timing=Timing(start_iso)
            )

    if step.progress_file is not None:
        progress_file = Path(step.progress_file)
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        with open(progress_file, "w") as f:
            f.write(f"{start_iso} Starting step {step.name}\n")

    files_in = match_patterns_in_dirs(volume_dirs, step.match_in)
    logging.info(f"Step '{step.name}': found {count_matches(files_in)} input files.")

    (container, exit_code, exception) = run_container(step, log_path, client_kwargs)
    finish = datetime.now(timezone.utc)
    finish_iso = finish.isoformat(sep="T")

    if exception is not None:
        # The container completed with an error.
        error_type_name = type(exception).__name__
        if isinstance(exception, APIError):
            error_message = f"{error_type_name}: {exception.explanation}\n"
        else:
            error_message = f"{error_type_name}: {exception.args}\n"

        with open(log_path, 'a') as f:
            f.write(error_message)

        logging.error(f"Step '{step.name}': error (see stack trace above) {error_message}")
        return StepResult(
            name=step.name,
            log_file=log_path.as_posix(),
            timing=Timing(start_iso),
            exit_code=exit_code
        )

    # It seems the container completed OK.
    files_out = match_patterns_in_dirs(volume_dirs, step.match_out)
    logging.info(f"Step '{step.name}': found {count_matches(files_out)} output files.")

    files_summary = match_patterns_in_dirs(volume_dirs, step.match_summary)
    logging.info(f"Step '{step.name}': found {count_matches(files_summary)} summary files.")

    if step.progress_file is not None:
        progress_file = Path(step.progress_file)
        if exit_code == 0:
            # Append a success messge to the progress_file.
            with open(progress_file, "a") as f:
                f.write(f"{finish_iso} exit code {exit_code}\n")
                f.write(f"{finish_iso} completed step {step.name}\n")

            # Rename the progress_file to <progress_file>.done.
            progress_file.rename(step.progress_file + ".done")
            logging.info(f"Step '{step.name}': renamed {progress_file} to {progress_done_file}.")
        else:
            # Append an error messge to the progress_file.
            with open(progress_file, "a") as f:
                f.write(f"{finish_iso} exit code {exit_code}\n")
                f.write(f"{finish_iso} error in step {step.name}\n")

    logging.info(f"Step '{step.name}': finished.")
    duration = finish - start
    return StepResult(
        name=step.name,
        image_id=container.image.id,
        exit_code=exit_code,
        log_file=log_path.as_posix(),
        files_done=files_done,
        files_in=files_in,
        files_out=files_out,
        files_summary=files_summary,
        timing=Timing(start.isoformat(sep="T"), finish.isoformat(sep="T"), duration.total_seconds()),
    )


def resolve_user(user: str) -> str:
    """Figure out user and group to run as: by name on host or container, or integer ids."""
    if user is None:
        # Use the container default user and group.
        return None

    if user.startswith("self"):
        # Special case invented by Proceed: current uid and/or gid on host.
        uid = getuid()
        parts = user.split(":")
        if len(parts) > 1:
            # Requesting a specific group or gid.
            group = parts[1]
            try:
                # Look up group by name and take the host gid.
                group_info = getgrnam(group)
                gid = group_info.gr_gid
            except:
                # Assume this is a gid and us as-is.
                gid = group
        else:
            # Use current gid.
            gid = getgid()
        return f"{uid}:{gid}"

    # Use whatever user or user:group was provided as-is.
    return user


def run_container(
    step: Step,
    log_path: Path,
    client_kwargs: dict[str, Any] = {},
    max_attempts: int = 3
) -> tuple[Container, int, Exception]:
    retried_exception = None
    attempts = 0
    while attempts < max_attempts:
        try:
            device_requests = []
            if step.gpus:
                if isinstance(step.gpus, list):
                    # Request specific gpus by id or index, similar to:
                    #   docker run --gpus device=GPU-3a23c669-1f69-c64e-cf85-44e9b07e7a2a
                    #   docker run --gpus '"device=0,2"'
                    gpu_strs = [str(gpu) for gpu in step.gpus]
                    logging.info(f"Container '{step.name}': requesting gpus: {gpu_strs}.")
                    gpu_request = DeviceRequest(
                        device_ids=gpu_strs,
                        capabilities=[["gpu"]]
                    )
                else:
                    # Request all gpus, similar to:
                    #   docker run --gpus all
                    logging.info(f"Container '{step.name}': requesting all gpus.")
                    gpu_request = DeviceRequest(
                        count=-1,
                        capabilities=[["gpu"]]
                    )
                device_requests.append(gpu_request)

            container_user = resolve_user(step.user)
            if container_user is None:
                logging.info(f"Container '{step.name}': running as default user (might be root).")
            else:
                logging.info(f"Container '{step.name}': running as user {container_user}.")

            if step.privileged:
                logging.warning(f"Container '{step.name}' using privileged mode.  Only use this for troubleshooting!")

            client = docker.from_env(**client_kwargs)
            if isinstance(step.command, list):
                command = [str(arg) for arg in step.command]
            else:
                command = step.command
            container = client.containers.run(
                step.image,
                command=command,
                environment=step.environment,
                device_requests=device_requests,
                network_mode=step.network_mode,
                mac_address=step.mac_address,
                volumes=normalize_volumes(step.volumes),
                working_dir=step.working_dir,
                auto_remove=False,
                remove=False,
                detach=True,
                user=container_user,
                shm_size=step.shm_size,
                privileged=step.privileged
            )
            logging.info(f"Container '{step.name}': waiting for process to complete.")

            # Tail the container logs and write new lines to the step log and the proceed log as they arrive.
            step_log_stream = container.logs(stdout=True, stderr=True, stream=True)
            with open(log_path, 'w') as f:
                for log_entry in step_log_stream:
                    log = log_entry.decode("utf-8")
                    f.write(log)
                    logging.info(f"Step '{step.name}': {log.strip()}")

            # Collect overall logs and status of the finished procedss.
            run_results = container.wait()
            exit_code = run_results['StatusCode']
            logging.info(f"Container '{step.name}': process completed with exit code {exit_code}")

            container.remove()

            return (container, exit_code, None)

        except APIError as api_error:
            if api_error.is_client_error():
                # Client errors are not worth retrying, just fail out.
                logging.error(f"Container had a Docker client error.", exc_info=True)
                return (None, -1, api_error)
            else:
                # Server errors might be transient and are worth retrying.
                logging.error(f"Container had a Docker server error, will retry.", exc_info=True)
                retried_exception = api_error

        except DockerException as docker_exception:
            # The other DockerExceptions besides APIError are probably not worth retrying, so just fail out.
            # https://github.com/docker/docker-py/blob/main/docker/errors.py
            logging.error(f"Container had a Docker error.", exc_info=True)
            return (None, -1, docker_exception)

        except Exception as unexpected_exception:
            # Other exceptions besides DockerException are unexpected!
            # But we have seen OSError here, for one.
            # Some of these seem to be transient, so we can retry them.
            logging.error(f"Container had an unexpected, non-Docker error, will retry", exc_info=True)
            retried_exception = unexpected_exception

        attempts += 1
        retry_log_message = f"Container attempts/retries at {attempts} out of {max_attempts}.\n"
        with open(log_path, 'a') as f:
            f.write(retry_log_message)
        logging.info(retry_log_message.strip())

    # If we got here it means we exhausted max_attempts, so we expect retried_exception to be filled in.
    return (None, -1, retried_exception)


def normalize_volumes(
    volumes: dict[str, Union[str, dict[str, str]]],
    default_mode: str = "rw"
) -> dict[str, dict[str, str]]:
    """Convert string paths to full dict form and make relative paths absolute."""
    normalized = {}
    for host_path, volume in volumes.items():
        host_absolute = Path(host_path).absolute().as_posix()
        if isinstance(volume, str):
            bind_absolute = Path(volume).absolute().as_posix()
            normalized[host_absolute] = {"bind": bind_absolute, "mode": default_mode}
        else:
            bind_absolute = Path(volume["bind"]).absolute().as_posix()
            volume["bind"] = bind_absolute
            normalized[host_absolute] = volume
    return normalized
