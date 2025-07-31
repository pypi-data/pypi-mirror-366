import structlog

from psenv.core.context import Context
from psenv.core.diff import ParameterDiff
from psenv.error_handling.exceptions import PsenvCLIError


class Synchronizer:
    def __init__(self, ctx: Context, param_diff: ParameterDiff, mode: str, dry_run: bool) -> None:
        self.ctx = ctx
        self.param_diff = param_diff
        self.mode = mode
        self.dry_run = dry_run
        self.logger = structlog.getLogger("psenv.synchronizer")

    def sync(self):
        if self._is_nothing_to_do():
            return

        if self.dry_run:
            self.execute_dry_run()
            return

        self.execute()

    def execute_dry_run(self) -> None:
        if self.mode == "add":
            self._log_dry_run_to_add()

        elif self.mode == "update":
            self._log_dry_run_to_add()
            self._log_dry_run_to_update()

        elif self.mode == "sync":
            self._log_dry_run_to_add()
            self._log_dry_run_to_update()
            self._log_dry_run_to_remove()
        else:
            raise PsenvCLIError(f"Invalid mode: {self.mode}. Must be one of 'add', 'update', or 'sync'.")

    def execute(self) -> None:
        if self.mode == "add":
            self._add_parameters()

        elif self.mode == "update":
            self._add_parameters()
            self._update_parameters()

        elif self.mode == "sync":
            self._add_parameters()
            self._update_parameters()
            self._delete_parameters()
        else:
            raise PsenvCLIError(f"Invalid mode: {self.mode}. Must be one of 'add', 'update', or 'sync'.")

    def _is_nothing_to_do(self) -> bool:
        if not self.param_diff.to_add and not self.param_diff.to_update and not self.param_diff.to_remove:
            self.logger.info("No parameters to add, update, or remove. Everything is up to date.")
            return True
        return False

    def _add_parameters(self) -> None:
        self.ctx.ps_client.put_parameters(self.param_diff.to_add)

    def _update_parameters(self) -> None:
        self.ctx.ps_client.put_parameters(self.param_diff.to_update, overwrite=True)

    def _delete_parameters(self) -> None:
        self.ctx.ps_client.delete_parameters(self.param_diff.to_remove)

    def _log_dry_run_to_add(self) -> None:
        for key in self.param_diff.to_add.keys():
            self.logger.info("[DRY RUN] Would add parameters: %s", key)

    def _log_dry_run_to_update(self) -> None:
        for key in self.param_diff.to_update.keys():
            self.logger.info("[DRY RUN] Would update parameters: %s", key)

    def _log_dry_run_to_remove(self) -> None:
        for key in self.param_diff.to_remove.keys():
            self.logger.info("[DRY RUN] Would remove parameters: %s", key)

    @staticmethod
    def get_mode_from_cliargs(cliargs) -> str:
        return Synchronizer.get_mode_from_flags(cliargs.add, cliargs.update, cliargs.sync)

    @staticmethod
    def get_mode_from_flags(add: bool, update: bool, sync: bool) -> str:
        flags = [add, update, sync]
        if sum(flags) != 1:
            raise ValueError("Exactly one of --add, --update, or --sync must be set.")
        if add:
            return "add"
        if update:
            return "update"
        if sync:
            return "sync"
        raise PsenvCLIError("Invalid mode flags.")
