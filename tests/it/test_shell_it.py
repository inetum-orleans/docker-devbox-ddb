import re
from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture
from ddb.__main__ import main


@pytest.mark.skipif("os.name == 'nt'")
class TestBashShell:
    def test_export_special_chars(self, capsys: CaptureFixture, project_loader):
        project_loader("export-special-chars")

        main(["configure"])

        main(["activate"])

        outerr = capsys.readouterr()
        script_lines = Path(outerr.out.split()[1].strip()).read_text().splitlines()
        matches = [re.match('export (.+)=.*$', x) for x in script_lines]
        matches = [x for x in matches if x]

        for match in matches:
            if match:
                assert '/' not in match.group(1)
