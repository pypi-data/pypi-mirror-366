from .._context import GenerationContext


class GenerateError(Exception):
    """Errors during randomly generation.
    """
    def __init__(self, message: str, context: GenerationContext):
        super(GenerateError, self).__init__(message)
        self.context = context


class GenerateConflictError(GenerateError):
    """Conflict errors in the schema during generation

    This error raises if schema conflict is occurred in generation.
    In other words, when no value satisfy the schema, this error is raised.
    However, if a conflict is discovered during the configuration of a Factory, a SchemaConflictError will be raised.
    """
    pass
