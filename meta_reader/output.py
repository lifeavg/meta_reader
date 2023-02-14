import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol

from meta_reader.file_loader import FileMeta
from meta_reader.settings import settings


@dataclass
class FieldMeta:
    name: str
    max_len: int


class Out(Protocol):

    def create(self) -> list[str]:
        ...


def calculate_field(name: str, files: Iterable[FileMeta], max_len_default: int = 0) -> FieldMeta:
    max_len = len(name)
    for file in files:
        max_len = max(max_len, len(file[name]))
    if max_len_default:
        max_len = min(max_len, max_len_default)
    return FieldMeta(name=name, max_len=max_len)


def normalize_str_len(string: str, target_len: int, extend_char: str = ' ') -> str:
    str_len = len(string)
    if str_len == target_len:
        return string
    elif str_len > target_len:
        return string[:target_len]
    else:
        return string + (extend_char * (target_len - str_len))


class OutTable:

    def __init__(self, fields: Iterable[str], files: Iterable[FileMeta], max_field_len: int) -> None:
        self._fields = [calculate_field(
            key, files, max_field_len) for key in fields]
        self._files = files

    def _header(self) -> list[str]:
        names = ' | '.join(
            [normalize_str_len(field.name, field.max_len) for field in self._fields])
        if names:
            return [names, ('-' * len(names))]
        return []

    def _line(self, file: FileMeta) -> str:
        return ' | '.join([normalize_str_len(file[field.name], field.max_len) for field in self._fields])

    def create(self) -> list[str]:
        table = self._header()
        for file in self._files:
            table.append(self._line(file))
        return table


class OutTsv:
    def __init__(self, fields: Iterable[str], files: Iterable[FileMeta]) -> None:
        self._fields = fields
        self._files = files

    def _header(self) -> str:
        return '\t'.join(self._fields)

    def _line(self, file: FileMeta) -> str:
        return '\t'.join([file[field] for field in self._fields])

    def create(self) -> list[str]:
        tsv = []
        tsv.append(self._header())
        for file in self._files:
            tsv.append(self._line(file))
        return tsv


class OutFieldMeta:

    def __init__(self, file: FileMeta) -> None:
        self._file = file

    def calculate_name_len(self) -> int:
        return max([len(field) for field in self._file.keys()])

    def create(self) -> list[str]:
        out = []
        max_len = self.calculate_name_len()
        for field, value in self._file.items():
            out.append(f'{normalize_str_len(field, max_len)}: '
                       f'{value[:shutil.get_terminal_size().columns - max_len - 1]}')
        return out


class Writer:

    def __init__(self, output: list[str]) -> None:
        self._output = output

    def file(self, file: Path) -> None:
        if not file.is_dir():    
            with file.open(mode='w', encoding=settings.encoding) as out_file:
                if out_file.writable():
                    for line in self._output:
                        out_file.write(line)
                        out_file.write('\n')

    def cli(self) -> None:
        for line in self._output:
            print(line)
