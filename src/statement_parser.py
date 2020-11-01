class StatementParser:
    def __init__(self, file_path: str):
        """

        :param file_path: path for the file
        """
        self._file_path = file_path
        self._raw_file = self._read_raw_file(file_path=self._file_path)
        self._statements = self._split_raw_file(self._raw_file)

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
