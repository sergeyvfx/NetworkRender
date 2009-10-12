"""
Listener.py workload dispatcher for remote renderservers.

Defines a single class Listener that implements a listener process that listens
to announcements of remote renderservers and spawns a L{NetworkRender.RenderThread} if it detects
a new one.
"""

__author__   ='Michel Anders (varkenvarken)'
__copyright__='(cc) non commercial use only and attribution by'
__url__      =["Author's site, http://www.swineworld.org/blender"]
__email__    =['varkenvarken is my nick at blendernation.org, PM me there']
__version__  ='1.00 2008-10-20'
__history__  =['0.01 2008-10-09, initial version',
               '0.02 2008-10-10, bugfix version',
               '1.00 2008-10-20, code refactoring'
               ]

from threading import Thread
import socket

import NetworkRender
NetworkRender.debugset()
from NetworkRender import debug

from NetworkRender.Configurer import Configurer

class Listener(Thread):
	"""
	Implements a listener process that listens to announcements of remote
	renderservers and spawns a RenderThread if it detects a new one.
	"""

	def __init__(self, scenename, context, name, fqueue, squeue, threadfactory, *args):
		"""
		Initialize a Listener instance.
		@param scenename: name of current scene
		@type scenename: string
		@param context: rendercontext of current scene
		@type context: Blender.Renderdata
		@param name: filename of saved .blend file
		@type name: string
		@param fqueue: worklist queue
		@type fqueue: Queue.queue
		@param squeue: statistics queue
		@type squeue: Queue.queue
		@param threadfactory: a classfactory to spawn worker threads
		@type threadfactory: NetworkRender.Renderthread
		@param args: additional arguments to be given to the threadfactory
		"""

		Thread.__init__(self)
		self.scenename = scenename
		self.context = context
		self.name = name
		self.factory = threadfactory
		self.fqueue = fqueue
		self.squeue = squeue
		self.args = args
		self.configurer = Configurer()
		debug('UDPlistener starting')
		self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)	
		debug('UDPlistener socket created %s' % self.socket)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		debug('UDPlistener options set')
		#self.ip = socket.gethostbyname(socket.gethostname())
		self.ip = '0.0.0.0'
		self.socket.bind((self.ip, self.configurer.get('ClientPort')))
		debug('UDPlistener listening on %s'%self.socket)

	def registerNode(self, uri):
#		if (self.uriMap.get(uri) == None):
		debug('spawning new thread for %s' % uri)
		rt = self.factory(uri, self.scenename, self.context,
						self.name, self.fqueue,
						self.squeue,*self.args)
		self.r.append(rt)
		self.uriMap[uri] = True
		rt.start()

	def run(self):
		"""
		Listen and spawn new worker threads if appropriate.

		Overridden from Thread. Implements a stoppable loop (stops
		when requestStop is called on this thread) and records with
		workerthreads were spawned.
		"""

		import time
		self.stop = False
		self.r = []
		self.uriMap = {}

		# Register static list of server
		servers = self.configurer.get('ClientServerList').split(',')
		for server in servers:
			if (server == ''):
				continue
			serverData = server.split(':')
			if (len (serverData) == 1):
				serverData.append(str(self.configurer.get('ServerPort')))
			self.registerNode('http://' + serverData[0] + ':' + serverData[1])

		while not self.stop:
			debug('UDPlistener ready for request on %s,%s' % self.socket.getsockname())
			try:
				self.socket.settimeout(5)
				data, addr = self.socket.recvfrom(512)
				debug('UDPlistener received request: %s from %s' % (data, addr))
				self.registerNode(data)
			except (socket.timeout) :
				debug('UDPlistener received nothing, will try again')
			finally:
				time.sleep(self.configurer.get('ServerBCastInterval'))
		debug('UDPlistener stopped')

	def requestStop(self):
		"""
		Request this thread to stop.
		"""

		self.stop=True

	def getRemotethreads(self):
		"""
		@returns: a list of previously spawned workerthreads.
		"""

		return self.r
