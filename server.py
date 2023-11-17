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
            except:
                return ''
            finally:
                if not request._disconnected:
                    request.finish()

        deferToThreadPool(reactor, reactor.getThreadPool(), _doRender)
        return NOT_DONE_YET

    def doRender(self, request):
        request.write(bytes('<html><body>', 'utf-8'))
        request.write(bytes('<table><tr><th>Key</th><th>Value</th></tr>', 'utf-8'))
        for i in range(30000):
            request.write(bytes(f'<tr><td>{i}</td><td>{i}</td></tr>', 'utf-8'))
        request.write(bytes('</body></html>', 'utf-8'))
        return b''
    

site = server.Site(Simple())
options = certificateOptionsFromFiles('key.pem', 'cert.pem')
options.lowerMaximumSecurityTo = ssl.TLSVersion.TLSv1_3
reactor.listenSSL(8080, site, options)
reactor.run()