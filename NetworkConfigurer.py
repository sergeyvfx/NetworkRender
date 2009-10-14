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

import Blender, NetworkRender

from Blender import *
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
	BGL.glRecti(0, 0, 710, 125)
	BGL.glColor3f(0.65, 0.65, 0.65)
	BGL.glRecti(0, 125, 710, 145)
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
	Blender.BGL.glVertex2i(345, 5)
	Blender.BGL.glVertex2i(345, 114)
	Blender.BGL.glVertex2i(50, 114)
	Blender.BGL.glEnd()

	configurer.setDrawValue('ServerAddr', \
						Draw.String("Serv addr: ", No_Event, 10, 92, 160, 15, \
								configurer.get('ServerAddr'), 32, \
								"IP address to send as main server address" +
								" (use 0.0.0.0 for auto-detect)"))

	configurer.setDrawValue('ServerPort', \
						Draw.Number('Port:', No_Event, 180, 92, 160, 15, \
								configurer.get('ServerPort'), 0, 65535, \
								"Port on which NetworkRender servers will be binded"))

	configurer.setDrawValue('ServerBCast', \
						Draw.String("BCast addr: ", No_Event, 10, 72, 160, 15, \
								configurer.get('ServerBCast'), 32, \
								"IP address for broadcast messages" +
								" (leave blank to disable broadcasting)"))

	configurer.setDrawValue('ServerBCastInterval', \
						Draw.Number('BCast int.:', No_Event, 180, 72, 160, 15, \
								configurer.get('ServerBCastInterval'), 0, 65535, \
								"Interval of broadcast clients notification"))

	configurer.setDrawValue('ServerSecureNets', \
						Draw.String("Secure nets: ", No_Event, 10, 52, 330, 15, \
								configurer.get('ServerSecureNets'), 250, \
								"Comma separated list of secure networks" +
								" (in format like 192.168.0.0/16)"))

	configurer.setDrawValue('ServerStaticMap', \
						Draw.String("Static map: ", No_Event, 10, 32, 330, 15, \
								configurer.get('ServerStaticMap'), 350, \
								"Static client-server map" +
								" (<client>[:<server>] pairs, delimited by comma)"))

	configurer.setDrawValue('ServerBufferSize', \
						Draw.Number("Buffer size: ", No_Event, 10, 12, 160, 15, \
								configurer.get('ServerBufferSize'), 1024, 10485760, \
								"Size of buffer to send data between server and client"))

	configurer.setDrawValue('ServerRenderPath', \
						Draw.String("", No_Event, 180, 12, 160, 15, \
								configurer.get('ServerRenderPath'), 250, \
								"Name of directory to save rendered images to"))

# Client configuration
	Blender.BGL.glColor3f(0,0,0)
	Blender.BGL.glRasterPos2i(370, 112)
	Blender.Draw.Text("Client")
	Blender.BGL.glBegin(Blender.BGL.GL_LINE_STRIP)
	Blender.BGL.glVertex2i(365, 114)
	Blender.BGL.glVertex2i(365, 45)
	Blender.BGL.glVertex2i(705, 45)
	Blender.BGL.glVertex2i(705, 114)
	Blender.BGL.glVertex2i(405, 114)
	Blender.BGL.glEnd()

	configurer.setDrawValue('ClientPort', \
						Draw.Number('Port:', No_Event, 370, 92, 160, 15, \
								configurer.get('ClientPort'), 0, 65535, \
								"Port on which NetworkRender clients will be binded"))
	configurer.setDrawValue('ClientLocalRendering', \
						Draw.Toggle("Local rendering", No_Event, 370, 72, 160, 15, \
								configurer.get('ClientLocalRendering'), \
								"Serve rendering queue by localhost machine"))

	configurer.setDrawValue('StillParts', \
						Draw.Number('StillParts:', No_Event, 540, 92, 160, 15, \
								configurer.get('StillParts'), 1, 16, \
								"Number of parts in each direction when still rendering"))

	menuname = 'Output file extension%t|' + configurer.getMenuExtensions()
	configurer.setDrawValue('ImageType', \
						Draw.Menu(menuname, No_Event, 540, 72, 160, 15, \
								configurer.get('ImageType'), \
								"Extension for output files"))

	configurer.setDrawValue('ClientServerList', \
						Draw.String("Servers: ", No_Event, 370, 52, 330, 15, \
								configurer.get('ClientServerList'), 32, \
								"List of servers to use" +
								" (<server>[:<port>] pairs, delimited by comma)"))


	Draw.PushButton("Apply changes", Event_Save, 370, 5, 165, 30, \
				"Apply changes of NetworkRender configuration")

	Draw.PushButton("Quit", Event_Close, 540, 5, 165, 30, \
				"Quit from NetworkRender configuration script")

Draw.Register(gui, event, bevent)
