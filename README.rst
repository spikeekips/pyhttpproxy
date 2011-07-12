##################################################
pyhttpproxy
##################################################

The `pyhttpproxy` is the HTTP request proxy server, it can handle
the `HTTP`, `HTTPS` with `x-forwarded-for` support.

In the case of `HTTPS`, it acts like well-known SSL-tunneling software,
`STUNNEL`, but `pyhttpproxy` can append the `X-Forwarded-For` in the last line
of header.


Feature
##################################################

 - `HTTP`, `HTTPS` proxy
 - support *virtual host*
 - support `X-Forwarded-For`


Install
##################################################

From Source
==================================================

Requirement
--------------------------------------------------

 - `Python` 2.6 or higher <http://python.org>
 - `pyOpenSSL` 0.12 or higher <http://pyopenssl.sourceforge.net/>
 - `Twisted Network Framework` 10.1 or higher <http://twistedmatrix.com>

just use ``pip`` ::

    sh $ pip install Twisted pyOpenSSL


`setup.py`
--------------------------------------------------

#. Download the latest version of `pyhttpproxy` from https://github.com/spikeekips/pyhttpproxy/downloads
#. Run the `setup.py`::

    sh $ tar xf pyhttpproxy-vX.X.X.tar.gz
    sh $ cd pyhttpproxy-vX.X.X
    sh $ python -V
    sh $ python setup.py install

Everything done.


Generate Priv & Cert Key For HTTPS
==================================================

If you have some trouble to generate ssl private and certificate key file, see
this page, http://www.akadia.com/services/ssh_test_certificate.html .


Deploy
##################################################

After installation finished, it's ready to deply. The deploy script are located
at ``/bin`` from the installation root path ::

You can run the deploy script like this, ::

    sh $ pyhttpproxy.py --port=8080 --ssl --ssl-priv-file=./server.key --ssl-cert-file=./server.crt --config=./pyhttpproxy.cfg -n

The client send the HTTPS request to the port 8080 of this host and the every
request to port 8080 of this host will be forwarded to the server, which is
defined in the `./pyhttpproxy.cfg`.

You can set these kind of options manually, ::

    sh $ ./pyhttpproxy.py  --help
    Usage: pyhttpproxy.py [options]
    Options:
      -n, --nodaemon                 don't daemonize, don't use default umask of
                                     0077
          --syslog                   Log to syslog, not to file
          --euid                     Set only effective user-id rather than real
                                     user-id. (This option has no effect unless the
                                     server is running as root, in which case it
                                     means not to shed all privileges after binding
                                     ports, retaining the option to regain
                                     privileges in cases such as spawning processes.
                                     Use with caution.)
          --vv                       verbose
          --without-x-forwarded-for  don't append `X-Forwarded-For` in the header
          --ssl                      use SSL
      -l, --logfile=                 log to a specified file, - for stdout
      -p, --profile=                 Run in profile mode, dumping results to
                                     specified file
          --profiler=                Name of the profiler to use (profile, cprofile,
                                     hotshot). [default: hotshot]
          --prefix=                  use the given prefix when syslogging [default:
                                     twisted]
          --pidfile=                 Name of the pidfile [default: twistd.pid]
          --chroot=                  Chroot to a supplied directory before running
      -u, --uid=                     The uid to run as.
      -g, --gid=                     The gid to run as.
          --umask=                   The (octal) file creation mask to apply.
          --config=                  server pool config
          --port=                    listen port
          --ssl-priv-file=           SSL private key file
          --ssl-cert-file=           SSL certificate file
          --timeout=                 client timeout [default: 20]
          --help-reactors            Display a list of possibly available reactor
                                     names.
          --version                  Print version information and exit.
          --spew                     Print an insanely verbose log of everything
                                     that happens. Useful when debugging freezes or
                                     locks in complex code.
      -b, --debug                    Run the application in the Python Debugger
                                     (implies nodaemon), sending SIGUSR2 will drop
                                     into debugger
          --reactor=                 
          --help                     Display this help and exit.

    twistd reads a twisted.application.service.Application out of a file and runs
    it.
    Commands:
        ftp              An FTP server.
        telnet           A simple, telnet-based remote debugging service.
        socks            A SOCKSv4 proxy service.
        manhole-old      An interactive remote debugger service.
        portforward      A simple port-forwarder.
        web              A general-purpose web server which can serve from a
                         filesystem or application resource.
        inetd            An inetd(8) replacement.
        news             A news server.
        xmpp-router      An XMPP Router server
        words            A modern words server
        dns              A domain name server.
        mail             An email service
        manhole          An interactive remote debugger service accessible via
                         telnet and ssh and providing syntax coloring and basic line
                         editing functionality.
        conch            A Conch SSH service.
        procmon          A process watchdog / supervisor

Examples
################################################################################

::

    sh $ pyhttpproxy.py --port=8080 --config=./pyhttpproxy.cfg -n
    sh $ pyhttpproxy.py --port=8080 --ssl --ssl-priv-file=./server.key --ssl-cert-file=./server.crt --config=./pyhttpproxy.cfg -n


`cfg` Config
################################################################################

.. note ::
    The `cfg` file of `pyhttpproxy` is the simple config like Microsoft Windows INI
    file.  For more information about `cfg` file of python, see the python
    documentation, http://docs.python.org/library/configparser.html .

::

    [www.naver.com]
    to = http://www.daum.net

    [www.facebook.com]
    to = http://plus.google.com

    [dev.flaskcon.com]
    to = http://dev.gamepresso.com:8080

In this config, the incoming request of `www.naver.com` will be forwarded to
`www.daum.net` with the protocol, `HTTP` and the port, `80`, which is the
default port of `HTTP`, and the incoming request of `dev.flaskcon.com` will be
forwarded to `dev.gamepresso.com`, with the protocol, `HTTP` and the port,
`8080`.


