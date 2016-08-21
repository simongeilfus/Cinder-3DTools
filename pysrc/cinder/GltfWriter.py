import c4d
import array
import math
import os
import re
import struct
import json
import shutil

class GltfWriter( object ):
	SCALAR = "SCALAR"
	VEC2 = "VEC2"
	VEC3 = "VEC3"
	VEC4 = "VEC4"
	MAT2 = "MAT2"
	MAT3 = "MAT3"
	MAT4 = "MAT4"
	BYTE = 0x1400 #GL_BYTE
	UNSIGNED_BYTE = 0x1401 #GL_UNSIGNED_BYTE
	SHORT = 0x1402 #GL_SHORT,
	UNSIGNED_SHORT = 0x1403 #GL_UNSIGNED_SHORT,
	FLOAT = 0x1406 #GL_FLOAT
	ARRAY_BUFFER = 34962
	ELEMENT_ARRAY_BUFFER = 34963
	TEXTURE_2D = 3553
	UNSIGNED_BYTE = 5121
	UNSIGNED_SHORT_5_6_5 = 33635
	UNSIGNED_SHORT_4_4_4_4 = 32819 
	UNSIGNED_SHORT_5_5_5_1 = 32820
	ALPHA = 6406 
	RGB = 6407 
	RGBA = 6408
	LUMINANCE = 6409 
	LUMINANCE_ALPHA = 6410
	NEAREST = 9728 
	LINEAR = 9729
	NEAREST_MIPMAP_NEAREST = 9984
	LINEAR_MIPMAP_NEAREST = 9985 
	NEAREST_MIPMAP_LINEAR = 9986 
	LINEAR_MIPMAP_LINEAR = 9987
	CLAMP_TO_EDGE = 33071
	MIRRORED_REPEAT = 33648
	REPEAT = 10497

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

	def copyImages( self, dstPath ):
		for imageInfo in self.imagePathsToMove:
			fileName = imageInfo["fileName"]
			srcPath = imageInfo["path"]
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

	def appendImage( self, fileName, pathToFile ):
		tempImage = {}
		tempImage["uri"] = fileName
		tempImage["name"] = fileName[0:fileName.index(".")]
		imageKey = "image-" + tempImage["name"]
		self.images[imageKey] = tempImage
		self.imagePathsToMove.append( { "fileName": fileName, "path": pathToFile } )
		return imageKey
		pass

	def appendSampler( self ):
		tempSampler = {}
		# TODO: How do we figure this out
		tempSampler["magFilter"] = self.LINEAR
		tempSampler["minFilter"] = self.NEAREST_MIPMAP_LINEAR
		tempSampler["wrapT"] = self.REPEAT
		tempSampler["wrapS"] = self.REPEAT
		self.samplerNum = self.samplerNum + 1
		samplerKey = "sampler-" + str(self.samplerNum)
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

	def appendMeshNode( self, parentName, nodeName, matrix, meshKeys ):
		if parentName != "":
			for node in self.nodes:
				if node["name"] == parentName:
					node["children"].append(nodeName)
					break
		tempNode = {}
		tempNode["name"] = nodeName
		tempNode["matrix"] = matrix
		tempNode["meshes"] = meshKeys
		nodeKey = nodeName.replace( " ", "_" )
		self.nodes[nodeKey] = tempNode
		return nodeKey

	def appendCameraNode( self, parentName, nodeName, matrix, cameraKey ):
		if parentName != "":
			for node in self.nodes:
				if node["name"] == parentName:
					node["children"].append(nodeName)
					break
		tempNode = {}
		tempNode["name"] = nodeName
		tempNode["matrix"] = matrix
		tempNode["camera"] = cameraKey
		nodeKey = nodeName.replace(" ", "_")
		self.nodes[nodeKey] = tempNode
		return nodeKey
		pass

	def appendLightNode( self, parentName, nodeName, matrix, lightKey ):
		if parentName != "":
			for node in self.nodes:
				if node["name"] == parentName:
					node["children"].append(nodeName)
					break
		tempNode = {}
		tempNode["name"] = nodeName
		tempNode["matrix"] = matrix
		tempNode["light"] = lightKey
		nodeKey = nodeName.replace(" ", "_")
		self.nodes[nodeKey] = tempNode
		return nodeKey
		pass

	def appendMaterial( self, materialKey, materialInfo ):
		self.materials[materialKey] = materialInfo
		pass