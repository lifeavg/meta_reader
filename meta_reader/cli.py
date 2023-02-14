import argparse
from pathlib import Path
from typing import Iterable

from meta_reader.file_loader import FileLoader, FileMeta, MetaReader
from meta_reader.output import Out, OutFieldMeta, OutTable, OutTsv, Writer


class Cli():

    def __init__(self) -> None:
        self.arguments = argparse.ArgumentParser(
            prog='mrd',
            description='Text file metadata parser')

        self.arguments.add_argument(
            '-path', metavar='P', type=Path, default=Path().cwd(),
            nargs='?', help='File or folder with target files')
        self.arguments.add_argument(
            '-out', metavar='O', type=Path, nargs='?', help='Output file')
        self.arguments.add_argument(
            '-type', metavar='T', default='tbl', choices=('tbl', 'tsv'),
            type=str, nargs='?', help='Output type, supported oly for folders')
        self.arguments.add_argument(
            '-column', metavar='C', default=20, type=int, nargs='?',
            help='Column max len for table')

    def _output_dest(self, out: Path) -> Path | None:
        if out and not out.is_dir():
            return out

    def _out_format(
        self,
        format: str,
        col_size: int,
        fields: Iterable[str],
        files: list[FileMeta]
    ) -> Out:
        match format:
            case 'tsv':
                return OutTsv(fields, files)
            case _:
                return OutTable(fields, files, col_size)

    def _write(self, writer: Writer, out: Path | None = None) -> None:
        if out:
            writer.file(out)
        else:
            writer.cli()

    def run(self, raw_args: list[str] | None = None) -> None:
        args = self.arguments.parse_args(raw_args)
        out = self._output_dest(args.out)

        if args.path.is_file() and FileLoader.is_target_file(args.path):
            meta = Writer(OutFieldMeta(
                MetaReader.read_meta(args.path)).create())
            self._write(meta, out)
        elif args.path.is_dir():
            fields, files = MetaReader.load_normalized_meta(args.path)
            out_format = self._out_format(
                args.type, args.column, fields, files)
            self._write(Writer(out_format.create()), out)
        else:
            pass
