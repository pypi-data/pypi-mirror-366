from contextvars import ContextVar


trace_id = ContextVar("trace_id", default='')
session_id = ContextVar("session_id", default='')
seq = ContextVar("seq", default=0)
user_id = ContextVar("user_id", default='0')
user_info = ContextVar("user_info", default={})
tenant_id = ContextVar("tenant_id", default=[])
dep_id = ContextVar("dep_id", default=[])

