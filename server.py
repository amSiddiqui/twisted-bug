import sys
from twisted.web import server, resource
from twisted.internet import selectreactor
if not 'twisted.internet.reactor' in sys.modules:
    selectreactor.install()
from twisted.internet import reactor
from twisted.internet import ssl
from pem.twisted import certificateOptionsFromFiles
from twisted.internet.threads import deferToThreadPool
from twisted.web.server import NOT_DONE_YET

class Simple(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        def _doRender():
            try:
                self.doRender(request)
            except Exception as e:
                print('Error while rendering:', e)
                request.write(bytes(f"<html><body>Error: {e}</body></html>", "utf-8"))
                if not request._disconnected:
                    print('Finishing request')
                    request.finish()
        deferToThreadPool(reactor, reactor.getThreadPool(), _doRender)
        return NOT_DONE_YET

    def doRender(self, request):
        request.write(bytes("<html><body>", "utf-8"))
        request.write(bytes("<table><tr><th>Key</th><th>Value</th></tr>", "utf-8"))
        for i in range(30000):
            try:
                request.write(bytes(f"<tr><td>{i}</td><td>{i}</td></tr>", "utf-8"))
            except Exception as e:
                print('Error while writing:', e)
                break
        request.write(bytes("</body></html>", "utf-8"))
        if not request._disconnected:
            print('Finishing request')
            request.finish()


site = server.Site(Simple())
options = certificateOptionsFromFiles('key.pem', 'cert.pem')
options.lowerMaximumSecurityTo = ssl.TLSVersion.TLSv1_3
reactor.listenSSL(8080, site, options)
reactor.run()
