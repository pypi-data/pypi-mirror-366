import argparse, logging, os, shutil, sys, tempfile
from pathlib import Path
from typing import Any
from warnings import warn

from .out import Maker


def version() -> str:
    try:
        from ._version import version

        return str(version)
    except ImportError:
        return "0.0.0"


def enable_weasyprint_logging() -> bool:
    try:
        from weasyprint import LOGGER

        LOGGER.setLevel(logging.INFO)
        LOGGER.addHandler(logging.StreamHandler())
        return True
    except ImportError:
        return False


class Main:
    infiles: list[Path]
    baseprint: Path | None
    outdir: Path | None
    copy: list[Path]
    directory: Path | None
    skip_pdf: bool
    defaults: list[Path]

    def __init__(self, cmd_line_args: Any = None):
        self.parser = argparse.ArgumentParser(prog="baseprinter")
        self.parser.add_argument("--version", action="version", version=version())
        self.parser.add_argument(
            "infiles", type=Path, nargs="*", help="pandoc input files"
        )
        self.parser.add_argument(
            "-b", "--baseprint", type=Path, help="baseprint output directory"
        )
        self.parser.add_argument(
            "-o", "--outdir", type=Path, help="HTML/PDF output directory"
        )
        self.parser.add_argument(
            "-c",
            "--copy",
            type=Path,
            default=[],
            action="append",
            help=argparse.SUPPRESS
        )
        self.parser.add_argument(
            "-C", "--directory", type=Path, help=argparse.SUPPRESS
        )
        self.parser.add_argument(
            "--skip-pdf", action="store_true", help="Do not generate PDF"
        )
        self.parser.add_argument(
            "-d",
            "--defaults",
            type=Path,
            default=[],
            action="append",
            help="pandoc default option settings",
        )
        self.parser.parse_args(cmd_line_args, self)

    def run(self) -> int:
        if self.directory:
            warn("--directory CLI option will be removed", DeprecationWarning)
            os.chdir(self.directory)
        print("Working directory:", os.getcwd())
        tempdir = None
        if not self.baseprint:
            self.baseprint = Path(tempfile.mkdtemp())
            tempdir = self.baseprint
        try:
            if self.outdir and not self.skip_pdf:
                if not enable_weasyprint_logging():
                    msg = "PDF can not be generated without weasyprint installed."
                    msg += "\nUse the --skip-pdf option or install weasyprint."
                    print(msg, file=sys.stderr)
                    return 1
            maker = Maker(self)
            return maker.make()
        except ValueError as ex:
            self.parser.print_help()
            print(ex, file=sys.stderr)
            return 1
        finally:
            if tempdir:
                shutil.rmtree(tempdir)
        return 0


def main(args: Any = None) -> int:
    return Main(args).run()


if __name__ == "__main__":
    exit(main())
