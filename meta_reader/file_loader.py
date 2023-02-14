from pathlib import Path
from typing import Generator, Iterable
from unicodedata import normalize

from meta_reader.char_mapper import to_en_chars
from meta_reader.settings import settings

FileMeta = dict[str, str]


class FileLoader:

    @staticmethod
    def load_files(folder: Path) -> Generator[Path, None, None]:
        if folder.is_dir():
            for item in folder.iterdir():
                if item.is_file():
                    yield item

    @staticmethod
    def is_target_file(file: Path) -> bool:
        if file.suffix.lower() == settings.suffix:
            return True
        return False


class MetaReader:

    @staticmethod
    def is_last(line: str) -> bool:
        parts = line.split(settings.divider)
        if len(parts) > 0 and parts[0].strip().lower() == 'scenario':
            return True
        return False

    @staticmethod
    def read_meta(file: Path) -> FileMeta:
        file_meta = {}
        file_meta['fileName'] = file.name
        with file.open(mode='r', encoding=settings.encoding) as file_data:
            for line in file_data.readlines():
                parts = to_en_chars(normalize('NFC', line)
                                    ).strip().split(settings.divider)
                if len(parts) > 0 and parts[0]:
                    file_meta[parts[0].strip()] = settings.divider.join(
                        parts[1:]).strip()
                if MetaReader.is_last(line):
                    break
        return file_meta

    @staticmethod
    def aggregate_keys(files: Iterable[FileMeta]) -> set[str]:
        all_keys: set[str] = set()
        for file_meta in files:
            all_keys |= set(file_meta.keys())
        return all_keys

    @staticmethod
    def add_missing_keys(file: FileMeta, keys: Iterable[str]) -> FileMeta:
        missing_keys: set[str] = set(keys) - set(file.keys())
        result_file = dict(file)
        if missing_keys:
            for key in missing_keys:
                result_file[key] = settings.undefined
        return result_file

    @staticmethod
    def load_normalized_meta(folder: Path) -> tuple[set[str], list[FileMeta]]:
        files = [MetaReader.read_meta(file) for file in FileLoader.load_files(
            folder) if FileLoader.is_target_file(file)]
        all_keys = MetaReader.aggregate_keys(files)
        files_all_fields = [MetaReader.add_missing_keys(
            file, all_keys) for file in files]
        return all_keys, files_all_fields
