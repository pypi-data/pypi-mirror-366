from ranjg._context import SchemaContext


class SchemaConflictError(Exception):
    """Conflict errors in the schema.

    This error raises if the schema has conflict.
    In other words, when no value satisfy the schema, this error is raised.

    When the schema is invalid (exp: ``schema.type`` is illegal string), ``InvalidSchemaError`` is raised.
    """
    def __init__(self, message: str, context: SchemaContext):
        super(Exception, self).__init__(message)
        self.context = context
