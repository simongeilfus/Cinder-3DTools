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
from c4d import gui

class C4DExporterOptions( object ) :
	def __init__( self ):
		self.exportSelectionOnly = False
		self.defaultTextureWidth = 512
		self.defaultTextureHeight = 512
		self.exportTextures = True
		self.bakeTransforms = False
		self.angleWeightedTransforms = False



class C4DExporter( BaseExporter ):

	def __init__( self, options = None ):
		BaseExporter.__init__( self )
		if options is None:
			self.options = C4DExporterOptions()
		else:
			self.options = options
		
	def cacheNodes( self ):

    	# get the active document
		doc = c4d.documents.GetActiveDocument()
		#doc = c4d.documents.GetActiveDocument().Polygonize( keepanimation=True )

		# Not 100% sure about this, but I wonder if this doesn't force generating
		# virtual caches on non-polygonal objects.
		# https://developers.maxon.net/docs/Cinema4DPythonSDK/html/modules/c4d.documents/BaseDocument/index.html#caching
		c4d.DrawViews(c4d.DRAWFLAGS_ONLY_ACTIVE_VIEW|c4d.DRAWFLAGS_NO_THREAD|c4d.DRAWFLAGS_NO_REDUCTION|c4d.DRAWFLAGS_STATICBREAK)

		# get document data
		docData = doc.GetDocumentData()

		# unit conversion
		# should probably use c4d.utils.CalculateTranslationScale
		# https://developers.maxon.net/docs/Cinema4DPythonSDK/html/modules/c4d.utils/index.html#c4d.utils.CalculateTranslationScale
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
		# modify the global UNIT_SCALE factor
		_c4d.UNIT_SCALE = scaleFactor

		# get document path
		self.documentPath = doc.GetDocumentPath()		

		# export
		if self.options.exportSelectionOnly :
			# get selection
			selected = doc.GetActiveObjects( c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER )
			numObjSelected = len( selected )
			if 0 == numObjSelected:
				gui.MessageDialog( "Nothing selected" )
				return False
			processed = 0.0
			# let the user know that we started the process
			c4d.StatusSetBar( 0 )
			for itObj in selected:
				self.nodes.append( C4DNode( itObj ) )
				processed = processed + 1.0
				c4d.StatusSetBar( 100.0 * float(processed) / float(numObjSelected) )
				pass
		else :
			# get full doc
			obj = doc.GetFirstObject()
			# let the user know that we started the process
			c4d.StatusSetBar(50)
			while obj :
				self.nodes.append( C4DNode( obj ) )
				obj = obj.GetNext()
			
		# Create a directory using the scene name
		self.sceneFileName = doc.GetDocumentName()

		# clear the status bar
		c4d.StatusClear()
		return True
		pass