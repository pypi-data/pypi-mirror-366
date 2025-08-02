import io, sys, zipfile
from typing import Union

from .printer import AXMLPrinter
from .parser_arsc import ARSCParser
from .helper.logging import LOGGER


class APK:
    def __init__(self, filename: str, raw: bool = False) -> None:

        if raw:
            self.zip = zipfile.ZipFile(io.BytesIO(filename), 'r')
        else:
            self.zip = zipfile.ZipFile(filename, 'r')

    def get_file(self, filename: str) -> bytes:
        if filename not in self.zip.namelist():
            LOGGER.error(f"'{filename}' not exists inside APK")
            sys.exit(1)
        return self.zip.read(filename)

    def get_android_manifest(self):
        return self.get_file("AndroidManifest.xml")

    def get_android_resources(self):
        return ARSCParser(self.get_file("resources.arsc"))
    
    @staticmethod
    def readFile(filename: str, binary: bool = True) -> bytes:
        return open(filename, 'rb' if binary else 'r').read()

    @staticmethod
    def is_android(filename: str) -> str:

        raw_file = open(filename, "rb").read()
    
        if raw_file[0:2] == b"PK" and b'AndroidManifest.xml' in raw_file:
            return "APK"
        elif raw_file[0:4] == b"\x03\x00\x08\x00" or raw_file[0:4] == b"\x00\x00\x08\x00":
            return "AXML"
        elif raw_file[0:4] == b"\x02\x00\x0C\x00":
            return "ARSC"
        return None

