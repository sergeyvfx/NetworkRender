"""
StillRenderThread.py still image specific functions for client side threads.

It defines a single class StillRenderThread that implements a single public
function 'render' that will be called by its abstract superclass L{NetworkRender.RenderThread}.
Its render() function renders a single part of a still image.
"""

__author__   ='Michel Anders (varkenvarken)'
__copyright__='(cc) non commercial use only and attribution by'
__url__      =["Author's site, http://www.swineworld.org/blender"]
__email__    =['varkenvarken is my nick at blendernation.org, PM me there']
__version__  ='1.00 2008-10-20'
__history__  =['1.00 2008-10-20, initial version'
                ]
from NetworkRender.PartRenderer import PartRenderer
from NetworkRender.RenderThread import RenderThread
from NetworkRender.Renderer import Renderer
import NetworkRender
NetworkRender.debugset()
from NetworkRender import debug

class StillRenderThread(RenderThread,Renderer,PartRenderer):
	"""
        Still image specific functions for client side threads.
        """
	def __init__(self,uri,scenename,context,name,fqueue,squeue,nparts):
                """
                Initialize a StillRenderThread
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
                @param nparts: the number of parts in either direction
                @type nparts: int
                """
		RenderThread.__init__(self,uri,scenename,context,fqueue,squeue)
		Renderer.__init__(self,uri,scenename,context,name)
		PartRenderer.__init__(self,nparts)
		
	def _renderStill(self):
		debug('%s render started for frame %d'%(self.uri,self.frame))
		if self.isLocal() :
			self._PartName(self.frame,self.nparts)
			debug('partname set')
			self._setParam(self.scn,self.context,self.frame,self.nparts)
			debug('setparam done')
			self.scn.update()
			self.context.renderPath=self.result
			debug('renderpath before %s'%self.context.renderPath)
			f=self.context.currentFrame()
			s,self.context.sFrame=self.context.sFrame,f
			e,self.context.eFrame=self.context.eFrame,f	########## remember to restore later!
			debug('current=%d start=%d end=%d' % (f,self.context.sFrame,self.context.eFrame))
			debug('start render')
			self.context.renderAnim()  # because .render doesn't work in the background
			self.result=self.context.getFrameFilename()
			self.context.sFrame,self.context.eFrame=s,e
			#self.context.saveRenderedImage(self.result, 0)
			debug('resetparam')
			self._resetParam(self.scn,self.context)
			debug('renderpath after %s'%self.context.renderPath)
		else:
			self.rpcserver.renderPart(self.scenename,self.frame,self.nparts)
			
		debug('%s render completed for frame %d'%(self.uri,self.frame))
		
	
	def render(self,frame):
                """
                Render a single part of a still image.
                @param frame: the partnumber
                @type frame: int
                """
		self.busy=True
		self.frame=frame
		self.animation=False
		self._sendBlendFile()
		self._renderStill()
		self._getResult()
		self._reset()
