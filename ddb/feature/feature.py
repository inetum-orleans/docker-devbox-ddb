# -*- coding: utf-8 -*-
from abc import ABC
from os import linesep
from typing import ClassVar, Iterable, Union

from dotty_dict import Dotty, dotty
from marshmallow import ValidationError

from .schema import FeatureSchema
from ..action import Action
from ..binary import Binary
from ..command import Command
from ..config import config
from ..phase import Phase
from ..registry import RegistryObject
from ..service import Service


class Feature(RegistryObject, ABC):  # pylint:disable=abstract-method
    """
    A feature provides phases, commands, binaries, actions and services. It can be configured with a key matching it's
    name in the configuration, and it's configuration should match a given schema.
    """

    @property
    def schema(self) -> ClassVar[FeatureSchema]:
        """
        Configuration schema for this feature.
        """
        return FeatureSchema

    @property
    def phases(self) -> Iterable[Phase]:
        """
        Phases provided by this feature.
        """
        return []

    @property
    def commands(self) -> Iterable[Command]:
        """
        Commands provided by this feature.
        """
        return []

    @property
    def binaries(self) -> Iterable[Binary]:
        """
        Binaries provided by this feature.
        """
        return []

    @property
    def actions(self) -> Iterable[Action]:
        """
        Actions provided by this feature.
        """
        return []

    @property
    def services(self) -> Iterable[Service]:
        """
        Services provided by this feature.
        """
        return []

    @property
    def dependencies(self) -> Iterable[str]:
        """
        Feature dependencies. It should match the name of other features. If may ends with '[optional]' if the
        dependency is optional.
        """
        return []

    def configure(self, bootstrap=False):
        """
        Configure this feature.
        """
        feature_config = config.data.get(self.name)
        try:
            valid_feature_config = self.validate_feature_configuration(feature_config, bootstrap)
        except ValidationError as err:
            raise FeatureConfigurationValidationError(self, err) from err
        config.data[self.name] = valid_feature_config

    def validate_feature_configuration(self, feature_config: Dotty, bootstrap=False):
        """
        Sanitize and validate using given schema part of the configuration.
        """
        schema = self.schema()
        raw_feature_config = feature_config

        if not raw_feature_config:
            raw_feature_config = {}
        feature_config = schema.dump(raw_feature_config)

        if not bootstrap:
            self._configure_defaults(dotty(feature_config))

            feature_config = schema.load(feature_config)
        feature_config = config.apply_environ_overrides(feature_config, config.env_override_prefix + "_" + self.name)

        return feature_config

    def _configure_defaults(self, feature_config: Dotty):
        """
        Override this method to load default values that may depend on the context.
        """

    def before_load(self):
        """
        Invoked before this feature is loaded.
        """

    def after_load(self):
        """
        Invoked after this feature is loaded.
        """

    @property
    def disabled(self):
        """
        Check if this feature is disabled.
        """
        return config.data.get(self.name + '.disabled')


class FeatureConfigurationError(Exception):
    """
    A generic feature configuration error.
    """

    def __init__(self, feature: Feature, *additional_messages: str):
        message = "Feature \"" + feature.name + "\" has invalid configuration."
        for additional_message in additional_messages:
            message += linesep + " " * 2 + additional_message
        super().__init__(message)


class FeatureConfigurationAutoConfigureError(FeatureConfigurationError):
    """
    Feature configuration error raised when something wrongs occurs during auto-configuration.
    """

    def __init__(self, feature: Feature, setting_name: str = None, error: Union[Exception, str] = None):
        super().__init__(feature,
                         setting_name + ": " + "auto-configuration has failed" +
                         (" (" + str(error) + "). " if error else ". ") +
                         "Please configure " + feature.name + "." + setting_name + " manually.")


class FeatureConfigurationReadOnlyError(FeatureConfigurationError):
    """
    Feature configuration error raised when a read-only property is defined in configuration files user.
    """

    def __init__(self, feature: Feature, setting_name: str = None):
        super().__init__(feature,
                         setting_name + ": " + "auto-configuration has failed" +
                         feature.name + "." + setting_name + " is a read-only property computed from other properties "
                                                             "and should not be defined in configuration files.")



class FeatureConfigurationValidationError(FeatureConfigurationError):
    """
    Feature configuration error raised on validation error.
    """

    def __init__(self, feature: Feature, validation_error: ValidationError = None):
        additional_messages = []
        for (field, field_messages) in validation_error.messages.items():
            for field_message in field_messages:
                additional_messages.append("%s: %s" % (field, field_message))
        super().__init__(feature, *additional_messages)
        self.validation_error = validation_error
