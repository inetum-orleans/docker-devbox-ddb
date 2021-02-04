from abc import ABC, abstractmethod
from typing import Optional, Set

from dotty_dict import Dotty

from ddb.config.merger import config_merger
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
    def get_new_value(self, config: Dotty):
        """
        Get property new value, regardless it's defined the new way or the old way.
        :param config: loaded configuration
        :raise KeyError: If no value is found in config.
        """

    @abstractmethod
    def get_old_value(self, config: Dotty):
        """
        Get property old value, regardless it's defined the new way or the old way.
        :param config: loaded configuration
        :raise KeyError: If no value is found in config.
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
        if self.old_config_key in config:
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
        old_value = config.pop(self.old_config_key)
        if old_value is not None:
            transformed_value = self.transformer(old_value, config)
            config[self.new_config_key] = transformed_value

    def get_new_value(self, config: Dotty):
        if self.new_config_key in config:
            return config.get(self.new_config_key)
        if self.old_config_key in config:
            return self.transformer(config.get(self.old_config_key), config)
        raise KeyError

    def get_old_value(self, config: Dotty):
        if self.new_config_key in config:
            return self.rollback_transformer(config.get(self.new_config_key), config)
        if self.old_config_key in config:
            return config.get(self.old_config_key)
        raise KeyError


class MigrationsDotty(Dotty):
    """
    Dotty that supports migrations when requesting deprecated keys and displays deprecation warnings.
    """

    def __init__(self, dictionary=None, namespace=""):
        if dictionary is None:
            dictionary = {}
        self.namespace = namespace
        super().__init__(dictionary)

    def _build_deprecation_dict(self, item):
        migrations = get_migrations_from_old_config_key_startswith(item + ".")
        deprecation_dict = Dotty({})

        for migration in migrations:
            try:
                deprecation_dict[migration.old_config_key[len(item + "."):]] = migration.get_new_value(self)
            except KeyError:
                pass

        return dict(deprecation_dict)

    def raw(self):
        """
        Build a new default Dotty instance using same data.
        :return:
        """
        return Dotty(self._data)

    def __getitem__(self, item):
        if isinstance(item, str):
            property_migration = get_migration_from_old_config_key(item)
            if property_migration:
                if not silent:
                    property_migration.warn()
                try:
                    return property_migration.get_old_value(Dotty(self._data))
                except KeyError:
                    pass
        try:
            value = super().__getitem__(item)
        except KeyError as key_error:
            deprecation_dict = self._build_deprecation_dict(item)
            if deprecation_dict:
                return deprecation_dict
            raise key_error

        if isinstance(value, dict):
            deprecation_dict = self._build_deprecation_dict(item)
            if deprecation_dict:
                value = config_merger.merge(deprecation_dict, value)

        return value


_default_history = (
    PropertyMigration("docker.build_image_tag_from_version",
                      "jsonnet.docker.build.image_tag_from", since="v1.6.0"),
    PropertyMigration("docker.build_image_tag_from",
                      "jsonnet.docker.build.image_tag_from", since="v1.6.0"),
    PropertyMigration("docker.build_image_tag",
                      "jsonnet.docker.build.image_tag", since="v1.6.0"),

    PropertyMigration("docker.cache_from_image",
                      "jsonnet.docker.build.cache_from_image", since="v1.6.0"),
    PropertyMigration("docker.directory",
                      "jsonnet.docker.build.context.base_directory", since="v1.6.0"),

    PropertyMigration("docker.jsonnet.binary_disabled",
                      "jsonnet.docker.binary.disabled", since="v1.6.0"),
    PropertyMigration("docker.jsonnet.virtualhost_disabled",
                      "jsonnet.docker.virtualhost.disabled", since="v1.6.0"),

    PropertyMigration("docker.reverse_proxy.network_id",
                      "jsonnet.docker.virtualhost.network_id", since="v1.6.0"),
    PropertyMigration("docker.reverse_proxy.network_names",
                      "jsonnet.docker.networks.names", since="v1.6.0"),
    PropertyMigration("docker.reverse_proxy.certresolver",
                      "jsonnet.docker.virtualhost.certresolver", since="v1.6.0"),
    PropertyMigration("docker.reverse_proxy.https",
                      "jsonnet.docker.virtualhost.https", since="v1.6.0"),
    PropertyMigration("docker.reverse_proxy.redirect_to_https",
                      "jsonnet.docker.virtualhost.redirect_to_https", since="v1.6.0"),
    PropertyMigration("docker.reverse_proxy.redirect_to_path_prefix",
                      "jsonnet.docker.virtualhost.redirect_to_path_prefix", since="v1.6.0"),

    PropertyMigration("docker.debug.disabled",
                      "jsonnet.docker.xdebug.disabled", since="v1.6.0"),
    PropertyMigration("docker.debug.host",
                      "jsonnet.docker.xdebug.host", since="v1.6.0"),

    PropertyMigration("docker.compose.service_context_root",
                      "jsonnet.docker.build.context.use_project_home", since="v1.6.0"),

    PropertyMigration("docker.compose.service_init",
                      "jsonnet.docker.service.init", since="v1.6.0"),

    PropertyMigration("docker.user.name",
                      "jsonnet.docker.user.name", since="v1.6.0"),
    PropertyMigration("docker.user.group",
                      "jsonnet.docker.user.group", since="v1.6.0"),
    PropertyMigration("docker.user.name_to_uid",
                      "jsonnet.docker.user.name_to_uid", since="v1.6.0"),
    PropertyMigration("docker.user.group_to_gid",
                      "jsonnet.docker.user.group_to_gid", since="v1.6.0"),

    PropertyMigration("docker.registry.name",
                      "jsonnet.docker.registry.name", since="v1.6.0"),
    PropertyMigration("docker.registry.repository",
                      "jsonnet.docker.registry.repository", since="v1.6.0"),

    PropertyMigration("docker.compose.project_name",
                      "jsonnet.docker.compose.project_name", since="v1.6.0"),
    PropertyMigration("docker.compose.network_name",
                      "jsonnet.docker.compose.network_name", since="v1.6.0"),
    PropertyMigration("docker.compose.file_version",
                      "jsonnet.docker.compose.version", since="v1.6.0"),

    PropertyMigration("docker.disabled_services",
                      "jsonnet.docker.compose.excluded_services", since="v1.6.0"),

    PropertyMigration("docker.build_image_tag",
                      "jsonnet.docker.build.image_tag", since="v1.6.0"),
    PropertyMigration("docker.build_image_tag",
                      "jsonnet.docker.build.image_tag_from", since="v1.6.0"),

    PropertyMigration("docker.port_prefix",
                      "jsonnet.docker.expose.port_prefix", since="v1.6.0"),
    PropertyMigration("docker.restart_policy",
                      "jsonnet.docker.service.restart", since="v1.6.0"),

    PropertyMigration("docker.reverse_proxy.type",
                      "jsonnet.docker.virtualhost.disabled", since="v1.6.0",
                      transformer=lambda type, config:
                      type == 'none' or (type is not None and not type),
                      rollback_transformer=lambda disabled, config:
                      config.get('jsonnet.docker.virtualhost.type') if not disabled else 'none'),
)

_history = None
_history_from_old_config_key_dict = None
_history_from_new_config_key_dict = None


def get_history():
    """
    Get migrations history.
    :return:
    """
    global _history  # pylint:disable=global-statement
    return _history


def set_history(history=_default_history):
    """
    Set migrations history.
    """
    global _history, _history_from_old_config_key_dict, _history_from_new_config_key_dict  # pylint:disable=global-statement
    _history = history

    _history_from_old_config_key_dict = {
        migration.old_config_key: migration for migration in history
        if isinstance(migration, AbstractPropertyMigration) and migration.old_config_key
    }

    _history_from_new_config_key_dict = {
        migration.new_config_key: migration for migration in history
        if isinstance(migration, AbstractPropertyMigration) and migration.new_config_key
    }
    _warns.clear()


set_history()


def get_migration_from_old_config_key(old_config_key: str) -> Optional[AbstractPropertyMigration]:
    """
    Get a migration from old config key.
    """
    return _history_from_old_config_key_dict.get(old_config_key)


def get_migration_from_new_config_key(new_config_key: str) -> Optional[AbstractPropertyMigration]:
    """
    Get a migration from new config key.
    """
    return _history_from_new_config_key_dict.get(new_config_key)


def get_migrations_from_old_config_key_startswith(old_config_key_start: str) -> Set[AbstractPropertyMigration]:
    """
    Get all migrations where old_config_key starts with given value
    """
    ret = set()
    for migration in get_history():
        if isinstance(migration, AbstractPropertyMigration) and \
                migration.old_config_key and \
                migration.old_config_key.startswith(old_config_key_start):
            ret.add(migration)
    return ret


def migrate(config: Dotty):
    """
    Migrate all defined migrations in given config data.
    """
    global silent  # pylint:disable=global-statement
    old_silent = silent
    try:
        silent = True
        for migration in get_history():
            if not migration.verify(config):
                migration.migrate(config)
    finally:
        silent = old_silent
