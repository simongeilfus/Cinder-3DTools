import c4d
from c4d import bitmaps, documents, gui, plugins, threading, utils, storage

import sys
sys.path.append( "C:\\Code\\Cinder\\Cinder-3DTools\\pysrc\\cinder" )
import C4D
reload( C4D )
from C4D import C4DExporter, C4DExporterOptions


# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1037872


# Main dialog
class ExporterDialog(gui.GeDialog):

    PATH_PICKER = 1000
    
    BUTTON_PATH_PICKER = 1001
    BUTTON_EXPORT_DOC = 1002
    BUTTON_EXPORT_SELECTION = 1003
    
    COMBO_EXPORT_TYPE = 1004
    COMBO_EXPORT_TYPE_GLTF = 1005
    COMBO_EXPORT_TYPE_TRIMESH = 1006
    
    OPTION_BAKE_TRANSFORM = 1007
    OPTION_ANGLE_WEIGHT_NORMALS = 1008

    MATERIALS_EXPORT_TEXTURES = 1009
    MATERIALS_TEXTURES_FORMAT = 1010
    MATERIALS_TEXTURES_FORMAT_JPG = 1011
    MATERIALS_TEXTURES_FORMAT_PNG = 1012
    MATERIALS_TEXTURES_WIDTH = 1013
    MATERIALS_TEXTURES_HEIGHT = 1014

    def CreateLayout( self ):

        self.SetTitle("glTF / ci::TriMesh Exporter")

        # Exporter Path & Options
        self.GroupBegin( id=0, flags=c4d.BFH_SCALEFIT, rows=2, title="Format Options", cols=3, groupflags=0 )
        self.GroupBorder( c4d.BORDER_WITH_TITLE_BOLD | c4d.BORDER_GROUP_TOP )
        self.GroupBorderSpace( 10, 10, 10, 10 )
        
        self.AddStaticText( 1200, c4d.BFH_LEFT, 0, 0, "Filename", c4d.BORDER_NONE )
        self.pathPicker = self.AddEditText( id=self.PATH_PICKER, flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, initw=250, inith=0)
        self.AddButton( id=self.BUTTON_PATH_PICKER, flags=c4d.BFH_LEFT, initw=15, inith=10, name="..." )
        
        self.AddStaticText( 1201, c4d.BFH_LEFT, 0, 0, "Format", c4d.BORDER_NONE )
        self.typeCombo = self.AddComboBox( id=self.COMBO_EXPORT_TYPE, flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, initw=120, inith=0)
        self.AddChild( self.typeCombo, self.COMBO_EXPORT_TYPE_GLTF, "glTF" )
        self.AddChild( self.typeCombo, self.COMBO_EXPORT_TYPE_TRIMESH, "TriMesh" )
        self.SetLong( id=self.COMBO_EXPORT_TYPE, value=self.COMBO_EXPORT_TYPE_GLTF )
        
        self.GroupEnd()

        # Options
        self.GroupBegin( id=0, flags=c4d.BFH_SCALEFIT, rows=2, title="Options", cols=1, groupflags=0 )
        self.GroupBorder( c4d.BORDER_WITH_TITLE_BOLD | c4d.BORDER_GROUP_TOP )
        self.GroupBorderSpace( 10, 10, 10, 10 )

        self.AddCheckbox( id=self.OPTION_BAKE_TRANSFORM, name="Bake Transforms", flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, initw=250, inith=0)
        self.AddCheckbox( id=self.OPTION_ANGLE_WEIGHT_NORMALS, name="Angle Weighted Normals", flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, initw=250, inith=0)

        self.GroupEnd()

        # Materials Options
        self.GroupBegin( id=0, flags=c4d.BFH_SCALEFIT, rows=2, title="Materials", cols=1, groupflags=0 )
        self.GroupBorder( c4d.BORDER_WITH_TITLE_BOLD | c4d.BORDER_GROUP_TOP )
        self.GroupBorderSpace( 10, 10, 10, 0 )

        self.AddCheckbox( id=self.MATERIALS_EXPORT_TEXTURES, name="Export Textures", flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, initw=250, inith=0)
        self.AddComboBox( id=self.MATERIALS_TEXTURES_FORMAT, flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, initw=120, inith=0)
        self.AddChild( self.MATERIALS_TEXTURES_FORMAT, self.MATERIALS_TEXTURES_FORMAT_JPG, "JPG" )
        self.AddChild( self.MATERIALS_TEXTURES_FORMAT, self.MATERIALS_TEXTURES_FORMAT_PNG, "PNG" )
        self.SetLong( self.MATERIALS_TEXTURES_FORMAT, self.MATERIALS_TEXTURES_FORMAT_JPG )
        self.GroupEnd()

        self.GroupBegin( id=0, flags=c4d.BFH_SCALEFIT, rows=2, title=" ", cols=2, groupflags=0 )
        self.GroupBorderSpace( 10, 0, 10, 10 )
        self.AddStaticText( 1202, c4d.BFH_LEFT, 0, 0, "Width", c4d.BORDER_NONE )
        self.AddEditNumberArrows( self.MATERIALS_TEXTURES_WIDTH, flags=c4d.BFH_LEFT )
        self.AddStaticText( 1203, c4d.BFH_LEFT, 0, 0, "Height", c4d.BORDER_NONE )
        self.AddEditNumberArrows( self.MATERIALS_TEXTURES_HEIGHT, flags=c4d.BFH_LEFT )
        self.SetInt32( self.MATERIALS_TEXTURES_WIDTH, 512 )
        self.SetInt32( self.MATERIALS_TEXTURES_HEIGHT, 512 )
        self.GroupEnd()

        # Export buttons
        self.GroupBegin( id=0, flags=c4d.BFH_SCALEFIT, rows=2, title="Export", cols=1, groupflags=0 )
        self.GroupBorder( c4d.BORDER_WITH_TITLE_BOLD | c4d.BORDER_GROUP_TOP )
        self.GroupBorderSpace( 10, 10, 10, 10 )

        self.AddButton( id=self.BUTTON_EXPORT_DOC, flags=c4d.BFH_LEFT, initw=120, inith=10, name="Document" )
        self.AddButton( id=self.BUTTON_EXPORT_SELECTION, flags=c4d.BFH_LEFT, initw=120, inith=10, name="Selection" )

        self.GroupEnd()

        # TODO: Remove
        self.SetString( self.pathPicker, "C:\\Users\\Simon\\Desktop\\glTFTest\\assets" )

        return True

    def Command( self, id, msg ):

        if id == self.BUTTON_PATH_PICKER:
            filePath = storage.SaveDialog( title="Cinder glTF Exporter", type=c4d.FILESELECTTYPE_ANYTHING, force_suffix="gltf" )
            if filePath is None:
                return
            else:
                self.SetString( self.pathPicker, filePath )

        elif id == self.BUTTON_EXPORT_SELECTION or id == self.BUTTON_EXPORT_DOC:
            filePath = self.GetString( self.pathPicker )
            if filePath is None:
                return

            exporterOptions = C4DExporterOptions()
            exporterOptions.exportSelectionOnly = ( id == self.BUTTON_EXPORT_SELECTION )
            exporterOptions.defaultTextureWidth = self.GetInt32( self.MATERIALS_TEXTURES_WIDTH )
            exporterOptions.defaultTextureHeight = self.GetInt32( self.MATERIALS_TEXTURES_HEIGHT )
            exporterOptions.exportTextures = self.GetBool( self.MATERIALS_EXPORT_TEXTURES )
            exporter = C4DExporter( exporterOptions )
            exporter.export( filePath )            

        return True

    def CoreMessage( self, id, msg ):
        if id==PLUGIN_ID:
            
            return True

        return gui.GeDialog.CoreMessage(self, id, msg)

    def AskClose( self ):
        return False

# Command Plugin
class ExporterCommandData(c4d.plugins.CommandData):
    dialog = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = ExporterDialog()
        
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=250, defaulth=50)
    

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = ExporterDialog()

        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)
    
            
    
if __name__=='__main__':

    plugins.RegisterCommandPlugin(id=PLUGIN_ID, str="gltfExporter",
                                  help="gltfExporter", info=0, dat=ExporterCommandData(), icon=None)
