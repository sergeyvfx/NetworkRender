"""
PartRenderer.py support functions for rendering a still in multiple parts.

Based on an implementation bij Macouno U{http://www.alienhelpdesk.com/pages/really_big_render/}
Kudos to him, implemenatation faults are completely mine.
"""

__author__   ='Michel Anders (varkenvarken)'
__copyright__='(cc) non commercial use only and attribution by'
__url__      =["Author's site, http://www.swineworld.org/blender"]
__email__    =['varkenvarken is my nick at blendernation.org, PM me there']
__version__  ='1.00 2008-10-20'
__history__  =['1.00 2008-10-20, initial version'
                ]

import NetworkRender
NetworkRender.debugset()
from NetworkRender import debug

from Blender import Camera

class PartRenderer:
	"""
	Support functions for rendering a still in multiple parts.
	"""

	def __init__(self, nparts = 4):
		self.nparts = nparts

	def _setParam(self,scn,context,partindex,nparts):
		"""
		Initializes scene and context for rendering a given part.

		Also saves the altered parameters of scene and context for
		later restoration by L{_resetParam()}. See L{NetworkRender.StillRenderThread}
		for typical use.

		@param scn: the current scene
		@type scn : Blender.Scene
		@param context: the current render context
		@type context: Scene.Renderdata
		@param partindex: the number of parts in either direction
		@type partindex: int
		@param nparts: the number of parts in either direction
		@type nparts: int.

		@requires: nparts = 2,3,4,5, ....
		@requires: partindex = [0, nparts^2 >
		"""

		self.nparts = nparts
		self.cam = Camera.Get(scn.getCurrentCamera().getName())
		self.scn = scn
		self.depth = context.imagePlanes
		self.aspx = float(context.sizeX) / float(context.sizeY)
		self.aspy = float(context.sizeY) / float(context.sizeX)
		self.camipo = None	  
		if self.cam.ipo:
			self.camipo = self.cam.ipo
			self.cam.ipo = None
		self.lens = self.cam.lens
		self.scale = self.cam.scale
		self.shiftX = self.cam.shiftX
		self.shiftY = self.cam.shiftY
		self.path = context.renderPath
		
		self.cam.scale = (self.scale / (nparts + 1))  
		self.cam.lens = (self.lens * (nparts))
	
		tileStart = [ i * -0.5 for i in range(nparts + 1)]
		print partindex, nparts, tileStart
		y = int(partindex/nparts)
		x = partindex%nparts
		shiftY = (-tileStart[nparts - 1] - float(y))
		shiftX = (float(x) + tileStart[nparts - 1])

		if self.aspx > 1.0 :
			shiftY /= self.aspx
		else :
			shiftX /= self.aspy

		self.cam.shiftX = shiftX
		self.cam.shiftY = shiftY

		debug('x=%d y=%d shiftX=%4.2f shiftY=%4.2f index=%d nparts%d'%(x, y, shiftX, shiftY, partindex, nparts))

	def _resetParam(self,scn,context):
		"""
		Restore original parameters of scene and context.
		"""

		if self.camipo:
			self.cam.ipo = self.camipo

		context.renderPath = self.path
		self.cam.lens = self.lens
		self.cam.scale = self.scale
		self.cam.shiftX = self.shiftX
		self.cam.shiftY = self.shiftY
		self.scn.update()
		return

	def _PartName(self,partindex,nparts):
		"""
		Create a temporary file for storing a rendered part.
		@param partindex: the partnumber
		@type partindex: int
		@param nparts: the number of parts in either direction
		@type nparts: int
		@returns: the temporary filename
		@rtype: string
		"""

		from tempfile import mkstemp
		import os

		p = '%d_%d' % (partindex, nparts * nparts - 1)
		fd,name = mkstemp(prefix = p, suffix = '.image')
		os.close(fd)
		self.result = name
		return name
