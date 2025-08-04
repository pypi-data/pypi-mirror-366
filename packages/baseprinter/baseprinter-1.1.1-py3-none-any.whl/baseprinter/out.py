import os, shutil, subprocess
from importlib import resources
from pathlib import Path
from typing import Any, Iterable
from warnings import warn


def run_pandoc(args: Iterable[Any], echo: bool = True) -> int:
    cmd = ["pandoc"] + [str(a) for a in args]
    if echo:
        print(" ".join(cmd))
    result = subprocess.run(cmd)
    return result.returncode


def make_jats_xml(target: Path, sources: Iterable[str], defaults: Iterable[str]) -> int:
    rp = resources.files(__package__).joinpath("pandoc")
    bd_path = rp.joinpath("baseprint.yaml")
    csl_path = rp.joinpath("citation-hack.csl")
    xml_path = rp.joinpath("baseprint-jats.xml")
    with (
        resources.as_file(bd_path) as bd,
        resources.as_file(csl_path) as csl,
        resources.as_file(xml_path) as xml
    ):
        os.makedirs(target.parent, exist_ok=True)
        opts = ["-d", bd, "--csl", csl, "--template", xml, "-o", target]
        for d in defaults:
            opts += ["-d", d]
        return run_pandoc(opts + list(sources))


def make_html_pdf(target: Path, skip_pdf: bool, baseprint: Path) -> None:
    import epijats

    config = epijats.EprinterConfig(dsi_domain="perm.pub")
    config.show_pdf_icon = not skip_pdf
    config.header_banner_msg = "WORKING DRAFT"
    pdf_target = None if skip_pdf else target / "article.pdf"
    epijats.eprint_dir(config, baseprint, target, pdf_target)


def clear_dir(dirpath: Path) -> None:
    if dirpath.exists():
        assert dirpath.is_dir()
        for entry in dirpath.iterdir():
            if entry.is_dir():
                shutil.rmtree(entry)
            else:
                os.unlink(entry)


def clone_subpath_nostat(sub: Path, destdir: Path) -> None:
    """this implementation avoids calling copystat so SELinux context is not copied"""

    assert not sub.is_absolute()
    if sub.is_dir():
        for root, subdirs, files in sub.walk():
            os.makedirs(destdir / root, exist_ok=True)
            for file in files:
                shutil.copy(sub / file, destdir / sub / file)
    else:
        os.makedirs(destdir / sub.parent, exist_ok=True)
        shutil.copy(sub, destdir / sub)


class Maker:
    def __init__(self, namespace: Any):
        self.defaults = namespace.defaults
        self.infiles = namespace.infiles
        self.baseprint = namespace.baseprint
        self.outdir = namespace.outdir
        self.skip_pdf = namespace.skip_pdf
        self.copypaths = [s.relative_to(os.curdir) for s in namespace.copy]

    def _check_args(self) -> None:
        if not (self.infiles or self.defaults):
            raise ValueError("Missing input file or pandoc defaults file")
        if not self.baseprint:
            msg = "Missing baseprint destination"
            raise ValueError(msg)
        if self.baseprint.exists():
            if not self.baseprint.is_dir():
                raise ValueError("Baseprint destination can not be a file")
            entries = [a.name for a in self.baseprint.iterdir()]
            if entries and "article.xml" not in entries:
                msg = "Aborting: baseprint destination contains non-baseprint content"
                raise ValueError(msg)
        if self.copypaths:
            warn("--copy CLI option will be removed", DeprecationWarning)
        for p in self.copypaths:
            if ".." in p.parts:
                raise ValueError("Copy path must not include '..': {}".format(p))

    def make(self) -> int:
        self._check_args()
        clear_dir(self.baseprint)
        for sub in self.copypaths:
            clone_subpath_nostat(sub, self.baseprint)
        retcode = make_jats_xml(
            self.baseprint / "article.xml", self.infiles, self.defaults
        )
        if retcode == 0 and self.outdir:
            make_html_pdf(self.outdir, self.skip_pdf, self.baseprint)
        return retcode
