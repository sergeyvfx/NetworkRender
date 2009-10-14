"""
Renderer.py is a gate between RenderThread + RendererImpl and finito
rendering threads classes.

This needs to prevent multiply inheritance of classes with defined methods
with the same name.
"""

__author__   = 'Sergey I. Sharybin'
__copyright__= '(cc) non commercial use only and attribution by'
__email__    = ['g.ulairi@gmail.com']
__version__  = '0.1'

from RenderThread import RenderThread
from RendererImpl import RendererImpl

class Renderer(RenderThread, RendererImpl):
	def __init__(self, uri, scenename, context, name, fqueue, squeue, imageType):
		"""
		Initialize a Renderer

		@param uri: uri of remote render server OR 'localhost'
		@param scenename: name of current scene
		@param context: current rendering context
		@param name: the filename of the saved .blendfile
		@param fqueue: worklist
		@param squeue: rendering statistics
		@param imageType: type of output image
		"""

		RenderThread.__init__(self, uri, scenename, context, fqueue, squeue)
		RendererImpl.__init__(self, uri, scenename, context, name, imageType)

	def serviceAlive(self):
		"""
		Check if queue servicing is alive or finished it successfully
		"""

		if (not RenderThread.serviceAlive(self)):
			return False

		if (not self.isLocal()):
			if (self.rpcserver):
				try:
					response = self.rpcserver.ping()

					if (response != 'I am alive'):
						# Trash is received
						return False
				except (xmlrpclib.Error, socket.error), e:
					print 'remote exception caught while pinging server', e
			else:
				# Renderer is not local, but there is no RPC server
				return False

		return True
