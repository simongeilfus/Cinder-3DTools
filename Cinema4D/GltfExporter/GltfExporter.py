
"""
import py_compile
py_compile.compile( "/Users/ryanbartley/Documents/clean_cinder/blocks/Cinder-3DTools/Cinema4D/GltfExporter/GltfExporter.py" )

import sys
sys.path.append( "/Users/ryanbartley/Documents/clean_cinder/blocks/Cinder-3DTools/Cinema4D/GltfExporter" )
import GltfExporter
reload( GltfExporter )
 
GltfExporter.exportSelected( "/Users/ryanbartley/Documents/clean_cinder/blocks/Cinder-3DTools/TriMeshViewer/assets" )"""

"""
import c4d
#Welcome to the world of Python


def main():
    doc = c4d.documents.GetActiveDocument()
    obj = doc.GetActiveObject()
    
    # get object
    #obj = op.GetObject()
    # get number of polygons on object.
    poly_count = obj.GetPolygonCount()
    
    # get selected polys
    sel_polys = obj.GetPolygonS()
    
    # put polys into a list of booles. This
    # will hold a True value if poly is selected
    # otherwise it will hold a False value
    list_polys = sel_polys.GetAll(poly_count)
    
    # loop through polys
    for i in xrange(poly_count):
        
        # if the list holds a True value
        if list_polys[i]:
            
            # print the index of the Poly.
            print "Poly at index %i is selected." % (i)
            
            
main()
"""

import c4d
import array
import math
import os
import re
import struct
import json
import shutil

## TriMesh
#
# This class is generic. Should be usable outside of Maya.
#
class TriMesh( object ):
	# noinspection PyPep8
	POSITION    = 0x00000001
	COLOR       = 0x00000002
	TEX_COORD_0 = 0x00000004
	TEX_COORD_1 = 0x00000008
	TEX_COORD_2 = 0x00000010
	TEX_COORD_3 = 0x00000020
	NORMAL      = 0x00000100
	TANGENT     = 0x00000200
	BITANGENT   = 0x00000400
	BONE_INDEX  = 0x00001000
	BONE_WEIGHT = 0x00002000
	CUSTOM_0    = 0x00010000
	CUSTOM_1    = 0x00020000
	CUSTOM_2    = 0x00040000
	CUSTOM_3    = 0x00080000
	CUSTOM_4    = 0x00100000
	CUSTOM_5    = 0x00200000
	CUSTOM_6    = 0x00400000
	CUSTOM_7    = 0x00800000
	CUSTOM_8    = 0x01000000
	CUSTOM_9    = 0x02000000	

	def __init__( self ):
		self.version    = int(2)
		self.indices    = array.array( 'H' )
		self.positions  = array.array( 'f' )
		self.colors     = array.array( 'f' )
		self.normals    = array.array( 'f' )
		self.texCoords0 = array.array( 'f' )
		self.texCoords1 = array.array( 'f' )
		self.texCoords2 = array.array( 'f' )
		self.texCoords3 = array.array( 'f' )
		self.tangents   = array.array( 'f' )
		self.bitangents = array.array( 'f' )

		self.positionsDims  = 0
		self.colorsDims     = 0
		self.normalsDims    = 0
		self.texCoords0Dims = 0
		self.texCoords1Dims = 0
		self.texCoords2Dims = 0
		self.texCoords3Dims = 0
		self.tangentsDims   = 0
		self.bitangentsDims = 0		
		pass

	def appendPosition( self, x, y, z = None, w = None ):
		self.positions.append( x )
		self.positions.append( y )
		if z is not None:
			self.positions.append( z )
		if w is not None:
			self.positions.append( w )
		if 0 == self.positionsDims:
			if w is not None:
				self.positionsDims = 4
			elif z is not None:
				self.positionsDims = 3
			else:
				self.positionsDims = 2
		pass

	def appendNormal( self, x, y, z ):
		self.normals.append( x )
		self.normals.append( y )
		self.normals.append( z )
		if 0 == self.normalsDims:
			self.normalsDims = 3
		pass

	def appendTangent( self, x, y, z ):
		self.tangents.append( x )
		self.tangents.append( y )
		self.tangents.append( z )
		if 0 == self.tangentsDims:
			self.tangentsDims = 3
		pass

	def appendBitangent( self, x, y, z ):
		self.bitangents.append( x )
		self.bitangents.append( y )
		self.bitangents.append( z )
		if 0 == self.bitangentsDims:
			self.bitangentsDims = 3
		pass

	def appendRgb( self, r, g, b ):
		self.colors.append( r )
		self.colors.append( g )
		self.colors.append( b )
		if 0 == self.colorsDims:
			self.colorsDims = 3
		pass

	def appendRgba( self, r, g, b, a ):
		self.colors.append( r )
		self.colors.append( g )
		self.colors.append( b )
		self.colors.append( a )
		if 0 == self.colorsDims:
			self.colorsDims = 4
		pass

	def appendTexCoord0( self, x, y, z = None, w = None ):
		self.texCoords0.append( x )
		self.texCoords0.append( y )
		if z is not None:
			self.texCoords0.append( z )
		if w is not None:
			self.texCoords0.append( w )
		if 0 == self.texCoords0Dims:
			if w is not None:
				self.texCoords0Dims = 4
			elif z is not None:
				self.texCoords0Dims = 3
			else:
				self.texCoords0Dims = 2			
		pass

	def appendTexCoord1( self, x, y, z = None, w = None ):
		self.texCoords1.append( x )
		self.texCoords1.append( y )
		if z is not None:
			self.texCoords1.append( z )
		if w is not None:
			self.texCoords1.append( w )
		if 0 == self.texCoords1Dims:
			if w is not None:
				self.texCoords1Dims = 4
			elif z is not None:
				self.texCoords1Dims = 3
			else:
				self.texCoords1Dims = 2
		pass

	def appendTexCoord2( self, x, y, z = None, w = None ):
		self.texCoords2.append( x )
		self.texCoords2.append( y )
		if z is not None:
			self.texCoords2.append( z )
		if w is not None:
			self.texCoords2.append( w )
		if 0 == self.texCoords2Dims:
			if w is not None:
				self.texCoords2Dims = 4
			elif z is not None:
				self.texCoords2Dims = 3
			else:
				self.texCoords2Dims = 2			
		pass

	def appendTexCoord3( self, x, y, z = None, w = None ):
		self.texCoords3.append( x )
		self.texCoords3.append( y )
		if z is not None:
			self.texCoords3.append( z )
		if w is not None:
			self.texCoords3.append( w )
		if 0 == self.texCoords3Dims:
			if w is not None:
				self.texCoords3Dims = 4
			elif z is not None:
				self.texCoords3Dims = 3
			else:
				self.texCoords3Dims = 2					
		pass

	def appendIndex( self, v ):
		self.indices.append( v )
		pass		

	def appendTriangle( self, v0, v1, v2 ):
		self.indices.append( v0 )
		self.indices.append( v1 )
		self.indices.append( v2 )
		pass

	def getNumVertices( self ):
		return len( self.indices )
		pass

	def writeAttrib( self, file, attrib, dims, size, data ):
		if 0 == size:
			return
		file.write( struct.pack( "I", attrib ) )
		file.write( struct.pack( "B", dims ) )
		file.write( struct.pack( "I", size ) )
		data.tofile( file )
		pass

	def write( self, path ):
		try:
			file = open( path, "wb" )
		except:
			print( "Failed to open file for write: %s" % path )
			return
		file.write( struct.pack( "B", self.version ) )
		file.write( struct.pack( "I", self.getNumVertices() ) )
		# Write indices
		if self.getNumVertices() > 0:
			self.indices.tofile( file )
		# Write attributes
		self.writeAttrib( file, TriMesh.POSITION, self.positionsDims, len( self.positions ), self.positions )
		self.writeAttrib( file, TriMesh.COLOR, self.colorsDims, len( self.colors ), self.colors )
		self.writeAttrib( file, TriMesh.NORMAL, self.normalsDims, len( self.normals ), self.normals )
		self.writeAttrib( file, TriMesh.TEX_COORD_0, self.texCoords0Dims, len( self.texCoords0 ), self.texCoords0 )
		self.writeAttrib( file, TriMesh.TEX_COORD_1, self.texCoords1Dims, len( self.texCoords1 ), self.texCoords1 )
		self.writeAttrib( file, TriMesh.TEX_COORD_2, self.texCoords2Dims, len( self.texCoords2 ), self.texCoords2 )
		self.writeAttrib( file, TriMesh.TEX_COORD_3, self.texCoords3Dims, len( self.texCoords3 ), self.texCoords3 )
		self.writeAttrib( file, TriMesh.TANGENT, self.tangentsDims, len( self.tangents ), self.tangents )
		self.writeAttrib( file, TriMesh.BITANGENT,  self.bitangentsDims, len( self.bitangents ), self.bitangents )
		file.close()
		pass

	# class TriMesh
	pass

class GltfAsset( object ):
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
		self.accessorNum = 0
		self.bufferViewNum = 0
		self.bufferNum = 0
		self.techniqueNum = 0
		self.textureNum = 0
		self.samplerNum = 0
		self.bufferName = "buffer"
		self.buffer = bytearray()
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
		if dims == 1:
			return self.SCALAR
		elif dims == 2:
			return self.VEC2
		elif dims == 3:
			return self.VEC3
		elif dims == 4:
			return self.VEC4

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

	def appendAttrib( self, attribArray, dims, bufferViewName, attribOffset ):
		# buffer positions
		offset = len(self.buffer)
		self.buffer.extend(struct.pack('%sf' % len(attribArray), *attribArray))
		attribType = self.getAttribType( dims )
		# create accessor
		accessorName = self.appendAccessor( bufferViewName, attribOffset, dims * 4, self.FLOAT, len(attribArray) / dims, attribType, None, None ) 
		length = len(self.buffer) - offset
		return accessorName, length

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
		if len(trimesh.positions) > 0: 
			# append attrib
			accessorName, length = self.appendAttrib( trimesh.positions, trimesh.positionsDims, bufferViewName, attribOffset )
			# push offset
			attribOffset = attribOffset + length
			# store accessorName
			tempAttributes["POSITION"] = accessorName
		if len(trimesh.normals) > 0:
			# append attrib
			accessorName, length = self.appendAttrib( trimesh.normals, trimesh.normalsDims, bufferViewName, attribOffset )
			# push offset
			attribOffset = attribOffset + length
			# store accessorName
			tempAttributes["NORMAL"] = accessorName
		if len(trimesh.texCoords0) > 0:
			# append attrib
			accessorName, length = self.appendAttrib( trimesh.texCoords0, trimesh.texCoords0Dims, bufferViewName, attribOffset )
			# push offset
			attribOffset = attribOffset + length
			# store accessorName
			tempAttributes["TEXCOORD_0"] = accessorName
		if len(trimesh.texCoords1) > 0:
			# append attrib
			accessorName, length = self.appendAttrib( trimesh.texCoords1, trimesh.texCoords1Dims, bufferViewName, attribOffset )
			# push offset
			attribOffset = attribOffset + length
			# store accessorName
			tempAttributes["TEXCOORD_1"] = accessorName
		if len(trimesh.texCoords2) > 0:
			# append attrib
			accessorName, length = self.appendAttrib( trimesh.texCoords2, trimesh.texCoords2Dims, bufferViewName, attribOffset )
			# push offset
			attribOffset = attribOffset + length
			# store accessorName
			tempAttributes["TEXCOORD_2"] = accessorName
		if len(trimesh.texCoords3) > 0:
			# append attrib
			accessorName, length = self.appendAttrib( trimesh.texCoords3, trimesh.texCoords3Dims, bufferViewName, attribOffset )
			# push offset
			attribOffset = attribOffset + length
			# store accessorName
			tempAttributes["TEXCOORD_3"] = accessorName
		if len(trimesh.colors) > 0:
			# append attrib
			accessorName, length = self.appendAttrib( trimesh.colors, trimesh.colorsDims, bufferViewName, attribOffset )
			# push offset
			attribOffset = attribOffset + length
			# store accessorName
			tempAttributes["COLOR"] = accessorName
		if len(trimesh.tangents) > 0:
			# append attrib
			accessorName, length = self.appendAttrib( trimesh.tangents, trimesh.tangentsDims, bufferViewName, attribOffset )
			# push offset
			attribOffset = attribOffset + length
			# store accessorName
			tempAttributes["TANGENT"] = accessorName
		if len(trimesh.bitangents) > 0:
			# append attrib
			accessorName, length = self.appendAttrib( trimesh.bitangents, trimesh.bitangentsDims, bufferViewName, attribOffset )
			# push offset
			attribOffset = attribOffset + length
			# store accessorName
			tempAttributes["BITANGENT"] = accessorName
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


## GltfExporter
#
#
class GltfExporter( object ):
	def __init__( self ):
		self.basePath = None
		self.bakeTranform = False
		self.angleWeightedNormals = False
		self.gltfFilePath = None		
		self.gltfAsset = None
		self.unitScale = 0.01
		self.documentPath = None
		pass

	## createFilePath
	def createFilePath( self, polyObj, path, materialName, ext ):
		# Use object name
		fileName = polyObj.GetName()
		# Remove the first instance of | 
		if fileName.startswith( "|" ):
			fileName = re.sub( "\|", "", fileName, count = 1 )
		# Replace all remaining instances of | with _
		fileName = re.sub( "\|", "_", fileName )
		# Replace all instances of : with _
		fileName = re.sub( ":", "_", fileName )
		# Add material name
		if materialName:
			fileName = "%s_%s" % ( fileName, materialName )	
		# Create full path
		if ext.startswith( "." ):
			fileName = os.path.join( path, fileName ) + ext	
		else: 			
			fileName = os.path.join( path, fileName ) + "." + ext	
		# Replace all \ with /
		fileName = fileName.replace( "\\", "/" )
		print fileName
		# Return it!
		return fileName
		pass

	## createTriMesh
	def createTriMesh( self, polyObj, polyFaces, colorRgb ):
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
				P0 = points[mv0] * self.unitScale 
				P1 = points[mv1] * self.unitScale
				P2 = points[mv2] * self.unitScale
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
				triMesh.appendRgb( colorRgb[0], colorRgb[1], colorRgb[2] )
				triMesh.appendNormal( N0[0], N0[1], N0[2] )
				triMesh.appendTexCoord0( u0, v0 )
				# Vert[0] 1 data
				triMesh.appendPosition( P1[0], P1[1], P1[2] )
				triMesh.appendRgb( colorRgb[0], colorRgb[1], colorRgb[2] )
				triMesh.appendNormal( N1[0], N1[1], N1[2] )
				triMesh.appendTexCoord0( u1, v1 )
				# Vert[0] 2 data
				triMesh.appendPosition( P2[0], P2[1], P2[2] )
				triMesh.appendRgb( colorRgb[0], colorRgb[1], colorRgb[2] )
				triMesh.appendNormal( N2[0], N2[1], N2[2] )
				triMesh.appendTexCoord0( u2, v2 )
				# Increment to next triangle
				fv1 += 1
				fv2 += 1				
				pass
			pass

		# Return
		return triMesh
		pass		

	def getMaterialFaces( self, polyObj ):
		materialFaces = []
		# Get tags
		tags = polyObj.GetTags()
		# Find the necessary tags
		textureTags = []
		selectionTags = {}
		for tag in tags:
			if c4d.Ttexture == tag.GetType():
				textureTags.append( tag ) 
				#print( "Found texture tag: TagName: %s, Tag Material Name: %s, Restriction: %s" % ( tag.GetName(), tag.GetMaterial().GetName(), tag[c4d.TEXTURETAG_RESTRICTION] ) )
			elif c4d.Tpolygonselection == tag.GetType():
				selectionTags[tag.GetName()] = tag
				print( "Found selection tag: %s" % tag.GetName() )
				pass
			pass

		polyCount = polyObj.GetPolygonCount()
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
						#print( "Restricted texture tag: %s %s %s" % ( textureTag.GetName(), textureTag.GetMaterial().GetName(), textureTag[c4d.TEXTURETAG_RESTRICTION] ) )
						pass
					pass
				pass			
		else:
			# If there's only one texture tag, it will apply to all faces.
			if 1 == len( textureTags ):
				material = textureTags[0].GetMaterial()
				faces = [i for i in range( polyCount )]
				materialFaces.append( { "material" : material, "faces" : faces } )
				usedFaces.extend( faces )
				pass

		# Process restrictedTextureTags in reverse
		for textureTag in reversed( restrictedTextureTags ):
			selectionName = textureTag[c4d.TEXTURETAG_RESTRICTION]
			#print( selectionName )
			selectedFaces = selectionTags[selectionName].GetBaseSelect()
			material = textureTag.GetMaterial()
			faces = []
			for faceIdx in range( polyCount ):
				if selectedFaces.IsSelected( faceIdx ) and ( faceIdx not in usedFaces ):
					faces.append( faceIdx )
					usedFaces.append( faceIdx )
					#try:
					#	unusedFaces.remove( faceIdx )
					#except ValueError:
					#	# remove will throw if th evalue isn't found - just ignore it.
					#	pass
					#pass
				pass
			if len( faces ) > 0:
				#print material.GetName(), faces
				materialFaces.append( { "material" : material, "faces" : faces } )	
			pass

		unusedFaces = []
		for faceIdx in range( polyCount ):
			if faceIdx not in usedFaces:
				unusedFaces.append( faceIdx )
				pass
			pass

		if len( unusedFaces ) > 0:
			#print unusedFaces
			materialFaces.append( { "material" : None, "faces" : unusedFaces } )
			pass

		return materialFaces
		pass

	def convertColor( self, colorVec ):
		return [colorVec.x, colorVec.y, colorVec.z, 1.0]

	def populateShaderParams( self, material ):
		values = {}
		colorFile = ""
		colorVec = None
		normalFile = ""
		diffuseVec = None
		diffuseFile = ""
		specularVec = None 
		specularFile = ""

		transparency = material[c4d.MATERIAL_USE_TRANSPARENCY]
		if transparency:
			values["transparent"] = transparency
			values["transparency"] = material[c4d.MATERIAL_TRANSPARENCY_COLOR]
		if material[c4d.MATERIAL_USE_COLOR]==True:
			colorVec=material[c4d.MATERIAL_COLOR_COLOR]          
			if(material[c4d.MATERIAL_COLOR_SHADER]):
				if material[c4d.MATERIAL_COLOR_SHADER].GetType() == c4d.Xbitmap:
					colorFile = str(material[c4d.MATERIAL_COLOR_SHADER][c4d.BITMAPSHADER_FILENAME])
				else:
					print "only supported shaders are bitmapshader!"
			    #exportData.AWDwarningObjects.append("
		if(material[c4d.MATERIAL_USE_NORMAL]):            
			if(material[c4d.MATERIAL_NORMAL_SHADER]):
				if material[c4d.MATERIAL_NORMAL_SHADER].GetType() == c4d.Xbitmap:
					normalFile = str(material[c4d.MATERIAL_NORMAL_SHADER][c4d.BITMAPSHADER_FILENAME])
				else:
					print "only supported shaders are bitmapshader!"   
		if(material[c4d.MATERIAL_USE_DIFFUSION]): # for now  use the diffuse tex as specularMap   
			diffuseVec = material[c4d.MATERIAL_DIFFUSION_COLOR]    
			if(material[c4d.MATERIAL_DIFFUSION_SHADER]):
				if material[c4d.MATERIAL_DIFFUSION_SHADER].GetType() == c4d.Xbitmap:
					diffuseFile = str(material[c4d.MATERIAL_DIFFUSION_SHADER][c4d.BITMAPSHADER_FILENAME])
				else:
					print "only supported shaders are bitmapshader!"
		if(material[c4d.MATERIAL_USE_SPECULARCOLOR]): 
			specularVec = material[c4d.MATERIAL_SPECULAR_COLOR]          
			if(material[c4d.MATERIAL_SPECULAR_SHADER]):
			    if material[c4d.MATERIAL_SPECULAR_SHADER].GetType() == c4d.Xbitmap:
					specularFile = str(material[c4d.MATERIAL_SPECULAR_SHADER][c4d.BITMAPSHADER_FILENAME])
			    else:
					print "only supported shaders are bitmapshader!"
			
			
		if(material[c4d.MATERIAL_USE_FOG]):  
			pass# add fog-method
		if(material[c4d.MATERIAL_USE_SPECULAR]):  
			pass
		if(material[c4d.MATERIAL_USE_GLOW]):
			pass
		#print colorFile + " " + str(colorVec) + " " + normalFile + " " + str(diffuseVec) + " " + diffuseFile + " " + str(specularVec) + " " + specularFile
		# TODO: need to query these values 
		if colorFile != "":
			imageKey = self.gltfAsset.appendImage( colorFile, self.documentPath )
			samplerKey = self.gltfAsset.appendSampler()
			textureKey = self.gltfAsset.appendTexture( imageKey, samplerKey )
			values["diffuse"] = textureKey
		elif colorVec is not None:
			values["diffuse"] = self.convertColor( colorVec )

		if diffuseFile is not "":
			imageKey = self.gltfAsset.appendImage( diffuseFile, self.documentPath )
			samplerKey = self.gltfAsset.appendSampler()
			textureKey = self.gltfAsset.appendTexture( imageKey, samplerKey )
			values["color"] = textureKey
		elif diffuseVec is not None:
			values["color"] = self.convertColor( diffuseVec )

		if specularFile is not "":
			imageKey = self.gltfAsset.appendImage( specularFile, self.documentPath )
			samplerKey = self.gltfAsset.appendSampler()
			textureKey = self.gltfAsset.appendTexture( imageKey, samplerKey )
			values["specular"] = textureKey
		elif specularVec is not None:
			values["specular"] = self.convertColor( specularVec )

		if normalFile is not "":
			imageKey = self.gltfAsset.appendImage( normalFile, self.documentPath )
			samplerKey = self.gltfAsset.appendSampler()
			textureKey = self.gltfAsset.appendTexture( imageKey, samplerKey )
			values["normal"] = textureKey

		values["ambient"] = [0.2, 0.2, 0.2, 1.0]
		values["emission"] = [0, 0, 0, 1.0]
		values["shininess"] = 256.0
		tempMaterial = {}
		tempMaterial["values"] = values
		tempMaterial["name"] = material.GetName().replace( " ", "_" )
		self.gltfAsset.techniqueNum = self.gltfAsset.techniqueNum + 1
		techniqueKey = "technique_" + str(self.gltfAsset.techniqueNum)
		materialKey = "material-" + tempMaterial["name"]

		if colorFile is not "":
			materialKey = materialKey + colorFile
		tempMaterial["technique"] = techniqueKey
		self.gltfAsset.appendMaterial( materialKey, tempMaterial )
		return techniqueKey, materialKey
		pass

	def addMeshNodes( self, parentName, nodeName, matrix, polyObj, materials ):
		# Write initial data to Json
		# Get color
		primitives = []
		for material in materials: 
			colorRgb = [0.8, 0.8, 0.8]
			colorFile = None
			try:
				[colorRgb, colorFile] = self.getColor( material["material"] )
			except:
				pass
			# Shader params
			techniqueKey, materialKey = self.populateShaderParams( material["material"] )

			# Get buffers
			trimesh = self.createTriMesh( polyObj, material["faces"], colorRgb )


			primitives.append( self.gltfAsset.createPrimitive( trimesh, materialKey ) )		
			pass
		meshKey = self.gltfAsset.appendMesh( nodeName + "Shape", primitives )
		return self.gltfAsset.appendMeshNode( parentName, nodeName, matrix, [meshKey] )
		pass

	def addLightNode( self, parentName, nodeName, matrix, node ):
		lightKey = "light_" + nodeName
		#lightKey = self.gltfAsset.appendLight( nodeName, node )
		return self.gltfAsset.appendLightNode( parentName, nodeName, matrix, lightKey )
		pass

	def addCameraNode( self, parentName, nodeName, matrix, node ):
		cameraKey = self.gltfAsset.appendCamera( nodeName, node )
		return self.gltfAsset.appendCameraNode( parentName, nodeName, matrix, cameraKey )
		pass

	def createMatrixArray( self, c4dMatrix ):
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
		elements.append( c4dMatrix.off.x * self.unitScale )
		elements.append( c4dMatrix.off.y * self.unitScale )
		elements.append( c4dMatrix.off.z * self.unitScale )
		elements.append( 1.0 )
		return elements
		pass 

	## exportSelected
	def exportSelected( self, path, bakeTranform, angleWeightedNormals ):
		self.basePath = path
		self.bakeTranform = bakeTranform
		self.angleWeightedNormals = angleWeightedNormals

		doc = c4d.documents.GetActiveDocument()

		validObjectTypes = [
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

		polyObjs = []
		meshNodes = []
		cameraNodes = []
		lightNodes = []

		selected = doc.GetActiveObjects( c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER )
		self.documentPath = doc.GetDocumentPath()
		print self.documentPath
		if 0 == len( selected ):
			print( "Nothing selected" )
			return

		for itObj in selected:
			obj = itObj
			objType = obj.GetType()
			if _c4d.OBJECT_EMPTY_POLYGON == objType:
				polyObjs.append( obj )
			else:
				if objType in validObjectTypes:
					try:
						tmpObj = obj.GetClone()
						tmpList = c4d.utils.SendModelingCommand( command = c4d.MCOMMAND_CURRENTSTATETOOBJECT, list = [tmpObj], mode = c4d.MODELINGCOMMANDMODE_ALL, doc = doc )
						c4d.utils.SendModelingCommand( command = c4d.MCOMMAND_TRIANGULATE, list = tmpList, doc = doc )

						if len( tmpList ) > 0:
							polyObjs.append( tmpList[0] )
							meshNodes.append( { "node" : obj, "meshInfo" : tmpList[0] } )
							pass
					except Exception, e:
						print( "Failed to convert %s (type=%d) to triangles: %s" % ( obj.GetName(), obj.GetType(), e ) )
						obj = None
						pass
				else:
					if objType == _c4d.OBJECT_CAMERA:
						cameraNodes.append({ "node" : obj })
					elif objType == _c4d.OBJECT_LIGHT:
						lightNodes.append({ "node" : obj })
					else:
						print( "Unsupported object %s (type=%d)" % ( obj.GetName(), obj.GetType() ) )
						obj = None
					pass
				pass
			#if obj is not None:
			#	polyObjs.append( obj )
			#	pass
			pass


		# Create a directory using the scene name
		sceneFileName = doc.GetDocumentName()
		if sceneFileName is None:
			sceneFileName = "untitled"
			pass
		sceneFileName = sceneFileName.replace( " ", "_" )
		self.gltfAsset = GltfAsset( sceneFileName )
		[sceneFile, sceneExt] = os.path.splitext( os.path.basename( sceneFileName ) )
		path = os.path.join( path, sceneFile )
		print( "Exporting as Cinder TriMesh data to %s" % path )
		if not os.path.exists( path ):
			os.makedirs( path )
		# Json scene file path
		self.binFilePath = os.path.join( path, self.gltfAsset.bufferName + ".bin" )
		self.binFilePath = self.binFilePath.replace( "\\", "/" )	
		self.gltfFilePath = os.path.join( path, sceneFile + ".gltf" )
		self.gltfFilePath = self.gltfFilePath.replace( "\\", "/" )	
		topNodes = []
		# Create Json doc
		# create mesh nodes
		for meshNode in meshNodes:
			obj = meshNode["node"]
			polyObj = meshNode["meshInfo"]
			matrix = self.createMatrixArray( obj.GetMl() )
			parent = obj.GetUp()
			nodeName = obj.GetName()
			parentName = ""
			if parent != None:
				parentName = obj.GetName()

			materials = self.getMaterialFaces( polyObj )
			nodeKey = self.addMeshNodes( parentName, nodeName, matrix, polyObj, materials )
			if parent == None:
				topNodes.append(nodeKey)
			pass
		
		for lightNode in lightNodes:
			obj = lightNode["node"]
			matrix = self.createMatrixArray( obj.GetMl() )
			parent = obj.GetUp()
			nodeName = obj.GetName()
			parentName = ""
			if parent != None:
				parentName = obj.GetName()
			nodeKey = self.addLightNode( parentName, nodeName, matrix, obj )
			if parent == None:
				topNodes.append(nodeKey)
			pass

		for cameraNode in cameraNodes:
			obj = cameraNode["node"]
			matrix = self.createMatrixArray( obj.GetMl() )
			parent = obj.GetUp()
			nodeName = obj.GetName()
			parentName = ""
			if parent != None:
				parentName = obj.GetName()
			nodeKey = self.addCameraNode( parentName, nodeName, matrix, obj )
			if parent == None:
				topNodes.append(nodeKey)
			pass

		# add the top nodes and create the scene object
		self.gltfAsset.appendScene( sceneFileName, topNodes )
		# finalize the byte buffer
		self.gltfAsset.finalizeBuffer()
		# write it out
		self.gltfAsset.copyImages( path )
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
	validKeys = ["bakeTransform", "angleWeightedNormals"]
	for key in kwargs.keys():
		if key not in validKeys:
			raise RuntimeError( "Unknown paramemter: %s" % key )
	# Grab arguemnts
	bakeTransform = kwargs.get( "bakeTransform", False )
	angleWeightedNormals = kwargs.get( "angleWeightedNormals", False )
	# Run exporter
	# Run exporter
	exporter = GltfExporter()
	exporter.exportSelected( path, bakeTransform, angleWeightedNormals )
	pass