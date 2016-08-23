
import TriMeshWriter
reload( TriMeshWriter )
from TriMeshWriter import TriMeshWriter

import GltfWriter
reload( GltfWriter )
from GltfWriter import GltfWriter

import os

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
		materialKey = "material-" + tempMaterial["name"]

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
		self.translate = None 
		self.rotation = None 
		self.scale = None
		pass
	## gltf writer
	def gltf( self, writer ):
		if self.hasMesh:
			meshKeys = []
			for mesh in self.meshes:
				mesh.gltf( writer )
				meshKeys.append( mesh.getKey() )
				pass
			writer.appendMeshNode( self.getKey(), self.getName(), self.getTransform(), meshKeys )
			pass
		elif self.hasCamera:
			self.camera.gltf( writer )
			writer.appendCameraNode( self.getKey(), self.getName(), self.getTransform(), self.camera.getKey() )
			pass
		elif self.hasLight:
			self.light.gltf( writer )
			writer.appendLightNode( self.getKey(), self.getName(), self.getTransform(), self.light.getKey() )
			pass
		elif self.isNull:
			writer.appendNode( self.getKey(), self.getName(), self.getTransform() )

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
	def getTranslate( self ): 
		if self.translate != None: return self.translate
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

## \class BaseExporter
#
#
class BaseExporter( object ):
	## c'tor
	def __init__( self ):
		#print( "BaseExporter c'tor" )
		self.outputPath = None
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
				raise RuntimeError( "Unknown paramemter: %s" % key )
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