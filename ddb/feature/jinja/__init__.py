from collections.abc import Iterable

from dotty_dict import Dotty

from ddb.action import Action
from ddb.feature import Feature

from ...utils.file import TemplateFinder
from .actions import JinjaAction
from .schema import JinjaSchema


class JinjaFeature(Feature):
    """
    Render template files with Jinja (https://jinja.palletsprojects.com).
    """

    @property
    def name(self) -> str:
        return "jinja"

    @property
    def dependencies(self) -> Iterable[str]:
        return ["core", "file"]

    @property
    def schema(self) -> type[JinjaSchema]:
        return JinjaSchema

    @property
    def actions(self) -> Iterable[Action]:
        return (JinjaAction(),)

    def _configure_defaults(self, feature_config: Dotty) -> None:
        includes = feature_config.get("includes")
        if includes is None:
            includes = TemplateFinder.build_default_includes_from_suffixes(
                feature_config["suffixes"], feature_config["extensions"]
            )
            feature_config["includes"] = includes
