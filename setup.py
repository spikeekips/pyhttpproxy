# -*- coding: utf-8 -*-

try :
    from gamepresso.common._distutils import setup
except ImportError :
    from setuptools import setup

from setuptools import find_packages


setup(
    name="pyhttpproxy",
    version="0.2",
    description="HTTPS request proxy server",
    long_description="The `pyhttpproxy` is the HTTP proxy server, it can handle the `HTTP`, `HTTPS` with `x-forwarded-for` support.",
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

    install_requires=(
        "Twisted>=12.0.0",
        "pyOpenSSL>=0.12",
    ),
    zip_safe=False,
    package_dir={"": "src", },
    packages = find_packages("src/") + ["twisted.plugins", ],
    package_data={
            "twisted": [
                    "plugins/twisted_pyhttpproxy.py",
                ],
        },
)


