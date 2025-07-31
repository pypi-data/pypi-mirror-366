import inspect
import sys
if sys.version_info >= (3, 11):
    # native PEP 654 support
    from builtins import ExceptionGroup
else:
    # backport installed via your env‑marker dependency
    from exceptiongroup import ExceptionGroup
from typing import Any, List, Optional, cast
from .module import no
from .exception import NoBaseException

def _handleEmptyCall(context: Any, isModule: bool) -> None:
    """0) EMPTY CALL: no args, no complaint, no soften"""
    if no.pending.value is not None:
        if no.hideTraceback: raze(no.pending.value)
        raise no.pending.value
    
    if isModule:
        exception = context._makeOne(0, None, [])
        if no.hideTraceback: raze(exception)
        raise exception
    
    if no.hideTraceback: raze(context)
    raise context


def _handleExceptionGroup(context: Any, isModule: bool, codes: List[int], complaint: Optional[str]) -> None:
    """1) EXCEPTION GROUP: single list-of-codes arg"""
    frame = inspect.stack()[1]
    caller = f"{frame.filename}:{frame.lineno}"
    if isModule:
        exceptions = [context._makeOne(c, complaint, []) for c in codes]
    else:
        exceptions = [context.__class__(c, complaint) for c in codes]
        if no.hideTraceback: raze(exceptions[0])
    raise ExceptionGroup("Multiple errors", exceptions)


def _handleSingleCode(
    context: Any,
    isModule: bool,
    code: int,
    complaint: Optional[str],
    soften: bool,
    exception: Optional[BaseException],
    traceback: Any
) -> None:
    """3) SINGLE-CODE CALL: no(code)"""
    # determine soft_flag
    softFlag = (
        context._registry.get(code, (None, "", [], False))[3]
        if isModule
        else context._softCodes.get(code, False)
    )
    # 3a) EARLY ACCUMULATION
    if no.pending.value is not None:
        pending = cast(NoBaseException, no.pending.value)
        defaultMsg = context._registry.get(code, (None, f"Error {code}", [], False))[1]
        pending.addCode(code, defaultMsg)
        if complaint:
            pending.addMessage(code, complaint)
        pending._softCodes[code] = softFlag
        # re-save pending to ensure modifications persist
        no.pending.value = pending
        return
    # 3b) MODULE-PROPAGATION
    if isModule and isinstance(exception, NoBaseException):
        e = exception  # type: NoBaseException
        context.propagate(e, code)
        if complaint:
            e.addMessage(code, complaint)
        e._softCodes[code] = softFlag
        if softFlag or soften:
            no.pending.value = e
            return
        if no.hideTraceback: raze(e)
        raise e
    # 3c) INSTANCE-PROPAGATION
    if not isModule and isinstance(context, NoBaseException):
        defaultMsg = no._registry.get(code, (None, f"Error {code}", [], False))[1]
        context.addCode(code, defaultMsg)
        if complaint:
            context.addMessage(code, complaint)
        context._softCodes[code] = softFlag
        if softFlag or soften:
            no.pending.value = context
            return
        if no.hideTraceback: raze(context)
        raise context
    # 3d) FRESH NEW EXCEPTION
    frame = inspect.stack()[1]
    caller = f"{frame.filename}:{frame.lineno}"
    exc = (
        context._makeOne(code, complaint, [])
        if isModule
        else context.__class__(code, complaint)
    )
    if softFlag or soften:
        no.pending.value = exc
        return
    if no.hideTraceback: raze(exc)
    raise exc


def _handleCodeExceptionLink(
    context: Any,
    isModule: bool,
    code: int,
    exception: BaseException,
    complaint: Optional[str],
    soften: bool,
    traceback: Any
) -> None:
    """4) CODE+EXCEPTION LINK: no(code, exc)"""
    softFlag = (
        context._registry.get(code, (None, "", [], False))[3]
        if isModule
        else context._softCodes.get(code, False)
    )
    print(f"Handling code exception link for code {code} with soft flag {softFlag}")
    if isModule:
        exc = context._makeOne(code, complaint, [exception])
        if softFlag or soften:
            no.pending.value = exc
            return
        if no.hideTraceback: raze(exc)
        raise exc
    else:
        defaultMsg = context._registry.get(code, (None, f"Error {code}", [], False))[1]
        context.addCode(code, defaultMsg)
        context._recordLinkedException(exception)
        if softFlag or soften:
            no.pending.value = context
            return
        if no.hideTraceback: raze(context)
        raise context


def _handleCodeMessage(
    context: Any,
    isModule: bool,
    code: int,
    complaint: str,
    soften: bool,
    traceback: Any
) -> None:
    """5) CODE+MESSAGE: no(code, custom_msg)"""
    softFlag = (
        context._registry.get(code, (None, "", [], False))[3]
        if isModule
        else context._softCodes.get(code, False)
    )
    if no.pending.value is not None:
        pending = cast(NoBaseException, no.pending.value)
        defaultMsg = context._registry.get(code, (None, f"Error {code}", [], False))[1]
        pending.addCode(code, defaultMsg)
        pending.addMessage(code, complaint)
        pending._softCodes[code] = softFlag
        # persist updated pending block
        no.pending.value = pending
        return
    if not isModule and isinstance(context, NoBaseException):
        context.addCode(code, no._registry.get(code, (None, "", [], False))[1])
        context.addMessage(code, complaint)
        context._softCodes[code] = softFlag
        if softFlag or soften:
            no.pending.value = context
            return
        if no.hideTraceback: raze(context)
        raise context
    frame = inspect.stack()[1]
    caller = f"{frame.filename}:{frame.lineno}"
    exc = (
        context._makeOne(code, complaint, [])
        if isModule
        else context.__class__(code, complaint)
    )
    if softFlag or soften:
        no.pending.value = exc
        return
    if no.hideTraceback: raze(exc)
    raise exc


def _handleCall(context: Any, isModule: bool, *args: Any, complaint: Optional[str]=None, soften: bool=False) -> None:
    """Router for no() calls"""
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    # 0) empty
    if not args and complaint is None and not soften:
        return _handleEmptyCall(context, isModule)
    # 1) exception group
    if len(args) == 1 and isinstance(args[0], list):
        return _handleExceptionGroup(context, isModule, args[0], complaint)
    # 2) noop for raw exceptions
    if len(args) == 1 and isinstance(args[0], BaseException):
        return
    # 3) single code
    if len(args) == 1 and isinstance(args[0], int):
        return _handleSingleCode(context, isModule, args[0], complaint, soften, exceptionValue, exceptionTraceback)
    # 4) code + exception
    if len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], BaseException):
        return _handleCodeExceptionLink(context, isModule, args[0], args[1], complaint, soften, exceptionTraceback)
    # 5) code + message
    if len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], str):
        return _handleCodeMessage(context, isModule, args[0], args[1], soften, exceptionTraceback)
    # fallback
    raise TypeError(f"Unsupported arguments for no(): {args}")

def raze(exception: NoBaseException) -> None:
    """Raise the no.way."""
    print(exception)
    sys.exit(1)