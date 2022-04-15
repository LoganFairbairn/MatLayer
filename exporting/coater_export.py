import bpy
from bpy.types import Operator, PropertyGroup

class COATER_OT_export(Operator):
    bl_idname = "coater.export"
    bl_label = "Export"
    bl_description = "Bakes and exports all selected textures to the textures folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        bpy.ops.coater.export_base_color()
        bpy.ops.coater.export_metallic()
        bpy.ops.coater.export_roughness()
        bpy.ops.coater.export_normals()
        bpy.ops.coater.export_height()
        bpy.ops.coater.export_emission()
        bpy.ops.coater.export_scattering()
        return {'FINISHED'}

class COATER_OT_export_base_color(Operator):
    bl_idname = "coater.export_base_color"
    bl_label = "Export Base Color"
    bl_description = "Bakes the Coater base color channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        #bpy.ops.coater.toggle_channel_preview()
        return {'FINISHED'}

class COATER_OT_export_metallic(Operator):
    bl_idname = "coater.export_metallic"
    bl_label = "Export Metallic Channel"
    bl_description = "Bakes the Coater metallic channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        return {'FINISHED'}

class COATER_OT_export_roughness(Operator):
    bl_idname = "coater.export_roughness"
    bl_label = "Export Roughness"
    bl_description = "Bakes the Coater roughness channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        return {'FINISHED'}

class COATER_OT_export_normals(Operator):
    bl_idname = "coater.export_normals"
    bl_label = "Export Normals"
    bl_description = "Bakes the Coater normal channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        return {'FINISHED'}

class COATER_OT_export_height(Operator):
    bl_idname = "coater.export_height"
    bl_label = "Export Height"
    bl_description = "Bakes the Coater height channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        return {'FINISHED'}

class COATER_OT_export_emission(Operator):
    bl_idname = "coater.export_emission"
    bl_label = "Export Emission"
    bl_description = "Bakes the Coater emission channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        return {'FINISHED'}

class COATER_OT_export_scattering(Operator):
    bl_idname = "coater.export_scattering"
    bl_label = "Export Scattering"
    bl_description = "Bakes the Coater scattering channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        return {'FINISHED'}