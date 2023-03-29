import bpy
from bpy.types import Operator, PropertyGroup

class MATLAY_exporting_settings(bpy.types.PropertyGroup):
    export_folder: bpy.props.StringProperty(default="", description="Path to folder location where baked texture are saved.", name="Export Folder Path")
    export_base_color: bpy.props.BoolProperty(default=True, name="Export Base Color")
    export_metallic: bpy.props.BoolProperty(default=True, name="Export Metallic")
    export_roughness: bpy.props.BoolProperty(default=True, name="Export Roughness")
    export_normals: bpy.props.BoolProperty(default=True, name="Export Normals")
    export_height: bpy.props.BoolProperty(default=True, name="Export Height")
    export_emission: bpy.props.BoolProperty(default=True, name="Export Emission")
    export_scattering: bpy.props.BoolProperty(default=True, name="Export Scattering")

class MATLAY_OT_export(Operator):
    bl_idname = "matlay.export"
    bl_label = "Export"
    bl_description = "Bakes and exports all selected textures to the textures folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        bpy.ops.matlay.export_base_color()
        bpy.ops.matlay.export_metallic()
        bpy.ops.matlay.export_roughness()
        bpy.ops.matlay.export_normals()
        bpy.ops.matlay.export_height()
        bpy.ops.matlay.export_emission()
        bpy.ops.matlay.export_scattering()
        return {'FINISHED'}

class MATLAY_OT_export_base_color(Operator):
    bl_idname = "matlay.export_base_color"
    bl_label = "Export Base Color"
    bl_description = "Bakes the MatLay base color channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        #bpy.ops.matlay.toggle_channel_preview()
        return {'FINISHED'}

class MATLAY_OT_export_metallic(Operator):
    bl_idname = "matlay.export_metallic"
    bl_label = "Export Metallic Channel"
    bl_description = "Bakes the MatLay metallic channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        return {'FINISHED'}

class MATLAY_OT_export_roughness(Operator):
    bl_idname = "matlay.export_roughness"
    bl_label = "Export Roughness"
    bl_description = "Bakes the MatLay roughness channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        return {'FINISHED'}

class MATLAY_OT_export_normals(Operator):
    bl_idname = "matlay.export_normals"
    bl_label = "Export Normals"
    bl_description = "Bakes the MatLay normal channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        return {'FINISHED'}

class MATLAY_OT_export_height(Operator):
    bl_idname = "matlay.export_height"
    bl_label = "Export Height"
    bl_description = "Bakes the MatLay height channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        return {'FINISHED'}

class MATLAY_OT_export_emission(Operator):
    bl_idname = "matlay.export_emission"
    bl_label = "Export Emission"
    bl_description = "Bakes the MatLay emission channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        return {'FINISHED'}

class MATLAY_OT_export_scattering(Operator):
    bl_idname = "matlay.export_scattering"
    bl_label = "Export Scattering"
    bl_description = "Bakes the MatLay scattering channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        return {'FINISHED'}