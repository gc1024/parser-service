# Stub: canvas service removed - agent system not available
import logging


class CanvasTemplateService:
    model = None

    @classmethod
    def get_all(cls):
        return []


class UserCanvasService:
    model = None

    @classmethod
    def get_by_id(cls, id):
        return False, None

    @classmethod
    def query(cls, **kwargs):
        return []
