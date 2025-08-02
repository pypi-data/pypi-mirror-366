from __future__ import annotations

import contextlib
import functools
import json
import logging
import os
import pathlib
import tempfile
import time
from collections.abc import Iterable, Mapping
from typing import Any, Callable, overload

import jubilant
from jubilant import _pretty, _yaml
from jubilant._juju import _format_config

from ._task import ExecTask29 as ExecTask
from ._task import Task29 as Task
from .statustypes import Status

logger_wait = logging.getLogger('jubilant.wait')


class Juju29(jubilant.Juju):
    """Instantiate this class to run Juju commands.

    Most methods directly call a single Juju CLI command. If a CLI command doesn't yet exist as a
    method, use :meth:`cli`.

    The class will automatically detect the version of the Juju CLI installed
    and adjust to use the appropriate commands and options for that version.

    Example::

        juju = jubilant.Juju()
        juju.deploy('snappass-test')

    Args:
        model: If specified, operate on this Juju model, otherwise use the current Juju model.
        wait_timeout: The default timeout for :meth:`wait` (in seconds) if that method's *timeout*
            parameter is not specified.
        cli_binary: Path to the Juju CLI binary. If not specified, uses ``juju`` and assumes it is
            in the PATH.
    """

    cli_version: str
    """The version of the Juju CLI binary, for example ``3.6.8``."""

    def __init__(
        self,
        *,
        model: str | None = None,
        wait_timeout: float = 3 * 60.0,
        cli_binary: str | pathlib.Path | None = None,
        cli_version: str | None = None,
    ):
        super().__init__(model=model, wait_timeout=wait_timeout, cli_binary=cli_binary)
        if cli_version is None:
            self.cli_version = json.loads(
                self.cli('version', '--format', 'json', include_model=False)
            )
        else:
            self.cli_version = cli_version

    @functools.cached_property
    def cli_major_version(self):
        return int(self.cli_version.split('.', 1)[0])

    def __repr__(self) -> str:
        args = [
            f'model={self.model!r}',
            f'wait_timeout={self.wait_timeout}',
            f'cli_binary={self.cli_binary!r}',
            f'cli_version={self.cli_version!r}',
        ]
        return f'Juju({", ".join(args)})'

    # Keep the public methods in alphabetical order, so we don't have to think
    # about where to put each new method.

    def add_secret(
        self,
        name: str,
        content: Mapping[str, str],
        *,
        info: str | None = None,
    ) -> jubilant.SecretURI:
        """Add a new named secret and returns its secret URI.

        Args:
            name: Name for the secret.
            content: Key-value pairs that represent the secret content, for example
                ``{'password': 'hunter2'}``.
            info: Optional description for the secret.
        """
        if self.cli_major_version < 3:
            raise NotImplementedError('Juju secrets requires Juju 3.')
        return super().add_secret(name, content, info=info)

    def deploy(
        self,
        charm: str | pathlib.Path,
        app: str | None = None,
        *,
        attach_storage: str | Iterable[str] | None = None,
        base: str | None = None,
        bind: Mapping[str, str] | str | None = None,
        channel: str | None = None,
        config: Mapping[str, jubilant.ConfigValue] | None = None,
        constraints: Mapping[str, str] | None = None,
        force: bool = False,
        num_units: int = 1,
        overlays: Iterable[str | pathlib.Path] = (),
        resources: Mapping[str, str] | None = None,
        revision: int | None = None,
        storage: Mapping[str, str] | None = None,
        to: str | Iterable[str] | None = None,
        trust: bool = False,
    ) -> None:
        """Deploy an application or bundle.

        Args:
            charm: Name of charm or bundle to deploy, or path to a local file (must start with
                ``/`` or ``.``).
            app: Optional application name within the model. Defaults to the charm name.
            attach_storage: Existing storage(s) to attach to the deployed unit, for example,
                ``foo/0`` or ``mydisk/1``. Not available for Kubernetes models.
            base: The base on which to deploy, for example, ``ubuntu@22.04``.
            bind: Either a mapping of endpoint-to-space bindings, for example
                ``{'database-peers': 'internal-space'}``, or a single space name, which is
                equivalent to binding all endpoints to that space.
            channel: Channel to use when deploying from Charmhub, for example, ``latest/edge``.
            config: Application configuration as key-value pairs, for example,
                ``{'name': 'My Wiki'}``.
            constraints: Hardware constraints for new machines, for example, ``{'mem': '8G'}``.
            force: If true, bypass checks such as supported bases.
            num_units: Number of units to deploy for principal charms.
            overlays: File paths of bundles to overlay on the primary bundle, applied in order.
            resources: Specify named resources to use for deployment, for example:
                ``{'bin': '/path/to/some/binary'}``.
            revision: Charmhub revision number to deploy.
            storage: Constraints for named storage(s), for example, ``{'data': 'tmpfs,1G'}``.
            to: Machine or container to deploy the unit in (bypasses constraints). For example,
                to deploy to a new LXD container on machine 25, use ``lxd:25``.
            trust: If true, allows charm to run hooks that require access to cloud credentials.
        """
        if self.cli_major_version >= 3:
            return super().deploy(
                charm,
                app,
                attach_storage=attach_storage,
                base=base,
                bind=bind,
                channel=channel,
                config=config,
                constraints=constraints,
                force=force,
                num_units=num_units,
                #                overlays=overlays,
                resources=resources,
                revision=revision,
                storage=storage,
                to=to,
                trust=trust,
            )

        # Need this check because str is also an iterable of str.
        if isinstance(overlays, str):
            raise TypeError('overlays must be an iterable of str or pathlib.Path, not str')

        args = ['deploy', str(charm)]
        if app is not None:
            args.append(app)

        if attach_storage:
            if isinstance(attach_storage, str):
                args.extend(['--attach-storage', attach_storage])
            else:
                args.extend(['--attach-storage', ','.join(attach_storage)])
        if base is not None:
            args.extend(['--series', _base_to_series(base)])
        if bind is not None:
            if not isinstance(bind, str):
                bind = ' '.join(f'{k}={v}' for k, v in bind.items())
            args.extend(['--bind', bind])
        if channel is not None:
            args.extend(['--channel', channel])
        if config is not None:
            for k, v in config.items():
                args.extend(['--config', _format_config(k, v)])
        if constraints is not None:
            for k, v in constraints.items():
                args.extend(['--constraints', f'{k}={v}'])
        if force:
            args.append('--force')
        if num_units != 1:
            args.extend(['--num-units', str(num_units)])
        #        for overlay in overlays:
        #            args.extend(['--overlay', str(overlay)])
        if resources is not None:
            for k, v in resources.items():
                args.extend(['--resource', f'{k}={v}'])
        if revision is not None:
            args.extend(['--revision', str(revision)])
        if storage is not None:
            for k, v in storage.items():
                args.extend(['--storage', f'{k}={v}'])
        if to:
            if isinstance(to, str):
                args.extend(['--to', to])
            else:
                args.extend(['--to', ','.join(to)])
        if trust:
            args.append('--trust')

        self.cli(*args)

    @overload
    def exec(
        self, command: str, *args: str, machine: int, wait: float | None = None
    ) -> ExecTask: ...

    @overload
    def exec(self, command: str, *args: str, unit: str, wait: float | None = None) -> ExecTask: ...

    def exec(  # type: ignore
        self,
        command: str,
        *args: str,
        machine: int | None = None,
        unit: str | None = None,
        wait: float | None = None,
    ) -> ExecTask:
        """Run the command on the remote target specified.

        You must specify either *machine* or *unit*, but not both.

        Note: this method does not support running a command on multiple units
        at once. If you need that, let us know, and we'll consider adding it
        with a new ``exec_multiple`` method or similar.

        Args:
            command: Command to run. Because the command is executed using the shell,
                arguments may also be included here as a single string, for example
                ``juju.exec('echo foo', ...)``.
            args: Arguments of the command.
            machine: ID of machine to run the command on.
            unit: Name of unit to run the command on, for example ``mysql/0`` or ``mysql/leader``.
            wait: Maximum time to wait for command to finish; :class:`TimeoutError` is raised if
                this is reached. Default is to wait indefinitely.

        Returns:
            The task created to run the command, including logs, failure message, and so on.

        Raises:
            ValueError: if the machine or unit doesn't exist.
            TaskError: if the command failed.
            TimeoutError: if *wait* was specified and the wait time was reached.
        """
        if self.cli_major_version >= 3:
            return super().exec(command, *args, machine=machine, unit=unit, wait=wait)  # type: ignore

        if (machine is not None and unit is not None) or (machine is None and unit is None):
            raise TypeError('must specify "machine" or "unit", but not both')

        cli_args = ['exec', '--format', 'json']
        if machine is not None:
            cli_args.extend(['--machine', str(machine)])
        else:
            assert unit is not None
            cli_args.extend(['--unit', unit])
        if wait is not None:
            cli_args.extend(['--timeout', f'{wait}s'])
        cli_args.append('--')
        cli_args.append(command)
        cli_args.extend(args)

        try:
            stdout, stderr = self._cli(*cli_args)
        except jubilant.CLIError as exc:
            if 'timed out' in exc.stderr:
                msg = f'timed out waiting for command, stderr:\n{exc.stderr}'
                raise TimeoutError(msg) from None
            if 'not found' in exc.stderr:
                if machine is not None:
                    raise ValueError(
                        f'machine {machine!r} not found, stderr:\n{exc.stderr}'
                    ) from None
                else:
                    raise ValueError(f'unit {unit!r} not found, stderr:\n{exc.stderr}') from None
            # The "juju exec" CLI command itself fails if the exec'd command fails.
            if 'task failed' not in exc.stderr:
                raise
            stdout = exc.stdout
            stderr = exc.stderr

        # Command doesn't return any stdout if no units exist.
        results: list[dict[str, Any]] = json.loads(stdout) if stdout.strip() else []
        if machine is not None:
            for result in results:
                if 'machine' in result and result['machine'] == str(machine):
                    break
            else:
                raise ValueError(f'machine {machine!r} not found, stderr:\n{stderr}')
        else:
            for result in results:
                if 'unit' in result and result['unit'] == unit:
                    break
            else:
                raise ValueError(f'unit {unit!r} not found, stderr:\n{stderr}')
        task = ExecTask._from_dict(result)
        task.raise_on_failure()
        return task

    def integrate(self, app1: str, app2: str, *, via: str | Iterable[str] | None = None) -> None:
        """Integrate two applications, creating a relation between them.

        The order of *app1* and *app2* is not significant. Each of them should
        be in the format ``<application>[:<endpoint>]``. The endpoint is only
        required if there's more than one possible integration between the two
        applications.

        To integrate an application in the current model with an application in
        another model (cross-model), prefix *app1* or *app2* with ``<model>.``.
        To integrate with an application on another controller, *app1* or *app2* must
        be an offer endpoint. See ``juju integrate --help`` for details.

        Args:
            app1: One of the applications (and endpoints) to integrate.
            app2: The other of the applications (and endpoints) to integrate.
            via: Inform the offering side (the remote application) of the
                source of traffic, to enable network ports to be opened. This
                is in CIDR notation, for example ``192.0.2.0/24``.
        """
        if self.cli_major_version >= 3:
            return super().integrate(app1, app2, via=via)

        args = ['relate', app1, app2]
        if via:
            if isinstance(via, str):
                args.extend(['--via', via])
            else:
                args.extend(['--via', ','.join(via)])
        self.cli(*args)

    def refresh(
        self,
        app: str,
        *,
        base: str | None = None,
        channel: str | None = None,
        config: Mapping[str, jubilant.ConfigValue] | None = None,
        force: bool = False,
        path: str | pathlib.Path | None = None,
        resources: Mapping[str, str] | None = None,
        revision: int | None = None,
        storage: Mapping[str, str] | None = None,
        trust: bool = False,
    ) -> None:
        """Refresh (upgrade) an application's charm.

        Args:
            app: Name of application to refresh.
            base: Select a different base than is currently running.
            channel: Channel to use when deploying from Charmhub, for example, ``latest/edge``.
            config: Application configuration as key-value pairs.
            force: If true, bypass checks such as supported bases.
            path: Refresh to a charm located at this path.
            resources: Specify named resources to use for deployment, for example:
                ``{'bin': '/path/to/some/binary'}``.
            revision: Charmhub revision number to deploy.
            storage: Constraints for named storage(s), for example, ``{'data': 'tmpfs,1G'}``.
            trust: If true, allows charm to run hooks that require access to cloud credentials.
        """
        if self.cli_major_version >= 3:
            return super().refresh(
                app,
                base=base,
                channel=channel,
                config=config,
                force=force,
                path=path,
                resources=resources,
                revision=revision,
                storage=storage,
                trust=trust,
            )

        args = ['refresh', app]

        if base is not None:
            args.extend(['--series', _base_to_series(base)])
        if channel is not None:
            args.extend(['--channel', channel])
        if force:
            args.extend(['--force', '--force-base', '--force-units'])
        if path is not None:
            args.extend(['--path', str(path)])
        if resources is not None:
            for k, v in resources.items():
                args.extend(['--resource', f'{k}={v}'])
        if revision is not None:
            args.extend(['--revision', str(revision)])
        if storage is not None:
            for k, v in storage.items():
                args.extend(['--storage', f'{k}={v}'])

        mgr = contextlib.nullcontext() if config is None else tempfile.TemporaryFile('w')  # noqa: SIM115
        with mgr as config_file:
            if config is not None:
                assert config_file is not None
                _yaml.safe_dump(config, config_file)
                config_file.flush()
                args.extend(['--config', config_file.name])
            self.cli(*args)

        if trust:
            self.trust(app)

    def run(  # type: ignore
        self,
        unit: str,
        action: str,
        params: Mapping[str, Any] | None = None,
        *,
        wait: float | None = None,
    ) -> Task | jubilant.Task:
        """Run an action on the given unit and wait for the result.

        Note: this method does not support running an action on multiple units
        at once. If you need that, let us know, and we'll consider adding it
        with a new ``run_multiple`` method or similar.

        Example::

            juju = jubilant.Juju()
            result = juju.run('mysql/0', 'get-password')
            assert result.results['username'] == 'USER0'

        Args:
            unit: Name of unit to run the action on, for example ``mysql/0`` or
                ``mysql/leader``.
            action: Name of action to run.
            params: Optional named parameters to pass to the action.
            wait: Maximum time to wait for action to finish; :class:`TimeoutError` is raised if
                this is reached. Default is to wait indefinitely.

        Returns:
            The task created to run the action, including logs, failure message, and so on.

        Raises:
            ValueError: if the action or the unit doesn't exist.
            TaskError: if the action failed.
            TimeoutError: if *wait* was specified and the wait time was reached.
        """
        if self.cli_major_version >= 3:
            return super().run(unit, action, params, wait=wait)

        args = ['run-action', '--format', 'json', unit, action]
        if wait is None:
            args.append('--wait')
        else:
            args.append(f'--wait={wait}s')

        params_file = None
        if params is not None:
            with tempfile.NamedTemporaryFile(
                'w+', delete=False, dir=self._temp_dir
            ) as params_file:
                _yaml.safe_dump(params, params_file)
            args.extend(['--params', params_file.name])

        try:
            try:
                stdout, stderr = self._cli(*args)
            except jubilant.CLIError as exc:
                if 'timed out' in exc.stderr or 'timeout reached' in exc.stderr:
                    msg = f'timed out waiting for action, stderr:\n{exc.stderr}'
                    raise TimeoutError(msg) from None
                # The "juju run" CLI command fails if the action has an uncaught exception.
                if 'task failed' not in exc.stderr:
                    raise
                stdout = exc.stdout
                stderr = exc.stderr

            # Command doesn't return any stdout if no units exist.
            all_tasks: dict[str, Any] = json.loads(stdout) if stdout.strip() else {}
            full_unit_name = f'unit-{unit.replace("/", "-")}'
            if full_unit_name not in all_tasks:
                raise ValueError(
                    f'action {action!r} not defined or unit {unit!r} not found, stderr:\n{stderr}'
                )
            task = Task._from_dict(all_tasks[full_unit_name])
            task.raise_on_failure()
            return task
        finally:
            if params_file is not None:
                os.remove(params_file.name)

    def status(self) -> Status | jubilant.Status:  # type: ignore
        """Fetch the status of the current model, including its applications and units."""
        stdout = self.cli('status', '--format', 'json')
        result = json.loads(stdout)
        # The status we get back depends on the Juju controller version, not the
        # CLI version.
        if result['model']['version'].startswith('2'):
            return Status._from_dict(result)
        return jubilant.Status._from_dict(result)

    def wait(  # type: ignore
        self,
        ready: Callable[[Status], bool],
        *,
        error: Callable[[Status], bool] | None = None,
        delay: float = 1.0,
        timeout: float | None = None,
        successes: int = 3,
    ) -> Status | jubilant.Status:
        """Wait until ``ready(status)`` returns true.

        This fetches the Juju status repeatedly (waiting *delay* seconds between each call),
        and returns the last status after the *ready* callable returns true for *successes*
        times in a row.

        This function logs the status object after the first status call, and after subsequent
        calls if the status object has changed.

        Example::

            juju = jubilant.Juju()
            juju.deploy('snappass-test')
            juju.wait(jubilant.all_active)

            # Or something more complex: wait specifically for 'snappass-test' to be active,
            # and raise if any app or unit is seen in "error" status while waiting.
            juju.wait(
                lambda status: jubilant.all_active(status, 'snappass-test'),
                error=jubilant.any_error,
            )

        Args:
            ready: Callable that takes a :class:`Status` object and returns true when the wait
                should be considered ready. It needs to return true *successes* times in a row
                before ``wait`` returns.
            error: Callable that takes a :class:`Status` object and returns true when ``wait``
                should raise an error (:class:`WaitError`).
            delay: Delay in seconds between status calls.
            timeout: Overall timeout; :class:`TimeoutError` is raised if this is reached.
                If not specified, uses the *wait_timeout* specified when the instance was created.
            successes: Number of times *ready* must return true for the wait to succeed.

        Raises:
            TimeoutError: If the *timeout* is reached. A string representation
                of the last status, if any, is added as an exception note.
            WaitError: If the *error* callable returns True. A string representation
                of the last status is added as an exception note.
        """
        if self.cli_major_version >= 3:
            return super().wait(
                ready,  # type: ignore
                error=error,  # type: ignore
                delay=delay,
                timeout=timeout,
                successes=successes,
            )
        if timeout is None:
            timeout = self.wait_timeout

        status = None
        success_count = 0
        start = time.monotonic()

        while time.monotonic() - start < timeout:
            prev_status = status

            stdout, _ = self._cli('status', '--format', 'json', log=False)
            result = json.loads(stdout)
            status = Status._from_dict(result)

            if status != prev_status:
                diff = _status_diff(prev_status, status)
                if diff:
                    logger_wait.info('wait: status changed:\n%s', diff)

            if error is not None and error(status):
                raise jubilant.WaitError(
                    f'error function {error.__qualname__} returned true\n{status}'
                )

            if ready(status):
                success_count += 1
                if success_count >= successes:
                    return status
            else:
                success_count = 0

            time.sleep(delay)

        if status is None:
            raise TimeoutError(f'wait timed out after {timeout}s')
        raise TimeoutError(f'wait timed out after {timeout}s\n{status}')


def _status_diff(old: Status | None, new: Status) -> str:
    """Return a line-based diff of two status objects."""
    if old is None:
        old_lines = []
    else:
        old_lines = [line for line in _pretty.gron(old) if _status_line_ok(line)]
    new_lines = [line for line in _pretty.gron(new) if _status_line_ok(line)]
    return '\n'.join(_pretty.diff(old_lines, new_lines))


def _status_line_ok(line: str) -> bool:
    """Return whether the status line should be included in the diff."""
    # Exclude controller timestamp as it changes every update and is just noise.
    field, _, _ = line.partition(' = ')
    if field == '.controller.timestamp':
        return False
    # Exclude status-updated-since timestamps as they just add noise (and log lines already
    # include timestamps).
    if field.endswith('.since'):
        return False
    return True


def _base_to_series(base: str) -> str:
    """Convert a base to a series name."""
    name, cycle = base.split('@', 1)
    if name != 'ubuntu':
        raise ValueError(f'base must be an Ubuntu base, not {name!r}')
    return {
        '14.04': 'trusty',
        '16.04': 'xenial',
        '18.04': 'bionic',
        '20.04': 'focal',
        '22.04': 'jammy',
        '24.04': 'noble',
        '24.10': 'oracular',
        '25.04': 'plucky',
        '25.10': 'questing',
    }[cycle]
