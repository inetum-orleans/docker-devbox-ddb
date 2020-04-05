from _pytest.logging import LogCaptureFixture

from ddb.__main__ import main


class TestErrorHandling:
    def test_invalid_jsonnet(self, project_loader, caplog: LogCaptureFixture):
        project_loader("invalid-jsonnet")

        exceptions = main(["configure"])
        assert len(exceptions) == 1

        messages = list(map(lambda r: r.message, caplog.records))
        assert 'An unexpected error has occured [phase:configure => JsonnetAction.execute()]: ' + \
               'STATIC ERROR: ./invalid.jsonnet:1:1-9: Unknown variable: trololol' in messages
