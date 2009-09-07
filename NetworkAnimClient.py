#!BPY
#"""
#Name: 'AnimationClient'
#Blender: 247
#Group: 'Render'
#Submenu: 'Network Rendering' animationclient
#Tooltip: 'Renders an animation locally and remote'
#"""

__author__   ='Michel Anders (varkenvarken)'
__copyright__='(cc) non commercial use only and attribution by'
__url__      =["Author's site, http://www.swineworld.org/blender"]
__email__    =['varkenvarken is my nick at blendernation.org, PM me there']
__version__  ='1.00 2008-10-20'
__history__  =['1.00 2008-10-20, code refactoring and documentation update',
               '0.03 2008-10-9, code cleanup and bug fixes',
               '0.02 2008-10-8 better debugging and robustness (requeueing failed frames)',
               '0.01 2008-10-6 initital version'
               ]

__bpydoc__="""\		
A simple render client that renders an animation on remote servers and
by itself. To be used with RenderServer

Usage: from the scripts menu select Render->Network Rendering->AnimationClient
	extensive debugging info is produced if the 'rt' variable in the anim panel
	of the rendering context is set to '7'

Installation: unpack NetworkRender.zip into your .blend/scripts directory
(this zip contains both scripts and supportfiles, including a subdirectory)

Prerequisite: a full Python 2.5 installation is required for this script to run.

Warning: this script listens on UDP port 8082. Your resident firewall may warn about that.

Security is your responsibility, not this scripts!

Current Limitations:
        Its only possible to render an animation as a sequence of images, not
        directly as an .avi 
"""

import NetworkRender
NetworkRender.debugset()
from NetworkRender import debug

from NetworkRender.AnimRenderThread import AnimRenderThread
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
listener = Listener(scenename,context,name,frames,stats,AnimRenderThread)
listener.start()

# create a local renderer (we wont let others do all the dirty work :-)
localrenderer = AnimRenderThread('localhost', scenename, context, name, frames,stats)

# initialize the worklist
for frame in range(context.sFrame, context.eFrame + 1):
	debug('queueing frame %d' %frame)
	frames.put(frame)

# start the local rendere and wait for it to end	
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
endtime = time.time()
NetworkRender.displaystats(stats, context.eFrame - context.sFrame + 1, starttime, endtime)
