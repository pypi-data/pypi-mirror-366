from os import linesep
from typing import Any, List

from BaseWriter import BaseWriter
from xlsxwriter import Workbook, format, worksheet

EXCEL_MAX_ROWS = 1_048_575


class XlsWriter(BaseWriter):
    file_extension = "xlsx"
    default_colored_status = True

    def __init__(
        self,
        output_filename: str,
        format_specifier: str = None,
        docs_max_len: Any = None,
        colored_status: bool = None,
        colored_rows: bool = False,
    ) -> None:
        self.colored_status: bool = colored_status if colored_status else XlsWriter.default_colored_status
        self.colored_rows: bool = colored_rows
        if type(self.colored_status) != bool:
            raise RuntimeError("Value of 'colored_status' parameter should be Truthy/Falsey.")
        if type(self.colored_rows) != bool:
            raise RuntimeError("Value of 'colored_rows' parameter should be Truthy/Falsey.")

        super().__init__(output_filename, format_specifier, docs_max_len)

        if self.colored_status or self.colored_rows:
            self.green: format.Format = self.file.add_format({"bg_color": "#C6EFCE", "font_color": "#006100"})
            self.red: format.Format = self.file.add_format(
                {"bg_color": "#FFC7CE", "font_color": "#9C0006", "bold": True}
            )

    def open_output_file(self, output_filename: str) -> None:
        self.file: Workbook = Workbook(
            ".".join([output_filename, XlsWriter.file_extension]), options={"strings_to_numbers": True}
        )
        self.writer: worksheet.Worksheet = self.file.add_worksheet()
        self.row_index: int = 0

    def __del__(self, *_) -> None:
        if hasattr(self, "file") and self.file:
            if self.colored_status and not self.colored_rows:
                self.add_conditional_formatting(self.status_index)
            self.file.close()
            super().print_success(self.file.filename)

    def write_header(self, data: List[str]):
        self.write_data(data)
        if "Status" in data:
            self.status_index = data.index("Status")

    def add_conditional_formatting(self, col: int):
        col_range = (1, col, EXCEL_MAX_ROWS, col)
        self.writer.conditional_format(
            *col_range, {"type": "cell", "criteria": "equal to", "value": '"PASS"', "format": self.green}
        )
        self.writer.conditional_format(
            *col_range, {"type": "cell", "criteria": "equal to", "value": '"FAIL"', "format": self.red}
        )

    def write_data(self, data: List[str]) -> None:
        row: List[str] = [" ".join(entry.replace(linesep, " ").split()) for entry in data]
        if self.colored_rows and hasattr(self, "status_index"):
            format = self.green if row[self.status_index] == "PASS" else self.red
        else:
            format = None
        self.writer.write_row(self.row_index, 0, row, cell_format=format)
        self.row_index += 1
