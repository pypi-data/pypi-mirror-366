import argparse, zipfile, sys, io

from typing import Union
import xml.etree.ElementTree as ET
import xml.dom.minidom

# 3rd party modules
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers import get_lexer_by_name

# internal modules
from .apk import APK
from .printer import AXMLPrinter
from .parser_arsc import ARSCParser
from .helper.logging import LOGGER

# AXMLPrinter
def androaxml_main(
    inp: str, outp: Union[str, None] = None, resource: Union[str, None] = None, resource_name: bool = False
) -> None:

    ret_type = APK.is_android(inp)
    if ret_type == "APK":
        a = APK(inp)
        src = resource and a.get_file(resource) or a.get_android_manifest()
        kwargs = {}
        
        if resource_name:
            kwargs["resource_name"] = resource_name
            if not resource:
                kwargs["arscobj"] = a.get_android_resources()
        if resource and resource_name:
            kwargs["arscobj"] = a.get_android_resources()

        axml = AXMLPrinter(src, **kwargs).get_buff()

    elif ".xml" in inp:
        axml = AXMLPrinter(APK.readFile(inp)).get_buff()
    else:
        LOGGER.error("Unknown File Type")
        sys.exit(1)

    buff = xml.dom.minidom.parseString(axml.decode('utf-8')).toprettyxml(encoding="utf-8")

    if outp:
        open(outp, "wb").write(buff)
    else:
        sys.stdout.write(
            highlight(
                buff,
                get_lexer_by_name("xml"),
                TerminalFormatter(),
            )
        )


# ARSCParser
def androarsc_main(
    arscobj: ARSCParser,
    outp: Union[str, None] = None,
    package: Union[str, None] = None,
    typ: Union[str, None] = None,
    locale: Union[str, None] = None,
) -> None:

    package = package or arscobj.get_packages_names()[0]
    ttype = typ or "public"
    locale = locale or '\x00\x00'

    if not hasattr(arscobj, "get_{}_resources".format(ttype)):
        exit(f"\nNo decoder found for type: '{ttype}'! Please open a bug report.\n")

    if ttype == "strings":
        x = arscobj.get_strings_resources()
    else:
        x = getattr(arscobj, "get_" + ttype + "_resources")(package, locale)

    buff = ET.tostring(ET.fromstring(x), encoding="UTF-8", xml_declaration=True)

    if outp:
        open(outp, "wb").write(buff)
    else:
        sys.stdout.write(
            highlight(
                buff,
                get_lexer_by_name("xml"),
                TerminalFormatter(),
            )
        )