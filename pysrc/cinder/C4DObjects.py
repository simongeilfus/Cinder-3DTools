
import Base
reload( Base )
from Base import BaseMaterial
from Base import BaseMesh
from Base import BaseLight
from Base import BaseCamera
from Base import BaseNode
from Base import BaseTransformAnimation
from Base import BaseVectorAnimation

import GltfWriter
reload( GltfWriter )
from GltfWriter import GltfWriter

import TriMesh
reload( TriMesh )
from TriMesh import TriMesh

import c4d
import array
import math

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
		if self.material != None:
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
		else:
			self.cacheDefaultMat()
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

	def cacheDefaultMat( self ):
		self.name = "Default_Mat"
		self.wraps.append( GltfWriter.CLAMP_TO_EDGE )
		self.wraps.append( GltfWriter.CLAMP_TO_EDGE )
		self.colors["color"] = [0.8, 0.8, 0.8, 1.0]
		self.colors["ambient"] = [0.2, 0.2, 0.2, 1.0]
		self.colors["emission"] = [0, 0, 0, 1.0]
		self.colors["shininess"] = 256.0
		self.colors["specular"] = [ 0, 0, 0, 1 ]
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
		num = 0
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
				num = num + 1
				# print num
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

		self.zfar = cameraInfo[c4d.CAMERAOBJECT_FAR_CLIPPING] * _c4d.UNIT_SCALE
		self.znear = cameraInfo[c4d.CAMERAOBJECT_NEAR_CLIPPING]	* _c4d.UNIT_SCALE
		pass
	## class BaseCamera
	pass

## \class BaseLight
#
#
class C4DLight( BaseLight ):
	LIGHT_TYPES = [
		{ c4d.LIGHT_TYPE_OMNI, BaseLight.POINT },
		{ c4d.LIGHT_TYPE_SPOT, BaseLight.SPOT }, 
		{ c4d.LIGHT_TYPE_DISTANT, BaseLight.DIRECTIONAL }
	]
	## c'tor
	def __init__( self, obj ):
		#print( "BaseLight c'tor" )
		BaseLight.__init__(self)	
		self.name = obj.GetName()	
		lightType = obj[c4d.LIGHT_TYPE]

		if lightType in C4DLight.LIGHT_TYPES.keys():
			self.lightType = C4DLight.LIGHT_TYPES[lightType]
		else:
			print "Unsupported light type."

		self.color = convertColor(obj[c4d.LIGHT_COLOR])
		self.brightness = obj[c4d.LIGHT_BRIGHTNESS]
		self.falloff = obj[c4d.LIGHT_DETAILS_FALLOFF]
		
		print "Light info: ", self.lightType, self.brightness, self.color, self.falloff

		# channelMatch = {'c4d.ID_BASEOBJECT_REL_POSITION,c4d.VECTOR_X':'transform.tx', 
		#  				'c4d.ID_BASEOBJECT_REL_POSITION,c4d.VECTOR_Y':'transform.ty', 
		#  				'c4d.ID_BASEOBJECT_REL_POSITION,c4d.VECTOR_Z':'transform.tz', 
		#  				'c4d.ID_BASEOBJECT_REL_SCALE,c4d.VECTOR_X':'transform.sx', 
		#  				'c4d.ID_BASEOBJECT_REL_SCALE,c4d.VECTOR_Y':'transform.sy', 
		#  				'c4d.ID_BASEOBJECT_REL_SCALE,c4d.VECTOR_Z':'transform.sz', 
		#  				'c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_X':'transform.rx', 
		#  				'c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_Y':'transform.ry', 
		#  				'c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_Z':'transform.rz', 
		#  				'c4d.ID_BASEOBJECT_ROTATION_ORDER':'transform.rotateOrder', 
		#  				'c4d.LIGHT_BRIGHTNESS':'transform.intensity', 
		#  				'c4d.LIGHT_COLOR,c4d.VECTOR_X':'transform.cr', 
		#  				'c4d.LIGHT_COLOR,c4d.VECTOR_Y':'transform.cg', 
		#  				'c4d.LIGHT_COLOR,c4d.VECTOR_Z':'transform.cb', 
		#  				'c4d.LIGHT_DETAILS_OUTERANGLE':'transform.coneAngle', 
		#  				'c4d.LIGHT_DETAILS_INNERANGLE':'transform.penumbraAngle', 
		#  				'c4d.LIGHT_DETAILS_FALLOFF':'transform.dropoff'}
        
  #       for light in self.lights:            
  #           #Export Lights
            
  #           if light[c4d.LIGHT_TYPE] in [0,1,3]:
  #               objectFileName = light.GetName().replace(':', '_').replace('.', '_')
  #               self.exportData(light, channelMatch, self.startFrame, self.endFrame, self.exportPath + objectFileName + '.fm2n')
  #               print "Exported: " + objectFileName
  #           else:
  #               c4d.gui.MessageDialog(light.GetName() + " is not supported in Nuke. You can just use Point-(Omni), Distance-(Infinite) and Spot-Lights!")
    
		pass
	## class BaseLight
	pass	

class C4DNode( BaseNode ):
	## c'tor
	def __init__( self, obj = None ):
		#print( "C4DNode c'tor" )
		BaseNode.__init__( self )	
		if obj is not None:
			self.obj = obj
			self.name = self.obj.GetName()
			print( "Determining object %s (type=%d)" % ( self.obj.GetName(), self.obj.GetType() ) )
			
			# cache attributes
			self.determineCacheAttributes()
			# extract transformation
			self.extractTranform()
			# figure out animation details
			self.determineAnimation()
			self.cacheHeirarchy()
			# if len(self.obj.GetCTracks()) > 0:
			# 	if self.needsAnimationHeirarchy():
			# 		self.cacheAsAnimationHeirarchy()
			# 		return
			# 	else:
			# 		self.cacheAnimation()
			# 	pass
			pass
		pass

	@staticmethod
	def createParentNodeWithCorrectiveTransform( name, children ):
		# create our parent
		node = C4DNode()
		node.name = name
		# create our swap matrix (left handed to right handed)
		matrix = c4d.Matrix()
		# matrix.v1 = c4d.Vector(-1.0, 0.0, 0.0)
		matrix.v3 = c4d.Vector(0.0, 0.0, -1.0)
		# cache each transform part, most likely the trans, 
		# scale and rot won't ever be used, here for completeness
		node.matrix = convertC4DMatrix( matrix )
		node.translation = [ 0.0, 0.0, 0.0 ]
		node.scale = [-1.0, 1.0, -1.0]
		quat = c4d.Quaternion()
		node.rotation = [quat.v.x, quat.v.y, quat.v.z, quat.w]
		# cache stuff
		node.isNull = True
		node.cached = True
		# now append the selected children
		for itObj in children:
			node.childNodes.append( C4DNode( itObj ) )
			pass
		# return it as a list
		return [node]
		pass
	
	def cacheHeirarchy( self ):
		# append children
		childBegIt = self.obj.GetDown()
		while childBegIt:
			self.childNodes.append( C4DNode( childBegIt ) )
			childBegIt = childBegIt.GetNext()
			pass
		pass
		pass

	def extractTranform( self ):
		# cache the relative matrix
		self.matrix = convertC4DMatrix( self.obj.GetMl() )
		trans = self.obj.GetRelPos()
		scale = self.obj.GetRelScale()
		self.scale = [ scale.x, scale.y, scale.z ]
		# NOTE: HPB rotation euler need to convert
		rot = self.obj.GetRelRot()
		if False:
			# attempt of left to righthandedness
			quat = c4d.Quaternion()
			if self.hasCamera:
				self.translation = [ trans.x * _c4d.UNIT_SCALE, 
								 	 trans.y * _c4d.UNIT_SCALE, 
								 	 -trans.z * _c4d.UNIT_SCALE ]
				mat_x = c4d.utils.MatrixRotX(rot.y)
				mat_y = c4d.utils.MatrixRotY(rot.x)
				mat_z = c4d.utils.MatrixRotZ(rot.z)
				mat = mat_x * mat_y * mat_z
				rh_mat = mat
				rh_mat.v1.x = -rh_mat.v1.x
				rh_mat.v2.x = -rh_mat.v2.x
				rh_mat.v3.y = -rh_mat.v3.y
				rh_mat.v3.z = -rh_mat.v3.z
				newRot = c4d.utils.MatrixToHPB(rh_mat)
				quat.SetHPB(newRot)
			else:
				self.translation = [ trans.x * _c4d.UNIT_SCALE, 
								 	 trans.y * _c4d.UNIT_SCALE, 
								    -trans.z * _c4d.UNIT_SCALE ]
				mat_x = c4d.utils.MatrixRotX(rot.y)
				mat_y = c4d.utils.MatrixRotY(rot.x)
				mat_z = c4d.utils.MatrixRotZ(rot.z)
				mat = mat_x * mat_y * mat_z
				rh_mat = mat
				rh_mat.v1.z = -rh_mat.v1.z
				rh_mat.v2.z = -rh_mat.v2.z
				rh_mat.v3.x = -rh_mat.v3.x
				rh_mat.v3.y = -rh_mat.v3.y
				newRot = c4d.utils.MatrixToHPB(rh_mat)
				quat.SetHPB(newRot)
			self.rotation = [quat.v.x, quat.v.y, quat.v.z, quat.w]
		else:
			# putting out the transform directly
			self.translation = [ trans.x, trans.y, trans.z ]
			quat.SetHPB(rot)
			self.rotation = [quat.v.x, quat.v.y, quat.v.z, quat.w]
		pass

	def needsAnimationHeirarchy( self ):
		tracks = self.obj.GetCTracks() #Get it's first animation track
		for track in tracks:
			if track.GetName() in C4DAnimation.ROTATION_PARAMS:
				return True 
		return False 
		pass

	def determineAnimation( self ):
		tracks = self.obj.GetCTracks() #Get it's first animation track 
		if len(tracks) == 0: 
			return # if it doesn't have any tracks. End the script
		# print "animtion for node: " + self.getName()
		self.animation = C4DTransformAnimation( self.getKey(), tracks, self.getTranslation(), 
									   self.getRotation(), self.getScale() )
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

class C4DVectorAnimation( BaseVectorAnimation ):

	def __init__( self, vectorType, transform, components ):
		BaseVectorAnimation.__init__( self, vectorType, transform, components )
		pass

	def makeQuatKeyframes( self ):
		retKeyFrames = []
		# print "----------------------------------------------"
		for keyframe in self.keyframes:
			vec = c4d.Vector(keyframe[1][0], keyframe[1][1], keyframe[1][2])
			quat = c4d.Quaternion()
			quat.SetHPB(vec)
			# string = "quat: "
			# for comp in [quat.v.x, quat.v.y, quat.v.z, quat.w]:
			# 	string += str(comp) + ", "
			# print string + "\n"
			retKeyFrames.append([quat.v.x, quat.v.y, quat.v.z, quat.w])
			pass
		return retKeyFrames
		pass

class C4DTransformAnimation( BaseTransformAnimation ):
	TRANFORM_PARAMS = { "translation" : { 'Position . X' : 'x', 'Position . Y' : 'y', 'Position . Z' : 'z' },
					    "rotation" : { 'Rotation . H' : 'h', 'Rotation . P' : 'p', 'Rotation . B' : 'b' },
					 	"scale" : { 'Scale . X' : 'x', 'Scale . Y' : 'y', 'Scale . Z' : 'z' } }
	
	def __init__(self, nodeKey, tracks, translation, rotation, scale):
		BaseTransformAnimation.__init__( self, nodeKey )
		self.transform["translation"] = C4DVectorAnimation("translation", translation, ['x','y','z'] ) 
		self.transform["rotation"] = C4DVectorAnimation("rotation", rotation, ['h','p','b'] )
		self.transform["scale"] = C4DVectorAnimation("scale", scale, ['x','y','z'])

		for track in tracks:
			name = track.GetName()
			cached = False
			print "----------------------------------------------------------------------------"			
			for paramKey in C4DTransformAnimation.TRANFORM_PARAMS.keys():
				if name in C4DTransformAnimation.TRANFORM_PARAMS[paramKey].keys():
					comp = C4DTransformAnimation.TRANFORM_PARAMS[paramKey][name]
					cur = track.GetCurve()
					cached = True
					for x in range(cur.GetKeyCount()):
						key = cur.GetKey(x)
						timePoint = key.GetTime().Get()
						lastTime = key.GetTimeLeft().Get()
						nextTime = key.GetTimeRight().Get()
						value = key.GetValue()
						lastValue = key.GetValueLeft()
						nextValue = key.GetValueRight()
						print "lastTime: " + str(lastTime) + " lastValue: " + str(lastValue) + " time: " + str(timePoint) + " value: " + str(value) + " nextTime: " + str(nextTime) + " value: " + str(nextValue)
						# TODO: need to figure out interpolation
						interpolation = key.GetInterpolation()
						if paramKey == "translation":
							value = value * _c4d.UNIT_SCALE
							pass
						self.transform[paramKey].addKeyFrame(comp, timePoint, value)
			if cached == False:
				print "Did not cache animation track - " + name
				pass
		pass
		

# def exportData(self, object, channels, startF, endF, exportFile):
# #        objectPath = object.path()
#         objectName = object.GetName().replace(':', '_').replace('.', '_')
#         objectType = c4d.GetObjectName(object.GetType())
    
#         channalsAnimated = []
#         channalsNotAnimated = []
        
#         objectNameWrite = objectName
#         #Get the right Object-Type to write out
#         if objectType == 'Camera':
#             objectNodeTypeWrite = 'camera'
#         elif objectType == 'Null':
#             objectNodeTypeWrite = 'locator'
#         elif objectType == 'Light':
#             if object[c4d.LIGHT_TYPE] == 0:
#                 #Omni-Light
#                 objectNodeTypeWrite = 'point' 
#             elif object[c4d.LIGHT_TYPE] == 1:
#                 #Spot-Light
#                 objectNodeTypeWrite = 'spot'
#             elif object[c4d.LIGHT_TYPE] == 3:
#                 #Infinite-Light
#                 objectNodeTypeWrite = 'directional'

        
        #Get all the animated channels of that object
        # allAnimatedChannels = object.GetCTracks()
        
#         #Create an array with all the names of the animated channels
        # allAnimatedChannelNames = []
#         for aniChannel in allAnimatedChannels:
#             allAnimatedChannelNames.append(aniChannel.GetName())


#         self.aniChannelMatch = {'transform.tx':'Position . X', 
#         						  'transform.ty':'Position . Y', 
#         						  'transform.tz':'Position . Z', 
#         						  'transform.sx':'Scale . X', 
#         						  'transform.sy':'Scale . Y', 
#         						  'transform.sz':'Scale . Z', 
#         						  'transform.cr':'Color . R', 
#         						  'transform.cg':'Color . G', 
#         						  'transform.cb':'Color . B', 
#         						  'transform.intensity':'Intensity'}

#         if object[c4d.ID_BASEOBJECT_ROTATION_ORDER] == 6: #When HPB
#             self.aniChannelMatch.update({'transform.rx':'Rotation . P', 'transform.ry':'Rotation . H', 'transform.rz':'Rotation . B'})
#         else:
#             self.aniChannelMatch.update({'transform.rx':'Rotation . X', 'transform.ry':'Rotation . Y', 'transform.rz':'Rotation . Z'})

  
#         #Invert the aniChannelMatch to have acces to the channelNames
#         channelMatch_inverted = dict( ((self.aniChannelMatch[k], k) for k in (self.aniChannelMatch) ) )
       
#         #Now split all the channels which should get exported in an animated and not animated group
#         for channel in channels:
#             channelAnimated = False

#             #Check if Channel is in MatchingDictionary (only animatable are in there), so if not there it will not be animated
#             if channels[channel] in self.aniChannelMatch:
#                 #If it is in dictionary and also in the dictionary with the animated channels then it is animated
#                 if self.aniChannelMatch[channels[channel]] in allAnimatedChannelNames:
#                     channelAnimated = True
                
#             #Now depending on the set value it adds it to the matching group
#             if channelAnimated:
#                 channalsAnimated.append(channel)
#             else:    
#                 channalsNotAnimated.append(channel)

        
#         #Output Values
#         writeOut = objectNameWrite + '\t'  + objectNodeTypeWrite + '\t\n'
            
#         #Write out not animated Channels  
#         for channel in channalsNotAnimated:
#             thisValue = self.getObjectParameterValue(object, channel, channels)

#             writeOut += "%s\t%s\n" % (channels[channel], thisValue)
                
#         writeOut += '+++++Animated+++++\n'
#         #Write out animated Channels
    
#         if len(channalsAnimated) > 0:
#             #List all animated Channels
#             writeOut += 'Frame'
#             for channel in channalsAnimated:
#                 #channelValues = channel.split(':')
#                 writeOut += "\t%s" % channels[channel]
#             writeOut += '\n'
                
#             #Go through all Frames    
#             for frame in range(startF, (endF+1)):
#                 #Write out Frame-Number
#                 writeOut += str(frame)
                
#                 #Set Frame - Maybe later differently
#                 self.setCurrentFrame(frame, self.doc)

#                 for channel in channalsAnimated:
#                     writeOut += "\t%s" % self.getObjectParameterValue(object, channel, channels)
#                 writeOut += '\n'
        
#         f = open(exportFile, 'w')
#         f.write(writeOut)
#         f.close()  