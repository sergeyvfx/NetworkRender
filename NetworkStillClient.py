#!BPY
#"""
#Name: 'StillClient'
#Blender: 247
#Group: 'Render'
#Submenu: 'Network Rendering' stillclient
#Tooltip: 'Renders a still image locally and remote'
#"""

__author__   ='Michel Anders (varkenvarken)'
__copyright__='(cc) non commercial use only and attribution by'
__url__      =["Author's site, http://www.swineworld.org/blender"]
__email__    =['varkenvarken is my nick at blendernation.org, PM me there']
__version__  ='1.00 2008-10-20'
__history__  =['1.00 2008-10-20, code refactoring and documentation update',
               '0.03 2008-10-9, code cleanup and bug fixes']

__bpydoc__="""\		
A simple render client that renders an still image in parts on remote servers and
by itself. To be used with RenderServer

Usage: from the scripts menu select Render->Network Rendering->StillClient
	extensive debugging info is produced if the 'rt' variable in the anim panel
	of the rendering context is set to '7'

Installation: unpack NetworkRender.zip into your .blend/scripts directory
(this zip contains all scripts and supportfiles, including a subdirectory)

Prerequisite: a full Python 2.5 installation is required for this script to run.

Warning: this script listens on UDP port 8082. Your resident firewall may warn about that.

Security is your responsibility, not this scripts!

Current Limitations: 
	The resulting parts are not (yet) commposited into a single image
	An image is (for now) always split into 2x2 parts

"""

from tempfile import mkstemp
import os

from Blender import Image
import NetworkRender
NetworkRender.debugset()
from NetworkRender import debug

from NetworkRender.StillRenderThread import StillRenderThread
import time
from Queue import Queue

frames=Queue()		# the worklist (either part- or framenumbers)
stats=Queue()		# statistics are communicated by the renderthreads via this queue

# lets start!
starttime=time.time()
# save the current .blend
(scn,context,scenename,name) = NetworkRender.saveblend()

# start listening for remote servers
from NetworkRender.Listener import Listener
listener=Listener(scenename,context,name,frames,stats,StillRenderThread,2)
listener.start()

# create a local renderer (we wont let others do all the dirty work :-)
localrenderer = StillRenderThread('localhost',scenename,context,name,frames,stats,2)

# initialize the worklist
for frame in range(4):
	debug('queueing frame %d' %frame)
	frames.put(frame)
	
# start the local renderer and wait for it to end
localrenderer.start()
localrenderer.join()

# wait for the remote renderers to finish and ask the listener to stop
rt = listener.getRemotethreads();
listener.requestStop()
for r in rt : 
	debug('waiting for end of thread %s'%r.getName())
	r.join()

# wait for the listener to stop (but not forever)
listener.join(20.0)

# display some statistics, to see if it was worth the effort
endtime=time.time()
partlist=NetworkRender.displaystats(stats,4,starttime,endtime)

# try to merge to parts and show the result in the image editor
fd,name = mkstemp(suffix='.jpg')
os.close(fd)
NetworkRender.collate(partlist,name)
im=Image.Load(name)
im.makeCurrent()

	