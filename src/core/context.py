from contextvars import ContextVar

permissions_var = ContextVar("permissions", default=[])
