#!/usr/bin/python
#coding=utf-8

from twisted.web import static, server
from twisted.internet import reactor, task
from twisted.internet.protocol import Protocol, Factory, ClientFactory
from twisted.spread import pb
from twisted.python import log

from txws import WebSocketFactory

import json, os, logging

curPath = os.path.dirname( __file__ )
conf = json.load( open( curPath + '/conf.json' ) )
pidFile = open( curPath + '/srv.pid', 'w' )
pidFile.write( str( os.getpid() ) )
pidFile.close()
observer = log.PythonLoggingObserver()
observer.start()
logging.basicConfig( level = logging.DEBUG,
        format='%(asctime)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S' )
wsClients = {}
controllers = {}

def sendIds():
    for client in wsClients.values():
        client.sendId()

class WSProtocol(Protocol):
    def dataReceived(self, data):
        #d = json.loads( data )
        #if d.has_key( 'id' ):
        #    self.id = d['id']
#            wsClients[ d['id'] ] = self
        if pbc:
            pbc.client.callRemote( "cmd", { "cmd": "toggle" } )
            print "remote cmd sent"


    def sendId( self ):
        self.transport.write( 'your id is ' + self.id )

class WSFactory( Factory ):
    protocol = WSProtocol

class PbConnection( pb.Referenceable ):
    def __init__( self, client, data ):
        controllers[ data['id'] ] = self
        self.controller = data
        self.client = client

    def remote_data( self, data ):
        for device in data['devices']:
            for prop in data['devices'][device]:
                self.controller['devices'][device][prop] = data['devices'][device][prop]


class PbServer( pb.Root ):

    def remote_connect( self, client, data ):
        pbc = PbConnection( client, data )
        print "pb client connected" 
        return pbc
        #d = json.loads( data )
        #client.callRemote( "cmd", { "cmd": "set", "state": 1 } )

siteRoot = static.File(conf['site']['root'])
reactor.listenTCP( conf['site']['port'], server.Site( siteRoot ) )
reactor.listenTCP( conf['pb']['port'], pb.PBServerFactory( PbServer() ) )
reactor.listenTCP( conf['ws']['port'],  WebSocketFactory( WSFactory() ) )
pingCall = task.LoopingCall( sendIds )
pingCall.start( 5 )
reactor.run()
