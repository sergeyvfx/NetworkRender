#!BPY

__author__ = "Sergey I. Sharybin"
__copyright__='(cc) non commercial use only and attribution by'
__version__ = "0.1"
__email__ = "g.ulairi@gmail.com"

import Blender
from Blender import Draw, Registry

class Configurer():
	__instance = None

	class __impl():
		def __init__(self):
			self.variables = {}
			self.initExtensions()
			self.initVariables()
			self.readRegistry()

		def initExtensions(self):
			self.extensions = {'jpeg': Blender.Scene.Render.JPEG, \
							'png': Blender.Scene.Render.PNG}

		def initVariables(self):
			self.declareVariable('ServerPort', 8080)
			self.declareVariable('ServerBCast', '255.255.255.255')
			self.declareVariable('ServerBCastInterval', 5)

			self.declareVariable('ClientPort', 8082)
			self.declareVariable('ClientLocalRendering', True)

			self.declareVariable('StillParts', 2)
			self.declareVariable('OutputExtension', Blender.Scene.Render.JPEG)

		def declareVariable(self, name, value):
			self.setDrawValue(name, Draw.Create(value))

		def setDrawValue(self, name, value):
			self.variables[name] = value

		def readRegistry(self):
			dict = Registry.GetKey('NetworkRender', False)
			if dict:
				try:
					for name in self.variables:
						self.variables[name].val = dict[name]
				except:
					# Error in stored registry. Rewrite it.
					self.writeRegistry()

		def writeRegistry(self):
			dict = {}
			for name in self.variables:
				dict[name] = self.variables[name].val
			Registry.SetKey('NetworkRender', dict, False)

		def get(self, name):
			return self.variables[name].val

		def set(self, name, value):
			self.variables[name].val = value

		def getExtenssions(self):
			return self.extenstions

		def getFileExtension(self, ext):
			for x in self.extensions:
				if  self.extensions[x] == ext:
					return x

		def getMenuExtensions(self):
			result = ''
			for x in self.extensions:
				if result <> '':
					result += '|'
				result += x + '%x' + str(self.extensions[x])
			return result

	def __init__(self):
		if Configurer.__instance is None:
			Configurer.__instance = Configurer.__impl()

		self.__dict__['_Configurer__instance'] = Configurer.__instance

	def __getattr__(self, attr):
		return getattr(self.__instance, attr)

	def __setattr__(self, attr, value):
		return setattr(self.__instance, attr, value)

	def destroy(self):
		Configurer.__instance = None
		del self.__dict__['_Configurer__instance']
