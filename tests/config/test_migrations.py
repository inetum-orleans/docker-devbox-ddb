import re

from _pytest.logging import LogCaptureFixture

from ddb.config import migrations
from ddb.config.migrations import PropertyMigration, MigrationsDotty


class TestWarnDeprecatedDotty:
    def teardown_method(self, test_method):
        migrations.set_history()

    def test_warn_deprecated_simple(self, caplog: LogCaptureFixture):
        history = (
            PropertyMigration("old_property",
                              "new_property", since="v1.1.0"),
        )

        migrations.set_history(history)

        data = MigrationsDotty({
            "old_property": "value"
        })

        migrations.migrate(data)

        assert data.get("old_property") == "value"
        assert data.get("new_property") == "value"

        logs = caplog.text

        assert re.match(
            r"WARNING .*\"old_property\" configuration property is deprecated since v1\.1\.0 and will be removed "
            r"in a future major release\. You should use \"new_property\" instead\.", logs)

    def test_warn_deprecated_deep(self, caplog: LogCaptureFixture):
        history = (
            PropertyMigration("some.namespace.old_property",
                              "another.namespace.new_property"),
        )

        migrations.set_history(history)

        data = MigrationsDotty()
        data["some.namespace.old_property"] = "value"

        migrations.migrate(data)

        assert data.get("some.namespace.old_property") == "value"
        assert data.get("another.namespace.new_property") == "value"

        assert data.get("some").get("namespace").get("old_property") == "value"
        assert data.get("another").get("namespace").get("new_property") == "value"

        assert data.get("some.namespace").get("old_property") == "value"
        assert data.get("another.namespace").get("new_property") == "value"

        logs = caplog.text

        assert re.match(
            r"WARNING .*\"some.namespace.old_property\" configuration property is deprecated and will be removed "
            r"in a future major release\. You should use \"another.namespace.new_property\" instead\.", logs)

    def test_compat_deep(self, caplog: LogCaptureFixture):
        history = (
            PropertyMigration("some.namespace.old_property",
                              "another.namespace.new_property"),
        )

        migrations.set_history(history)

        data = MigrationsDotty()
        data["another.namespace.new_property"] = "value"

        assert data.get("some.namespace.old_property") == "value"
        assert data.get("another.namespace.new_property") == "value"

        assert data.get("some").get("namespace").get("old_property") == "value"
        assert data.get("another").get("namespace").get("new_property") == "value"

        assert data.get("some.namespace").get("old_property") == "value"
        assert data.get("another.namespace").get("new_property") == "value"

        logs = caplog.text

        assert re.match(
            r"WARNING .*\"some.namespace.old_property\" configuration property is deprecated and will be removed "
            r"in a future major release\. You should use \"another.namespace.new_property\" instead\.", logs)

    def test_compat_deep_merge(self, caplog: LogCaptureFixture):
        history = (
            PropertyMigration("some.namespace.old_property",
                              "another.namespace.new_property"),
        )

        migrations.set_history(history)

        data = MigrationsDotty()
        data["another.namespace.new_property"] = "value"
        data["some.namespace.another"] = "foo"

        assert data.get("some.namespace.another") == "foo"
        assert data.get("some.namespace.old_property") == "value"
        assert data.get("another.namespace.new_property") == "value"

        assert data.get("some").get("namespace").get("another") == "foo"
        assert data.get("some").get("namespace").get("old_property") == "value"
        assert data.get("another").get("namespace").get("new_property") == "value"

        logs = caplog.text

        assert re.match(
            r"WARNING .*\"some.namespace.old_property\" configuration property is deprecated and will be removed "
            r"in a future major release\. You should use \"another.namespace.new_property\" instead\.", logs)
