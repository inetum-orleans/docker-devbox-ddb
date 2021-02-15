from ddb.feature.core.actions import is_version_greater


class TestCoreFeature:
    def test_is_version_greater(self):
        assert is_version_greater('1.9.2', '1.10.0')
        assert not is_version_greater('1.10.0', '1.9.2')
        assert not is_version_greater('1.10.0', '1.10.0')

        assert is_version_greater('v1.9.2', '1.10.0')
        assert not is_version_greater('v1.10.0', '1.9.2')
        assert not is_version_greater('v1.10.0', '1.10.0')

        assert is_version_greater('1.9.2', 'v1.10.0')
        assert not is_version_greater('1.10.0', 'v1.9.2')
        assert not is_version_greater('1.10.0', 'v1.10.0')

        assert is_version_greater('v1.9.2', 'v1.10.0')
        assert not is_version_greater('v1.10.0', 'v1.9.2')
        assert not is_version_greater('v1.10.0', 'v1.10.0')
