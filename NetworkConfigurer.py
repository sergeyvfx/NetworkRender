#!BPY

"""Registration info for Blender menus
Name: 'NetworkRender configurator'
Blender: 2.49
Group: 'Render'
Tip: 'Configuration script for NetworkRender'
"""

__author__ = "Sergey I. Sharybin"
__copyright__="(cc) non commercial use only and attribution by"
__version__ = "0.1"
__email__ = "g.ulairi@gmail.com"

import Blender
from Blender import *

import NetworkRender
from NetworkRender.Configurer import Configurer

No_Event,Event_Quit,Event_Save,Event_Close = range(4)

configurer = Configurer()

def event(evt, val):
	if evt == Draw.ESCKEY or evt == Draw.QKEY:
		bevent(Event_Quit) 

def bevent(evt):
	if evt == Event_Quit:
		Blender.Draw.Exit()

	if evt == Event_Close:
		global configurer
		configurer.destroy()
		Blender.Draw.Exit()

	if evt == Event_Save:
		configurer.writeRegistry()

def gui():
	global configurer

	BGL.glClearColor(0.5, 0.5, 0.5, 0.0)
	BGL.glClear(BGL.GL_COLOR_BUFFER_BIT)

	BGL.glColor3f(0.7, 0.7, 0.7)
	BGL.glRecti(0, 0, 530, 125)
	BGL.glColor3f(0.65, 0.65, 0.65)
	BGL.glRecti(0, 125, 530, 145)
	BGL.glColor3f(0.0, 0.0, 0.0)
	BGL.glRasterPos2f(5, 131)
	Draw.Text("NetworkRender configurator")

# Server configuration
	Blender.BGL.glColor3f(0,0,0)
	Blender.BGL.glRasterPos2i(10, 112)
	Blender.Draw.Text("Server")
	Blender.BGL.glBegin(Blender.BGL.GL_LINE_STRIP)
	Blender.BGL.glVertex2i(5, 114)
	Blender.BGL.glVertex2i(5, 5)
	Blender.BGL.glVertex2i(175, 5)
	Blender.BGL.glVertex2i(175, 114)
	Blender.BGL.glVertex2i(50, 114)
	Blender.BGL.glEnd()

	configurer.setDrawValue('ServerPort', \
						Draw.Number('Port:', No_Event, 10, 92, 160, 15, \
								configurer.get('ServerPort'), 0, 65535, \
								"Port on which NetworkRender servers will be binded"))

	configurer.setDrawValue('ServerAddr', \
						Draw.String("Serv addr: ", No_Event, 10, 72, 160, 15, \
								configurer.get('ServerAddr'), 32, \
								"IP address to send as main server address" +
								" (use 0.0.0.0 for auto-detect)"))

	configurer.setDrawValue('ServerBCast', \
						Draw.String("BCast addr: ", No_Event, 10, 52, 160, 15, \
								configurer.get('ServerBCast'), 32, \
								"IP address for broadcast messages"))

	configurer.setDrawValue('ServerBCastInterval', \
						Draw.Number('BCast int.:', No_Event, 10, 32, 160, 15, \
								configurer.get('ServerBCastInterval'), 0, 65535, \
								"Interval ob broadcast clients notification"))

	configurer.setDrawValue('ServerStaticMap', \
						Draw.String("Static map: ", No_Event, 10, 12, 160, 15, \
								configurer.get('ServerStaticMap'), 32, \
								"Static client-server map" +
								" (<client>:<server> pairs, delimited by comma)"))

# Client configuration
	Blender.BGL.glColor3f(0,0,0)
	Blender.BGL.glRasterPos2i(190, 112)
	Blender.Draw.Text("Client")
	Blender.BGL.glBegin(Blender.BGL.GL_LINE_STRIP)
	Blender.BGL.glVertex2i(185, 114)
	Blender.BGL.glVertex2i(185, 65)
	Blender.BGL.glVertex2i(525, 65)
	Blender.BGL.glVertex2i(525, 114)
	Blender.BGL.glVertex2i(225, 114)
	Blender.BGL.glEnd()

	configurer.setDrawValue('ClientPort', \
						Draw.Number('Port:', No_Event, 190, 92, 160, 15, \
								configurer.get('ClientPort'), 0, 65535, \
								"Port on which NetworkRender clients will be binded"))
	configurer.setDrawValue('ClientLocalRendering', \
						Draw.Toggle("Local rendering", No_Event, 190, 72, 160, 15, \
								configurer.get('ClientLocalRendering'), \
								"Serve rendering queue by localhost machine"))

	configurer.setDrawValue('StillParts', \
						Draw.Number('StillParts:', No_Event, 360, 92, 160, 15, \
								configurer.get('StillParts'), 1, 16, \
								"Number of parts in each direction when still rendering"))

	menuname = 'Output file extension%t|' + configurer.getMenuExtensions()
	configurer.setDrawValue('ImageType', \
						Draw.Menu(menuname, No_Event, 360, 72, 160, 15, \
								configurer.get('ImageType'), \
								"Extension for output files"))


	Draw.PushButton("Apply changes", Event_Save, 185, 5, 165, 35, \
				"Apply changes of NetworkRender configuration")

	Draw.PushButton("Quit", Event_Close, 360, 5, 165, 35, \
				"Quit from NetworkRender configuration script")

Draw.Register(gui, event, bevent)
