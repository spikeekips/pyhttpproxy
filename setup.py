# -*- coding: utf-8 -*-

from distutils.core import setup

long_description = """The `pyhttpproxy` is the HTTP proxy server, it can handle
the `HTTP`, `HTTPS` with `x-forwarded-for` support."""


setup(
    name="pyhttpproxy",
    version="0.1",
    description="HTTPS request proxy server",
    long_description=long_description.replace("\n", " ").strip(),
    author="Spike^ekipS",
    author_email="spikeekips@gmail.com",
    url="https://github.com/spikeekips/pyhttpproxy",
    download_url="https://github.com/spikeekips/pyhttpproxy/downloads",
    platforms=["Any", ],
    license="GNU General Public License (GPL)",

    classifiers=(
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: No Input/Output (Daemon)",
        "Framework :: Twisted",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: System :: Networking",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ),

    data_files=(
        ("bin", ("src/pyhttpproxy.py", ), ),
    ),

    install_requires=(
        "Twisted>=10.1.0",
        "pyOpenSSL>=0.12",
    ),

)
