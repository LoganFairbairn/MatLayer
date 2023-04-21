import bpy
from bpy.types import Operator
from bpy.utils import resource_path
from pathlib import Path
from ..core import material_channels
from ..core import layer_nodes
from ..core import layer_masks
from ..utilities import info_messages
import os

class MATLAY_OT_delete_unused_images(Operator):
    """Deletes unused saved layer and mask images from folders."""
    bl_idname = "matlay.delete_unused_images"
    bl_label = "Delete Unused Images"
    bl_description = "Deletes unused saved layer and mask images from folders. This is a quick method for clearing out unused textures created with this add-on"

    def execute(self, context):
        # Create a list of all images used within the layer stack.
        used_image_paths = []

        material_layers = context.scene.matlay_layers
        masks = context.scene.matlay_masks
        material_channel_list = material_channels.get_material_channel_list()

        for material_channel_name in material_channel_list:
            for i in range(0, len(material_layers)):
                nodes = layer_nodes.get_all_nodes_in_layer(material_channel_name, i, context, False)
                for node in nodes:
                    if node:
                        if node.bl_static_type == 'TEX_IMAGE':
                            if node.image != None and node.image.filepath != '':
                                if node.image.filepath not in used_image_paths:
                                    used_image_paths.append(node.image.filepath)
                                    print("Added image path: " + node.image.filepath)

        for i in range(0, len(material_layers)):
            for c in range(0, len(masks)):
                node = layer_masks.get_mask_node('MaskTexture', material_channel_name, i, c, False)
                if node:
                    if node.bl_static_type == 'TEX_IMAGE':
                        if node.image != None and node.image.filepath != '':
                            if node.image.filepath not in used_image_paths:
                                used_image_paths.append(node.image.filepath)
                                print("Added image path: " + node.image.filepath)


        # Delete all images in the layer / mask folder that are not linked to any layers.
        matlay_image_path = os.path.join(bpy.path.abspath("//"), "Matlay")
        layer_image_path = os.path.join(matlay_image_path, "Layers")
        mask_image_path = os.path.join(matlay_image_path, "Masks")

        folder_images = []
        if os.path.exists(layer_image_path):
            for file in os.listdir(layer_image_path):
                file_path = os.path.join(layer_image_path, file)
                folder_images.append(file_path)
                print("Added file: " + file_path)

        if os.path.exists(mask_image_path):
            for file in os.listdir(mask_image_path):
                file_path = os.path.join(mask_image_path, file)
                folder_images.append(file_path)
                print("Added file: " + file_path)
        
        for path in folder_images:
            if path not in used_image_paths:
                if os.path.exists(path):
                    os.remove(path)
                    print("Deleted unused image: " + path)

        return{'FINISHED'}

class MATLAY_OT_append_workspace(Operator):
    '''Appends a suggested layout for using this add-on.'''
    bl_idname = "matlay.append_workspace"
    bl_label = "Append Workspace"
    bl_description = "Appends a suggested workspace for using this add-on"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        workspace = bpy.data.workspaces.get('Matlay')
        if workspace:
            info_messages.popup_message_box("The default workspace already exists, manually delete it and click this operator again to re-load the workspace.", 'Info', 'INFO')
            return {'FINISHED'}


        USER = Path(resource_path('USER'))
        ADDON = "Matlay"
        BLEND_FILE = "Matlay.blend"
        source_path =  str(USER / "scripts/addons" / ADDON / "blend" / BLEND_FILE)

        blendfile = source_path
        section = "\\WorkSpace\\"
        object = "Matlay"

        filepath  = blendfile + section + object
        directory = blendfile + section
        filename  = object

        bpy.ops.wm.append(
            filepath=filepath, 
            filename=filename,
            directory=directory)

        # Set the current workspace to the appended workspace.
        bpy.context.window.workspace = bpy.data.workspaces['Matlay']

        # Reset the main pannel tab.
        context.scene.matlay_panel_properties.sections = 'SECTION_TEXTURE_SET'

        return {'FINISHED'}