
from Base import BaseExporter
from Base import BaseMaterial
from Base import BaseMesh
from Base import BaseLight
from Base import BaseCamera

import c4d
import array
import math
import os
import re
import struct
import json
import shutil

class _c4d( object ):
	OBJECT_EMPTY_POLYGON  = 5100
	OBJECT_CONE           = 5162
	OBJECT_CUBE           = 5159
	OBJECT_CYLINDER       = 5170
	OBJECT_DISC           = 5164
	OBJECT_PLANE          = 5168
	OBJECT_POLYGON        = 5174
	OBJECT_SPHERE         = 5160
	OBJECT_TORUS          = 5163
	OBJECT_CAPSULE        = 5171
	OBJECT_OIL_TANK       = 5172
	OBJECT_TUBE           = 5165
	OBJECT_PYRAMID        = 5167
	OBJECT_PLATONIC       = 5161
	OBJECT_CAMERA 		  = 5103
	OBJECT_LIGHT		  = 5102
	OBJECT_NULL			  = 5140
	pass

## \class C4DMaterial
#
#
class C4DMaterial( BaseMaterial ):
	## c'tor
	def __init__( self ):
		print( "C4DMaterial c'tor" )
		super( BaseMaterial, self ).__init__()
		pass

	## getName
	def getName( self ):
		raise NotImplementedError()
		pass	

	def gltf( writer ):
		raise NotImplementedError()
		pass	

	## class C4DMaterial
	pass

## \class BaseMesh
#
#
class C4DMesh( BaseMesh ):
	## c'tor
	def __init__( self, polyObj, materials ):
		print( "BaseMesh c'tor" )
		super( BaseMesh, self ).__init__()
		self.materials = materials
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
class C4DCamera( BaseCamera ):
	## c'tor
	def __init__( self ):
		print( "BaseCamera c'tor" )		
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
class C4DLight( BaseLight ):
	## c'tor
	def __init__( self ):
		print( "BaseLight c'tor" )		
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

class C4DNode( BaseNode ):
	## c'tor
	def __init__( self ):
		print( "BaseNode c'tor" )		
		pass

	def gltf( writer ):
		raise NotImplementedError()
		pass

	## getName
	def getName( self ):
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

class C4DExporter( BaseExporter ):
	def __init__( self ):
		super( C4DExporter, self ).__init__()
		print( "C4DExporter c'tor" )
		self.basePath = None
		self.bakeTranform = False
		self.angleWeightedNormals = False
		self.gltfFilePath = None		
		self.gltfAsset = None
		self.unitScale = 0.01
		self.documentPath = None
		pass
	# class BaseExporter
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

		polyObjs = []
		meshNodes = []
		cameraNodes = []
		lightNodes = []
		nullNodes = []

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
				if objType in meshObjects:
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
					elif objType == _c4d.OBJECT_NULL:
						nullNodes.append({ "node" : obj })
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