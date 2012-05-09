# -*- coding: utf-8 -*-


import re
import os
import urlparse
import urllib
import ConfigParser
import warnings
import resource

from twisted.application import service, internet
from twisted.internet import reactor, ssl, protocol
from twisted.python import usage
from twisted.web import proxy, server, resource as _resource


server.version = "gamepresso.web.server/v20120424"


class Options (usage.Options, ) :
    synopsis = "[sub options]"
    longdesc = """"""
    optFlags = (
        ["vv", None, "verbose", ],
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
        ["timeout", None, 20, "client timeout", ],
    )

    def postOptions (self, *a, **kw) :
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


class BadRequestErrorPage (_resource.Resource, ) :
    def render(self, request):
        request.setResponseCode(400, )
        return ""

    def getChild(self, chnam, request):
        return self


class FakeReactor (object, ) :
    def __init__ (self, timeout, ) :
        self._timeout = timeout

    def connectTCP (self, *a, **kw) :
        if "timeout" not in kw :
            kw["timeout"] = self._timeout

        return reactor.connectTCP(*a, **kw)


class ProxyClientFactory (proxy.ProxyClientFactory, ) :
    def __init__(self, command, rest, version, headers, data, father) :
        if "host-original" in headers :
            headers['host'] = headers.get("host-original")

        proxy.ProxyClientFactory.__init__(self, command, rest, version, headers, data, father, )


class ReverseProxyResource (proxy.ReverseProxyResource, ) :
    proxyClientFactoryClass = ProxyClientFactory

    def getChild (self, path, request, ) :
        return self.__class__(
                self.host,
                self.port,
                self.path + "/" + urllib.quote(path, safe="", ),
                self.reactor,
            )


class ProxyResource (_resource.Resource, ) :
    isLeaf = False
    RE_REMOVE_COMMA = re.compile(",[\s]*$", )

    def __init__ (self, config, without_x_forwarded_for=False, timeout=20, ) :
        self._config = config
        self._timeout = timeout
        self._without_x_forwarded_for = without_x_forwarded_for

        _resource.Resource.__init__(self, )

    def getChild (self, path, request, ) :
        _host_orig = urllib.splitport(request.getHeader("host"), )[0]
        _key = "%s:%s" % ("https" if request.isSecure() else "http", _host_orig, )

        try :
            _to = self._config.get(_key, "to", )
        except ConfigParser.NoSectionError :
            return BadRequestErrorPage()

        _p = urlparse.urlsplit(_to, )
        (_host, _port, ) = urllib.splitnport(_p.netloc, 443 if _p.scheme == "https" else 80, )

        if not self._without_x_forwarded_for :
            _headers = request.getAllHeaders()
            _xf = ("%s, " % self.RE_REMOVE_COMMA.sub(
                    "", _headers.get('x-forwarded-for')).strip()
                ) if "x-forwarded-for" in _headers else ""

            _x_forwarded_for = _xf + request.client.host
            _x_forwarded_proto = "https" if request.isSecure() else "http"
            request.received_headers['x-forwarded-for'] = _x_forwarded_for
            request.received_headers['x-forwarded-proto'] = _x_forwarded_proto

        request.received_headers['host-original'] = _host_orig
        request.content.seek(0, 0)
        return ReverseProxyResource(
                _host,
                _port,
                "/" + path if path else "/",
                reactor=FakeReactor(self._timeout, ),
            )


def makeService (config, ) :
    if config.get("verbose") :
        import pprint
        pprint.pprint(config, )

    protocol.Factory.noisy = config.get("verbose", )

    resource.setrlimit(resource.RLIMIT_NOFILE, (2048, 2048, ), )

    _ms = service.MultiService()

    _kw = dict(
            config=read_config(config.get("config"), ),
            without_x_forwarded_for=config.get("without-x-forwarded-for"),
            timeout=config.get("timeout"),
        )

    if config.get("http") :
        internet.TCPServer(
                config.get("http-port"),
                server.Site(ProxyResource(**_kw), ),
            ).setServiceParent(_ms, )

    if config.get("https") :
        internet.SSLServer(
                config.get("https-port"),
                server.Site(ProxyResource(**_kw), ),
                ssl.DefaultOpenSSLContextFactory(
                        config.get("ssl-priv-file"),
                        config.get("ssl-cert-file"),
                    ),
            ).setServiceParent(_ms, )

    return _ms




