import pytest

from odio import OdioException
from odio.v1_1 import create_spreadsheet


def test_writerow(tmpdir):
    with pytest.raises(
        OdioException,
        match="Version '1.1' isn't supported for creating spreadsheets. Use versions "
        "1.3 or 1.2 instead.",
    ):
        create_spreadsheet()
