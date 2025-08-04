from typing import Optional

from eopf import EOLogging
from eopf.exceptions.errors import CriticalException, ExceptionWithExitCode


class ErrorPolicy:
    def __init__(self) -> None:
        self._errors: list[Exception] = []
        self._raised_error: Optional[Exception] = None
        self._logger = EOLogging().get_logger("eopf.error_policy")

    def handle(self, exc: Exception) -> None:
        raise NotImplementedError

    def finalize(self) -> None:
        """Optionally raise if needed at end"""
        if self.raised:
            raise self._raised_error
        if len(self.errors) == 0:
            return
        # Create a synthetic exception at the end
        exit_code = 1
        message = ""
        has_critical: bool = False
        for f in self.errors:
            if isinstance(f, ExceptionWithExitCode):
                exit_code = f.exit_code if f.exit_code > exit_code else exit_code
            if isinstance(f, CriticalException):
                has_critical = True
            message += f"{str(f)};"
        if has_critical:
            raise CriticalException(message, exit_code=exit_code)
        else:
            raise ExceptionWithExitCode(message, exit_code=exit_code)

    @property
    def errors(self) -> list[Exception]:
        return self._errors

    @property
    def raised(self) -> bool:
        return self._raised_error is not None


class FailFastPolicy(ErrorPolicy):
    def handle(self, exc: Exception) -> None:
        self.errors.append(exc)
        # In case it has already raised an exception we always raise the initial one
        if self.raised:
            self._logger.error(f"Error occurs while handling a previous error {exc}")
            raise self._raised_error
        self._raised_error = exc
        # All exceptions
        raise exc


class BestEffortPolicy(ErrorPolicy):
    def handle(self, exc: Exception) -> None:
        self.errors.append(exc)
        # In case it has already raised an exception we always raise the initial one
        if self.raised:
            self._logger.error(f"Error occurs while handling a previous error {exc}")
            raise self._raised_error
        # Only our exception get a bypass, all the other ones are re raised
        if not isinstance(exc, ExceptionWithExitCode):
            self._raised_error = exc
            raise exc


class FailOnCriticalPolicy(ErrorPolicy):
    def handle(self, exc: Exception) -> None:
        self.errors.append(exc)
        # In case it has already raised an exception we always raise the initial one
        if self.raised:
            self._logger.error(f"Error occurs while handling a previous error {exc}")
            raise self._raised_error
        if isinstance(exc, CriticalException) or not isinstance(exc, ExceptionWithExitCode):
            self._raised_error = exc
            raise exc


ERROR_POLICY_MAPPING = {
    "FAIL_FAST": FailFastPolicy,
    "FAIL_ON_CRITICAL": FailOnCriticalPolicy,
    "BEST_EFFORT": BestEffortPolicy,
}
