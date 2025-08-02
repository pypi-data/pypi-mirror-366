"""
Test the CLI
"""

from pathlib import Path

import pytest
import tempfile

from playa import PDFPasswordIncorrect
from playa.cli import main
from playa.exceptions import PDFEncryptionError
from tests.data import ALLPDFS, PASSWORDS, XFAILS


@pytest.mark.parametrize("path", ALLPDFS, ids=str)
def test_cli_metadata(path: Path):
    if path.name in XFAILS:
        pytest.xfail("Intentionally corrupt file: %s" % path.name)
    passwords = PASSWORDS.get(path.name, [""])
    for password in passwords:
        try:
            # FIXME: Verify that output is valid JSON
            main(["--password", password, "--non-interactive", str(path)])
            main(["--password", password, "--non-interactive", "--outline", str(path)])
            main(
                ["--password", password, "--non-interactive", "--structure", str(path)]
            )
        except PDFPasswordIncorrect:
            pass
        except PDFEncryptionError:
            pytest.skip("cryptography package not installed")


@pytest.mark.parametrize("path", ALLPDFS, ids=str)
def test_cli_outline(path: Path):
    if path.name in XFAILS:
        pytest.xfail("Intentionally corrupt file: %s" % path.name)
    passwords = PASSWORDS.get(path.name, [""])
    for password in passwords:
        try:
            # FIXME: Verify that output is valid JSON
            main(["--password", password, "--non-interactive", "--outline", str(path)])
        except PDFPasswordIncorrect:
            pass
        except PDFEncryptionError:
            pytest.skip("cryptography package not installed")


@pytest.mark.parametrize("path", ALLPDFS, ids=str)
def test_cli_structure(path: Path):
    if path.name in XFAILS:
        pytest.xfail("Intentionally corrupt file: %s" % path.name)
    passwords = PASSWORDS.get(path.name, [""])
    for password in passwords:
        try:
            # FIXME: Verify that output is valid JSON
            main(
                ["--password", password, "--non-interactive", "--structure", str(path)]
            )
        except PDFPasswordIncorrect:
            pass
        except PDFEncryptionError:
            pytest.skip("cryptography package not installed")


@pytest.mark.parametrize("path", ALLPDFS, ids=str)
def test_cli_images(path: Path):
    if path.name in XFAILS:
        pytest.xfail("Intentionally corrupt file: %s" % path.name)
    passwords = PASSWORDS.get(path.name, [""])
    for password in passwords:
        try:
            # FIXME: Verify that output is valid JSON
            with tempfile.TemporaryDirectory() as tempdir:
                main(
                    [
                        "--password",
                        password,
                        "--non-interactive",
                        "--images",
                        tempdir,
                        str(path),
                    ]
                )
        except PDFPasswordIncorrect:
            pass
        except PDFEncryptionError:
            pytest.skip("cryptography package not installed")


@pytest.mark.parametrize("path", ALLPDFS, ids=str)
def test_cli_fonts(path: Path):
    if path.name in XFAILS:
        pytest.xfail("Intentionally corrupt file: %s" % path.name)
    passwords = PASSWORDS.get(path.name, [""])
    for password in passwords:
        try:
            # FIXME: Verify that output is valid JSON
            with tempfile.TemporaryDirectory() as tempdir:
                main(
                    [
                        "--password",
                        password,
                        "--non-interactive",
                        "--fonts",
                        tempdir,
                        str(path),
                    ]
                )
        except PDFPasswordIncorrect:
            pass
        except PDFEncryptionError:
            pytest.skip("cryptography package not installed")
