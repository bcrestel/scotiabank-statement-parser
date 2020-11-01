import re
from typing import List

import pandas as pd
from confs.constants import FILE_PATH

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Nov', 'Dec']
STATEMENT_COLUMNS = ['reference', 'transaction_date', 'post_date', 'details', 'amount']

class StatementParser:
    def __init__(self, file_path: str):
        """

        :param file_path: path for the file
        """
        self._file_path = file_path
        self._raw_file = self._read_raw_file(file_path=self._file_path)
        self._statements = self._split_raw_file(self._raw_file)
        for key in self._statements.keys():
            self._statements[key] = self._convert_statement_str_to_pd(self._statements[key])

    def _read_raw_file(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            input_file = file.read()
        return input_file

    def _split_raw_file(self, raw_file: str) -> dict:
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
        for line_number, match in enumerate(index_regex_match):
            if line_number == 0:
                index_line_start = match.start()
                continue
            index_line_end = match.start()
            line = self._parse_single_line(statement[index_line_start:index_line_end])
            all_lines.append(line)
            index_line_start = match.start()
        df_statement = pd.DataFrame(all_lines, columns=STATEMENT_COLUMNS)
        return df_statement

    def _parse_single_line(self, statement_line: str) -> List[str]:
        """
        Split a single line from the statement into the right columns

        :param statement_line: a line from the statement
        :return: split into columns
        """
        space_split = statement_line.split(' ')

        ref = int(space_split[0])

        transaction_date = ' '.join(space_split[1:3])

        post_date = ' '.join(space_split[3:5])

        # find column of the amount
        col_amount = -1
        while len(space_split[col_amount]) < 1:
            col_amount -= 1
        amount = space_split[col_amount]
        amount = self._convert_amount_to_float(amount=amount)

        details = ' '.join(space_split[5:col_amount])
        return ref, transaction_date, post_date, details, amount

    def _convert_amount_to_float(self, amount: str) -> float:
        amount = amount.replace(',','')
        if amount[-1] == '-':
            amount = -1.0 * float(amount[:-1])
        else:
            amount = float(amount)
        return amount


if __name__ == "__main__":
    bb = StatementParser(FILE_PATH)
    print(bb._statements)
