# exceptions.py

class ResolveError(Exception):
    """
        Raised when path resolution fails.
    """
    pass


class TemplateNotFoundError(Exception):
    """
        Raised when a named template is not found.
    """
    pass


class HookExecutionError(Exception):
    """
        Raised when a before/after hook fails.
    """
    pass


class InvalidTemplateError(Exception):
    """
        Raised when a template is invalid or incomplete.
    """
    pass


class ContextValidationError(Exception):
    """
        Raised when a context fails validation for a template.
    """
    pass
