
import TriMeshWriter
reload( TriMeshWriter )
from TriMeshWriter import TriMeshWriter

import GltfWriter
reload( GltfWriter )
from GltfWriter import GltfWriter

import os
import array

## \class BaseMaterial
#
#
class BaseMaterial( object ):
	## c'tor
	def __init__( self ):
		#print( "BaseMaterial c'tor" )	
		self.name = ""
		colorRgb = [0.8, 0.8, 0.8]
		self.wraps = []
		self.files = {}
		self.colors = {}	
		pass
	## getName - returns the name of the Material
	def getName( self ):
		if self.name != "": return self.name 
		else: raise NotImplementedError()
		pass
	## getKey - returns what should be a unique name for this material
	def getKey( self ): return "material-" + self.getName().replace(':', '_').replace('.', '_').replace(' ', '_')
	## gltf writer function
	def gltf( self, writer ):
		values = {}
		colorFile = ""

		fileKeys = self.files.keys()
		if len( fileKeys ) > 0:
			samplerKey = writer.appendSampler( self.wraps[0], self.wraps[1] )
			for key in fileKeys:
				filename = self.files[key]
				if key == "color":
					colorFile = filename
				imageKey = writer.appendImage( filename ) 
				textureKey = writer.appendTexture( imageKey, samplerKey )
				values[key] = textureKey
				pass
			pass

		colorKeys = self.colors.keys()
		for color in colorKeys:
			values[color] = self.colors[color]
			pass

		tempMaterial = {}
		tempMaterial["values"] = values
		tempMaterial["name"] = self.getName()

		writer.techniqueNum = writer.techniqueNum + 1
		techniqueKey = "technique_" + str(writer.techniqueNum)
		materialKey = self.getKey() # "material-" + tempMaterial["name"]

		if colorFile is not "":
			materialKey = materialKey + colorFile
		tempMaterial["technique"] = techniqueKey
		writer.appendMaterial( materialKey, tempMaterial )
		return techniqueKey, materialKey
		pass

	## class BaseMaterial
	pass

## \class BaseMesh
#
#
class BaseMesh( object ):
	## c'tor
	def __init__( self ):
		#print( "BaseMesh c'tor" )
		self.name = ""	
		# this holds multiple dict objects, each has a 
		# "trimesh" (a TriMesh) value and "material" (a BaseMaterial) value
		self.primitives = []
		pass

	## getName
	def getName( self ): 
		if self.name != "": return self.name + " Shape"
		else: raise NotImplementedError() 
	## getKey
	def getKey( self ): return self.getName().replace(':', '_').replace('.', '_').replace(' ', '_') + "-lib"
	## getTriMeshes
	def getTriMeshes( self ):
		raise NotImplementedError()
		pass	
	def gltf( self, writer ):
		primitives = []
		for prim in self.primitives:
			prim["material"].gltf( writer )			
			primitives.append( writer.createPrimitive( prim["trimesh"], prim["material"].getKey() ) )
			pass
		writer.appendMesh( self.getKey(), self.getName(), primitives )
		pass

	## class BaseMesh
	pass

## \class BaseCamera
#
#
class BaseCamera( object ):
	PROJECTION = 0
	ORTHOGRAPHIC = 1
	## c'tor
	def __init__( self ):
		#print( "BaseCamera c'tor" )
		# needed variables	
		self.name = ""
		self.aspectRatio = None
		self.yfov = None
		self.xmag = None 
		self.ymag = None 
		self.zfar = None 
		self.znear = None
		# should be either Projection or Orthographic above
		self.cameraType = None 
		pass
	## getName
	def getName( self ): 
		if self.name != "": return self.name
		else: raise NotImplementedError()
	## getKey
	def getKey( self ): return "camera_" + self.name
	## gltf writer
	def gltf( self, writer ):
		tempCameraObject = {}
		tempTypeObj = {}
		if self.cameraType == BaseCamera.PROJECTION:
			tempTypeObj["aspectRatio"] = self.aspectRatio
			tempTypeObj["yfov"] = self.yfov
			tempCameraObject["type"] = "perspective"
		elif self.cameraType == BaseCamera.ORTHOGRAPHIC:
			tempTypeObj["xmag"] = self.xmag
			tempTypeObj["ymag"] = self.ymag
			tempCameraObject["type"] = "orthographic"
		else:
			print "unknown camera type"

		tempTypeObj["zfar"] = self.zfar
		tempTypeObj["znear"] = self.znear
		tempCameraObject[tempCameraObject["type"]] = tempTypeObj
		writer.cameras[self.getKey()] = tempCameraObject
		pass
	## class BaseCamera
	pass

## \class BaseLight
#
#
class BaseLight( object ):
	POINT = 0
	SPOT = 1
	DIRECTIONAL = 2
	## c'tor
	def __init__( self ):
		#print( "BaseLight c'tor" )		
		pass

	## getName
	def getName( self ): 
		if self.name != "": return self.name
		else: raise NotImplementedError()
	## getKey
	def getKey( self ): return "light_" + self.getName().replace(':', '_').replace('.', '_').replace(' ', '_')
	## gltf
	def gltf( self, writer ):
		pass
	## class BaseLight
	pass	

class BaseNode( object ):
	## c'tor
	def __init__( self ):
		#print( "BaseNode c'tor" )	
		self.name = ""
		# needed variables for writer
		self.animation = None
		self.cached = False
		self.hasMesh = False 
		self.meshes = []
		self.hasCamera = False 
		self.camera = None
		self.hasLight = False
		self.light = None
		self.isNull = False 
		self.childNodes = []
		# needed transform info
		self.matrix = None 
		self.translation = None 
		self.rotation = None 
		self.scale = None
		pass
	## gltf writer
	def gltf( self, writer ):
		trans = {}

		if self.hasCamera == False:
			# self.animation.gltf( writer )
			trans["translation"] = self.getTranslation()
			trans["rotation"] = self.getRotation()
			trans["scale"] = self.getScale()
		else:
			trans["matrix"] = self.getTransform()
			pass

		if self.hasMesh:
			meshKeys = []
			for mesh in self.meshes:
				mesh.gltf( writer )
				meshKeys.append( mesh.getKey() )
				pass
			writer.appendMeshNode( self.getKey(), self.getName(), trans, meshKeys )
			pass
		elif self.hasCamera:
			self.camera.gltf( writer )
			writer.appendCameraNode( self.getKey(), self.getName(), trans, self.camera.getKey() )
			pass
		elif self.hasLight:
			self.light.gltf( writer )
			writer.appendLightNode( self.getKey(), self.getName(), trans, self.light.getKey() )
			pass
		elif self.isNull:
			writer.appendNode( self.getKey(), self.getName(), trans )

		for child in self.childNodes:
			key = child.getKey()
			child.gltf( writer )
			writer.appendChild( self.getKey(), key )
			pass
		pass
	## getKey - returns unique key for this node
	def getKey( self ): return self.getName().replace(':', '_').replace('.', '_').replace(' ', '_')
	## getName - returns name of node
	def getName( self ): 
		if self.name != "": return self.name
		else: raise NotImplementedError()
	## getTransform - returns parent relative mat4
	def getTransform( self ): 
		if self.matrix != None: return self.matrix
		else: raise NotImplementedError()
	## getTranslate - returns parent relative vec3 translate
	def getTranslation( self ): 
		if self.translation != None: return self.translation
		else: raise NotImplementedError()
	## getRotation - returns parent relative quat rotation
	def getRotation( self ): 
		if self.rotation != None: return self.rotation
		else: raise NotImplementedError()
	## getScale - returns parent relative vec3 scale
	def getScale( self ): 
		if self.scale != None: return self.scale
		else: raise NotImplementedError()
	## class BaseNode
	pass

class BaseVectorAnimation(object):
	"""docstring for C4DTranslation"""
	def __init__(self, vectorType, transform, components):
		self.vectorType = vectorType
		self.transform = []
		self.transform.extend(transform)
		self.components = components
		self.keyframes = []
		self.finalized = False
		pass

	def addKeyFrame(self, component, time, value):
		self.finalized = False
		inserted = False
		indexLess = -1
		for idx, keyframe in enumerate(self.keyframes):
			if time == keyframe[0]:
				index = self.components.index(component)
				keyframe[1][index] = value
				inserted = True
				break
			elif time < keyframe[0]:
				indexLess = idx
				break
			pass
		if not inserted:
			values = [ None, None, None ]
			index = self.components.index(component)
			values[index] = value
			keyframe = [time, values]
			if indexLess > -1:
				self.keyframes.insert(indexLess, keyframe)
			else:
				self.keyframes.append(keyframe)
			pass
		pass

	def getKeyframeComponents( self ):
		if not self.finalized:
			self.finalize()
		if self.vectorType == "rotation":
			return self.makeQuatKeyframes()
		else:
			return [ keyframe[1] for keyframe in self.keyframes ]
		pass

	def makeQuatKeyframes( self ):
		raise NotImplementedError()
		pass

	def getKeyframeTimes( self ):
		if not self.finalized:
			self.finalize()
		return [ keyframe[0] for keyframe in self.keyframes ]
		pass

	def getDims( self ):
		if self.vectorType == "translation" or self.vectorType == "scale":
			return 3
		elif self.vectorType == "rotation":
			return 4
		pass

	def finalize( self ):
		rollingTransform = self.transform
		for keyframe in self.keyframes:
			for x in range(len(self.components)):
				if keyframe[1][x] == None:
					keyframe[1][x] = rollingTransform[x]
				rollingTransform[x] = keyframe[1][x]
				pass
			pass
		self.finalized = True 
		pass

	def isValid( self ): return len(self.keyframes) > 1
	
	def __str__( self ):
		string = self.vectorType + ": " + str(self.transform) + "\n"
		for keyframe in self.keyframes:
			keyString = ""
			for x in range(3):
				keyString += self.components[x] + ": " + str(keyframe[1][x]) + ", "
			string += str(keyframe[0]) + ": " + keyString + "\n\n"
			pass
		return string
		pass

## \class BaseAnimation
#
#
class BaseTransformAnimation(object):
	"""docstring for BaseAnimation"""
	# transComp, rotComp, scaleComp are all the components that the Animation should look for
	def __init__(self, nodeKey):
		self.nodeKey = nodeKey
		self.transform = {}
		pass
	
	def gltf( self, writer ):
		validTransforms = {}
		# copy the keyframes and get the times
		for key in self.transform.keys():
			if self.transform[key].isValid():
				self.transform[key].finalize()
				validTransforms[key] = self.transform[key]
			pass

		timeSharedParameters = []
		transformKeys = validTransforms.keys()
		for outerKey in transformKeys:
			# if this is already contained continue
			contained = False
			for sharedParameters in timeSharedParameters:
				for param in sharedParameters["parameters"]:
					if outerKey == param["parameter"]:
						contained = True
						pass
					pass
			if contained:
				continue
			# create the timeset object
			timeSet = {}
			# grab the times of the keyframes
			outerTimeKeys = validTransforms[outerKey].getKeyframeTimes()
			timeSet["time"] = outerTimeKeys
			timeSet["parameters"] = []
			# append this to the parameters
			timeSet["parameters"].append({ "parameter" : outerKey, 
				 						   "keys" : validTransforms[outerKey].getKeyframeComponents(), 
				 						   "dims" : validTransforms[outerKey].getDims() })
			# go through the rest of the transforms to see if theres matches
			for compKey in transformKeys:
				# if this is not what I'm comparing to
				if outerKey != compKey:
					# grab the times of the compare keyframes
					compTimeKeys = validTransforms[compKey].getKeyframeTimes()
					notContained = True 
					# is this already contained in another parameter
					for sharedParameters in timeSharedParameters:
						for param in sharedParameters["parameters"]:
							if compKey == param["parameter"]:
								notContained = False
								pass
							pass
						pass
					# check if these time keys are equal
					if notContained and set(outerTimeKeys) == set(compTimeKeys):
						# add this to the shared parameters
						timeSet["parameters"].append({ "parameter" : compKey, 
				 						   			   "keys" : validTransforms[compKey].getKeyframeComponents(), 
				 						   			   "dims" : validTransforms[compKey].getDims() })
			timeSharedParameters.append(timeSet)
			pass
		writer.appendAnimation( self.nodeKey, timeSharedParameters )
		pass

## \class BaseExporter
#
#
class BaseExporter( object ):
	## c'tor
	def __init__( self ):
		#print( "BaseExporter c'tor" )
		self.outputPath = None
		self.nodes = []
		pass

	## getMeshes
	def getMeshes( self ):
		raise NotImplementedError()
		pass

	def cacheNodes( self ):
		raise NotImplementedError()
		pass

	## getMeshesSelected
	def getMeshesSelected( self ):
		raise NotImplementedError()
		pass

	def exportTriMesh( self ):
		# Get meshes
		if selected:
			self.meshes = self.getMeshesSelected()
		else:
			self.meshes = self.getMeshes()
			pass
		# Do export
		# Bail if there's nothing to export
		if 0 == len( self.meshes ):
			print( "Nothing to export" )
			return
			pass
		# Export to requested file type
		tw = TriMeshWriter( self.path, self.meshes )
		tw.write()
		pass

	def exportGltf( self ):
		self.gltf = GltfWriter( self.sceneFileName, self.outputPath, self.documentPath )
		# gather the top of the heirarchy nodes
		topNodes = []
		for node in self.nodes:
			topNodes.append( node.getKey() )
			# write to gltf
			node.gltf( self.gltf )
			pass

		# add the top nodes and create the scene object
		self.gltf.appendScene( self.sceneName, topNodes )
		# 
		self.gltf.finalize()
		pass

	## exportSelected
	def export( self, path, *args, **kwargs ):
		# Error check arguments
		validKeys = ["bakeTransform", "angleWeightedNormals", "bakeColor", "selected"]
		for key in kwargs.keys():
			if key not in validKeys:
				raise RuntimeError( "Unknown parameter: %s" % key )
		# Grab arguemnts
		# TODO: Make this a global so we don't have to pass it everywhere
		options = {}
		options["bakeTransform"] = kwargs.get( "bakeTransform", False )
		options["angleWeightedNormals"] = kwargs.get( "angleWeightedNormals", False )
		options["bakeColor"] = kwargs.get( "bakeColor", True )
		options["selected"] = kwargs.get( "selected", True )

		self.outputPath = path

		if not self.cacheNodes():
			return

		if self.sceneFileName is None:
			print "No scene file name. Using untitled."
			self.sceneFileName = "untitled"
			pass
		# build the scene name
		self.sceneFileName = self.sceneFileName.replace(':', '_').replace('.', '_').replace(' ', '_')
		# split it
		[sceneFile, sceneExt] = os.path.splitext( os.path.basename( self.sceneFileName ) )
		self.sceneName = sceneFile
		# get the output path
		self.outputPath = os.path.join( self.outputPath, self.sceneName )
		print( "Exporting as Cinder Gltf data to %s" % self.outputPath )
		# create it if it doesn't exist
		if not os.path.exists( self.outputPath ):
			os.makedirs( self.outputPath )	
		
		self.exportGltf()
		pass		
	# class BaseExporter 
	pass