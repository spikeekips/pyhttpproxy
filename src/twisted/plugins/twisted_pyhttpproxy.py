# -*- coding: utf-8 -*-

from twisted.application.service import ServiceMaker

pyhttpproxy_run = ServiceMaker(
        "pyhttpproxy",
        "pyhttpproxy.tap",
        "http proxy server",
        "pyhttpproxy", 
    )


