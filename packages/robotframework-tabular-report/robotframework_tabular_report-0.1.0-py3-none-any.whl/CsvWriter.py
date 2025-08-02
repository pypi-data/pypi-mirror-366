import csv
from os import linesep
from typing import Any, List, TextIO

from BaseWriter import BaseWriter


class CsvWriter(BaseWriter):
    file_extension: str = "csv"
    default_delim: str = ","

    def __init__(
        self, output_filename: str, format_specifier: str = None, docs_max_len: Any = None, delim: str = None
    ) -> None:
        if not delim:
            self.delim = CsvWriter.default_delim
        else:
            self.delim = "\t" if delim == "TAB" else delim

        super().__init__(output_filename, format_specifier, docs_max_len)

    def open_output_file(self, output_filename: str) -> None:
        self.file: TextIO = open(".".join([output_filename, CsvWriter.file_extension]), encoding="UTF-8", mode="w")
        self.writer = csv.writer(self.file, delimiter=self.delim)

    def __del__(self, *_) -> None:
        if hasattr(self, "file") and self.file:
            self.file.close()
            super().print_success(self.file.name)

    def write_data(self, data: List[str]) -> None:
        row: List[str] = [" ".join(entry.replace(linesep, " ").split()) for entry in data]
        self.writer.writerow(row)

    write_header = write_data
