from __future__ import annotations

import pytest

import json, os, tempfile, tomllib
from dataclasses import dataclass
from pathlib import Path
from subprocess import run
from typing import Any

from bs4 import BeautifulSoup

from baseprinter import __main__


CASES_DIR = Path(__file__).parent / "cases"


def get_expected(case: str) -> dict[str, Any]:
    with open(CASES_DIR / case / "expected.toml", "rb") as f:
        return tomllib.load(f)


def _run(args) -> int:
    if isinstance(args, str):
        args = args.split()
    return __main__.main(args)


@dataclass
class PdfInfo:
    num_pages: int
    title: str | None

    @staticmethod
    def loadf(path: Path | str) -> PdfInfo:
        args = ["exiftool", "-j", "-Title", "-PageCount", str(path)]
        res = run(args, capture_output=True)
        assert 0 == res.returncode
        d = json.loads(res.stdout)[0]
        return PdfInfo(d['PageCount'], d.get('Title'))


@dataclass
class Output:
    baseprint: BeautifulSoup
    html: BeautifulSoup
    pdf: PdfInfo | None = None

    @staticmethod
    def get(case: str, skip_pdf: bool) -> Output:
        with open(CASES_DIR / case / "init.toml", "rb") as f:
            infiles = tomllib.load(f)['infiles']
        os.chdir(CASES_DIR / case / "src")
        with tempfile.TemporaryDirectory() as tmp:
            cmdline = f"{infiles} -b {tmp}/baseprint -o {tmp}/preview"
            if skip_pdf:
                cmdline += " --skip-pdf"
        assert 0 == _run(cmdline)
        with (
            open(f"{tmp}/baseprint/article.xml") as baseprint,
            open(f"{tmp}/preview/index.html") as preview_html,
        ):
            ret = Output(
                BeautifulSoup(baseprint, "xml"),
                BeautifulSoup(preview_html, "xml"),
            )
            if not skip_pdf:
                ret.pdf = PdfInfo.loadf(f"{tmp}/preview/article.pdf")
        return ret


def check_html(expected, html):
    if title := expected.get('title'):
        assert title == html.title.string
        assert title == html.h1.string
    if abstract := expected.get('abstract'):
        assert abstract.strip() == html.p.string.strip()


@pytest.mark.slow
@pytest.mark.parametrize("case", os.listdir(CASES_DIR))
def test_with_pdf(case):
    out = Output.get(case, skip_pdf=False)
    expected = get_expected(case)
    check_html(expected, out.html)
    assert expected['num_pages'] == out.pdf.num_pages
    if title := expected.get('title'):
        assert title == out.pdf.title


@pytest.mark.parametrize("case", os.listdir(CASES_DIR))
def test_without_pdf(case):
    out = Output.get(case, skip_pdf=True)
    check_html(get_expected(case), out.html)
