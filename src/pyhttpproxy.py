#!/Volumes/Userland/Users/spikeekips/workspace/chainpang/m/bin/python
# -*- coding: utf-8 -*-


import re
import os
import sys
import urlparse
import urllib
import resource
import ConfigParser
import warnings

from twisted.scripts._twistd_unix import ServerOptions
from twisted.application import service, internet
from twisted.internet import reactor
from twisted.web import http, proxy
from twisted.python import usage
from twisted.internet import ssl


class ProxyRequest (proxy.ProxyRequest, ) :
    RE_REMOVE_COMMA = re.compile(",[\s]*$", )

    protocols = {'http': proxy.ProxyClientFactory, }

    def __init__(self, channel, queued, reactor=reactor):
        proxy.ProxyRequest.__init__(self, channel, queued, reactor=reactor, )

    def process(self):
        _host_orig = urllib.splitport(self.getHeader("host"), )[0]
        _key = "%s:%s" % ("https" if self.isSecure() else "http", _host_orig, )

        try :
            _to = self.channel.factory.server_pool.get(_key, "to", )
        except ConfigParser.NoSectionError :
            self.channel.transport.write("HTTP/1.1 400 Bad Request\r\n\r\n")
            self.channel.transport.loseConnection()
            return

        _p = urlparse.urlsplit(_to, )
        (_host, _port, ) = urllib.splitnport(_p.netloc, 443 if _p.scheme == "https" else 80, )

        class_ = self.protocols.get(_p.scheme, proxy.ProxyClientFactory, )
        headers = self.getAllHeaders().copy()
        headers['host'] = "%s:%s" % (_host_orig, _port, )

        if not self.channel.factory.without_x_forwarded_for :
            _xf = ("%s, " % self.RE_REMOVE_COMMA.sub(
                    "", headers.get('x-forwarded-for')).strip()
                ) if "x-forwarded-for" in headers else ""
            headers['x-forwarded-for'] = _xf + self.client.host
            headers['x-forwarded-proto'] = "https" if self.isSecure() else "http"

        self.content.seek(0, 0, )
        clientFactory = class_(
                self.method, self.uri, self.clientproto, headers, self.content.read(), self, )
        self.reactor.connectTCP(_host, _port, clientFactory, )


class Proxy (proxy.Proxy, ) :
    requestFactory = ProxyRequest


class ProxyFactory (http.HTTPFactory, ) :
    protocol = Proxy

    def __init__ (self,
                    clientproto="https",
                    server_pool=dict(),
                    timeout=20,
                    without_x_forwarded_for=False,
                    verbose=False,
                ) :
        http.HTTPFactory.__init__(self, timeout=timeout, )

        self.clientproto = clientproto
        self.without_x_forwarded_for = without_x_forwarded_for
        self.verbose = verbose

        self.server_pool = server_pool


class Options (ServerOptions, ) :
    synopsis = "Usage: %s [options]" % os.path.basename(sys.argv[0])
    optFlags = (
        ["vv", None, "verbose", ],
        ["test", None, "run doctest", ],
        ["without-x-forwarded-for", None,
            "don't append `X-Forwarded-For` in the header", ],
        ["https", None, "use SSL", ],
        ["http", None, "use http", ],
    )
    optParameters = (
        ["config", None, None, "server pool config", ],
        ["http-port", None, 8080, "listen http port", ],
        ["https-port", None, 443, "listen https port", ],
        ["ssl-priv-file", None, None, "SSL private key file", ],
        ["ssl-cert-file", None, None, "SSL certificate file", ],
        ["timeout", None, "20", "client timeout", ],
    )
    unused_short = ("-o", "-f", "-s", "-y", "-d", )
    unused_long = ("--rundir=", "--python=", "--savestats", "--no_save",
        "--encrypted", "--file=", "--source=", "--test", "--originalname", )

    def __init__ (self, *a, **kw) :
        ServerOptions.__init__(self, *a, **kw)

        for i in self.unused_long :
            if self.longOpt.count(i[2:]) > 0 :
                del self.longOpt[self.longOpt.index(i[2:])]

    def parseOptions (self, *a, **kw) :
        self._skip_reactor = kw.get("skip_reactor")
        if "skip_reactor" in kw :
            del kw["skip_reactor"]

        super(Options, self).parseOptions(*a, **kw)

        if not self.get("config") :
            raise usage.UsageError("'config' must be int value.", )

        if not os.path.exists(self.get("config"), ) :
            raise usage.UsageError("`config`, %s does not exist." % self.get("config"), )

        if not self.get("http-port") and not self.get("https-port") :
            raise usage.UsageError("`http-port` or `https-port` must be given.", )

        if self.get("http") and not self.get("http-port") :
            raise usage.UsageError("`http-port` must be given.", )

        if self.get("https") and not self.get("https-port") :
            raise usage.UsageError("`https-port` must be given.", )

        if self.get("https") :
            if not self.get("ssl-priv-file") or not self.get("ssl-cert-file") :
                raise usage.UsageError(
            "For `https`, `ssl-priv-file` and `ssl-cert-file` must be given.", )

        self.opt_timeout(self.get("timeout"), )

    def opt_http_port (self, value, ) :
        try :
            self["http-port"] = int(value, )
        except ValueError :
            raise usage.UsageError("invalid `http-port`, '%s', it must be int value." % value, )

    def opt_https_port (self, value, ) :
        try :
            self["https-port"] = int(value, )
        except ValueError :
            raise usage.UsageError("invalid `https-port`, '%s', it must be int value." % value, )

    def opt_timeout (self, value, ) :
        try :
            self["timeout"] = int(value, )
        except ValueError :
            raise usage.UsageError(
                "invalid `timeout`, '%s', it must be int value." % value, )

    def opt_vv (self, value, ) :
        del self["vv"]
        self["verbose"] = True

    def opt_reactor (self, v, ) :
        if self._skip_reactor :
            return
        return ServerOptions.opt_reactor(self, v, )

def read_config (c, ) :
    _config = ConfigParser.ConfigParser()
    _config.read(c, )

    # read `include`d confs
    if _config.has_section("include") and _config.has_option("include", "file", ):
        _files = [
                os.path.join(
                    os.path.dirname(c, ),
                    f.strip(),
                ) for f in _config.get("include", "file", ).split(",") if f.strip()
            ]
        for f in _files :
            if not os.path.exists(f, ) :
                warnings.warn("can not find the included config file, '%s'. we will skip this file." % f, )

            # dump confs to the main
            _c = ConfigParser.ConfigParser()
            _c.read(f, )
            for k in _c.sections() :
                if not _config.has_section(k, ) :
                    _config.add_section(k, )

                _config.set(k, "to", _c.get(k, "to", ), )

    return _config


if __name__ == "__builtin__"  :
    _options = Options()
    _options.parseOptions(skip_reactor=True, )

    resource.setrlimit(resource.RLIMIT_NOFILE, (2048, 2048, ), )
    application = service.Application("incheon", )

    ################################################################################
    # run HTTPS
    _a = list()
    _kw = dict()

    if _options.get("http") :
        internet.TCPServer(
            _options.get("http-port"),
            ProxyFactory(
                clientproto="http",
                server_pool=read_config(_options.get("config")),
                timeout=_options.get("timeout"),
                without_x_forwarded_for=_options.get("without-x-forwarded-for"),
                verbose=_options.get("verbose"),
            ),
        ).setServiceParent(application, )

    if _options.get("https") :
        internet.SSLServer(
            _options.get("https-port"),
            ProxyFactory(
                clientproto="https",
                server_pool=read_config(_options.get("config")),
                timeout=_options.get("timeout"),
                without_x_forwarded_for=_options.get("without-x-forwarded-for"),
                verbose=_options.get("verbose"),
            ),
            ssl.DefaultOpenSSLContextFactory(
                _options.get("ssl-priv-file"),
                _options.get("ssl-cert-file"),
            ),
        ).setServiceParent(application, )

elif __name__ == "__main__"  :
    _found = False
    _n = list()
    _n.append(sys.argv[0], )
    for i in sys.argv[1:] :
        if _found :
            _found = False
            continue
        elif i in Options.unused_short :
            _found = True
            continue
        elif filter(i.startswith, Options.unused_long, ) :
            continue

        _n.append(i, )

    _n.extend(["-y", __file__, ], )
    sys.argv = _n

    from twisted.application import app
    from twisted.scripts.twistd import runApp
    app.run(runApp , Options, )

