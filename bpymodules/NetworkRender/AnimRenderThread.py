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

from NetworkRender.RenderThread import RenderThread
from NetworkRender.Renderer import Renderer
import NetworkRender
NetworkRender.debugset()
from NetworkRender import debug

class AnimRenderThread(RenderThread,Renderer):
	
	def __init__(self,uri,scenename,context,name,fqueue,squeue):
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
                """
                RenderThread.__init__(self,uri,scenename,context,fqueue,squeue)
		Renderer.__init__(self,uri,scenename,context,name)
		
	def _renderFrame(self):
		debug('%s render started for frame %d'%(self.uri,self.frame))
		if self.isLocal():
			self.context.currentFrame(self.frame)
			s,self.context.sFrame=self.context.sFrame,self.frame
			e,self.context.eFrame=self.context.eFrame,self.frame    ########## remember to restore later!
			self.context.renderAnim()
			self.result=self.context.getFrameFilename()
			self.context.sFrame,self.context.eFrame=s,e
		else:
			self.rpcserver.renderFrame(self.scenename,self.frame)
		debug('%s render completed for frame %d'%(self.uri,self.frame))
		
	def render(self,frame):
                """
                Render a single frame.
                @param frame: the framenumber to render
                @type frame: int
                """
		self.busy=True
		self.frame=frame
		self.animation=True
		self._sendBlendFile()
		self._renderFrame()
		self._getResult()
		self._reset()

