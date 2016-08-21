
from TriMeshWriter import TriMeshWriter
import GltfWriter
## \class BaseMaterial
#
#
class BaseMaterial( object ):
	## c'tor
	def __init__( self ):
		print( "BaseMaterial c'tor" )	
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
		print( "BaseMesh c'tor" )
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
class BaseLight( object ):
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

class BaseNode( object ):
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

	def getParentName( self ):
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
		print( "BaseExporter c'tor" )
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