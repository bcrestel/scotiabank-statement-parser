import os
import pathlib
import re
from typing import List

import numpy as np
import pandas as pd

from confs.constants import FILE_PATH, OUTPUT_DIR

MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
STATEMENT_COLUMNS = ["reference", "transaction_date", "post_date", "details", "amount"]


class StatementParser:
    def __init__(self, file_path: str):
        """

        :param file_path: path for the file
        """
        self._file_path = file_path
        self._raw_file = self._read_raw_file(file_path=self._file_path)
        self._statements = self._split_raw_file(self._raw_file)
        for key in self._statements.keys():
            try:
                self._statements[key] = self._convert_statement_str_to_pd(
                    self._statements[key]
                )
            except ValueError as err:
                print(key)
                print(self._statements[key])
                raise err

    @classmethod
    def convert_to_csv(cls, input_file: str, output_dir: str) -> None:
        """
        Process the input_file and save each statement in output_dir

        :param input_file: intput_file
        :param output_dir: directory where to save the processed statements
        """
        parser = cls(file_path=input_file)
        os.makedirs(output_dir, exist_ok=True)
        for statement_period, statement_activities in parser._statements.items():
            path = pathlib.Path(output_dir, statement_period)
            statement_activities.to_csv(path)

    @staticmethod
    def _read_raw_file(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            input_file = file.read()
        return input_file

    @staticmethod
    def _split_raw_file(raw_file: str) -> dict:
        """
        Split a raw statement file with statements for multiple periods
        into a dict: period -> statement

        :param raw_file: each period in a single str
        :return: dict(str, str)
        """
        input_file = raw_file.split("\n")

        line_count = 0
        statements = {}
        while line_count < len(input_file):
            line = input_file[line_count]
            if len(line) == 0:
                line_count += 1
                continue
            else:
                key = line
                value = input_file[line_count + 1]
                statements.update({key: value})
                line_count += 2
        return statements

    def _convert_statement_str_to_pd(self, statement: str) -> pd.DataFrame:
        """
        Process a single statement and convert to a pd.DataFrame

        :param statement: single-line statement
        :return: Statement in a DataFrame format
        """
        regex_pattern = f"\d\d\d\s+(?:{'|'.join(MONTHS)})"
        index_regex_match = re.finditer(regex_pattern, statement)
        all_lines = []
        index_line_start = 0
        for line_number, match in enumerate(index_regex_match):
            if line_number == 0:
                index_line_start = match.start()
                continue
            index_line_end = match.start()
            line = self._parse_single_line(statement[index_line_start:index_line_end])
            all_lines.append(line)
            index_line_start = match.start()
        df_statement = pd.DataFrame(all_lines, columns=STATEMENT_COLUMNS)
        self._check_pd_converstion(df_statement=df_statement, all_lines=all_lines)
        return df_statement

    @staticmethod
    def _check_pd_converstion(
        df_statement: pd.DataFrame, all_lines: List[List[str]]
    ) -> None:
        """
        Run a few checks on the converted statement

        :param df_statement: statement in a dataframe format
        :param all_lines: all lines parsed
        """
        if len(df_statement) != len(all_lines):
            print(len(df_statement), len(all_lines))
            raise ValueError("Some activities were lost during the conversion")

        references = df_statement["reference"].to_numpy(dtype=float)
        if np.all(references != np.linspace(1, len(all_lines), len(all_lines))):
            print(references)
            print(all_lines)
            raise ValueError("References are not contiguous")

    def _parse_single_line(self, statement_line: str) -> List[str]:
        """
        Split a single line from the statement into the right columns

        :param statement_line: a line from the statement
        :return: split into columns
        """
        space_split = statement_line.split(" ")

        ref = int(space_split[0])

        transaction_date = " ".join(space_split[1:3])

        post_date = " ".join(space_split[3:5])

        # find column of the amount
        col_amount = -1
        while len(space_split[col_amount]) < 1:
            col_amount -= 1
        amount = space_split[col_amount]
        amount = self._convert_amount_to_float(amount=amount)

        details = " ".join(space_split[5:col_amount])
        return ref, transaction_date, post_date, details, amount

    @staticmethod
    def _convert_amount_to_float(amount: str) -> float:
        amount = amount.replace(",", "")
        if amount[-1] == "-":
            amount = -1.0 * float(amount[:-1])
        else:
            amount = float(amount)
        return amount


if __name__ == "__main__":
    StatementParser.convert_to_csv(input_file=FILE_PATH, output_dir=OUTPUT_DIR)
