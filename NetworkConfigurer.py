#!BPY

"""Registration info for Blender menus
Name: 'NetworkRender configurator'
Blender: 2.49
Group: 'Render'
Tip: 'Configuration script for NetworkRender'
"""

__author__ = "Sergey I. Sharybin"
__copyright__='(cc) non commercial use only and attribution by'
__version__ = "0.1"
__email__ = "g.ulairi@gmail.com"

import Blender
from Blender import *

import NetworkRender
from NetworkRender.Configurer import Configurer

No_Event,Event_Quit,Event_Save = range(3)

configurer = Configurer()

def event(evt, val):
	if evt == Draw.ESCKEY or evt == Draw.QKEY:
		bevent(Event_Quit) 

def bevent(evt):
	if evt == Event_Quit:
		Blender.Draw.Exit()

	if evt == Event_Save:
		configurer.writeRegistry()

def gui():
	global configurer

	BGL.glClearColor(0.5, 0.5, 0.5, 0.0)
	BGL.glClear(BGL.GL_COLOR_BUFFER_BIT)

	BGL.glColor3f(0.7, 0.7, 0.7)
	BGL.glRecti(0, 0, 360, 85)
	BGL.glColor3f(0.65, 0.65, 0.65)
	BGL.glRecti(0, 85, 360, 105)
	BGL.glColor3f(0.0,0.0,0.0)
	BGL.glRasterPos2f(5,91)
	Draw.Text("NetworkRender configurator")

# Server configuration
	Blender.BGL.glColor3f(0,0,0)
	Blender.BGL.glRasterPos2i(10,72)
	Blender.Draw.Text("Server")
	Blender.BGL.glBegin(Blender.BGL.GL_LINE_STRIP)
	Blender.BGL.glVertex2i(5,74)
	Blender.BGL.glVertex2i(5,5)
	Blender.BGL.glVertex2i(175,5)
	Blender.BGL.glVertex2i(175,74)
	Blender.BGL.glVertex2i(50,74)
	Blender.BGL.glEnd()

	configurer.setDrawValue('ServerPort', Draw.Number('Port:', No_Event, 10, 52, 160, 15, configurer.get('ServerPort'), 0, 65535, "Port on which NetworkRender servers will be binded"))
	configurer.setDrawValue('ServerBCast', Draw.String("BCast addr: ", No_Event, 10, 32, 160, 15, configurer.get('ServerBCast'), 32, "IP address for broadcast messages"))
	configurer.setDrawValue('ServerBCastInterval', Draw.Number('BCast int.:', No_Event, 10, 12, 160, 15, configurer.get('ServerBCastInterval'), 0, 65535, "Interval ob broadcast clients notification"))

# Client configuration
	Blender.BGL.glColor3f(0,0,0)
	Blender.BGL.glRasterPos2i(190,72)
	Blender.Draw.Text("Client")
	Blender.BGL.glBegin(Blender.BGL.GL_LINE_STRIP)
	Blender.BGL.glVertex2i(185,74)
	Blender.BGL.glVertex2i(185,25)
	Blender.BGL.glVertex2i(355,25)
	Blender.BGL.glVertex2i(355,74)
	Blender.BGL.glVertex2i(225,74)
	Blender.BGL.glEnd()

	configurer.setDrawValue('ClientPort', Draw.Number('Port:', No_Event, 190, 52, 160, 15, configurer.get('ClientPort'), 0, 65535, "Port on which NetworkRender clients will be binded"))
	configurer.setDrawValue('ClientLocalRendering', Draw.Toggle("Local rendering", No_Event, 190, 32, 160, 15, configurer.get('ClientLocalRendering'), "Serve rendering queue by localhost machine"))

	Draw.PushButton("Save changes", Event_Save, 185, 5, 170, 15, "Save changes on NetworkRender configuration")

Draw.Register(gui, event, bevent)
