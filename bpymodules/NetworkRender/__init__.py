"""
NetworkRender.py helperfunctions/classes for Network Rendering in Blender

This file is called __init__.py since there is both a module NetworkRender and
a package NetworkRender
"""

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

def allowedAddress(own,other):
	"""
	Check whether two ip addresses are local to eachother.
	@param own: ip-address as dotted quad, i.e. 1.2.3.4
	@param other: ip-address as dotted quad, i.e. 1.2.3.4

	The 'other' address is considered local (and therefor allowed) to the
	'own'address if it is:
	 - a localhost address 127.*.*.*
	 - in a local C-address range and shares the first 3 quads
	 - in a local B-address range and shares the first 2 quads
	 - in a local A-address range and shares the first quad
	"""
	a,b,c,d= own.split('.')
	A,B,C,D= other.split('.')
	if A=="127": return True
	elif a=="192" and b=="168":
		if a==A and b==B and c==C: return True
	elif a=="172" and int(b)>=16 and int(b)<=31:
		if a==A and b==B: return True
	elif a=="10":
		if a==A: return True
	return False

import Blender
	
def _debug(*args):
	print 'debug:',args

def _nodebug(*args): pass

def debugset():
	"""
	Enable debuging output if the Blender 'rt' variable is set to 7
	"""
	global debug
	if Blender.Get('rt') == 7 :
		print 'debugmode on'
		debug = _debug
	else :
		print 'debugmode off'
		debug = _nodebug
	

import Blender.Window
from threading import Thread

class Interrupt(Thread):
	"""
	unfortunately, as of yet this does not seem to work :-(
	"""
	def run(self):
		from time import sleep
		global running
		while not Blender.Window.TestBreak(): 
			sleep(5)
		running=False

import os
from Blender import Scene

def saveblend():
	"""
	Save the current .blend file as a temporary file.
	@returns: (scn,context,scenename,name)

	scn is the current scene object
	context the current rendering context
	scenename the name of the current scene
	name the name of the temporary file

	@warning: sideeffect: sets displaymode to 0 (=rendering in imagewindow) to
	prevent rendering window popping up
	"""
	Blender.PackAll()
	from tempfile import mkstemp
	fd,name = mkstemp(suffix = '.blend')
	os.close(fd)
	Blender.Set('compressfile',True)
	Blender.Save(name,1)
	scn = Scene.getCurrent()
	scenename = scn.getName()
	context = scn.getRenderingContext()
	context.displayMode=0 #to prevent an additional render window popping up
	return (scn,context,scenename,name)

def displaystats(stats,n,starttime,endtime):
	"""
	Print rendertime statistics for the various remote and local threads.
	@param stats: a queue of tuples (frames, seconds, errorframes)
	@type stats: Queue.queue
	@param n: total number of frames to render
	@type n: int         
	@param starttime: start time in seconds since epoch
	@type starttime: float  
	@param endtime: end time in second since epoch
	@type endtime: float
	@returns: per frame filenames sorted by framenumber
	"""
	from collections import defaultdict
	stats_f = defaultdict(int)
	stats_t = defaultdict(float)
	stats_e = defaultdict(int)
	namelist = {}
	while not stats.empty():
			s = stats.get()
			stats.task_done()
			stats_f[s[0]] = stats_f[s[0]]+1       # tally frames
			stats_t[s[0]] = stats_t[s[0]]+s[2]    # tally times
			stats_e[s[0]] = stats_e[s[0]]+s[3]    # tally errorframes
			if s[3] == 0 : namelist[s[1]]=s[4]  # record filename of frame
	te = 0.0
	for i in stats_e : 
			te += stats_e[i]
	print '\nrender statistics\n-----------------'
	print '%30s %7s %s'%('server','frames','time')
	for i in stats_f :
			print '%30s %3d/%3d %5.1f'%(i,stats_f[i],stats_e[i],stats_t[i])
	print '%30s %3d/%3d %5.1f'%('total',n,te,endtime-starttime)

	if stats_t['localhost'] != 0 and stats_f['localhost'] != 0:
		org = (n) * stats_t['localhost'] / stats_f['localhost']
		gain = 1.0 - (endtime - starttime) / org
		print 'done. gain is %4.1f%%'% (gain * 100.0)
	else:
		print 'done.'
	#print namelist
	return [namelist[key] for key in sorted(namelist.keys())]

def collate(imagelist,outputfilename):
	"""
	Collate a list of images to a single image.
	@param imagelist: list of filenames
	@param outputfilename: file to write collated images to
	"""
	try:
		import PIL
		from PIL import Image
		debug('trying to import Python Image Library')
	except ImportError,NameError:
		debug('no luck importing Python Image Library')
                return None
	from math import sqrt
	nparts = len(imagelist)
	n = int(sqrt(nparts))
	debug(imagelist)
	im = Image.open(imagelist[0])
	size = im.size
	im = Image.new('RGBA', (n * size[0], n * size[1]))
	i = 0
	for part in imagelist:
		debug('adding image part %d from %s' % (i,part))
		pim = Image.open(part)
		size = pim.size
		dy = int(i/n)
		dx = i%n
		im.paste(pim,(dx * size[0], dy * size[1]))
		i += 1

	im.save(outputfilename)
	debug('saved collated images to %s'% outputfilename)
