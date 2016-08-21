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

	def __init__( self, sceneName ):
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

	def copyImages( self, srcPath, dstPath ):
		for imageInfo in self.imagePathsToMove:
			fileName = imageInfo
			src = os.path.join( srcPath, fileName )
			dst = os.path.join( dstPath, fileName )
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

	def appendMesh( self, meshName, primitives ):
		# make temp mesh object
		tempMesh = {}
		tempMesh["name"] = meshName
		tempMesh["primitives"] = primitives
		meshKey = meshName.replace( " ", "_" ) + "-lib"
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
		self.textures = {}
		self.colors = {}	
		pass

	## getName
	def getName( self ):
		raise NotImplementedError()
		pass	

	def gltf( writer ):
		raise NotImplementedError()
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
		self.trimeshes = []
		self.materials = []		
		pass

	## getName
	def getName( self ):
		raise NotImplementedError()
		pass

	## getTriMeshes
	def getTriMeshes( self ):
		raise NotImplementedError()
		pass	

	def gltf( writer ):
		raise NotImplementedError()
		pass

	## class BaseMesh
	pass

## \class BaseCamera
#
#
class BaseCamera( object ):
	## c'tor
	def __init__( self ):
		#print( "BaseCamera c'tor" )		
		pass

	## getName
	def getName( self ):
		raise NotImplementedError()
		pass

	def gltf( writer ):
		raise NotImplementedError()
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
		raise NotImplementedError()
		pass

	def gltf( writer ):
		raise NotImplementedError()
		pass

	## class BaseLight
	pass	

class BaseNode( object ):
	## c'tor
	def __init__( self ):
		#print( "BaseNode c'tor" )		
		pass

	def gltf( writer ):
		raise NotImplementedError()
		pass

	## getName
	def getName( self ):
		raise NotImplementedError()
		pass

	def getParentKey( self ):
		raise NotImplementedError()
		pass

	def getTransform( self ):
		raise NotImplementedError()
		pass

	def getTranslate( self ):
		raise NotImplementedError()
		pass

	def getRotation( self ):
		raise NotImplementedError()
		pass

	def getScale( self ):
		raise NotImplementedError()
		pass

	## class BaseLight
	pass	

## \class BaseExporter
#
#
class BaseExporter( object ):
	## c'tor
	def __init__( self, options, path ):
		#print( "BaseExporter c'tor" )
		self.outputPath = path
		self.bakeColor = options["bakeColor"]
		self.bakeTransform = options["bakeTransform"]
		self.selected = options["selected"]
		self.angleWeightedNormals = options["angleWeightedNormals"]
		pass

	## getMeshes
	def getMeshes( self ):
		raise NotImplementedError()
		pass

	## getMeshesSelected
	def getMeshesSelected( self ):
		raise NotImplementedError()
		pass

	## exportMeshes
	def exportMeshes( self ):
		# Bail if there's nothing to export
		if 0 == len( self.meshes ):
			print( "Nothing to export" )
			return
			pass
		# Export to requested file type
		tw = TriMeshWriter( self.path, self.meshes )
		tw.write()
		pass

	## export
	def export( self, path, *args, **kwargs ):
		self.path = path
		# Parse arguments
		selected = kwargs.get( "selected", False )
		# Get meshes
		if selected:
			self.meshes = self.getMeshesSelected()
		else:
			self.meshes = self.getMeshes()
			pass
		# Do export
		self.exportMeshes()
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
	materialVals = [
		(c4d.MATERIAL_USE_TRANSPARENCY, None, 							c4d.MATERIAL_TRANSPARENCY_COLOR, "transparency"),
		(c4d.MATERIAL_USE_COLOR, 		c4d.MATERIAL_COLOR_SHADER, 		c4d.MATERIAL_COLOR_COLOR, "color"),
		(c4d.MATERIAL_USE_NORMAL, 		c4d.MATERIAL_NORMAL_SHADER, 	None, "normal" ),
		(c4d.MATERIAL_USE_DIFFUSION, 	c4d.MATERIAL_DIFFUSION_SHADER, 	None, "diffuse"),
		(c4d.MATERIAL_USE_SPECULARCOLOR,c4d.MATERIAL_SPECULAR_SHADER, 	c4d.MATERIAL_SPECULAR_COLOR, "specular")
	]

	def __init__( self, materialSet ):
		#print( "C4DMaterial c'tor" )
		super( BaseMaterial, self ).__init__()
		colorRgb = [0.8, 0.8, 0.8]
		self.files = {}
		self.colors = {}
		self.material = materialSet["material"]
		self.wraps = []
		self.wraps.append( materialSet["repeat_u"] )
		self.wraps.append( materialSet["repeat_v"] )
		self.name = self.material.GetName()
		
		# TODO: decide what to do with these.	
		# c4d.MATERIAL_USE_FOG c4d.MATERIAL_USE_SPECULAR c4d.MATERIAL_USE_GLOW
		
		for use, texture, color, key in C4DMaterial.materialVals:
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
					self.files["color"] = str(self.material[texture][c4d.BITMAPSHADER_FILENAME])
				else:
					print "only supported shaders are bitmapshader!"
			elif self.material[color]:
				self.colors["color"] = convertColor(self.material[color]) 
		pass

	## getName
	def getName( self ): return self.name.replace( " ", "_" )
	def getKey( self ): return "material-" + self.name 

	def gltf( self, writer ):
		values = {}
		colorFile = ""

		# TODO: pull out transparency, transparent, ambient, emission, 
		# shininess, and grab repeats for samplers

		#GL_REPEAT: The integer part of the coordinate will be ignored and a repeating pattern is formed.
		#GL_MIRRORED_REPEAT: The texture will also be repeated, but it will be mirrored when the integer part of the coordinate is odd.
		#GL_CLAMP_TO_EDGE: The coordinate will simply be clamped between 0 and 1.
		#GL_CLAMP_TO_BORDER: The coordinates that fall outside the range will be given a specified border color.
		fileKeys = self.files.keys()
		if len( fileKeys ) > 0:
			wraps = []
			for wrap in self.wraps:
				if wrap == 1.0:
					wraps.append( GltfWriter.CLAMP_TO_EDGE )
				else:
					wraps.append( GltfWriter.REPEAT )

			samplerKey = writer.appendSampler( wraps[0], wraps[1] )

			for key in fileKeys:
				filename = self.files[key]
				if key == "color":
					colorFile = filename
				imageKey = writer.appendImage( filename ) 
				textureKey = writer.appendTexture( imageKey, samplerKey )
				values[key] = textureKey
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
	## class C4DMaterial
	pass

## \class BaseMesh
#
#
class C4DMesh( BaseMesh ):
	## c'tor
	def __init__( self, meshObj ):
		#print( "BaseMesh c'tor" )
		super( BaseMesh, self ).__init__()
		# name is whatever
		self.meshObj = meshObj
		self.name = meshObj.GetName() + " Shape"
		# key has to be unique, which this probably won't
		self.primitives = []
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

	## getName
	def getName( self ): return self.name 
	def getKey( self ): return self.name.replace( " ", "_" ) + "-lib"
	## getTriMeshes
	def getTriMeshes( self ): return this.meshes	

	def gltf( self, writer ):
		primitives = []
		for prim in self.primitives:
			prim["material"].gltf( writer )			
			primitives.append( writer.createPrimitive( prim["trimesh"], prim["material"].getKey() ) )
			pass
		writer.appendMesh( self.getName(), primitives )
		pass

	## class BaseMesh
	pass

## \class BaseCamera
#
#
class C4DCamera( BaseCamera ):
	PROJECTION = 0
	ORTHOGRAPHIC = 1
	## c'tor
	def __init__( self, cameraInfo ):
		#print( "BaseCamera c'tor" )	
		self.name = cameraInfo.GetName()
		self.projectionType = cameraInfo[c4d.CAMERA_PROJECTION]
		# ugly but that's c4d
		doc = c4d.documents.GetActiveDocument()
		renderData = doc.GetActiveRenderData()
		aspectRatio = renderData[c4d.RDATA_FILMASPECT]

		if self.projectionType == c4d.Pperspective:
			# TODO: How do we get aspect ratio
			self.projectionType = C4DCamera.PROJECTION
			self.aspectRatio = aspectRatio
			self.yfov = cameraInfo[c4d.CAMERAOBJECT_FOV_VERTICAL]
			self.type = "perspective"
		# TODO: how do we figure out if this is an orthographic
		else:
			# TODO: How do we get xmag, ymag
			self.projectionType = C4DCamera.ORTHOGRAPHIC
			self.xmag = 1
			self.ymag = 1
			self.type = "orthographic"

		self.zfar = cameraInfo[c4d.CAMERAOBJECT_FAR_CLIPPING]
		self.znear = cameraInfo[c4d.CAMERAOBJECT_NEAR_CLIPPING]	
		pass
	## getName
	def getName( self ): return self.name
	## getKey
	def getKey( self ): return "camera_" + self.name
	## gltf
	def gltf( self, writer ):
		tempCameraObject = {}
		tempTypeObj = {}
		if self.projectionType == C4DCamera.PROJECTION:
			tempTypeObj["aspectRatio"] = self.aspectRatio
			tempTypeObj["yfov"] = self.yfov
			tempCameraObject["type"] = "perspective"
		else:
			tempTypeObj["xmag"] = self.xmag
			tempTypeObj["ymag"] = self.ymag
			tempCameraObject["type"] = "orthographic"

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
class C4DLight( BaseLight ):
	## c'tor
	def __init__( self, obj ):
		#print( "BaseLight c'tor" )	
		self.name = obj.GetName()	
		pass

	## getName
	def getName( self ): self.name
	def getKey( self ): return "light_" + self.name

	def gltf( self, writer ):
		
		pass

	## class BaseLight
	pass	

class C4DNode( BaseNode ):
	## c'tor
	def __init__( self, obj ):
		#print( "C4DNode c'tor" )
		super( C4DNode, self ).__init__()	
		self.obj = obj
		self.name = self.obj.GetName()
		# types
		self.cached = False
		self.hasMesh = False 
		self.hasCamera = False 
		self.hasLight = False
		self.isNull = False 
		self.meshes = []
		self.childNodes = []
		# cache the relative matrix
		self.matrix = convertC4DMatrix( self.obj.GetMl() )
		trans = self.obj.GetRelPos()
		self.translation = [ trans.x, trans.y, trans.z ]
		scale = self.obj.GetRelScale()
		self.scale = [ scale.x, scale.y, scale.z ]
		# NOTE: HPB rotation euler need to convert
		rot = self.obj.GetRelRot()
		self.rotation = [ rot.x, rot.y, rot.z ]
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

	## getName
	def getName( self ): return self.name
	## TODO: this isn't safe for uniqueness
	def getKey( self ): return self.name.replace( " ", "_" )

	def getParentKey( self ):
		parent = self.obj.GetUp()
		if parent != None:
			return parent.GetName().replace( " ", "_" )
		return ""
		pass

	def getTransform( self ): return self.matrix
	def getTranslate( self ): return self.translation
	def getRotation( self ): return self.rotation
	def getScale( self ): return self.scale

	## class BaseLight
	pass	

class C4DExporter( BaseExporter ):

	def __init__( self, options, path ):
		super( C4DExporter, self ).__init__( options, path )
		#print( "C4DExporter c'tor" )
		self.gltfFilePath = None		
		self.gltfAsset = None
		self.documentPath = None
		self.path = None
		pass
	# class BaseExporter
	pass

	## exportSelected
	def exportSelected( self ):
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
		sceneFileName = doc.GetDocumentName()
		if sceneFileName is None:
			sceneFileName = "untitled"
			pass
		sceneFileName = sceneFileName.replace( " ", "_" )
		self.gltfAsset = GltfWriter( sceneFileName )
		[sceneFile, sceneExt] = os.path.splitext( os.path.basename( sceneFileName ) )
		path = os.path.join( self.outputPath, sceneFile )
		print( "Exporting as Cinder TriMesh data to %s" % path )
		if not os.path.exists( path ):
			os.makedirs( path )
		# Json scene file path
		self.binFilePath = os.path.join( path, self.gltfAsset.bufferName + ".bin" )
		self.binFilePath = self.binFilePath.replace( "\\", "/" )	
		self.gltfFilePath = os.path.join( path, sceneFile + ".gltf" )
		self.gltfFilePath = self.gltfFilePath.replace( "\\", "/" )	
		topNodes = []

		for node in self.nodes:
			topNodes.append( node.getKey() )
			node.gltf( self.gltfAsset )
			pass

		# add the top nodes and create the scene object
		self.gltfAsset.appendScene( sceneFileName, topNodes )

		# finalize the byte buffer
		self.gltfAsset.finalizeBuffer()
		# write it out
		self.gltfAsset.copyImages( self.documentPath, path )
		binFile = open( self.binFilePath, "w" )
		binFile.write( self.gltfAsset.buffer )
		print( "Wrote %s" % self.binFilePath )
		# finalize the asset
		prettyJson = self.gltfAsset.finalizeAsset()
		# write it out
		gltfFile = open( self.gltfFilePath, "w" )
		gltfFile.write( prettyJson )	
		print( "Wrote %s" % self.gltfFilePath )
		pass		
	# class GltfExporter 
	pass

def exportSelected( path, *args, **kwargs ):
	# Error check arguments
	validKeys = ["bakeTransform", "angleWeightedNormals", "bakeColor", "selected"]
	for key in kwargs.keys():
		if key not in validKeys:
			raise RuntimeError( "Unknown paramemter: %s" % key )
	# Grab arguemnts
	options = {}
	options["bakeTransform"] = kwargs.get( "bakeTransform", False )
	options["angleWeightedNormals"] = kwargs.get( "angleWeightedNormals", False )
	options["bakeColor"] = kwargs.get( "bakeColor", True )
	options["selected"] = kwargs.get( "selected", True )
	# Run exporter
	# Run exporter
	exporter = C4DExporter( options, path )
	exporter.exportSelected()
	pass