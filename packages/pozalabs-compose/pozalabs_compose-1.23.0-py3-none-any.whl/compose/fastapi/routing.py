from fastapi import APIRouter as _FastAPIRouter

_OVERRIDE_DEFAULTS = {"response_model_by_alias": False}
_OVERRIDE_METHODS = {
    "get",
    "post",
    "put",
    "delete",
    "options",
    "head",
    "patch",
    "trace",
    "api_route",
    "add_api_route",
}

APIRouter = _FastAPIRouter

for method_name in _OVERRIDE_METHODS:
    func = getattr(APIRouter, method_name)
    func.__kwdefaults__ = func.__kwdefaults__ | _OVERRIDE_DEFAULTS
