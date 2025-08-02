#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click, sys, zipfile

from .main import androarsc_main, androaxml_main
from .helper.logging import LOGGER
from typing import Union

# internal modules
from .apk import APK
from .printer import AXMLPrinter
from .parser_arsc import ARSCParser


# AXMLPrinter
@click.group(help=__doc__)
@click.option(
    "--verbose",
    "--debug",
    'verbosity',
    flag_value='verbose',
    help="Print more",
)

def entry_point(verbosity):
    if verbosity is None:
        LOGGER.setLevel("INFO")
    else:
        LOGGER.setLevel("ERROR")

@entry_point.command()
@click.option(
    '--input',
    '-i',
    'input_',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help='AndroidManifest.xml or APK to parse (legacy option)',
)
@click.option(
    '--resource-name',
    '-n',
    is_flag=True,
    default=False,
    help='Use ID2Name, Default is ID ( @7F140004 𒁍 @xml/network_security_config | _attr_01010003 𒁍 android:name )',
)
@click.option(
    "--resource",
    "-r",
    help="Resource (any binary XML file) inside the APK to parse instead of AndroidManifest.xml",
)
@click.option(
    '--output',
    '-o',
    help='filename to save the decoded AndroidManifest.xml to, default stdout',
)
@click.argument(
    'file_',
    required=False,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)

def axml(input_, output, file_, resource, resource_name):
    """
    Parse the AndroidManifest.xml.

    Parsing is either direct or from a given APK and prints in XML format or
    saves to file.

    This tool can also be used to process any AXML encoded file, for example
    from the layout directory.

    Example:

    ├➢ AXMLPrinter ( Support APK & XML )\n
         ╰┈➤ ARParser axml -i AndroidManifest.xml\n
         ╰┈➤ ARParser axml AndroidManifest.xml\n
         ╰┈➤ ARParser axml Apk_Path.apk\n
    ├➢ ID2Name, Default is ID ( @7F140004 𒁍 @xml/network_security_config | _attr_01010003 𒁍 android:name )\n
         ╰┈➤ ARParser axml Apk_Path.apk -n\n
    ├➢ ResParser ( Res AXML Parse )\n
         ╰┈➤ ARParser axml Apk_Path.apk -r res/xml/xyz.xml\n
         ╰┈➤ ARParser axml Apk_Path.apk -r res/xml/xyz.xml -n

    """
    if file_ is not None and input_ is not None:
        LOGGER.info("Can not give --input and positional argument! Please use only one of them!")
        sys.exit(1)

    if file_ is None and input_ is None:
        LOGGER.info("Give one file to decode!")
        sys.exit(1)

    if file_ is not None:
        androaxml_main(file_, output, resource, resource_name)
    elif input_ is not None:
        androaxml_main(input_, output, resource, resource_name)


# ARSCParser
@entry_point.command()
@click.option(
    '--input',
    '-i',
    'input_',
    type=click.Path(exists=True),
    help='resources.arsc or APK to parse (legacy option)',
)
@click.argument(
    'file_',
    required=False,
)
@click.option(
    '--output',
    '-o',
    # required=True,  #  not required due to --list-types
    help='filename to save the decoded resources to like ( public.xml ) ',
)
@click.option(
    '--package',
    '-p',
    help='Show only resources for the given package name '
    '(default: the first package name found)',
)
@click.option(
    '--locale',
    '-l',
    help='Show only resources for the given locale (default: \'\\x00\\x00\')',
)
@click.option(
    '--type',
    '-t',
    'type_',
    help='Show only resources of the given type (default: public)',
)
@click.option(
    '-id',
    'id_',
    help="Resolve the given ID for the given locale and package. Provide the hex ID!",
)
@click.option(
    '-list-packages',
    is_flag=True,
    default=False,
    help='List all package names and exit',
)
@click.option(
    '-list-locales',
    is_flag=True,
    default=False,
    help='List all package names and exit',
)
@click.option(
    '-list-types',
    is_flag=True,
    default=False,
    help='List all types and exit',
)

def arsc(input_, file_, output, package, locale, type_, id_, list_packages, list_locales, list_types,):
    """
    Decode resources.arsc either directly from a given file or from an APK.

    Example:

        ├➢ hex ID ( Resolve 𒁍 locale and package )\n
             ╰┈➤ ARParser arsc app.apk -id 7f060008\n
        ├➢ Locale ( en-rIN, en-rGB, zh-rCN etc. )\n
             ╰┈➤ ARParser arsc app.apk -l en-rIN\n
        ├➢ Type [string|strings|bool|id|color|dimen|integer|public]\n
             ╰┈➤ ARParser arsc app.apk -t string
    """

    if file_ and input_:
        LOGGER.info("Can not give --input and positional argument! Please use only one of them!")
        sys.exit(1)

    if not input_ and not file_:
        LOGGER.info("Give one file to decode!")
        sys.exit(1)

    if input_:
        fname = input_
    else:
        fname = file_

    ret_type = APK.is_android(fname)
    if ret_type == "APK":
        a = APK(fname)
        arscobj = a.get_android_resources()
        if not arscobj:
            LOGGER.error("The APK does not contain a resources file!")
            sys.exit(0)
    elif ret_type == "ARSC":
        with open(fname, 'rb') as fp:
            arscobj = ARSCParser(fp.read())
            if not arscobj:
                LOGGER.error("The resources file seems to be invalid!")
                sys.exit(1)
    else:
        LOGGER.error("Unknown file type!")
        sys.exit(1)

    if id_:
        # Strip the @, if any
        if id_[0] == "@":
            id_ = id_[1:]
        try:
            i_id = int(id_, 16)
        except ValueError:
            exit("ID '{}' could not be parsed! Have you supplied the correct hex ID?".format(id_))


        name = arscobj.get_resource_xml_name(i_id)
        if not name:
            exit("Specified resource was not found!")

        print("@{:08x} resolves to '{}'".format(i_id, name))
        print()

        # All the information is in the config.
        # we simply need to get the actual value of the entry
        for config, entry in arscobj.get_resolved_res_configs(i_id):
            print(
                "{} = '{}'".format(
                    (
                        config.get_qualifier()
                        if not config.is_default()
                        else "<default>"
                    ),
                    entry,
                )
            )

        sys.exit(0)

    if list_packages:
        print("\n".join(arscobj.get_packages_names()))
        sys.exit(0)

    if list_locales:
        for p in arscobj.get_packages_names():
            print("In Package:", p)
            print(
                "\n".join(
                    map(
                        lambda x: (
                            "  \\x00\\x00"
                            if x == "\x00\x00"
                            else "  {}".format(x)
                        ),
                        sorted(arscobj.get_locales(p)),
                    )
                )
            )
        sys.exit(0)

    if list_types:
        for p in arscobj.get_packages_names():
            print("In Package:", p)
            for locale in sorted(arscobj.get_locales(p)):
                print(
                    "  In Locale: {}".format(
                        "\\x00\\x00" if locale == "\x00\x00" else locale
                    )
                )
                print(
                    "\n".join(
                        map(
                            "    {}".format,
                            sorted(arscobj.get_types(p, locale)),
                        )
                    )
                )
        sys.exit(0)

    androarsc_main(
        arscobj, outp=output, package=package, typ=type_, locale=locale
    )

if __name__ == '__main__':
    entry_point()