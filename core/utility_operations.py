# This module contains extra utility operations that assist with using this add-on or material editing in general.

import bpy
import os
from bpy.types import Operator
from bpy.utils import resource_path
from pathlib import Path
from ..core import debug_logging
from ..core import blender_addon_utils as bau
from ..preferences import ADDON_NAME

class MATLAYER_OT_append_default_workspace(Operator):
    bl_idname = "matlayer.append_default_workspace"
    bl_label = "Append Workspace"
    bl_description = "Appends a suggested workspace for using this add-on"

    def execute(self, context):
        workspace = bpy.data.workspaces.get('MatLayer')
        if workspace:
            debug_logging.log_status("The default workspace already exists, manually delete it and click this operator again to re-load the workspace.", self, 'INFO')
            return {'FINISHED'}
        
        USER = Path(resource_path('USER'))
        ADDON = ADDON_NAME
        BLEND_FILE = "Assets.blend"
        source_path =  str(USER / "scripts/addons" / ADDON / "blend" / BLEND_FILE)
        
        with bpy.data.libraries.load(source_path) as (data_from, data_to):
            data_to.workspaces = ["MatLayer"]

        # Set the current workspace to the appended workspace.
        bpy.context.window.workspace = bpy.data.workspaces['MatLayer']
        
        # Set the UI to the default tab.
        context.scene.matlayer_panel_properties.sections = 'SECTION_EDIT_MATERIALS'

        # Set up a material asset browser for the user.
        preferences = bpy.context.preferences
        if not preferences.filepaths.asset_libraries.get("MatLayer Default Assets"):
            bpy.ops.preferences.asset_library_add()
            new_library = bpy.context.preferences.filepaths.asset_libraries[-1]
            new_library.name = "MatLayer Default Assets"
            new_library.path = str(USER / "scripts/addons" / ADDON / "blend")

        self.report({'INFO'}, "Appended workspace (check the workspaces / user interface layouts at the top of your screen).")

        return {'FINISHED'}

class MATLAYER_OT_set_decal_layer_snapping(Operator):
    bl_idname = "matlayer.set_decal_layer_snapping"
    bl_label = "Set Decal Layer Snapping"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Sets optimal snapping settings for positioning decal layers. You can disable the snapping mode by selecting the magnet icon in the middle top area of the 3D viewport"

    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_elements = {'FACE'}
        bpy.context.scene.tool_settings.snap_target = 'CENTER'
        bpy.context.scene.tool_settings.use_snap_align_rotation = True
        return {'FINISHED'}

class MATLAYER_OT_append_hdri_world(Operator):
    bl_idname = "matlayer.append_hdri_world"
    bl_label = "Append HDRI World"
    bl_description = "Appends a world environment setup for HDRI lighting"

    def execute(self, context):
        bau.append_world('HDRIWorld')
        bpy.context.scene.world = bpy.data.worlds['HDRIWorld']
        return {'FINISHED'}

class MATLAYER_OT_remove_unused_raw_textures(Operator):
    bl_idname = "matlayer.remove_unused_textures"
    bl_label = "Remove Unused Textures"
    bl_description = "Removes all unused textures from the blend file, and all textures not used in the external raw texture folder"

    def execute(self, context):
        external_folder_path = bau.get_texture_folder_path(folder='RAW_TEXTURES')

        # Delete all images externally then internally for all images with no users.
        for image in bpy.data.images:
            if image.users <= 0:
                image_name = image.name
                if not image.filepath == "":
                    file_extension = os.path.splitext(image.filepath)[1]
                    image_path = os.path.join(external_folder_path, image_name + file_extension)
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        debug_logging.log("Deleted unused external image: {0}".format(image_name))

                bpy.data.images.remove(image)
                debug_logging.log("Deleted unused internal image: {0}".format(image_name))

        # If the image exists externally, but doesn't exist in blend data, delete it.
        internal_image_names = []
        for image in bpy.data.images:
            internal_image_names.append(image.name)
        external_textures = os.listdir(external_folder_path)
        for texture_name_and_extension in external_textures:
            texture_name = os.path.splitext(texture_name_and_extension)[0]
            if texture_name not in internal_image_names:
                image_path = os.path.join(external_folder_path, texture_name_and_extension)
                os.remove(image_path)
                debug_logging.log("Deleted external image that doesn't exist internally: {0}".format(texture_name))

        return {'FINISHED'}
    
class MATLAYER_OT_append_material_ball(Operator):
    bl_idname = "matlayer.append_material_ball"
    bl_label = "Append Material Ball"
    bl_description = "Appends a material ball object designed to be optimal for testing materials"

    def execute(self, context):
        bau.append_object("MaterialBall")
        return {'FINISHED'}

def add_outline(outline_object, self):
    '''Adds an outline to the specified object by adding a solidify modifier with inverted normals and an outline material to it.'''
    # Ensure the selected object is a mesh.
    if outline_object is None or outline_object.type != 'MESH':
        debug_logging.log_status("Object must be a mesh.", self, type='INFO')
        return
    
    # If an outline material is already applied, cancel the operation.
    outline_material_name = "Outline"
    for mat in outline_object.data.materials:
        if mat and mat.name == outline_material_name:
            debug_logging.log_status("Outline material already applied.", self, type='INFO')
            return
    
    # Create an outline material if one does not exist.
    outline_material = bpy.data.materials.get(outline_material_name)
    if not outline_material:
        outline_material = bpy.data.materials.new(name=outline_material_name)
        outline_material.use_nodes = True
        outline_material.use_backface_culling = True
        outline_material.use_backface_culling_shadow = True
        outline_material.use_backface_culling_lightprobe_volume = True

        nodes = outline_material.node_tree.nodes
        links = outline_material.node_tree.links
        for node in nodes:
            nodes.remove(node)
        emission_node = nodes.new(type="ShaderNodeEmission")
        emission_node.location = (-200, 0)
        emission_node.inputs["Color"].default_value = (0, 0, 0, 1)
        emission_node.inputs["Strength"].default_value = 1.0
        output_node = nodes.new(type="ShaderNodeOutputMaterial")
        output_node.location = (0, 0)
        links.new(emission_node.outputs["Emission"], output_node.inputs["Surface"])

    # Add the outline material to the object in a new material slot.
    outline_object.data.materials.append(outline_material)

    # Add a solidify modifier and adjust its settings so it acts as an outline.
    solidify = outline_object.modifiers.new(name="Black Outline", type='SOLIDIFY')
    solidify.thickness = self.thickness
    solidify.offset = -1
    solidify.use_flip_normals = True
    solidify.material_offset = len(outline_object.data.materials) - 1
    
class MATLAYER_OT_add_black_outline(bpy.types.Operator):
    bl_idname = "matlayer.add_black_outline"
    bl_label = "Add Black Outline"
    bl_description = "Adds a black outline to all selected objects by adding solidify modifiers with inverted normals and an outline material to them"
    bl_options = {'REGISTER', 'UNDO'}

    thickness: bpy.props.FloatProperty(
        name="Outline Thickness",
        description="Thickness of the outline",
        default=0.002,
        min=0.001,
        max=10.0,
    )

    def execute(self, context):

        # Add an outline to all selected objects.
        for obj in context.selected_objects:
            add_outline(obj, self)
            
        # Log completion.
        debug_logging.log_status("Added a black outline to all selected objects.", self, type='INFO')
        return {'FINISHED'}
