import sys
from twisted.web import server, resource
from twisted.internet import selectreactor

if not "twisted.internet.reactor" in sys.modules:
    selectreactor.install()
from twisted.internet import reactor
from twisted.internet import ssl
from pem.twisted import certificateOptionsFromFiles
from twisted.internet.threads import deferToThreadPool
from twisted.web.server import NOT_DONE_YET


class Simple(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        d = deferToThreadPool(
            reactor, reactor.getThreadPool(), self.handle_request, request
        )
        d.addCallback(self.result_finished, request)
        return NOT_DONE_YET

    def handle_request(self, request):
        dataToBeWritten = ""
        try:
            dataToBeWritten += self.doRender(request)
        except Exception as e:
            dataToBeWritten = f"<html><body>Error: {e}</body></html>"
            print("Error while rendering:", e)

        return dataToBeWritten

    def doRender(self, request):
        data = """
        <html><body>
        <table><tr><th>Key</th><th>Value</th></tr>
        """
        for i in range(30000):
            data += f"<tr><td>{i}</td><td>{i}</td></tr>"
        return data + "</table></body></html>"

    def result_finished(self, result, request):
        try:
            request.write(result.encode("utf-8"))
        except Exception as e:
            print("Error while writing:", e)
        print("Request finished")
        request.finish()


site = server.Site(Simple())
options = certificateOptionsFromFiles("key.pem", "cert.pem")
options.lowerMaximumSecurityTo = ssl.TLSVersion.TLSv1_3
reactor.listenSSL(8080, site, options)
reactor.run()
