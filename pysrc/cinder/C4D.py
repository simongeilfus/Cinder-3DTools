"""
import sys
sys.path.append( "/Users/ryanbartley/Documents/clean_cinder/blocks/Cinder-3DTools/pysrc/cinder" )
import C4D
reload( C4D )
from C4D import C4DExporter
 
exporter = C4DExporter()
exporter.export( "/Users/ryanbartley/Documents/clean_cinder/blocks/Cinder-3DTools/TriMeshViewer/assets" )
"""

import c4d

import Base
reload( Base )
from Base import BaseExporter

import C4DObjects
reload( C4DObjects )
from C4DObjects import C4DNode
from C4DObjects import C4DMaterial
from C4DObjects import C4DMesh
from C4DObjects import C4DCamera
from C4DObjects import C4DLight

class C4DExporter( BaseExporter ):

	def __init__( self ):
		BaseExporter.__init__( self )
		#print( "C4DExporter c'tor" )
		pass
	# class BaseExporter
	pass

	def cacheNodes( self ):
		print "cacheNodes"
		doc = c4d.documents.GetActiveDocument()

		selected = doc.GetActiveObjects( c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER )
		self.documentPath = doc.GetDocumentPath()
		print self.documentPath
		if 0 == len( selected ):
			print( "Nothing selected" )
			return False

		self.nodes = []
		for itObj in selected:
			self.nodes.append( C4DNode( itObj ) )
			pass

		# Create a directory using the scene name
		self.sceneFileName = doc.GetDocumentName()
		return True
		pass