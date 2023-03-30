import os
import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import BoolProperty, StringProperty
from ..layers import toggle_channel_preview
from ..texture_set_settings import texture_set_settings
from ..utilities import print_info_messages

#----------------------------- EXPORT SETTINGS -----------------------------#

class MATLAY_exporting_settings(bpy.types.PropertyGroup):
    export_folder: StringProperty(default="", description="Path to folder location where exported texture are saved. If empty, an export folder will be created next to your .blend file and exported textures will be automatically saved there.", name="Export Folder Path")
    show_advanced_settings: BoolProperty(default=False, name="Show Advanced Settings", description="Click to show / hide advanced baking settings. Advanced settings generally don't need to be edited")
    export_base_color: BoolProperty(default=True, name="Export Base Color", description="Include the base color in batch exporting.")
    export_subsurface: BoolProperty(default=True, name="Export Subsurface", description="Include the subsurface in batch exporting.")
    export_subsurface_color: BoolProperty(default=True, name="Export Subsurface Color", description="Include the subsurface color in batch exporting.")
    export_metallic: BoolProperty(default=True, name="Export Metallic", description="Include the metallic in batch exporting.")
    export_specular: BoolProperty(default=True, name="Export Specular", description="Include the specular in batch exporting.")
    export_roughness: BoolProperty(default=True, name="Export Roughness", description="Include the roughness in batch exporting.")
    export_normals: BoolProperty(default=True, name="Export Normals", description="Include the normals in batch exporting.")
    export_height: BoolProperty(default=True, name="Export Height", description="Include the height in batch exporting.")
    export_emission: BoolProperty(default=True, name="Export Emission", description="Include the emission in batch exporting.")

#----------------------------- EXPORT FUNCTIONS -----------------------------#

def bake_and_export_material_channel(material_channel_name, context):
    '''Bakes the material channel to a texture and saves the output image to a folder.'''
    if bpy.context.active_object == None:
        print_info_messages.show_message_box("No export.", "MatLay baking error.", 'ERROR')
        return

    # Isolate the material channel.
    toggle_channel_preview.toggle_material_channel_preview(True, material_channel_name, context)

    # Define the background color for the exported images.
    export_image_background_color = (0.0, 0.0, 0.0, 1.0)
    if material_channel_name == 'NORMAL':
        export_image_background_color = (0.25, 0.25, 0.5, 1.0)

    # Create a new image in Blender's data and image node.
    export_image_name = bpy.context.active_object.name + "_" + material_channel_name
    export_image = bpy.data.images.get(export_image_name)
    if export_image != None:
        bpy.data.images.remove(export_image)
    export_image = bpy.ops.image.new(name=export_image_name, 
                                     width=texture_set_settings.get_texture_width(), 
                                     height=texture_set_settings.get_texture_height(), 
                                     color=export_image_background_color, 
                                     alpha=False, 
                                     generated_type='BLANK', 
                                     float=False, 
                                     use_stereo_3d=False, 
                                     tiled=False)
    
    # Create a folder for the exported texture files.
    export_path = bpy.path.abspath("//") + 'Exports'
    if os.path.exists(export_path) == False:
        os.mkdir(export_path)

    export_image = bpy.data.images.get(export_image_name)
    export_image.filepath = export_path + "/" + export_image_name + ".png"
    export_image.file_format = 'PNG'

    material_nodes = context.active_object.active_material.node_tree.nodes
    image_node = material_nodes.new('ShaderNodeTexImage')
    image_node.image = export_image

    # Bake to the image texture.
    bpy.context.scene.render.bake.use_selected_to_active = False
    bpy.ops.object.bake(type='EMIT')

    # Save the image.
    if export_image:
        if export_image.is_dirty:
            export_image.save()
        else:
            print_info_messages.show_message_box("Exported image pixel data wasn't updated during baking.", "MatLay baking error.", 'ERROR')

    # Delete the image node.
    material_nodes.remove(image_node)

    # De-isolate the material channel.
    toggle_channel_preview.toggle_material_channel_preview(False, material_channel_name, context)

class MATLAY_OT_export(Operator):
    bl_idname = "matlay.export"
    bl_label = "Batch Export"
    bl_description = "Bakes and exports all selected textures to the textures folder"

    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        bpy.ops.matlay.export_base_color()
        bpy.ops.matlay.export_subsurface()
        bpy.ops.matlay.export_subsurface_color()
        bpy.ops.matlay.export_metallic()
        bpy.ops.matlay.export_specular()
        bpy.ops.matlay.export_roughness()
        bpy.ops.matlay.export_normals()
        bpy.ops.matlay.export_height()
        bpy.ops.matlay.export_emission()
        return {'FINISHED'}

class MATLAY_OT_export_base_color(Operator):
    bl_idname = "matlay.export_base_color"
    bl_label = "Export Base Color"
    bl_description = "Bakes the MatLay base color channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        if bpy.context.scene.matlay_export_settings.export_base_color:
            bake_and_export_material_channel('COLOR', context)
        return {'FINISHED'}

class MATLAY_OT_export_subsurface(Operator):
    bl_idname = "matlay.export_subsurface"
    bl_label = "Export Subsurface"
    bl_description = "Bakes the MatLay subsurface and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        if bpy.context.scene.matlay_export_settings.export_subsurface:
            bake_and_export_material_channel('SUBSURFACE', context)
        return {'FINISHED'}

class MATLAY_OT_export_subsurface_color(Operator):
    bl_idname = "matlay.export_subsurface_color"
    bl_label = "Export Subsurface COLOR"
    bl_description = "Bakes the MatLay subsurface color and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        if bpy.context.scene.matlay_export_settings.export_subsurface_color:
            bake_and_export_material_channel('SUBSURFACE_COLOR', context)
        return {'FINISHED'}

class MATLAY_OT_export_metallic(Operator):
    bl_idname = "matlay.export_metallic"
    bl_label = "Export Metallic Channel"
    bl_description = "Bakes the MatLay metallic channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        if bpy.context.scene.matlay_export_settings.export_metallic:
            bake_and_export_material_channel('METALLIC', context)
        return {'FINISHED'}

class MATLAY_OT_export_specular(Operator):
    bl_idname = "matlay.export_specular"
    bl_label = "Export Specular"
    bl_description = "Bakes the MatLay specular and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        if bpy.context.scene.matlay_export_settings.export_specular:
            bake_and_export_material_channel('SPECULAR', context)
        return {'FINISHED'}

class MATLAY_OT_export_roughness(Operator):
    bl_idname = "matlay.export_roughness"
    bl_label = "Export Roughness"
    bl_description = "Bakes the MatLay roughness channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        if bpy.context.scene.matlay_export_settings.export_roughness:
            bake_and_export_material_channel('ROUGHNESS', context)
        return {'FINISHED'}

class MATLAY_OT_export_normals(Operator):
    bl_idname = "matlay.export_normals"
    bl_label = "Export Normals"
    bl_description = "Bakes the MatLay normal channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        if bpy.context.scene.matlay_export_settings.export_normals:
            bake_and_export_material_channel('NORMAL', context)
        return {'FINISHED'}

class MATLAY_OT_export_height(Operator):
    bl_idname = "matlay.export_height"
    bl_label = "Export Height"
    bl_description = "Bakes the MatLay height channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        if bpy.context.scene.matlay_export_settings.export_height:
            bake_and_export_material_channel('HEIGHT', context)
        return {'FINISHED'}

class MATLAY_OT_export_emission(Operator):
    bl_idname = "matlay.export_emission"
    bl_label = "Export Emission"
    bl_description = "Bakes the MatLay emission channel and saves the result to the export folder"

    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        if bpy.context.scene.matlay_export_settings.export_emission:
            bake_and_export_material_channel('EMISSION', context)
        return {'FINISHED'}