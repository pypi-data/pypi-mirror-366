# RERO-Invenio-Files
# Copyright (C) 2024 RERO.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Pdf support for the RERO invenio instances."""

import os

from fpdf import FPDF


class PDFGenerator(FPDF):
    """Generate a PDF file from a given data."""

    def __init__(self, data, *arg, **kwargs):
        """Create a PDFGenerator object.

        Example of input data:
        .. code-block:: python
            data = dict(
                header='Header',
                title='Simple Title',
                authors=['Author1, Author2'],
                summary='Summary'
            )
        :param data: dict - the given data.
        """
        self.data = data
        font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        super().__init__(*arg, **kwargs)
        self.add_font(
            "NotoSans",
            style="",
            fname=os.path.join(font_dir, "NotoSans-Regular.ttf"),
            uni=True,
        )
        self.add_font(
            "NotoSans",
            style="I",
            fname=os.path.join(font_dir, "NotoSans-Italic.ttf"),
            uni=True,
        )

    def header(self):
        """Generate the header page."""
        self.set_font("NotoSans", size=14)
        self.cell(
            0,
            10,
            self.data.get("header", "Generated using RERO Invenio Files"),
            align="R",
            border="B",
        )
        self.ln(20)

    def render(self):
        """Render the main pdf page body."""
        self.add_page()
        if title := self.data.get("title"):
            self.set_font("NotoSans", size=24)
            self.multi_cell(0, 8, title, align="C")
            self.ln(4)

        if authors := self.data.get("authors"):
            self.set_font("NotoSans", "I", size=14)
            self.multi_cell(0, 6, "; ".join(authors), padding=(0, 50, 0), align="C")
            self.ln(4)

        if summary := self.data.get("summary"):
            self.set_font("NotoSans", size=12)
            self.multi_cell(0, 5, summary, padding=(0, 20, 0))

    def footer(self):
        """Generate the page footer."""
        self.set_y(-15)
        self.set_font("NotoSans", "I", 8)
        # printing the page number
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C", border="T")
