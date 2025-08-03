# SPDX-License-Identifier: Apache-2.0.
# Copyright (c) 2024 - 2025 Waldiez and contributors.

# pylint: disable=too-many-instance-attributes,unused-argument
# pylint: disable=too-many-arguments,too-many-positional-arguments
# pylint: disable=too-many-public-methods,too-many-locals

"""Base runner for Waldiez workflows."""

import shutil
import sys
import tempfile
import threading
from pathlib import Path
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Optional,
    Type,
)

from aiofiles.os import wrap
from anyio.from_thread import start_blocking_portal
from typing_extensions import Self

from waldiez.exporter import WaldiezExporter
from waldiez.logger import WaldiezLogger, get_logger
from waldiez.models import Waldiez

from .environment import refresh_environment, reset_env_vars, set_env_vars
from .post_run import after_run
from .pre_run import (
    a_install_requirements,
    install_requirements,
)
from .protocol import WaldiezRunnerProtocol
from .utils import (
    a_chdir,
    chdir,
)

if TYPE_CHECKING:
    from autogen.events import BaseEvent  # type: ignore[import-untyped]


class WaldiezBaseRunner(WaldiezRunnerProtocol):
    """Base runner for Waldiez.

    Initialization parameters:
        - waldiez: The Waldiez flow to run.
        - output_path: Path to save the output file.
        - uploads_root: Root directory for uploads.
        - structured_io: Whether to use structured I/O.
        - skip_patch_io: Whether to skip patching I/O functions.
        - dot_env: Path to a .env file for environment variables.

    Methods to override:
        - _before_run: Actions to perform before running the flow.
        - _a_before_run: Async actions to perform before running the flow.
        - _run: Actual implementation of the run logic.
        - _a_run: Async implementation of the run logic.
        - _after_run: Actions to perform after running the flow.
        - _a_after_run: Async actions to perform after running the flow.
        - _start: Implementation of non-blocking start logic.
        - _a_start: Async implementation of non-blocking start logic.
        - _stop: Actions to perform when stopping the flow.
        - _a_stop: Async actions to perform when stopping the flow.
    """

    _structured_io: bool
    _output_path: str | Path | None
    _uploads_root: str | Path | None
    _dot_env_path: str | Path | None
    _skip_patch_io: bool
    _running: bool

    def __init__(
        self,
        waldiez: Waldiez,
        output_path: str | Path | None,
        uploads_root: str | Path | None,
        structured_io: bool,
        skip_patch_io: bool = False,
        dot_env: str | Path | None = None,
    ) -> None:
        """Initialize the Waldiez manager."""
        self._waldiez = waldiez
        WaldiezBaseRunner._running = False
        WaldiezBaseRunner._structured_io = structured_io
        WaldiezBaseRunner._output_path = output_path
        WaldiezBaseRunner._uploads_root = uploads_root
        WaldiezBaseRunner._skip_patch_io = skip_patch_io
        WaldiezBaseRunner._dot_env_path = dot_env
        self._called_install_requirements = False
        self._exporter = WaldiezExporter(waldiez)
        self._stop_requested = threading.Event()
        self._logger = get_logger()
        self._print: Callable[..., None] = print
        self._send: Callable[["BaseEvent"], None] = self._print
        self._input: (
            Callable[..., str] | Callable[..., Coroutine[Any, Any, str]]
        ) = input
        self._last_results: list[dict[str, Any]] = []
        self._last_exception: Exception | None = None
        self._execution_complete_event = threading.Event()
        self._execution_thread: Optional[threading.Thread] = None

    def is_running(self) -> bool:
        """Check if the workflow is currently running.

        Returns
        -------
        bool
            True if the workflow is running, False otherwise.
        """
        return WaldiezBaseRunner._running

    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """Wait for non-blocking execution to complete.

        This is a base implementation that subclasses can override if needed.

        Parameters
        ----------
        timeout: float | None
            The maximum time to wait for completion, in seconds.
            If None, wait indefinitely.

        Returns
        -------
        bool
            True if the workflow completed successfully, False if it timed out.
        """
        # Default implementation - subclasses can override
        if not self.is_running():
            return True

        if self._execution_thread and self._execution_thread.is_alive():
            self._execution_thread.join(timeout)
            return not self._execution_thread.is_alive()

        return self._execution_complete_event.wait(timeout or 0)

    def get_execution_stats(self) -> dict[str, Any]:
        """Get basic execution statistics.

        Returns
        -------
        dict[str, Any]
            A dictionary containing execution statistics.
        - is_running: Whether the runner is currently running.
        - has_thread: Whether there is an execution thread.
        - thread_alive: Whether the execution thread is alive.
        - has_error: Whether there was an error during execution.
        """
        return {
            "is_running": self.is_running(),
            "has_thread": self._execution_thread is not None,
            "thread_alive": (
                self._execution_thread.is_alive()
                if self._execution_thread
                else False
            ),
            "has_error": self._last_exception is not None,
        }

    # Helper for subclasses
    def _signal_completion(self) -> None:
        """Signal that execution has completed."""
        self._execution_complete_event.set()

    def _reset_completion_state(self) -> None:
        """Reset completion state for new execution."""
        self._execution_complete_event.clear()

    def _before_run(
        self,
        output_file: Path,
        uploads_root: Path | None,
    ) -> Path:
        """Run before the flow execution."""
        self.log.info("Preparing workflow file: %s", output_file)
        temp_dir = Path(tempfile.mkdtemp())
        file_name = output_file.name
        with chdir(to=temp_dir):
            self._exporter.export(
                path=file_name,
                force=True,
                uploads_root=uploads_root,
                structured_io=WaldiezBaseRunner._structured_io,
            )
            if self._dot_env_path:
                shutil.copyfile(
                    str(self._dot_env_path),
                    str(temp_dir / ".env"),
                )
        return temp_dir

    async def _a_before_run(
        self,
        output_file: Path,
        uploads_root: Path | None,
    ) -> Path:
        """Run before the flow execution asynchronously."""
        temp_dir = Path(tempfile.mkdtemp())
        file_name = output_file.name
        async with a_chdir(to=temp_dir):
            self._exporter.export(
                path=file_name,
                uploads_root=uploads_root,
                structured_io=self.structured_io,
                force=True,
            )
            if self._dot_env_path:
                wrapped = wrap(shutil.copyfile)
                await wrapped(
                    str(self._dot_env_path),
                    str(temp_dir / ".env"),
                )
        return temp_dir

    def _run(
        self,
        temp_dir: Path,
        output_file: Path,
        uploads_root: Path | None,
        skip_mmd: bool,
        skip_timeline: bool,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Run the Waldiez flow."""
        raise NotImplementedError(
            "The _run method must be implemented in the subclass."
        )

    async def _a_run(
        self,
        temp_dir: Path,
        output_file: Path,
        uploads_root: Path | None,
        skip_mmd: bool,
        skip_timeline: bool,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Run the Waldiez flow asynchronously."""
        raise NotImplementedError(
            "The _a_run method must be implemented in the subclass."
        )

    def _start(
        self,
        temp_dir: Path,
        output_file: Path,
        uploads_root: Path | None,
        skip_mmd: bool,
        skip_timeline: bool,
    ) -> None:
        """Start running the Waldiez flow in a non-blocking way."""
        raise NotImplementedError(
            "The _start method must be implemented in the subclass."
        )

    async def _a_start(
        self,
        temp_dir: Path,
        output_file: Path,
        uploads_root: Path | None,
        skip_mmd: bool,
        skip_timeline: bool,
    ) -> None:
        """Start running the Waldiez flow in a non-blocking way asynchronously.

        Parameters
        ----------
        temp_dir : Path
            The path to the temporary directory created for the run.
        output_file : Path
            The path to the output file.
        uploads_root : Path | None
            The root path for uploads, if any.
        skip_mmd : bool
            Whether to skip generating the mermaid diagram.
        """
        raise NotImplementedError(
            "The _a_start method must be implemented in the subclass."
        )

    def _after_run(
        self,
        results: list[dict[str, Any]],
        output_file: Path,
        uploads_root: Path | None,
        temp_dir: Path,
        skip_mmd: bool,
        skip_timeline: bool,
    ) -> None:
        """Run after the flow execution."""
        # Save results
        self._last_results = results

        # Reset stop flag for next run
        self._stop_requested.clear()
        after_run(
            temp_dir=temp_dir,
            output_file=output_file,
            flow_name=self.waldiez.name,
            uploads_root=uploads_root,
            skip_mmd=skip_mmd,
            skip_timeline=skip_timeline,
        )
        self.log.info("Cleanup completed")

    async def _a_after_run(
        self,
        results: list[dict[str, Any]],
        output_file: Path,
        uploads_root: Path | None,
        temp_dir: Path,
        skip_mmd: bool,
        skip_timeline: bool,
    ) -> None:
        """Run after the flow execution asynchronously."""
        self._after_run(
            results=results,
            output_file=output_file,
            uploads_root=uploads_root,
            temp_dir=temp_dir,
            skip_mmd=skip_mmd,
            skip_timeline=skip_timeline,
        )

    def _stop(self) -> None:
        """Actions to perform when stopping the flow."""
        raise NotImplementedError(
            "The _stop method must be implemented in the subclass."
        )

    async def _a_stop(self) -> None:
        """Asynchronously perform actions when stopping the flow."""
        raise NotImplementedError(
            "The _a_stop method must be implemented in the subclass."
        )

    # ===================================================================
    # HELPER METHODS
    # ===================================================================
    @staticmethod
    def _prepare_paths(
        output_path: str | Path | None = None,
        uploads_root: str | Path | None = None,
    ) -> tuple[Path, Path | None]:
        """Prepare the output and uploads paths."""
        uploads_root_path: Path | None = None
        if uploads_root is not None:
            uploads_root_path = Path(uploads_root)
            WaldiezBaseRunner._uploads_root = uploads_root_path

        if output_path is not None:
            output_path = Path(output_path)
            WaldiezBaseRunner._output_path = output_path
        if not WaldiezBaseRunner._output_path:
            WaldiezBaseRunner._output_path = Path.cwd() / "waldiez_flow.py"
        output_file: Path = Path(WaldiezBaseRunner._output_path)
        return output_file, uploads_root_path

    def gather_requirements(self) -> set[str]:
        """Gather extra requirements to install before running the flow.

        Returns
        -------
        set[str]
            A set of requirements that are not already installed and do not
            include 'waldiez' in their name.
        """
        extra_requirements = {
            req
            for req in self.waldiez.requirements
            if req not in sys.modules and "waldiez" not in req
        }
        if "python-dotenv" not in extra_requirements:
            extra_requirements.add("python-dotenv")
        return extra_requirements

    def install_requirements(self) -> None:
        """Install the requirements for the flow."""
        if not self._called_install_requirements:
            self._called_install_requirements = True
            extra_requirements = self.gather_requirements()
            if extra_requirements:
                install_requirements(extra_requirements)

    async def a_install_requirements(self) -> None:
        """Install the requirements for the flow asynchronously."""
        if not self._called_install_requirements:
            self._called_install_requirements = True
            extra_requirements = self.gather_requirements()
            if extra_requirements:
                await a_install_requirements(extra_requirements)

    # ===================================================================
    # PUBLIC PROTOCOL IMPLEMENTATION
    # ===================================================================

    def before_run(
        self,
        output_file: Path,
        uploads_root: Path | None,
    ) -> Path:
        """Run the before_run method synchronously.

        Parameters
        ----------
        output_file : Path
            The path to the output file.
        uploads_root : Path | None
            The root path for uploads, if any.

        Returns
        -------
        Path
            The path to the temporary directory created before running the flow.
        """
        return self._before_run(
            output_file=output_file,
            uploads_root=uploads_root,
        )

    async def a_before_run(
        self,
        output_file: Path,
        uploads_root: Path | None,
    ) -> Path:
        """Run the _a_before_run method asynchronously.

        Parameters
        ----------
        output_file : Path
            The path to the output file.
        uploads_root : Path | None
            The root path for uploads, if any.

        Returns
        -------
        Path
            The path to the temporary directory created before running the flow.
        """
        return await self._a_before_run(
            output_file=output_file,
            uploads_root=uploads_root,
        )

    def run(
        self,
        output_path: str | Path | None = None,
        uploads_root: str | Path | None = None,
        structured_io: bool | None = None,
        skip_mmd: bool = False,
        skip_timeline: bool = False,
        dot_env: str | Path | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Run the Waldiez flow in blocking mode.

        Parameters
        ----------
        output_path : str | Path | None
            The output path, by default None.
        uploads_root : str | Path | None
            The runtime uploads root, by default None.
        structured_io : bool
            Whether to use structured IO instead of the default 'input/print',
            by default False.
        skip_mmd : bool
            Whether to skip generating the mermaid diagram, by default False.
        skip_timeline : bool
            Whether to skip generating the timeline JSON.
        dot_env : str | Path | None
            The path to the .env file, if any.
        **kwargs : Any
            Additional keyword arguments for the run method.

        Returns
        -------
        list[dict[str, Any]]
            The result of the run.

        Raises
        ------
        RuntimeError
            If the runner is already running.
        """
        if dot_env is not None:
            resolved = Path(dot_env).resolve()
            if resolved.is_file():
                WaldiezBaseRunner._dot_env_path = resolved
        if structured_io is not None:
            WaldiezBaseRunner._structured_io = structured_io
        if self.is_running():
            raise RuntimeError("Workflow already running")
        if self.waldiez.is_async:
            with start_blocking_portal(backend="asyncio") as portal:
                return portal.call(
                    self.a_run,
                    output_path,
                    uploads_root,
                    structured_io,
                    skip_mmd,
                )
        output_file, uploads_root_path = self._prepare_paths(
            output_path=output_path,
            uploads_root=uploads_root,
        )
        temp_dir = self.before_run(
            output_file=output_file,
            uploads_root=uploads_root_path,
        )
        self.install_requirements()
        refresh_environment()
        WaldiezBaseRunner._running = True
        results: list[dict[str, Any]] = []
        old_env_vars = set_env_vars(self.waldiez.get_flow_env_vars())
        try:
            with chdir(to=temp_dir):
                sys.path.insert(0, str(temp_dir))
                results = self._run(
                    temp_dir=temp_dir,
                    output_file=output_file,
                    uploads_root=uploads_root_path,
                    skip_mmd=skip_mmd,
                    skip_timeline=skip_timeline,
                )
        finally:
            WaldiezBaseRunner._running = False
            reset_env_vars(old_env_vars)
        self.after_run(
            results=results,
            output_file=output_file,
            uploads_root=uploads_root_path,
            temp_dir=temp_dir,
            skip_mmd=skip_mmd,
            skip_timeline=skip_timeline,
        )
        self._print("<Waldiez> - Done running the flow.")
        if sys.path[0] == str(temp_dir):
            sys.path.pop(0)
        return results

    # noinspection DuplicatedCode
    async def a_run(
        self,
        output_path: str | Path | None = None,
        uploads_root: str | Path | None = None,
        structured_io: bool | None = None,
        skip_mmd: bool = False,
        skip_timeline: bool = False,
        dot_env: str | Path | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Run the Waldiez flow asynchronously.

        Parameters
        ----------
        output_path : str | Path | None
            The output path, by default None.
        uploads_root : str | Path | None
            The runtime uploads root, by default None.
        structured_io : bool
            Whether to use structured IO instead of the default 'input/print',
            by default False.
        skip_mmd : bool
            Whether to skip generating the mermaid diagram, by default False.
        skip_timeline : bool
            Whether to skip generating the timeline JSON, by default False.
        dot_env : str | Path | None
            The path to the .env file, if any.
        **kwargs : Any
            Additional keyword arguments for the run method.

        Returns
        -------
        list[dict[str, Any]]
            The result of the run.

        Raises
        ------
        RuntimeError
            If the runner is already running.
        """
        if dot_env is not None:
            resolved = Path(dot_env).resolve()
            if resolved.is_file():
                WaldiezBaseRunner._dot_env_path = resolved
        if structured_io is not None:
            WaldiezBaseRunner._structured_io = structured_io
        if self.is_running():
            raise RuntimeError("Workflow already running")
        output_file, uploads_root_path = self._prepare_paths(
            output_path=output_path,
            uploads_root=uploads_root,
        )
        temp_dir = await self._a_before_run(
            output_file=output_file,
            uploads_root=uploads_root_path,
        )
        await self.a_install_requirements()
        refresh_environment()
        WaldiezBaseRunner._running = True
        results: list[dict[str, Any]] = []
        old_env_vars = set_env_vars(self.waldiez.get_flow_env_vars())
        try:
            async with a_chdir(to=temp_dir):
                sys.path.insert(0, str(temp_dir))
                results = await self._a_run(
                    temp_dir=temp_dir,
                    output_file=output_file,
                    uploads_root=uploads_root_path,
                    skip_mmd=skip_mmd,
                    skip_timeline=skip_timeline,
                )
        finally:
            WaldiezBaseRunner._running = False
            reset_env_vars(old_env_vars)
        await self._a_after_run(
            results=results,
            output_file=output_file,
            uploads_root=uploads_root_path,
            temp_dir=temp_dir,
            skip_mmd=skip_mmd,
            skip_timeline=skip_timeline,
        )
        if sys.path[0] == str(temp_dir):
            sys.path.pop(0)
        return results

    def start(
        self,
        output_path: str | Path | None,
        uploads_root: str | Path | None,
        structured_io: bool | None = None,
        skip_mmd: bool = False,
        skip_timeline: bool = False,
        dot_env: str | Path | None = None,
        **kwargs: Any,
    ) -> None:
        """Start running the Waldiez flow in a non-blocking way.

        Parameters
        ----------
        output_path : str | Path | None
            The output path.
        uploads_root : str | Path | None
            The runtime uploads root.
        structured_io : bool | None
            Whether to use structured IO instead of the default 'input/print'.
        skip_mmd : bool
            Whether to skip generating the mermaid diagram, by default False.
        skip_timeline : bool
            Whether to skip generating the timeline JSON, by default False.
        dot_env : str | Path | None
            The path to the .env file, if any.
        **kwargs : Any
            Additional keyword arguments for the start method.

        Raises
        ------
        RuntimeError
            If the runner is already running.
        """
        if dot_env is not None:
            resolved = Path(dot_env).resolve()
            if resolved.is_file():
                WaldiezBaseRunner._dot_env_path = resolved
        if structured_io is not None:
            WaldiezBaseRunner._structured_io = structured_io
        if self.is_running():
            raise RuntimeError("Workflow already running")
        output_file, uploads_root_path = self._prepare_paths(
            output_path=output_path,
            uploads_root=uploads_root,
        )
        temp_dir = self.before_run(
            output_file=output_file,
            uploads_root=uploads_root_path,
        )
        self.install_requirements()
        refresh_environment()
        WaldiezBaseRunner._running = True
        self._start(
            temp_dir=temp_dir,
            output_file=output_file,
            uploads_root=uploads_root_path,
            skip_mmd=skip_mmd,
            skip_timeline=skip_timeline,
        )

    # noinspection DuplicatedCode
    async def a_start(
        self,
        output_path: str | Path | None,
        uploads_root: str | Path | None,
        structured_io: bool | None = None,
        skip_mmd: bool = False,
        skip_timeline: bool = False,
        dot_env: str | Path | None = None,
        **kwargs: Any,
    ) -> None:
        """Asynchronously start running the Waldiez flow in a non-blocking way.

        Parameters
        ----------
        output_path : str | Path | None
            The output path.
        uploads_root : str | Path | None
            The runtime uploads root.
        structured_io : bool | None = None
            Whether to use structured IO instead of the default 'input/print'.
        skip_mmd : bool = False
            Whether to skip generating the mermaid diagram, by default False.
        skip_timeline : bool = False
            Whether to skip generating the timeline JSON, by default False.
        dot_env : str | Path | None = None
            The path to the .env file, if any.
        **kwargs : Any
            Additional keyword arguments for the start method.

        Raises
        ------
        RuntimeError
            If the runner is already running.
        """
        if dot_env is not None:
            resolved = Path(dot_env).resolve()
            if resolved.is_file():
                WaldiezBaseRunner._dot_env_path = resolved
        if structured_io is not None:
            WaldiezBaseRunner._structured_io = structured_io
        if self.is_running():
            raise RuntimeError("Workflow already running")
        output_file, uploads_root_path = self._prepare_paths(
            output_path=output_path,
            uploads_root=uploads_root,
        )
        temp_dir = await self._a_before_run(
            output_file=output_file,
            uploads_root=uploads_root_path,
        )
        await self.a_install_requirements()
        refresh_environment()
        WaldiezBaseRunner._running = True
        await self._a_start(
            temp_dir=temp_dir,
            output_file=output_file,
            uploads_root=uploads_root_path,
            skip_mmd=skip_mmd,
            skip_timeline=skip_timeline,
        )

    def after_run(
        self,
        results: list[dict[str, Any]],
        output_file: Path,
        uploads_root: Path | None,
        temp_dir: Path,
        skip_mmd: bool,
        skip_timeline: bool,
    ) -> None:
        """Actions to perform after running the flow.

        Parameters
        ----------
        results : list[dict[str, Any]]
            The results of the flow run.
        output_file : Path
            The path to the output file.
        uploads_root : Path | None
            The root path for uploads, if any.
        temp_dir : Path
            The path to the temporary directory used during the run.
        skip_mmd : bool
            Whether to skip generating the mermaid diagram.
        skip_timeline : bool
            Whether to skip generating the timeline JSON.
        """
        self._after_run(
            results=results,
            output_file=output_file,
            uploads_root=uploads_root,
            temp_dir=temp_dir,
            skip_mmd=skip_mmd,
            skip_timeline=skip_timeline,
        )

    async def a_after_run(
        self,
        results: list[dict[str, Any]],
        output_file: Path,
        uploads_root: Path | None,
        temp_dir: Path,
        skip_mmd: bool,
        skip_timeline: bool,
    ) -> None:
        """Asynchronously perform actions after running the flow.

        Parameters
        ----------
        results : list[dict[str, Any]]
            The results of the flow run.
        output_file : Path
            The path to the output file.
        uploads_root : Path | None
            The root path for uploads, if any.
        temp_dir : Path
            The path to the temporary directory used during the run.
        skip_mmd : bool
            Whether to skip generating the mermaid diagram.
        skip_timeline : bool

        """
        await self._a_after_run(
            results=results,
            output_file=output_file,
            uploads_root=uploads_root,
            temp_dir=temp_dir,
            skip_mmd=skip_mmd,
            skip_timeline=skip_timeline,
        )

    def stop(self) -> None:
        """Stop the runner if it is running."""
        if not self.is_running():
            return
        try:
            self._stop()
        finally:
            WaldiezBaseRunner._running = False

    async def a_stop(self) -> None:
        """Asynchronously stop the runner if it is running."""
        if not self.is_running():
            return
        try:
            await self._a_stop()
        finally:
            WaldiezBaseRunner._running = False

    # ===================================================================
    # PROPERTIES AND CONTEXT MANAGERS
    # ===================================================================

    @property
    def waldiez(self) -> Waldiez:
        """Get the Waldiez instance."""
        return self._waldiez

    @property
    def is_async(self) -> bool:
        """Check if the workflow is async."""
        return self.waldiez.is_async

    @property
    def running(self) -> bool:
        """Get the running status."""
        return self.is_running()

    @property
    def log(self) -> WaldiezLogger:
        """Get the logger for the runner."""
        return self._logger

    @property
    def structured_io(self) -> bool:
        """Check if the runner is using structured IO."""
        return WaldiezBaseRunner._structured_io

    @property
    def dot_env_path(self) -> str | Path | None:
        """Get the path to the .env file, if any."""
        return WaldiezBaseRunner._dot_env_path

    @property
    def output_path(self) -> str | Path | None:
        """Get the output path for the runner."""
        return WaldiezBaseRunner._output_path

    @property
    def uploads_root(self) -> str | Path | None:
        """Get the uploads root path for the runner."""
        return WaldiezBaseRunner._uploads_root

    @property
    def skip_patch_io(self) -> bool:
        """Check if the runner is skipping patching IO."""
        return WaldiezBaseRunner._skip_patch_io

    @classmethod
    def load(
        cls,
        waldiez_file: str | Path,
        name: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        requirements: list[str] | None = None,
        output_path: str | Path | None = None,
        uploads_root: str | Path | None = None,
        structured_io: bool = False,
        dot_env: str | Path | None = None,
    ) -> "WaldiezBaseRunner":
        """Load a waldiez flow from a file and create a runner.

        Parameters
        ----------
        waldiez_file : str | Path
            The path to the waldiez file.
        name : str | None, optional
            The name of the flow, by default None.
        description : str | None, optional
            The description of the flow, by default None.
        tags : list[str] | None, optional
            The tags for the flow, by default None.
        requirements : list[str] | None, optional
            The requirements for the flow, by default None.
        output_path : str | Path | None, optional
            The path to save the output file, by default None.
        uploads_root : str | Path | None, optional
            The root path for uploads, by default None.
        structured_io : bool, optional
            Whether to use structured IO instead of the default 'input/print',
            by default False.
        dot_env : str | Path | None, optional
            The path to the .env file, if any, by default None.

        Returns
        -------
        WaldiezBaseRunner
            An instance of WaldiezBaseRunner initialized with the loaded flow.
        """
        waldiez = Waldiez.load(
            waldiez_file,
            name=name,
            description=description,
            tags=tags,
            requirements=requirements,
        )
        return cls(
            waldiez=waldiez,
            output_path=output_path,
            uploads_root=uploads_root,
            structured_io=structured_io,
            dot_env=dot_env,
        )

    def __enter__(self) -> Self:
        """Enter the context manager."""
        return self

    async def __aenter__(self) -> Self:
        """Enter the context manager asynchronously."""
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        """Exit the context manager."""
        if self.is_running():
            self.stop()

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        """Exit the context manager asynchronously."""
        if self.is_running():
            await self.a_stop()
