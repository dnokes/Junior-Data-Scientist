"""Compat wrapper so both `carms.main:app` and `carms.api.main:app` work."""

from carms.api.main import app, create_app

__all__ = ["app", "create_app"]
