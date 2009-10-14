"""
AnimRenderThread.py animation specific functions for client side threads.

It defines a single class AnimRenderThread that implements a single public
function 'render' that will be called by its abstract superclass L{NetworkRender.RenderThread}.
"""

__author__   ='Michel Anders (varkenvarken)'
__copyright__='(cc) non commercial use only and attribution by'
__url__      =["Author's site, http://www.swineworld.org/blender"]
__email__    =['varkenvarken is my nick at blendernation.org, PM me there']
__version__  ='1.00 2008-10-20'
__history__  =['1.00 2008-10-20, initial version'
                ]

import NetworkRender

from NetworkRender.RenderThread import RenderThread
from NetworkRender.Renderer import Renderer

NetworkRender.debugset()
from NetworkRender import debug

class AnimRenderThread(Renderer):
	
	def __init__(self, uri, scenename, context, name, fqueue, squeue, imageType):
		"""
		Initialize a AnimRenderThread
		@param uri: uri of remote render server OR 'localhost'
		@type uri: string
		@param scenename: name of current scene
		@type scenename: string
		@param context: current rendering context
		@type context: Scene.Renderdata
		@param name: the filename of the saved .blendfile
		@type name: string
		@param fqueue: worklist
		@type fqueue: Queue.queue
		@param squeue: rendering statistics
		@type squeue: Queue.queue
		@param imageType: type of output image
		@type imageType: int
		"""

		Renderer.__init__(self, uri, scenename, context, name,
						fqueue, squeue, imageType)

	def _renderFrame(self):
		debug('%s render started for frame %d'%(self.uri,self.frame))
		if self.isLocal():
			self.context.currentFrame(self.frame)

			# remember to restore later!
			s,self.context.sFrame = self.context.sFrame,self.frame
			e,self.context.eFrame = self.context.eFrame,self.frame
			oldImagetype = self.context.imageType

			self.context.imageType = self.imageType
			self.context.renderAnim()
			self.result = self.context.getFrameFilename()

			# Restore changed settings
			self.context.sFrame,self.context.eFrame = s,e
			self.context.imageType = oldImagetype
		else:
			self.rpcserver.renderFrame(self.scenename, self.frame, self.imageType)
		debug('%s render completed for frame %d'%(self.uri, self.frame))

	def render(self,frame):
		"""
		Render a single frame.
		@param frame: the framenumber to render
		@type frame: int
		"""

		self.busy = True
		self.frame = frame
		self.animation = True
		self._sendBlendFile()
		self._renderFrame()
		self._getResult()
		self._reset()
