from io import BytesIO

from odio import parse_document
from odio.v1_3 import create_spreadsheet


def test_parse_document():
    sheet = create_spreadsheet()
    with BytesIO() as f:
        sheet.save(f)
        f.seek(0)
        parse_document(f)
