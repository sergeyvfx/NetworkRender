#!BPY
"""
#Name: 'RenderServer'
#Blender: 247
#Group: 'Render'
#Submenu: 'Network Rendering' renderserver
#Tooltip: 'Provide rendering services to clients'
"""

__author__   ='Michel Anders (varkenvarken)'
__copyright__='(cc) non commercial use only and attribution by'
__url__      =["Author's site, http://www.swineworld.org/blender"]
__email__    =['varkenvarken is my nick at blendernation.org, PM me there']
__version__  ='1.00 2008-10-20'
__history__  =['1.00 2008-10-20, code refactoring and documentation update',
               '0.01 2008-10-6 initital version'
               ]

__bpydoc__="""\		
A simple render server that provides services to render a single animation frame
or part of a large still image for client over RPC.

It announces itself by broadcasting the uri for the RPC server on the network.
To be used with RenderAnimClient and/ord RenderStillClient

Usage: from the scripts menu select
Render->Network Rendering->RenderServer

Installation: unpack NetworkRender.zip into your .blender/scripts directory
(this zip contains both client and server scripts and supportfiles) Make sure you unpack the
directory structures as well. See website for an example of the correct directory structie 

Prerequisite: a full Python 2.5 installation is required for this script to run.

Warning: this script provides a RPC service on TCP port 8080. Your resident firewall may
warn about that. This server will by accept incoming connections only from machines 
that it considers to be on the local subnet but this is shallow security indeed: always
make sure you are on a secure network segment! Security is your responsibility, not this scripts!

Current Limitations:
        Although the server can be stopped by remote client (it provides a stop
        service) it is not yet possible to interrupt the server by a keyboard action.
"""


import SocketServer
from SimpleXMLRPCServer import SimpleXMLRPCServer,SimpleXMLRPCRequestHandler
from xmlrpclib import Binary
import socket
from threading import Thread
import NetworkRender
NetworkRender.debugset()
from NetworkRender import debug

class Server(SimpleXMLRPCServer):
	"""
	a SimpleXMLRPCServer that will stop if a global var running is set to False	(e.g. by a registered function)
	
	It broadcasts its own uri to all on UDP/8082 before handling a request (to make zero configuration clients possible)
	and verifies that requests originate from a local (presumably secure) network.
	
	"""
	
	def __init__(self,address,handler):
			SimpleXMLRPCServer.__init__(self,address,handler)
			self.broadcast=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			# Allow the socket to broadcast, set the socket options.
			self.broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			self.ip=socket.gethostbyname(socket.gethostname())
			self.uri='http://'+self.ip+':8080'
				
	def server_bind(self):
		# allow fast restart of the server after it's killed
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		SimpleXMLRPCServer.server_bind(self)

	def broadcast_uri(self):
			from time import sleep
			global running
			while running:
				self.broadcast.sendto(self.uri,('255.255.255.255',8082))
				sleep(5)
	
	def verify_request(self, request, client_address):
		"""
		forbid requests except from specific client hosts
		
		"""
		return NetworkRender.allowedAddress(self.ip,client_address[0])
		
	def serve_till_stopped(self):
		global running
		running = True
		broadcastthread=Thread(name='broadcast', target=self.broadcast_uri)
		broadcastthread.setDaemon(True)
		broadcastthread.start()
		while running:
			self.handle_request()

from NetworkRender.PartRenderer import PartRenderer

class Render(PartRenderer):
	"""
	Provides methods for remote clients to render single frames and (part of) stills.
	
	Besides functions to actually render something, it also provides functionality to upload a
	.blend file and to retrieve the rendered image.
	"""
	
	def ping(self) : 
		"""
		Signal existance to client.
		
		"""
		
		return 'I am alive'
	
	def newfile(self) :
		"""
		Create a temporary .blend file and open it for writing.
		
		This would initiate a .blend file upload from the client. Typical client code woukd be:
			
		file=open('clientsideblendfile','rb''
		server.newfile()
		buffer = True
		while buffer :
			buffer = file.read(8000)
			r=server.put(xmlrpclib.Binary(buffer))
		file.close()
		server.endfile()
		"""
		
		from tempfile import mkstemp
		import os
		fd,name = mkstemp(suffix='.blend')
		os.close(fd)
		self.name = name
		fd = open(name,'wb',8000)
		self.fd = fd
		print name
		return 1

	def put(self,data):
		"""
		Transfer a block of data from client to temporary serverside .blend.
		@data: a string of binary data
			
		see newfile()
		"""
		
		self.fd.write(str(data))
		return 1
	
	def endfile(self) :
		"""
		Close temporary serverside .blend.
		
		see newfile()
		"""
		
		self.fd.close()
		return 1
	
	def renderFrame(self,scenename,frame):
		"""
		Render a single frame of a scene.
		@scenename: the name of the scene to render
		@frame: the number of the frame
		
		"""
		
		import bpy
		lib = bpy.libraries.load(self.name)
		print self.name,' loaded'
		scn = lib.scenes.link(scenename)
		context = scn.getRenderingContext()
		print 'remote render start',frame
		context.displayMode=0 #to prevent an additional render window popping up
		context.currentFrame(frame)
		s,context.sFrame=context.sFrame,frame
		e,context.eFrame=context.eFrame,frame    ########## remember to restore later!
		context.renderAnim()
		context.sFrame,context.eFrame=s,e
		print 'remote render end frame',frame
		self.result=context.getFrameFilename()
		return 'render finished'

	def renderPart(self,scenename,partindex, nparts):
		"""
		Render a single part of a multipart still. 
		@scenename: the name of the scene to render
		@partindex: the partnumber to render ( 0 <= partindex < nparts^2 ) 
		@nparts   : the number of parts a still is divided in boyh directions
			
		Based on Macouno's Really Big Render ( http://www.alienhelpdesk.com/python_scripts/really_big_render )
		Kudos to him, implementation errors are entirely mine.
		See NetworkRender.PartRenderer for additonal info.
		
		"""
		
		import bpy
		lib = bpy.libraries.load(self.name)
		print self.name,' loaded'
		scn = lib.scenes.link(scenename)
		context = scn.getRenderingContext()
		print 'remote render start part',partindex
		context.displayMode=0 		#to prevent an additional render window popping up
		
		self._PartName(partindex,nparts)
		# change camera related stuff
		self._setParam(scn,context,partindex,nparts)		
		scn.update()
		context.renderPath=self.result
		f=context.currentFrame()
		s,context.sFrame=context.sFrame,f
		e,context.eFrame=context.eFrame,f    ########## remember to restore later!
		debug('current=%d start=%d end=%d' % (f,context.sFrame,context.eFrame))
		debug('start render')
		context.renderPath=self.result
		context.renderAnim()  # because .render doesn't work in the background
		context.sFrame,context.eFrame=s,e
		self.result=context.getFrameFilename()
		self._resetParam(scn,context)
		
		print 'remote render end part',partindex
		return 'render finished'

	def getResult(self):
		"""
		Start downloading rendered image to client.
		@returns: the serverside name of the rendered image
		
		Typical client side code would be:
		name = server.getResult()
		file=open(name,'wb',8000)
		while True:
			data=str(self.rpcserver.get())
			if len(data)<=0: break
			else: file.write(str(data))
		file.close()
			
		"""
		self.fd2=open(self.result,'rb',8000)
		return self.result
	
	def get(self):
		"""
		Retrieve a block of data from a serverside rendered image.
		@returns: A xmlrpclib.Binary object
		
		See getResult().
		"""
		
		data=self.fd2.read(8000)
		if len(data)<=0: self.fd2.close()
		return Binary(data)
	
	def stop (self): global running; running = False; return 'stop requested'


# Instantiate and bind to localhost:8080
server = Server(('',8080),SimpleXMLRPCRequestHandler)
 
# Register example object instance
server.register_instance(Render())
 
# run!
server.serve_till_stopped()

# bye
print 'Render server terminated'
