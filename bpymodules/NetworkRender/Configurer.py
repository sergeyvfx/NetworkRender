#!BPY

__author__ = "Sergey I. Sharybin"
__copyright__='(cc) non commercial use only and attribution by'
__version__ = "0.1"
__email__ = "g.ulairi@gmail.com"

import Blender
from Blender import Draw, Registry

class Configurer():
	"""
	NetworkRendering configurer singleton
	"""

	__instance = None

	class __impl():
		"""
		Instance for configurer singleton
		"""

		def __init__(self):
			self.variables = {}
			self.initExtensions()
			self.initVariables()
			self.readRegistry()

		def initExtensions(self):
			"""
			Initialize list of extensions
			"""
			self.extensions = {'jpeg': Blender.Scene.Render.JPEG, \
							'png': Blender.Scene.Render.PNG}

		def initVariables(self):
			"""
			Initialize variables dictionary with their default values
			"""

			self.declareVariable('ServerPort', 8080)
			self.declareVariable('ServerAddr', '0.0.0.0')
			self.declareVariable('ServerBCast', '255.255.255.255')
			self.declareVariable('ServerBCastInterval', 5)
			self.declareVariable('ServerStaticMap', '')

			self.declareVariable('ClientPort', 8082)
			self.declareVariable('ClientLocalRendering', True)

			self.declareVariable('StillParts', 2)
			self.declareVariable('ImageType', Blender.Scene.Render.JPEG)

		def declareVariable(self, name, value):
			"""
			Declare variable in dictionary
			@param name: name of variable to declare
			@param value: variable's value
			"""
			self.setDrawValue(name, Draw.Create(value))

		def setDrawValue(self, name, value):
			"""
			Set button value to dictionary
			@param name: name of variable
			"""
			self.variables[name] = value

		def readRegistry(self):
			"""
			Read variables' values from registry to dictionary
			"""
			dict = Registry.GetKey('NetworkRender', False)
			if dict:
				try:
					for name in self.variables:
						self.variables[name].val = dict[name]
				except:
					# Error in stored registry. Rewrite it.
					self.writeRegistry()

		def writeRegistry(self):
			"""
			Write dictionary variables' values to registry for future usage
			"""
			dict = {}
			for name in self.variables:
				dict[name] = self.variables[name].val
			Registry.SetKey('NetworkRender', dict, False)

		def get(self, name):
			"""
			Get variable's value
			@param name - name of variable to get
			"""
			return self.variables[name].val

		def set(self, name, value):
			"""
			Set variable's value
			@param name: name of variable to set value of
			@param value: new variable's value
			"""
			self.variables[name].val = value

		def getExtenssions(self):
			"""
			Get dictionary of known extensions
			"""
			return self.extenstions

		def getFileExtension(self, type):
			"""
			Get file extension by imageType constant
			@param type: imageType to get extension for
			"""
			for x in self.extensions:
				if  self.extensions[x] == type:
					return x

		def getMenuExtensions(self):
			"""
			Get string with extensions which could be used for menu title
			"""
			result = ''
			for x in self.extensions:
				if result <> '':
					result += '|'
				result += x + '%x' + str(self.extensions[x])
			return result

	def __init__(self):
		"""
		Initialize configuration singleton
		"""
		if Configurer.__instance is None:
			Configurer.__instance = Configurer.__impl()

		self.__dict__['_Configurer__instance'] = Configurer.__instance

	def __getattr__(self, attr):
		return getattr(self.__instance, attr)

	def __setattr__(self, attr, value):
		return setattr(self.__instance, attr, value)

	def destroy(self):
		"""
		Destroy stored instance of object
		"""
		Configurer.__instance = None
		del self.__dict__['_Configurer__instance']
