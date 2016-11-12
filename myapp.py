import os, sys

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, \
    listenWS


class BroadcastServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            # msg = "{} from {}".format(payload.decode('utf8'), self.peer)
            msg = payload.decode('utf8')
            #print 'onMessage', type(self), self
            print '----- Received msg from', self.peer

            # print '\n----- self', type(self)
            # print '-', self
            # # print dir(self)
            # print '\n--- peer', type(self.peer)
            # print '-', self.peer
            # # print dir(self.peer)
            # print '\n--- factory', type(self.factory)
            # print '-', self.factory
            # print 'host', self.factory.host
            # print 'port', self.factory.port
            # print 'externalPort', self.factory.externalPort
            # print 'path', self.factory.path
            # print 'server', self.factory.server
            # print 'url', self.factory.url
            # # print dir(self.factory)
            # print '\n--- transport', type(self.transport)
            # print '-', self.transport
            # print 'hostname', self.transport.hostname
            # print 'client', self.transport.client
            # print 'server', self.transport.server
            # print 'socket', self.transport.socket
            # print 'getHost()', self.transport.getHost()
            # print 'getPeer()', self.transport.getPeer()

            # print self.transport
            # print dir(self.transport)
            self.factory.broadcast(msg, self)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):
    """Simple broadcast server broadcasting any message it receives to all
    currently connected clients."""

    def __init__(self, url, externalPort):
        WebSocketServerFactory.__init__(self, url, externalPort=externalPort)
        self.clients = []

    def register(self, client):
        if client not in self.clients:
            print("registered client {}".format(client.peer))
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)

    def broadcast(self, msg, source):
        print("Broadcasting msg from {} (total clients={})".format(source.peer, len(self.clients)))
        # print msg
        for c in self.clients:
            if c == source:
                #print 'skipping broadcast to original source:', type(c), c
                continue
            c.sendMessage(msg.encode('utf8'))
            # print("message sent to {}".format(c.peer))
            print 'message sent from %s to %s' % (c.transport.getHost(), c.transport.getPeer())
            # print 'client: ', type(c)


class BroadcastPreparedServerFactory(BroadcastServerFactory):
    """Functionally same as above, but optimized broadcast using
    prepareMessage and sendPreparedMessage."""

    def broadcast(self, msg):
        print("broadcasting prepared message '{}' ..".format(msg))
        preparedMsg = self.prepareMessage(msg)
        for c in self.clients:
            c.sendPreparedMessage(preparedMsg)
            print("prepared message sent to {}".format(c.peer))


if __name__ == '__main__':
    print 'TEMP version of APP is trying to come up...........................................................'

    log.startLogging(sys.stdout)

    ServerFactory = BroadcastServerFactory
    # ServerFactory = BroadcastPreparedServerFactory

    # factory = ServerFactory(u"ws://127.0.0.1:9000")
    port = int(os.environ.get("PORT", 5000))
    print 'PORT from environment', port
    factory = ServerFactory(u"ws://0.0.0.0:" + unicode(port), externalPort=80) #externalPort=5000 for local testing
    factory.protocol = BroadcastServerProtocol

    print 'isSecure', factory.isSecure
    print 'server', factory.server
    print 'port', factory.port
    print 'externalPort', factory.externalPort
    print 'url', factory.url
    print 'headers', factory.headers

    listenWS(factory)

    # webdir = File(".")
    # web = Site(webdir)
    # reactor.listenTCP(9050, web)

    reactor.run()
