from abc import ABC, abstractmethod
from typing import Optional

from dotty_dict import Dotty

from ddb.context import context

silent = False
_warns = set()


class AbstractDeprecation(ABC):
    """
    Abstract deprecation.
    """

    def warn(self, source=None):
        """
        Display deprecated warning.
        """


class AbstractMigration(AbstractDeprecation):
    """
    Abstract migration.
    """

    @abstractmethod
    def verify(self, config: Dotty) -> bool:
        """
        Verify the given configuration with this migration.
        :param config: loaded configuration
        :return: True if migration should be applied, else otherwise
        """

    @abstractmethod
    def migrate(self, config: Dotty):
        """
        Apply changes on configuration to make it work with latest changes.
        :param config: loaded configuration
        """

    @abstractmethod
    def compat(self, config: Dotty):
        """
        Apply changes on configuration to ensure backward compatibility of projects.
        :param config: loaded configuration
        """


class AbstractPropertyMigration(AbstractMigration):
    """
    Abstract migration based on single move/rename.
    """

    @property
    @abstractmethod
    def old_config_key(self) -> str:
        """
        Old property configuration key
        """

    @property
    @abstractmethod
    def new_config_key(self) -> str:
        """
        New property configuration key
        """

    @property
    @abstractmethod
    def requires_value_migration(self) -> bool:
        """
        Does this migration change the value of configuration when migrating to new config key.
        """


class PropertyMigration(AbstractPropertyMigration):
    """
    Migration based on single move/rename. Value can be changed using an optional transformer function.
    """

    def __init__(self,
                 old_config_key,
                 new_config_key,
                 transformer=None,
                 rollback_transformer=None,
                 since=None,
                 removed_in="a future major release"):
        self._default_transformer = lambda value, config: value
        self._old_config_key = old_config_key
        self._new_config_key = new_config_key
        self.transformer = transformer if transformer else self._default_transformer
        self.rollback_transformer = rollback_transformer if rollback_transformer else self._default_transformer
        self.since = since
        self.removed_in = removed_in

    @property
    def old_config_key(self):
        return self._old_config_key

    @property
    def new_config_key(self):
        return self._new_config_key

    @property
    def requires_value_migration(self):
        return self.transformer != self._default_transformer

    def verify(self, config: Dotty):
        if self.old_config_key in config and \
                config.get(self.new_config_key) != self.transformer(config.get(self.old_config_key), config):
            self.warn()
            return False
        return True

    def warn(self, source=None):
        if not silent:
            since_message = f" since {self.since}" if self.since else ""
            source_message = f" (in \"{source}\")." if source else "."

            message = "[deprecated] " + \
                      f"\"{self.old_config_key}\" configuration property is deprecated{since_message} " \
                      f"and will be removed in {self.removed_in}. " + \
                      f"You should use \"{self.new_config_key}\" instead{source_message}"

            if message not in _warns:
                _warns.add(message)
                context.log.warning(message)

    def migrate(self, config: Dotty):
        if self.old_config_key in config:
            transformed_value = self.transformer(config.get(self.old_config_key), config)
            if config.get(self.new_config_key) != transformed_value:
                config[self.new_config_key] = transformed_value

    def compat(self, config: Dotty):
        if self.new_config_key in config:
            transformed_value = self.rollback_transformer(config.get(self.new_config_key), config)
            if config.get(self.old_config_key) != transformed_value:
                config[self.old_config_key] = transformed_value


class WarnDeprecatedDotty(Dotty):
    """
    Dotty that display deprecation warnings when accessing deprecated keys.
    """

    def __init__(self, dictionary=None):
        if dictionary is None:
            dictionary = {}
        super().__init__(dictionary)

    def __getitem__(self, item):
        if not silent:
            if isinstance(item, str):
                property_migration = get_migration_from_old_config_key(item)
                if property_migration:
                    property_migration.warn()
        return super().__getitem__(item)


history = (
    PropertyMigration("docker.build_image_tag_from_version",
                      "jsonnet.docker.build.image_tag_from", since="v1.5.x"),
    PropertyMigration("docker.build_image_tag_from",
                      "jsonnet.docker.build.image_tag_from", since="v1.5.x"),
    PropertyMigration("docker.build_image_tag",
                      "jsonnet.docker.build.image_tag", since="v1.5.x"),

    PropertyMigration("docker.cache_from_image",
                      "jsonnet.docker.build.cache_from_image", since="v1.5.x"),
    PropertyMigration("docker.directory",
                      "jsonnet.docker.build.context.base_directory", since="v1.5.x"),

    PropertyMigration("docker.jsonnet.binary_disabled",
                      "jsonnet.docker.binary.disabled", since="v1.5.x"),
    PropertyMigration("docker.jsonnet.virtualhost_disabled",
                      "jsonnet.docker.virtualhost.disabled", since="v1.5.x"),

    PropertyMigration("docker.reverse_proxy.network_id",
                      "jsonnet.docker.virtualhost.network_id", since="v1.5.x"),
    PropertyMigration("docker.reverse_proxy.network_names",
                      "jsonnet.docker.networks.names", since="v1.5.x"),
    PropertyMigration("docker.reverse_proxy.certresolver",
                      "jsonnet.docker.virtualhost.certresolver", since="v1.5.x"),
    PropertyMigration("docker.reverse_proxy.https",
                      "jsonnet.docker.virtualhost.https", since="v1.5.x"),
    PropertyMigration("docker.reverse_proxy.redirect_to_https",
                      "jsonnet.docker.virtualhost.redirect_to_https", since="v1.5.x"),
    PropertyMigration("docker.reverse_proxy.redirect_to_path_prefix",
                      "jsonnet.docker.virtualhost.redirect_to_path_prefix", since="v1.5.x"),

    PropertyMigration("docker.debug.disabled",
                      "jsonnet.docker.xdebug.disabled", since="v1.5.x"),
    PropertyMigration("docker.debug.host",
                      "jsonnet.docker.xdebug.host", since="v1.5.x"),

    PropertyMigration("docker.compose.service_context_root",
                      "jsonnet.docker.build.context.use_project_home", since="v1.5.x"),

    PropertyMigration("docker.compose.service_init",
                      "jsonnet.docker.service.init", since="v1.5.x"),

    PropertyMigration("docker.user.name",
                      "jsonnet.docker.user.name", since="v1.5.x"),
    PropertyMigration("docker.user.group",
                      "jsonnet.docker.user.group", since="v1.5.x"),
    PropertyMigration("docker.user.name_to_uid",
                      "jsonnet.docker.user.name_to_uid", since="v1.5.x"),
    PropertyMigration("docker.user.group_to_gid",
                      "jsonnet.docker.user.group_to_gid", since="v1.5.x"),

    PropertyMigration("docker.registry.name",
                      "jsonnet.docker.registry.name", since="v1.5.x"),
    PropertyMigration("docker.registry.repository",
                      "jsonnet.docker.registry.repository", since="v1.5.x"),

    PropertyMigration("docker.compose.project_name",
                      "jsonnet.docker.compose.project_name", since="v1.5.x"),
    PropertyMigration("docker.compose.network_name",
                      "jsonnet.docker.compose.network_name", since="v1.5.x"),
    PropertyMigration("docker.compose.file_version",
                      "jsonnet.docker.compose.version", since="v1.5.x"),

    PropertyMigration("docker.path_mapping",
                      "jsonnet.docker.path_mapping", since="v1.5.x"),
    PropertyMigration("docker.disabled_services",
                      "jsonnet.docker.compose.excluded_services", since="v1.5.x"),

    PropertyMigration("docker.build_image_tag",
                      "jsonnet.docker.build.image_tag", since="v1.5.x"),
    PropertyMigration("docker.build_image_tag",
                      "jsonnet.docker.build.image_tag_from", since="v1.5.x"),

    PropertyMigration("docker.port_prefix",
                      "jsonnet.docker.expose.port_prefix", since="v1.5.x"),
    PropertyMigration("docker.restart_policy",
                      "jsonnet.docker.service.restart", since="v1.5.x"),

    PropertyMigration("docker.reverse_proxy.type",
                      "jsonnet.docker.virtualhost.disabled", since="v1.5.x",
                      transformer=lambda type, config:
                      type == 'none',
                      rollback_transformer=lambda disabled, config:
                      config.get('jsonnet.docker.virtualhost.type') if not disabled else 'none'),
)

_history_from_old_config_key_dist = {migration.old_config_key: migration for migration in history
                                     if isinstance(migration, AbstractPropertyMigration) and migration.old_config_key}

_history_from_new_config_key_dist = {migration.new_config_key: migration for migration in history
                                     if isinstance(migration, AbstractPropertyMigration) and migration.new_config_key}


def get_migration_from_old_config_key(old_config_key: str) -> Optional[AbstractPropertyMigration]:
    """
    Get a migration from old config key.
    """
    return _history_from_old_config_key_dist.get(old_config_key)


def get_migration_from_new_config_key(new_config_key: str) -> Optional[AbstractPropertyMigration]:
    """
    Get a migration from new config key.
    """
    return _history_from_new_config_key_dist.get(new_config_key)


def migrate(config: Dotty):
    """
    Migrate all defined migrations in given config data.
    """
    global silent  # pylint:disable=global-statement
    old_silent = silent
    try:
        silent = True
        for migration in history:
            if not migration.verify(config):
                migration.migrate(config)
            migration.compat(config)
    finally:
        silent = old_silent


def compat(config: Dotty):
    """
    Compat all defined migrations in given config data.
    """
    global silent  # pylint:disable=global-statement
    old_silent = silent
    try:
        silent = True
        for migration in history:
            migration.compat(config)
    finally:
        silent = old_silent
