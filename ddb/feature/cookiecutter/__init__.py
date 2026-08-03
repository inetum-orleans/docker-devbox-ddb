from collections.abc import Iterable
from typing import Any

from dotty_dict import Dotty

from ddb.action import Action
from ddb.feature import Feature

from .actions import CookiecutterAction
from .schema import CookiecutterFeatureSchema


class CookiecutterFeature(Feature):
    """
    Generate code from a cookiecutter template available on github (https://cookiecutter.readthedocs.io).
    """

    @property
    def name(self) -> str:
        return "cookiecutter"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core"]

    @property
    def schema(self) -> type[CookiecutterFeatureSchema]:
        return CookiecutterFeatureSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (CookiecutterAction(),)

    def _configure_defaults(self, feature_config: Dotty) -> None:
        if "templates" in feature_config:
            feature_config["templates"] = [self._sanitize_template(t) for t in feature_config["templates"]]

    @staticmethod
    def _sanitize_template(template: dict[str, Any]) -> dict[str, Any]:
        if template.get("output_dir"):
            template["extra_context"] = {"directory": "."}
        return template
