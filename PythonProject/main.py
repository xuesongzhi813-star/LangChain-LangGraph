import logging

from fastapi import FastAPI

from app.api.structural import router as structural_router

_applog=logging.getLogger("app")
if not _applog.handlers:
    _fmt = logging.Formatter("%(levelname)s:%(name)s: %(message)s")
    _h=logging.StreamHandler()
    _h.setFormatter(_fmt)
    _applog.addHandler(_h)

app = FastAPI(title="好物优选客服助手")
app.include_router(structural_router)
