"""
import sys
sys.path.append( "/Users/ryanbartley/Documents/clean_cinder/blocks/Cinder-3DTools/pysrc" )
import C4D
reload( C4D )
 
C4D.exportSelected( "/Users/ryanbartley/Documents/clean_cinder/blocks/Cinder-3DTools/TriMeshViewer/assets" )
"""

import c4d
import array
import math
import os
import re
import struct
import json
import shutil
from TriMesh import TriMesh

class GltfWriter( object ):
	# components
	SCALAR = "SCALAR"
	VEC2 = "VEC2"
	VEC3 = "VEC3"
	VEC4 = "VEC4"
	MAT2 = "MAT2"
	MAT3 = "MAT3"
	MAT4 = "MAT4"
	# data types
	BYTE = 0x1400 #GL_BYTE
	UNSIGNED_BYTE = 0x1401 #GL_UNSIGNED_BYTE
	SHORT = 0x1402 #GL_SHORT,
	UNSIGNED_SHORT = 0x1403 #GL_UNSIGNED_SHORT,
	FLOAT = 0x1406 #GL_FLOAT
	# buffer 
	ARRAY_BUFFER = 34962
	ELEMENT_ARRAY_BUFFER = 34963
	TEXTURE_2D = 3553
	# pixel data types
	UNSIGNED_BYTE = 5121
	UNSIGNED_SHORT_5_6_5 = 33635
	UNSIGNED_SHORT_4_4_4_4 = 32819 
	UNSIGNED_SHORT_5_5_5_1 = 32820
	# Pixel order
	ALPHA = 6406 
	RGB = 6407 
	RGBA = 6408
	LUMINANCE = 6409 
	LUMINANCE_ALPHA = 6410
	# Sampler defines
	NEAREST = 9728 
	LINEAR = 9729
	NEAREST_MIPMAP_NEAREST = 9984
	LINEAR_MIPMAP_NEAREST = 9985 
	NEAREST_MIPMAP_LINEAR = 9986 
	LINEAR_MIPMAP_LINEAR = 9987
	CLAMP_TO_EDGE = 33071
	MIRRORED_REPEAT = 33648
	REPEAT = 10497
	# types
	FLOAT_VEC2 	= 0x8B50
	FLOAT_VEC3  = 0x8B51
	FLOAT_VEC4  = 0x8B52
	INT_VEC2    = 0x8B53
	INT_VEC3    = 0x8B54
	INT_VEC4    = 0x8B55
	BOOL        = 0x8B56
	BOOL_VEC2   = 0x8B57
	BOOL_VEC3   = 0x8B58
	BOOL_VEC4   = 0x8B59
	FLOAT_MAT2  = 0x8B5A
	FLOAT_MAT3  = 0x8B5B
	FLOAT_MAT4  = 0x8B5C
	SAMPLER_1D  = 0x8B5D
	SAMPLER_2D  = 0x8B5E
	SAMPLER_3D  = 0x8B5F
	SAMPLER_CUBE= 0x8B60

	def __init__( self, sceneName, outputPath, srcPath ):
		# gltf objects
		self.nodes = {}
		self.accessors = {}
		self.animations = {}
		self.bufferViews = {}
		self.buffers = {}
		self.cameras = {}
		self.images = {}
		self.materials = {}
		self.meshes = {}
		self.nodes = {}
		self.programs = {}
		self.samplers = {}
		self.scene = sceneName
		self.scenes = {}
		self.shaders = {}
		self.skins = {}
		self.techniques = {}
		self.textures = {}

		# UID numbers for specific objects
		self.accessorNum = 0
		self.bufferViewNum = 0
		self.bufferNum = 0
		self.techniqueNum = 0
		self.textureNum = 0
		self.samplerNum = 0

		# buffer work
		self.bufferName = "buffer"
		self.buffer = bytearray()

		# collection of Image Paths for copying
		self.imagePathsToMove = []

		# create asset
		self.asset = {}
		self.asset["generator"] = "Cinder-3DTools"
		self.asset["premultipliedAlpha"] = False 
		tempProfile = {}
		tempProfile["api"] = "WebGL"
		tempProfile["version"] = "1.0.2"
		self.asset["profile"] = tempProfile
		self.asset["version"] = "1.0"

		# Json scene file path
		self.outputPath = outputPath
		self.srcPath = srcPath
		self.binFilePath = os.path.join( self.outputPath, self.bufferName + ".bin" )
		self.binFilePath = self.binFilePath.replace( "\\", "/" )	
		self.gltfFilePath = os.path.join( self.outputPath, self.scene + ".gltf" )
		self.gltfFilePath = self.gltfFilePath.replace( "\\", "/" )
		pass

	def finalize( self ):
		# finalize the byte buffer
		self.finalizeBuffer()
		# copy the assets
		self.copyImages()
		# write the binfile
		binFile = open( self.binFilePath, "w" )
		binFile.write( self.buffer )
		print( "Wrote %s" % self.binFilePath )
		# finalize the asset
		prettyJson = self.finalizeAsset()
		# write it out
		gltfFile = open( self.gltfFilePath, "w" )
		gltfFile.write( prettyJson )	
		print( "Wrote %s" % self.gltfFilePath )

		pass

	def finalizeAsset( self ):
		gltfAsset = {}
		gltfAsset["accessors"] = self.accessors
		gltfAsset["animations"] = self.animations
		gltfAsset["asset"] = self.asset 
		gltfAsset["bufferViews"] = self.bufferViews
		gltfAsset["buffers"] = self.buffers
		gltfAsset["cameras"] = self.cameras
		gltfAsset["images"] = self.images
		gltfAsset["materials"] = self.materials 
		gltfAsset["meshes"] = self.meshes
		gltfAsset["nodes"] = self.nodes
		gltfAsset["programs"] = self.programs
		gltfAsset["samplers"] = self.samplers
		gltfAsset["scene"] = self.scene
		gltfAsset["scenes"] = self.scenes
		gltfAsset["shaders"] = self.shaders
		gltfAsset["skins"] = self.skins
		gltfAsset["techniques"] = self.techniques
		gltfAsset["textures"] = self.textures
		gltfJson = json.dumps( gltfAsset, sort_keys=True, indent=4, separators=(',', ': ') )
		return gltfJson

	def getAttribType( self, dims ):
		if dims == 1: return self.SCALAR
		elif dims == 2: return self.VEC2
		elif dims == 3: return self.VEC3
		elif dims == 4: return self.VEC4

	def appendCamera( self, cameraName, cameraInfo ):
		tempCameraObject = {}
		projectionType = cameraInfo[c4d.CAMERA_PROJECTION]
		
		if projectionType == c4d.Pperspective:
			tempPerspective = {}
			tempPerspective["aspectRatio"] = 1.5
			tempPerspective["yfov"] = cameraInfo[c4d.CAMERAOBJECT_FOV_VERTICAL]
			tempPerspective["zfar"] = cameraInfo[c4d.CAMERAOBJECT_FAR_CLIPPING]
			tempPerspective["znear"] = cameraInfo[c4d.CAMERAOBJECT_NEAR_CLIPPING]
			tempCameraObject["perspective"] = tempPerspective
			tempCameraObject["type"] = "perspective"
		else:
			tempOrtho = {}
			tempOrtho["xmag"] = 1.5
			tempOrtho["ymag"] = cameraInfo[c4d.CAMERAOBJECT_FOV_VERTICAL]
			tempOrtho["zfar"] = cameraInfo[c4d.CAMERAOBJECT_FAR_CLIPPING]
			tempOrtho["zNear"] = cameraInfo[c4d.CAMERAOBJECT_NEAR_CLIPPING]
			tempCameraObject["orthographic"] = tempOrtho
			tempCameraObject["type"] = "orthographic"

		cameraKey = "camera_" + cameraName
		self.cameras[cameraKey] = tempCameraObject
		return cameraKey
		pass

	def appendLight( self, lightName, lightInfo ):
		# todo: this
		pass

	def getCurrentBufferOffset( self ):
		return len(self.buffer)
		pass

	def appendScene( self, sceneName, topNodes ):
		tempScene = {}
		tempScene["nodes"] = topNodes
		self.scenes[sceneName] = tempScene
		pass

	def finalizeBuffer( self ):
		tempBuffer = {}
		tempBuffer["byteLength"] = len(self.buffer)
		tempBuffer["type"] = "arraybuffer"
		tempBuffer["uri"] = self.bufferName + ".bin"
		self.buffers[self.bufferName] = tempBuffer
		pass

	def copyImages( self ):
		for imageInfo in self.imagePathsToMove:
			fileName = imageInfo
			src = os.path.join( self.srcPath, fileName )
			dst = os.path.join( self.outputPath, fileName )
			print src
			print dst
			shutil.copyfile( src, dst )

	def appendBufferView( self, bufferName, byteOffset, byteLength, target ):
		tempBufferView = {}
		tempBufferView["buffer"] = bufferName
		tempBufferView["byteOffset"] = byteOffset
		tempBufferView["byteLength"] = byteLength
		tempBufferView["target"] = target
		self.bufferViewNum += 1
		name = "bufferview_" + str(self.bufferViewNum)
		self.bufferViews[name] = tempBufferView  
		return name
		pass

	def appendAccessor( self, bufferViewName, byteOffset, byteStride, componentType, count, dataType, minBounding, maxBounding ):
		tempAccessor = {}
		tempAccessor["bufferView"] = bufferViewName
		tempAccessor["byteOffset"] = byteOffset
		tempAccessor["byteStride"] = byteStride
		tempAccessor["componentType"] = componentType
		tempAccessor["count"] = count
		tempAccessor["type"] = dataType
		# if (minBounding is not None && len(minBounding) > 0):
		# 	tempAccessor["min"] = minBounding
		# if (maxBounding is not None && len(maxBounding) > 0):
		# 	tempAccessor["max"] = maxBounding
		self.accessorNum += 1
		name = "accessor_" + str(self.accessorNum)
		self.accessors[name] = tempAccessor
		return name
		pass

	def appendImage( self, fileName ):
		tempImage = {}
		tempImage["uri"] = fileName
		tempImage["name"] = fileName[0:fileName.index(".")]
		imageKey = "image-" + tempImage["name"]
		self.images[imageKey] = tempImage
		self.imagePathsToMove.append( fileName )
		return imageKey
		pass

	def appendSampler( self, wrapS, wrapT ):
		tempSampler = {}
		# TODO: How do we figure this out
		tempSampler["magFilter"] = self.LINEAR
		tempSampler["minFilter"] = self.NEAREST_MIPMAP_LINEAR
		tempSampler["wrapS"] = wrapS
		tempSampler["wrapT"] = wrapT
		self.samplerNum = self.samplerNum + 1
		samplerKey = "sampler_" + str(self.samplerNum)
		tempSampler["name"] = samplerKey
		self.samplers[samplerKey] = tempSampler
		return samplerKey
		pass

	def appendTexture( self, imageKey, samplerKey ):
		tempTexture = {}
		# TODO: How do we figure this out
		tempTexture["format"] = self.RGB
		tempTexture["internalFormat"] = self.RGB
		tempTexture["sampler"] = samplerKey
		tempTexture["source"] = imageKey
		tempTexture["target"] = self.TEXTURE_2D
		self.textureNum = self.textureNum + 1
		textureKey = "texture-" + str(self.textureNum)
		tempTexture["name"] = textureKey
		tempTexture["type"] = self.UNSIGNED_BYTE
		self.textures[textureKey] = tempTexture
		return textureKey
		pass

	def appendAttrib( self, attribArray, dims, bufferViewName, attribOffset, attribMap, attribKey ):
		if len(attribArray) == 0:
			return 0
		# buffer positions
		offset = len(self.buffer)
		self.buffer.extend(struct.pack('%sf' % len(attribArray), *attribArray))
		attribType = self.getAttribType( dims )
		# create accessor
		accessorName = self.appendAccessor( bufferViewName, attribOffset, dims * 4, self.FLOAT, len(attribArray) / dims, attribType, None, None ) 
		length = len(self.buffer) - offset
		# store accessorName
		attribMap[attribKey] = accessorName
		return length

	def createPrimitive( self, trimesh, materialKey ):
		# make temp primitive
		tempPrimitive = {}
		tempPrimitive["mode"] = 4 #GL_TRIANGLES
		# TODO: This isn't a good way to be guaranteeing uniqueness
		tempPrimitive["material"] = materialKey
		indicesCount = len(trimesh.indices)
		if indicesCount > 0:
			# buffer indices
			indexOffset = len(self.buffer)
			self.buffer.extend(struct.pack('%sH' % len(trimesh.indices), *trimesh.indices))
			indexLength = len(self.buffer) - indexOffset
			# create bufferView for indices
			bufferViewName = self.appendBufferView( self.bufferName, indexOffset, indexLength, self.ELEMENT_ARRAY_BUFFER )
			# indices has their own bufferView so the offset is 0 and length is the same
			# create accessor
			accessorName = self.appendAccessor( bufferViewName, 0, 0, self.UNSIGNED_SHORT, indicesCount, self.SCALAR, None, None )
			tempPrimitive["indices"] = accessorName
			pass
		# create bufferView 
		offset = len(self.buffer)
		bufferViewName = self.appendBufferView( self.bufferName, offset, 0, self.ARRAY_BUFFER )
		# rolling attrib offset into the buffer
		attribOffset = 0
		# create attrib object
		tempAttributes = {} 
		# append POSITIONS and push offset
		attribOffset += self.appendAttrib( trimesh.positions, trimesh.positionsDims, bufferViewName, attribOffset, tempAttributes, "POSITION" ) 
		# append NORMALS attrib
		attribOffset += self.appendAttrib( trimesh.normals, trimesh.normalsDims, bufferViewName, attribOffset, tempAttributes, "NORMAL" )
		# append texcoords
		attribOffset += self.appendAttrib( trimesh.texCoords0, trimesh.texCoords0Dims, bufferViewName, attribOffset, tempAttributes, "TEXCOORD_0" )
		# append texcoords
		attribOffset += self.appendAttrib( trimesh.texCoords1, trimesh.texCoords1Dims, bufferViewName, attribOffset, tempAttributes, "TEXCOORD_1" )
		# append texcoords
		attribOffset += self.appendAttrib( trimesh.texCoords2, trimesh.texCoords2Dims, bufferViewName, attribOffset, tempAttributes, "TEXCOORD_2" )
		# append texcoords
		attribOffset += self.appendAttrib( trimesh.texCoords3, trimesh.texCoords3Dims, bufferViewName, attribOffset, tempAttributes, "TEXCOORD_3" )
		# append colors
		attribOffset += self.appendAttrib( trimesh.colors, trimesh.colorsDims, bufferViewName, attribOffset, tempAttributes, "COLOR" )
		# append tangents
		attribOffset += self.appendAttrib( trimesh.tangents, trimesh.tangentsDims, bufferViewName, attribOffset, tempAttributes, "TANGENT" )
		# append attrib
		attribOffset += self.appendAttrib( trimesh.bitangents, trimesh.bitangentsDims, bufferViewName, attribOffset, tempAttributes, "BITANGENT" )
		# resolve BufferView Length
		self.bufferViews[bufferViewName]["byteLength"] = attribOffset
		tempPrimitive["attributes"] = tempAttributes
		return tempPrimitive

	def appendMesh( self, meshKey, meshName, primitives ):
		# make temp mesh object
		tempMesh = {}
		tempMesh["name"] = meshName
		tempMesh["primitives"] = primitives
		self.meshes[meshKey] = tempMesh
		return meshKey
		pass

	def appendMeshNode( self, nodeKey, nodeName, matrix, meshKeys ):
		tempNode = {}
		tempNode["name"] = nodeName
		tempNode["matrix"] = matrix
		tempNode["meshes"] = meshKeys
		self.nodes[nodeKey] = tempNode
		pass

	def appendCameraNode( self, nodeKey, nodeName, matrix, cameraKey ):
		tempNode = {}
		tempNode["name"] = nodeName
		tempNode["matrix"] = matrix
		tempNode["camera"] = cameraKey
		self.nodes[nodeKey] = tempNode
		pass

	def appendLightNode( self, nodeKey, nodeName, matrix, lightKey ):
		tempNode = {}
		tempNode["name"] = nodeName
		tempNode["matrix"] = matrix
		tempNode["light"] = lightKey
		self.nodes[nodeKey] = tempNode
		pass

	def appendNode( self, nodeKey, nodeName, matrix ):
		tempNode = {}
		tempNode["name"] = nodeName
		tempNode["matrix"] = matrix
		self.nodes[nodeKey] = tempNode
		pass

	def appendChild( self, parentKey, childKey ):
		if "children" in self.nodes[parentKey]:
			self.nodes[parentKey]["children"].append(childKey)
		else:
			self.nodes[parentKey]["children"] = [childKey]
		pass

	def appendMaterial( self, materialKey, materialInfo ):
		self.materials[materialKey] = materialInfo
		pass

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
	def getKey( self ): return "material-" + self.getName() 
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
	def getKey( self ): return self.getName().replace( " ", "_" ) + "-lib"
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
	def getKey( self ): return "light_" + self.getName()
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
	def getKey( self ): return self.getName().replace( " ", "_" )
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

		self.cacheNodes()

		if self.sceneFileName is None:
			print "No scene file name. Using untitled."
			self.sceneFileName = "untitled"
			pass
		# build the scene name
		self.sceneFileName = self.sceneFileName.replace( " ", "_" )
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


class _c4d( object ):
	OBJECT_BASE_MESH	= 5100
	OBJECT_CONE     	= 5162
	OBJECT_CUBE     	= 5159
	OBJECT_CYLINDER 	= 5170
	OBJECT_DISC     	= 5164
	OBJECT_PLANE    	= 5168
	OBJECT_POLYGON  	= 5174
	OBJECT_SPHERE   	= 5160
	OBJECT_TORUS    	= 5163
	OBJECT_CAPSULE  	= 5171
	OBJECT_OIL_TANK 	= 5172
	OBJECT_TUBE     	= 5165
	OBJECT_PYRAMID  	= 5167
	OBJECT_PLATONIC 	= 5161
	OBJECT_CAMERA 		= 5103
	OBJECT_LIGHT		= 5102
	OBJECT_NULL			= 5140

	UNIT_SCALE 			= 0.01
	pass

meshObjects = [
			_c4d.OBJECT_CONE,
			_c4d.OBJECT_CUBE,
			_c4d.OBJECT_CYLINDER,
			_c4d.OBJECT_DISC,
			_c4d.OBJECT_PLANE,
			_c4d.OBJECT_POLYGON,
			_c4d.OBJECT_SPHERE,
			_c4d.OBJECT_TORUS,
			_c4d.OBJECT_CAPSULE,
			_c4d.OBJECT_OIL_TANK,
			_c4d.OBJECT_TUBE,
			_c4d.OBJECT_PYRAMID,
			_c4d.OBJECT_PLATONIC
		]

def convertC4DMatrix( c4dMatrix ):
	elements = []
	elements.append( c4dMatrix.v1.x )
	elements.append( c4dMatrix.v1.y )
	elements.append( c4dMatrix.v1.z )
	elements.append( 0.0 )
	elements.append( c4dMatrix.v2.x )
	elements.append( c4dMatrix.v2.y )
	elements.append( c4dMatrix.v2.z )
	elements.append( 0.0 )
	elements.append( c4dMatrix.v3.x )
	elements.append( c4dMatrix.v3.y )
	elements.append( c4dMatrix.v3.z )
	elements.append( 0.0 )
	elements.append( c4dMatrix.off.x * _c4d.UNIT_SCALE )
	elements.append( c4dMatrix.off.y * _c4d.UNIT_SCALE )
	elements.append( c4dMatrix.off.z * _c4d.UNIT_SCALE )
	elements.append( 1.0 )
	return elements
	pass

def convertColor( colorVec ):
	return [colorVec.x, colorVec.y, colorVec.z, 1.0]

## \class C4DMaterial
#
#
class C4DMaterial( BaseMaterial ):
	## c'tor
	MATERIAL_VALS = [
		(c4d.MATERIAL_USE_TRANSPARENCY, None, 							c4d.MATERIAL_TRANSPARENCY_COLOR, "transparency"),
		(c4d.MATERIAL_USE_COLOR, 		c4d.MATERIAL_COLOR_SHADER, 		c4d.MATERIAL_COLOR_COLOR, "color"),
		(c4d.MATERIAL_USE_NORMAL, 		c4d.MATERIAL_NORMAL_SHADER, 	None, "normal" ),
		(c4d.MATERIAL_USE_DIFFUSION, 	c4d.MATERIAL_DIFFUSION_SHADER, 	None, "diffuse"),
		(c4d.MATERIAL_USE_SPECULARCOLOR,c4d.MATERIAL_SPECULAR_SHADER, 	c4d.MATERIAL_SPECULAR_COLOR, "specular")
	]

	def __init__( self, materialSet ):
		#print( "C4DMaterial c'tor" )
		BaseMaterial.__init__(self)
		#print "should've called base con"
		self.material = materialSet["material"]
		self.name = self.material.GetName()
		#GL_REPEAT: The integer part of the coordinate will be ignored and a repeating pattern is formed.
		#GL_MIRRORED_REPEAT: The texture will also be repeated, but it will be mirrored when the integer part of the coordinate is odd.
		#GL_CLAMP_TO_EDGE: The coordinate will simply be clamped between 0 and 1.
		#GL_CLAMP_TO_BORDER: The coordinates that fall outside the range will be given a specified border color.
		# TODO: decide what the different values determine
		if materialSet["repeat_u"] == 1.0:
			self.wraps.append( GltfWriter.CLAMP_TO_EDGE )
		else:
			self.wraps.append( GltfWriter.REPEAT )
		if materialSet["repeat_v"] == 1.0:
			self.wraps.append( GltfWriter.CLAMP_TO_EDGE )
		else:
			self.wraps.append( GltfWriter.REPEAT )
		
		# TODO: decide what to do with these.	
		# c4d.MATERIAL_USE_FOG c4d.MATERIAL_USE_SPECULAR c4d.MATERIAL_USE_GLOW
		
		for use, texture, color, key in C4DMaterial.MATERIAL_VALS:
			self.cacheMaterialValues( use, texture, color, key )

		# TODO: How do we find these values
		self.colors["ambient"] = [0.2, 0.2, 0.2, 1.0]
		self.colors["emission"] = [0, 0, 0, 1.0]
		self.colors["shininess"] = 256.0
		pass

	def cacheMaterialValues( self, use, texture, color, key ):
		if self.material[use]==True:         
			if self.material[texture]:
				if self.material[texture].GetType() == c4d.Xbitmap:
					self.files[key] = str(self.material[texture][c4d.BITMAPSHADER_FILENAME])
				else:
					print "only supported shaders are bitmapshader!"
			elif self.material[color]:
				self.colors[key] = convertColor(self.material[color]) 
		pass

## \class BaseMesh
#
#
class C4DMesh( BaseMesh ):
	## c'tor
	def __init__( self, meshObj ):
		#print( "BaseMesh c'tor" )
		BaseMesh.__init__( self )
		# name is whatever
		self.meshObj = meshObj
		self.name = meshObj.GetName()
		# key has to be unique, which this probably won't
		# first we get the division of faces
		materialSets = self.getMaterialSets()
		for materialSet in materialSets: 
			# Cache the material first
			mat = C4DMaterial( materialSet )
			# Cache the buffers
			trimesh = self.createTriMesh( self.meshObj, materialSet["faces"] )
			# push it on to the primitives
			self.primitives.append( { "trimesh" : trimesh, "material" : mat } )		
			pass
		pass

	def getMaterialSets( self ):
		materialSets = []
		# Get tags
		tags = self.meshObj.GetTags()
		# Find the necessary tags
		textureTags = []
		selectionTags = {}
		for tag in tags:
			if c4d.Ttexture == tag.GetType():
				textureTags.append( tag ) 
			elif c4d.Tpolygonselection == tag.GetType():
				selectionTags[tag.GetName()] = tag
				print( "Found selection tag: %s" % tag.GetName() )
				pass
			pass

		polyCount = self.meshObj.GetPolygonCount()
		usedFaces = []

		# Ordering matters for restrictedTextureTags
		restrictedTextureTags = []
		if len( selectionTags ) > 0:
			uniqueSelections = []
			for textureTag in textureTags:
				if textureTag[c4d.TEXTURETAG_RESTRICTION] is not None:
					selectionName = textureTag[c4d.TEXTURETAG_RESTRICTION]
					if ( selectionName in selectionTags.keys() ) and ( selectionName not in uniqueSelections ):
						uniqueSelections.append( selectionName )
						restrictedTextureTags.append( textureTag )
						pass
					pass
				pass			
		else:
			# If there's only one texture tag, it will apply to all faces.
			if 1 == len( textureTags ):
				material = textureTags[0].GetMaterial()
				faces = [i for i in range( polyCount )]
				# decide if we should do U and V
				# print "tex tile x", textureTags[0][c4d.TEXTURETAG_TILESX], "tex tile y", textureTags[0][c4d.TEXTURETAG_TILESY]
				materialSets.append( { "material" : material, "faces" : faces, 
									   "repeat_u" : textureTags[0][c4d.TEXTURETAG_TILESX],
									   "repeat_v" : textureTags[0][c4d.TEXTURETAG_TILESY] } )

				usedFaces.extend( faces )
				pass

		# Process restrictedTextureTags in reverse
		for textureTag in reversed( restrictedTextureTags ):
			selectionName = textureTag[c4d.TEXTURETAG_RESTRICTION]
			selectedFaces = selectionTags[selectionName].GetBaseSelect()
			material = textureTag.GetMaterial()
			faces = []
			for faceIdx in range( polyCount ):
				if selectedFaces.IsSelected( faceIdx ) and ( faceIdx not in usedFaces ):
					faces.append( faceIdx )
					usedFaces.append( faceIdx )
				pass
			if len( faces ) > 0:

				print "tex tile x", textureTag[c4d.TEXTURETAG_TILESX], "tex tile y", textureTag[c4d.TEXTURETAG_TILESY]
				materialSets.append( { "material" : material, "faces" : faces,
									   "repeat_u" : textureTag[c4d.TEXTURETAG_TILESX],
									   "repeat_v" : textureTag[c4d.TEXTURETAG_TILESY] } )	
			pass

		unusedFaces = []
		for faceIdx in range( polyCount ):
			if faceIdx not in usedFaces:
				unusedFaces.append( faceIdx )
				pass
			pass

		if len( unusedFaces ) > 0:
			materialSets.append( { "material" : None, "faces" : unusedFaces,
								   "repeat_u" : None, "repeat_v" : None } )
			pass

		return materialSets
		pass

	def createTriMesh( self, polyObj, polyFaces ):
		# All polygons
		polys = polyObj.GetAllPolygons()		
		# Mesh points
		points = polyObj.GetAllPoints()		
		# Mesh normals
		normals = polyObj.CreatePhongNormals()
		# Mesh UVs
		uvwTag = polyObj.GetTag( c4d.Tuvw )
		# TriMesh
		triMesh = TriMesh()
		#colorRgb = [0.5, 0.5, 0.5]
		# Polygon faces attached to current material
		#polyFaces = materialFaces["faces"]
		for polyId in polyFaces:
			# Polygon
			poly = polys[polyId]
			# Polygon vertex indices, normals, and UVs for triangulation
			polyVerts = [poly.a, poly.b, poly.c]
			normalIdx = 4 * polyId
			polyNormals = [normals[normalIdx + 0], normals[normalIdx + 1], normals[normalIdx + 2] ]
			polyUvs = ["a", "b", "c"]
			if not poly.IsTriangle():
				polyVerts.append( poly.d )
				polyNormals.append( normals[normalIdx + 3] )
				polyUvs.append( "d" )
			# Number of triangles and poly relative indices
			numTris = len( polyVerts ) - 2
			fv0 = 0
			fv1 = 1
			fv2 = 2
			for i in range( numTris ):
				# Vertex indices
				mv0 = polyVerts[fv0]
				mv1 = polyVerts[fv1]
				mv2 = polyVerts[fv2]
				# Positions
				P0 = points[mv0] * _c4d.UNIT_SCALE 
				P1 = points[mv1] * _c4d.UNIT_SCALE 
				P2 = points[mv2] * _c4d.UNIT_SCALE 
				#print( "P0", P0 )
				#print( "P1", P1 )
				#print( "P2", P2 )
				# Normals
				N0 = polyNormals[fv0]
				N1 = polyNormals[fv1]
				N2 = polyNormals[fv2]
				#print( "N0", N0 )
				#print( "N1", N1 )
				#print( "N2", N2 )			
				# UV
				[u0,v0] = [0,0]
				[u1,v1] = [0,0]
				[u2,v2] = [0,0]
				if uvwTag is not None:
					uvwDict = uvwTag.GetSlow( polyId )
					if uvwDict is not None:
						uv0 = uvwDict[polyUvs[fv0]]
						uv1 = uvwDict[polyUvs[fv1]]
						uv2 = uvwDict[polyUvs[fv2]]
						#[u0,v0] = [1.0 -uv0.x, -uv0.y]
						#[u1,v1] = [1.0 -uv1.x, -uv1.y]
						#[u2,v2] = [1.0 -uv2.x, -uv2.y]
						[u0,v0] = [uv0.x, 1.0 - uv0.y]
						[u1,v1] = [uv1.x, 1.0 - uv1.y]
						[u2,v2] = [uv2.x, 1.0 - uv2.y]						
						pass
					pass
				#print( "%f, %f" % ( u0, v0 ) );
				# Vertex 0 data
				triMesh.appendPosition( P0[0], P0[1], P0[2] )
				triMesh.appendNormal( N0[0], N0[1], N0[2] )
				triMesh.appendTexCoord0( u0, v0 )
				# Vert[0] 1 data
				triMesh.appendPosition( P1[0], P1[1], P1[2] )
				triMesh.appendNormal( N1[0], N1[1], N1[2] )
				triMesh.appendTexCoord0( u1, v1 )
				# Vert[0] 2 data
				triMesh.appendPosition( P2[0], P2[1], P2[2] )
				triMesh.appendNormal( N2[0], N2[1], N2[2] )
				triMesh.appendTexCoord0( u2, v2 )
				colorRgb = [ 0.8, 0.8, 0.8 ]
				# TODO: how can we get vertex color info from the verts
				if colorRgb:
					triMesh.appendRgb( colorRgb[0], colorRgb[1], colorRgb[2] )
					triMesh.appendRgb( colorRgb[0], colorRgb[1], colorRgb[2] )				
					triMesh.appendRgb( colorRgb[0], colorRgb[1], colorRgb[2] )
				# Increment to next triangle
				fv1 += 1
				fv2 += 1				
				pass
			pass

		# Return
		return triMesh
		pass	
	## class BaseMesh
	pass

## \class BaseCamera
#
#
class C4DCamera( BaseCamera ):
	## c'tor
	def __init__( self, cameraInfo ):
		#print( "BaseCamera c'tor" )	
		BaseCamera.__init__(self)
		self.name = cameraInfo.GetName()
		self.projectionType = cameraInfo[c4d.CAMERA_PROJECTION]
		# ugly but that's c4d
		doc = c4d.documents.GetActiveDocument()
		renderData = doc.GetActiveRenderData()
		aspectRatio = renderData[c4d.RDATA_FILMASPECT]

		if self.projectionType == c4d.Pperspective:
			# TODO: How do we get aspect ratio
			self.projectionType = BaseCamera.PROJECTION
			self.aspectRatio = aspectRatio
			self.yfov = cameraInfo[c4d.CAMERAOBJECT_FOV_VERTICAL]
			self.cameraType = BaseCamera.PROJECTION
		# TODO: how do we figure out if this is an orthographic
		else:
			# TODO: How do we get xmag, ymag
			self.projectionType = BaseCamera.ORTHOGRAPHIC
			self.xmag = 1
			self.ymag = 1
			self.cameraType = BaseCamera.ORTHOGRAPHIC

		self.zfar = cameraInfo[c4d.CAMERAOBJECT_FAR_CLIPPING]
		self.znear = cameraInfo[c4d.CAMERAOBJECT_NEAR_CLIPPING]	
		pass
	## class BaseCamera
	pass

## \class BaseLight
#
#
class C4DLight( BaseLight ):
	## c'tor
	def __init__( self, obj ):
		#print( "BaseLight c'tor" )
		BaseLight.__init__(self)	
		self.name = obj.GetName()	
		pass
	## class BaseLight
	pass	

class C4DNode( BaseNode ):
	## c'tor
	def __init__( self, obj ):
		#print( "C4DNode c'tor" )
		BaseNode.__init__( self )	
		self.obj = obj
		self.name = self.obj.GetName()
		# extract transformation
		self.extractTranform()
		# cache attributes
		self.determineCacheAttributes()
		# cache attributes
		self.determineAnimation()
		# append children
		childBegIt = self.obj.GetDown()
		while childBegIt:
			self.childNodes.append( C4DNode( childBegIt ) )
			childBegIt = childBegIt.GetNext()
			pass
		pass

	def extractTranform( self ):
		# cache the relative matrix
		self.matrix = convertC4DMatrix( self.obj.GetMl() )
		trans = self.obj.GetRelPos()
		self.translation = [ trans.x, trans.y, trans.z ]
		scale = self.obj.GetRelScale()
		self.scale = [ scale.x, scale.y, scale.z ]
		# NOTE: HPB rotation euler need to convert
		rot = self.obj.GetRelRot()
		self.rotation = [ rot.x, rot.y, rot.z ]
		pass

	def determineAnimation( self ):
		track = self.obj.GetFirstCTrack() #Get it's first animation track 
		if not track: 
			return # if it doesn't have any tracks. End the script
		curve = track.GetCurve() #Get the curve for the track found
		count = curve.GetKeyCount() #Count how many keys are on it
		print count, str(curve)
		pass

	def determineCacheAttributes( self ):
		objType = self.obj.GetType()
		doc = c4d.documents.GetActiveDocument()
		if _c4d.OBJECT_BASE_MESH == objType:
			self.cacheAsMeshNode( self.obj )
		else:
			if objType in meshObjects:
				tmpObj = self.obj.GetClone()
				tmpList = c4d.utils.SendModelingCommand( command = c4d.MCOMMAND_CURRENTSTATETOOBJECT, list = [tmpObj], 
														 mode = c4d.MODELINGCOMMANDMODE_ALL, doc = doc )
				c4d.utils.SendModelingCommand( command = c4d.MCOMMAND_TRIANGULATE, list = tmpList, doc = doc )

				if len( tmpList ) > 0:
					self.cacheAsMeshNode( tmpList[0] )
				else:
					print("problem converting mesh node: " + getName())
					pass
			else:
				if objType == _c4d.OBJECT_CAMERA:
					self.cacheAsCameraNode()
				elif objType == _c4d.OBJECT_LIGHT:
					self.cacheAsLightNode()
				elif objType == _c4d.OBJECT_NULL:
					self.cacheAsNullNode()
				else:
					print( "Unsupported object %s (type=%d)" % ( obj.GetName(), obj.GetType() ) )
					obj = None
				pass
			pass
		if not self.cached:
			print( "Unsupported object %s (type=%d)" % ( obj.GetName(), obj.GetType() ) )
			pass
		pass

	# we take an object here because we may have cloned and modeled the obj
	def cacheAsMeshNode( self, obj ):
		# this would be where we'd determine how many meshes we'd want
		self.hasMesh = True	
		self.cached = True 
		self.meshes.append( C4DMesh( obj ) )
		pass

	def cacheAsCameraNode( self ):
		self.hasCamera = True
		self.cached = True
		self.camera = C4DCamera( self.obj )
		pass

	def cacheAsLightNode( self ):
		self.hasLight = True
		self.cached = True
		self.light = C4DLight( self.obj )
		pass

	def cacheAsNullNode( self ):
		self.isNull = True
		self.cached = True
		# cache the few attributes, possibly this isn't needed
		pass

	## class BaseLight
	pass	

class C4DExporter( BaseExporter ):

	def __init__( self ):
		BaseExporter.__init__( self )
		#print( "C4DExporter c'tor" )
		pass
	# class BaseExporter
	pass

	def cacheNodes( self ):
		doc = c4d.documents.GetActiveDocument()

		selected = doc.GetActiveObjects( c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER )
		self.documentPath = doc.GetDocumentPath()
		print self.documentPath
		if 0 == len( selected ):
			print( "Nothing selected" )
			return

		self.nodes = []
		for itObj in selected:
			self.nodes.append( C4DNode( itObj ) )
			pass

		# Create a directory using the scene name
		self.sceneFileName = doc.GetDocumentName()
		pass