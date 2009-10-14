"""
RendererImpl.py common functions for rendering (local and
remote) of stills and parts.

It defines a single class RendererImpl that implements sending a .blend file
if needed, retrieving results and some support functions. It does NOT
implement the actual rendering of parts or frames (see
L{Network.AnimRenderThread} and L{Network.StillRenderThread})
NOR communication with the environment (see L{Network.RenderThread})
"""

__author__   = 'Michel Anders (varkenvarken)'
__copyright__= '(cc) non commercial use only and attribution by'
__url__      = ["Author's site, http://www.swineworld.org/blender"]
__email__    = ['varkenvarken is my nick at blendernation.org, PM me there']
__version__  = '1.00 2008-10-20'
__history__  = ['1.00 2008-10-20, initial version']

import xmlrpclib, NetworkRender

from xmlrpclib import Server,Binary
from Blender import Scene
from NetworkRender.Configurer import Configurer

NetworkRender.debugset()
from NetworkRender import debug

class RendererImpl():
	"""
	Common functions for rendering frames and part of stills.
	"""

	def __init__(self, uri, scenename, context, name, imageType):
		"""
		@param uri: uri of remote renderserver OR 'localhost'
		@type uri: string
		@param scenename: name of current scene
		@type scenename: string
		@param context: current render context
		@type context: Scene.Renderdata
		@param name: filename of saved .blend file
		@type name: string
		@param imageType: type of output image
		@type imageType: int
		"""

		self.configurer = Configurer()
		self.uri = uri
		self.scenename = scenename
		self.context = context
		self.name = name
		self.rpcserver = None
		self.blendSent = False
		self.imageType = imageType

		if uri == 'localhost':
			self.blendSent = True
			self.scn = Scene.Get(scenename)
		else:
			self.rpcserver = Server(uri)

		self._reset()

	def _reset(self):
		self.busy = False
		self.frame = None

	def isLocal(self):
		"""
		returns True if these services run on 'localhost'
		@rtype: boolean
		"""

		return self.uri == 'localhost'

	def _sendBlendFile(self):
		"""
		Sent saved .blendfile if needed.

		Uploads saved .blend file to remote host if not already done so.
		"""

		if self.isLocal() or self.blendSent:
			pass
		else:
			self.rpcserver.newfile()
			fd = open(self.name, 'rb', self.configurer.get('ServerBufferSize'))
			debug('%s sending .blend: %s'%(self.uri, fd))
			n = 0
			buffer = True
			while buffer :
				buffer = fd.read(self.configurer.get('ServerBufferSize'))
				if buffer:
					r = self.rpcserver.put(Binary(buffer))
					debug('%s put response %s' % (self.uri, r))
					n = n + 1
					debug('%s %d blocks put'%(self.uri, n))
			fd.close()
			r = self.rpcserver.endfile()
			debug('%s endfile called, response %s'%(self.uri, r))
		self.blendSent = True

	def _getResult(self):
		"""
		Download rendered frame or part from remote server.
		"""

		debug('%s saving frame %d'%(self.uri, self.frame))
		if not self.isLocal():
			debug('%s getting remote frame %d'%(self.uri, self.frame))
			rname = self.rpcserver.getResult()

			from tempfile import mkstemp
			import os
			from os import path

			remotedir,remotefile = path.split(rname)
			if self.animation == True :
				localdir,localfile = path.split(self.context.getFrameFilename())
				name = path.join(localdir,remotefile)

			fd,tname = mkstemp(suffix = remotefile)
			os.close(fd)
			debug('%s saving remote frame %d as tempfile %s' %
				(self.uri, self.frame, tname))
			fd = open(tname,'wb',self.configurer.get('ServerBufferSize'))

			while True:
				data = str(self.rpcserver.get())
				if len(data) <= 0:
					fd.close()
					break
				else:
					fd.write(str(data))

			fd.close()
			if self.animation == True :
				debug('%s frame %d renaming %s to %s'%(self.uri,self.frame, tname, name))
				if os.access(name, os.F_OK):
					os.unlink(name) # windows won't let us rename to an existing file
				debug("%s %s exists? %s" % (self.uri,tname, os.access(tname, os.F_OK)))
				os.rename(tname,name)

				# why all this trouble? the source file on the serverside might
				# be on the exact same location as the file we try to write
				# on the clientside if we run the server and the on the same
				# machine (as we might do for testing)
				self.result = name
			else :
				self.result = tname

			print 'Saved: %s (remotely rendered)'% self.result
		else:
			print 'Saved: %s (locally rendered)'% self.result
			pass
		debug('%s saving frame %d done'%(self.uri,self.frame))
