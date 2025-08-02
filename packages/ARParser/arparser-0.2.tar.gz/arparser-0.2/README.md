<p align="center">
<a href="https://t.me/rktechnoindians"><img title="Made in INDIA" src="https://img.shields.io/badge/MADE%20IN-INDIA-SCRIPT?colorA=%23ff8100&colorB=%23017e40&colorC=%23ff0000&style=for-the-badge"></a>
</p>

<a name="readme-top"></a>


# ARParser


<p align="center"> 
<a href="https://t.me/rktechnoindians"><img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=800&size=35&pause=1000&color=F74848&center=true&vCenter=true&random=false&width=435&lines=ARParser" /></a>
 </p>
 
# Androguard's axml

This is a library for handling the AXML file format.  "AXML" is the informal
common name for the compiled binary XML data format used in Android app files.
The Android Open Source Project does not seem to have named the format, other
than referring to is as "binary XML" or "compiled XML".  So AXML stands for
Android XML. The file format is based on compiling XML source into a binary
format based on [protobuf](). There are a number of different Android XML file
types that are compiled to AXML, these are generically known as [Android
Resources](https://developer.android.com/guide/topics/resources/available-resources).
All of these files are included in the APK's ZIP package with the file extension
`.xml` even though they are actually AXML and not XML.

Some specific data files, like String Resources and Style Resources, are instead
compiled into a single file `resources.arsc` in its own data format, known as
ASRC.  AXML files often refer to values that are in `resources.arsc`.

The entry point for an app is the "[app
manifest](https://developer.android.com/guide/topics/manifest/manifest-element)"
defines the essential data points that every app must have, like Package Name
and Version Code, and includes lots of other metadata that describe the
app. Every Android app file (APK) must include
[`AndroidManifest.xml`](https://developer.android.com/guide/topics/manifest/manifest-intro),
which in the APK is the compiled binary AXML format, not XML, despite the file
extension.  The source code files for the binary app manifest file are also
called `AndroidManifest.xml`, but they are actually XML.  There can be
[multiple](https://developer.android.com/build/manage-manifests) source files,
but there is only ever one single compiled binary `AndroidManifest.xml` that is
valid in the APK.

https://developer.android.com/guide/topics/manifest/manifest-intro#reference


Installation Method
-------
**💢 Requirement PKG 💢**

    termux-setup-storage && pkg update -y && pkg upgrade -y && pkg install python libxslt -y && pip install click pygments rich lxml

**👉🏻 To install ARParser, Run only any one cmd from the Installation Method**

**💢 PYPI ( Just Testing ) 💢**

    pip install ARParser

**1st. Method**

`💢 For Latest Commit ( From Main  Branch )  💢`

    pip install --force-reinstall https://github.com/TechnoIndian/ARParser/archive/refs/heads/main.zip

`Or`

    pip install --force-reinstall https://github.com/TechnoIndian/ARParser/archive/refs/heads/main.tar.gz

`Or`

    curl -Ls https://github.com/TechnoIndian/Tools/releases/download/Tools/ARParser.sh | bash

**2nd. Method**

    pkg install python git && pip install --force-reinstall git+https://github.com/TechnoIndian/ARParser.git


Uninstall ARParser
-----

    pip uninstall ARParser


Usage
-----

#### AXMLPrinter

**├➢ AXMLPrinter ( Support APK & XML )**

    ARParser axml -i AndroidManifest.xml

`Or`

    ARParser axml AndroidManifest.xml

`With APK`

    ARParser axml Apk_Path.apk
    
**├➢ ID2Name, Default is ID ( @7F140004 𒁍 @xml/network_security_config | _attr_01010003 𒁍 android:name )**

    ARParser axml Apk_Path.apk -n

**├➢ ResParser ( Res AXML Parse )**

    ARParser axml Apk_Path.apk -r res/xml/xyz.xml

`ID2Name`

    ARParser axml Apk_Path.apk -r res/xml/xyz.xml -n

**Mode Help ( --help )**

    ARParser axml --help 

#### ARSCParser

**├➢ Public XML ( Default )**

    ARParser arsc Apk_Path.apk

**├➢ hex ID ( Resolve 𒁍 locale and package )**

    ARParser arsc Apk_Path.apk -id 7f060008

**├➢ Locale ( en-rIN, en-rGB, zh-rCN etc. )**

    ARParser arsc Apk_Path.apk -l en-rIN

**├➢ Type [string|strings|bool|id|color|dimen|integer|public]**

    ARParser arsc Apk_Path.apk -t string

**Mode Help ( --help )**

    ARParser arsc --help 


## Current status

 - Passing androguard tests for axml and arsc.

#### Structure

~~~~
axml/
├── axml/
│   ├── __init__.py       # Expose the public API (parse_axml, AXMLParser, AXMLPrinter)
│   ├── apk.py            # input APK_Path.apk, AndroidManifest.xml, resources.arsc
│   ├── cli.py            # Command Helper
│   ├── main.py           # Script Execution 
│   ├── constants.py      # All constants (chunk types, flag values...)
│   ├── exceptions.py     # Custom exceptions (like ResParserError)
│   ├── stringblock.py    # The StringBlock class and its helper functions (_decode8, _decode16...)
│   ├── parser_arsc.py    # The resources parser class and related parsing functions
│   ├── parser_axml.py    # The AXMLParser class and related parsing functions
│   ├── printer.py        # The AXMLPrinter class for converting parsed AXML into an ElementTree
│   └── formatters.py     # Helper functions like format_value and any formatting utilities
│   ├── resources
│   │   ├── __init__.py
│   │   ├── public.json
│   │   ├── public.py
│   │   └── public.xml
├── tests/
│   └── test_*.py    # Unit tests for each module
├── setup.py              # Packaging file
├── pyproject.toml        # Build configuration
└── README.md             # Project description and usage instructions
~~~~

### Goals

 - Write tests early approach, so we can immediately verify breaking changes.
 - Expose a clean public API
 - Standalone capabilities for axml parsing
 - Provide basic documentation


### Coding style

 - Follow [PEP 257](https://peps.python.org/pep-0257/) guidelines using the reStructuredText (reST) format for all docstrings.

## AXML binary format

Some references about the binary AXML format:

* [_aapt2_](https://developer.android.com/tools/aapt2) compiles XML to protobuf-based AXML
* [_aapt2_ source code](https://android.googlesource.com/platform/frameworks/base/+/master/tools/aapt2)
* [_aapt_ source code](https://android.googlesource.com/platform/frameworks/base/+/master/tools/aapt)
* The binary format for `AndroidManifest.xml` is defined in [`ApkInfo.proto`](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/tools/aapt2/ApkInfo.proto).

![Android binary XML](https://raw.githubusercontent.com/senswrong/AndroidBinaryXml/main/AndroidBinaryXml.png)

<!-- back up URL in case the one above goes away
![Android binary XML](https://github.com/user-attachments/assets/6439a13a-5a50-4f32-b106-c70c9fb9acf1)
-->


## 🇮🇳 Welcome By Techno India 🇮🇳

**Credit**

* [_axml_](https://github.com/androguard/axml) compiles XML to protobuf-based AXML
* [_androguard_](https://github.com/androguard/androguard) compiles XML to protobuf-based AXML

[![Telegram](https://img.shields.io/badge/TELEGRAM-CHANNEL-red?style=for-the-badge&logo=telegram)](https://t.me/rktechnoindians)
  </a><p>
[![Telegram](https://img.shields.io/badge/TELEGRAM-OWNER-red?style=for-the-badge&logo=telegram)](https://t.me/RK_TECHNO_INDIA)
</p>