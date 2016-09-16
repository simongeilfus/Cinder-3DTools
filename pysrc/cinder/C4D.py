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
from C4DObjects import _c4d

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
		#print self.documentPath


		# get document data
		docData = doc.GetDocumentData()
		# unit convertion
		unitScale = docData[c4d.DOCUMENT_DOCUNIT].GetUnitScale()
		# start at the project scale
		scaleFactor = unitScale[0]
		# and convert using the project unit
		if unitScale[1] == c4d.DOCUMENT_UNIT_KM :
		    scaleFactor *= 1000.0
		elif unitScale[1] == c4d.DOCUMENT_UNIT_M :
		    scaleFactor *= 1.0
		elif unitScale[1] == c4d.DOCUMENT_UNIT_CM :
		    scaleFactor *= 0.01
		elif unitScale[1] == c4d.DOCUMENT_UNIT_MM :
		    scaleFactor *= 0.001
		elif unitScale[1] == c4d.DOCUMENT_UNIT_MICRO :
		    scaleFactor *= 0.00001
		elif unitScale[1] == c4d.DOCUMENT_UNIT_MILE :
		    scaleFactor *= 1.0
		elif unitScale[1] == c4d.DOCUMENT_UNIT_YARD :
		    scaleFactor *= 1.0
		elif unitScale[1] == c4d.DOCUMENT_UNIT_FOOT :
		    scaleFactor *= 1.0
		elif unitScale[1] == c4d.DOCUMENT_UNIT_INCH :
		    scaleFactor *= 1.0
		pass

		print "Testing"
		_c4d.UNIT_SCALE = C4DProjectRescale
		print _c4d.UNIT_SCALE
		print C4DProjectRescale
		print " \n"
		

		if 0 == len( selected ):
			print( "Nothing selected" )
			return False
		# self.nodes = C4DNode.createParentNodeWithCorrectiveTransform("left_handed_to_right_handed_transform", selected )
		
		for itObj in selected:
			self.nodes.append( C4DNode( itObj ) )
			pass
		# Create a directory using the scene name
		self.sceneFileName = doc.GetDocumentName()
		return True
		pass