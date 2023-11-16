# This file provides functions to assist with importing, saving, or editing image files / textures for this add-on.

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper        # For importing images.
from ..core import texture_set_settings as tss
from ..core import debug_logging
from ..core import blender_addon_utils
from .. import preferences
import random
import os                                           # For saving layer images.
import shutil

def get_random_image_id():
    '''Generates a random image id number.'''
    return str(random.randrange(10000,99999))

def set_image_colorspace_by_material_channel(image, material_channel_name):
    '''Correctly sets an image's colorspace based on the provided material channel.'''
    match material_channel_name:
        case 'COLOR':
            image.colorspace_settings.name = 'sRGB'

        case 'METALLIC':
            image.colorspace_settings.name = 'Non-Color'

        case 'ROUGHNESS':
            image.colorspace_settings.name = 'Non-Color'

        case 'NORMAL':
            image.colorspace_settings.name = 'Non-Color'

        case 'HEIGHT':
            image.colorspace_settings.name = 'Non-Color'
    
        case 'EMISSION':
            image.colorspace_settings.name = 'sRGB'

        case 'SCATTERING':
            image.colorspace_settings.name = 'sRGB'

def check_for_directx(filename):
    if "NormalDX" in filename or "NDX" in filename:
        return True
    else:
        return False

def save_raw_image(original_image_path, original_image_name):
    '''Saves an imported texture to a folder next to the saved blend file. This can help keep textures used in materials within the blend file in a static location next to the blend file for organizational purposes.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    if addon_preferences.save_imported_textures:

        debug_logging.log("Attempting to copy the imported texture into the raw textures folder.")

        # Create a raw textures folder if one doesn't already exist.
        raw_textures_folder_path = os.path.join(bpy.path.abspath("//"), "Raw Textures")
        if os.path.exists(raw_textures_folder_path) == False:
            os.mkdir(raw_textures_folder_path)
        
        # In some cases, the original image name may include the file extension of the image already. 
        # We'll remove this to avoid saving images with the file extension in the name.
        original_image_name_extension = os.path.splitext(original_image_name)[1]
        if original_image_name_extension:
            original_image_name = original_image_name.replace(original_image_name_extension, '')

        # Save the raw texture in a folder next to the saved blend file if it doesn't exist within that folder.
        original_file_format = os.path.splitext(original_image_path)
        destination_path = "{0}/{1}{2}".format(raw_textures_folder_path, original_image_name, original_file_format[1])
        if not os.path.exists(destination_path):
            shutil.copyfile(original_image_path, destination_path)
            debug_logging.log("Imported image copied to the raw texture folder.")
        debug_logging.log("Imported image already exists within the raw texture folder.")

class MATLAYER_OT_add_texture_node_image(Operator):
    bl_idname = "matlayer.add_texture_node_image"
    bl_label = "Add Texture Node Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates a new image (uses texture set pixel resolution) and adds it to the specified texture node"

    node_tree_name: StringProperty(default="")
    node_name: StringProperty(default="")
    material_channel_name: StringProperty(default="")

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status("Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        if self.node_name == "":
            debug_logging.log_status("Provided texture node name is blank when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if not texture_node:
            debug_logging.log_status("Can't find the specified texture node when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        # Assign the new image a random name.
        image_name = "Image_" + get_random_image_id()
        while bpy.data.images.get(image_name) != None:
            image_name = "Image_" + get_random_image_id()

        # Create a new image of the texture size defined in the texture set settings.
        addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
        image_width = tss.get_texture_width()
        image_height = tss.get_texture_height()
        new_image = blender_addon_utils.create_image(image_name, image_width, image_height, alpha_channel=True, thirty_two_bit=addon_preferences.thirty_two_bit)
    
        # If a material channel is defined, set the color space.
        if self.material_channel_name != "":
            set_image_colorspace_by_material_channel(new_image, self.material_channel_name)

        # Save the imported image to an external folder next to the blend file.
        image = bpy.data.images[image_name]
        if image:
            blender_addon_utils.save_image(image, file_format='PNG', type='RAW_TEXTURE', colorspace='sRGB')

        texture_node.image = new_image                                              # Add the new image to the image node.
        bpy.context.scene.tool_settings.image_paint.canvas = texture_node.image     # Select the new texture for painting.
        
        return {'FINISHED'}

class MATLAYER_OT_import_texture_node_image(Operator, ImportHelper):
    bl_idname = "matlayer.import_texture_node_image"
    bl_label = "Import Texture"
    bl_description = "Opens a menu that allows the user to import a texture file into the specified texture node"
    bl_options = {'REGISTER', 'UNDO'}

    node_tree_name: StringProperty(default="")
    node_name: StringProperty(default="")
    material_channel_name: StringProperty(default="")

    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp;*.exr',
        options={'HIDDEN'}
    )

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status("Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        if self.node_name == "":
            debug_logging.log_status("Provided texture node name is blank when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if not texture_node:
            debug_logging.log_status("Can't find the specified texture node when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        # Open a window to import an image into blender.
        head_tail = os.path.split(self.filepath)
        image_name = head_tail[1]

        # Delete images with the same name if they exist.
        image = bpy.data.images.get(image_name)
        if image:
            debug_logging.log("Removed " + image.name)
            bpy.data.images.remove(image)
            
        bpy.ops.image.open(filepath=self.filepath)
        image = bpy.data.images[image_name]
        texture_node.image = image
                
        # If a material channel is defined, set the color space.
        if self.material_channel_name != "":
            set_image_colorspace_by_material_channel(image, self.material_channel_name)

        # Print a warning about using DirectX normal maps for users if it's detected they are using one.
        if check_for_directx(image_name) and self.material_channel_name == 'NORMAL':
            debug_logging.log_status("You may have imported a DirectX normal map which will cause your imported normal map to appear inverted.", self, type='WARNING')

        # Copy the imported image to a folder next to the blend file (if save imported textures is on in the settings).
        save_raw_image(self.filepath, image.name)
        return {'FINISHED'}

class MATLAYER_OT_edit_texture_node_image_externally(Operator):
    bl_idname = "matlayer.edit_texture_node_image_externally"
    bl_label = "Edit Image Externally"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Exports the specified material channel image to the external image editing software defined in Blenders preferences"

    node_tree_name: StringProperty(default="")
    node_name: StringProperty(default="")

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status("Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        if self.node_name == "":
            debug_logging.log_status("Provided texture node name is blank when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if not texture_node:
            debug_logging.log_status("Can't find the specified texture node when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        # Save the image if it needs saving.
        if texture_node.image.is_dirty:
            texture_node.image.save()

        # Select and then export the image to the external image editing software.
        context.scene.tool_settings.image_paint.canvas = texture_node.image
        bpy.ops.image.external_edit(filepath=texture_node.image.filepath)

        return {'FINISHED'}

class MATLAY_OT_export_uvs(Operator):
    bl_idname = "matlayer.export_uvs"
    bl_label = "Export UVs"
    bl_description = "Exports the selected object's UV layout to a folder next to the blend file"

    def execute(self, context):
        blender_addon_utils.set_valid_material_editing_mode()
        blender_addon_utils.verify_material_operation_context(self)

        original_mode = bpy.context.object.mode
        active_object = bpy.context.active_object

        if active_object.data.uv_layers.active == None:
            self.report({'ERROR'}, "Active object has no active UV layout to export UVs for. Add one, or select a different object.")
            return{'FINISHED'}

        # Set edit mode and select all uvs.
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.uv.select_all(action='SELECT')

        # Save UV layout to a folder.
        uv_image_name = bpy.context.active_object.name + "_" + "UVLayout"
        uv_layout_path = blender_addon_utils.get_layer_image_path(uv_image_name, 'PNG')
        bpy.ops.uv.export_layout(filepath=uv_layout_path, size=(tss.get_texture_width(), tss.get_texture_height()))

        # Reset mode and log completion.
        bpy.ops.object.mode_set(mode = original_mode)
        debug_logging.log_status("Exporting UV Layout complete - {0}".format(uv_layout_path), self, type='INFO')

        return{'FINISHED'}

class MATLAY_OT_image_edit_uvs(Operator):
    bl_idname = "matlayer.image_edit_uvs"
    bl_label = "Image Edit UVs"
    bl_description = "Exports the selected object's UV layout to the image editor defined in Blender's preferences (Edit -> Preferences -> File Paths -> Applications -> Image Editor)"

    def execute(self, context):
        blender_addon_utils.set_valid_material_editing_mode()
        blender_addon_utils.verify_material_operation_context(self)

        original_mode = bpy.context.object.mode
        active_object = bpy.context.active_object

        if active_object.data.uv_layers.active == None:
            self.report({'ERROR'}, "Active object has no active UV layout to export UVs for. Add one, or select a different object.")
            return{'FINISHED'}

        # Set edit mode and select all uvs.
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.uv.select_all(action='SELECT')

        # Save UV layout to a folder.
        uv_image_name = bpy.context.active_object.name + "_" + "UVLayout"
        uv_layout_path = blender_addon_utils.get_layer_image_path(uv_image_name, 'PNG')
        bpy.ops.uv.export_layout(filepath=uv_layout_path, size=(tss.get_texture_width(), tss.get_texture_height()))

        # Load the UV layout into Blender's data so it can be exported directly from Blender.
        uv_image = bpy.data.images.get(uv_image_name + ".png")
        if uv_image:
            bpy.data.images.remove(uv_image)
        uv_layout_image = bpy.data.images.load(uv_layout_path)

        # Select and export UV layout.
        context.scene.tool_settings.image_paint.canvas = uv_layout_image
        bpy.ops.image.external_edit(filepath=uv_layout_image.filepath)

        # Reset mode.
        bpy.ops.object.mode_set(mode = original_mode)
        
        return{'FINISHED'}

class MATLAYER_OT_reload_texture_node_image(Operator):
    bl_idname = "matlayer.reload_texture_node_image"
    bl_label = "Reload Texture Node Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Reloads the texture node image from it's associated saved file"

    node_tree_name: StringProperty(default="")
    node_name: StringProperty(default="")

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status("Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        if self.node_name == "":
            debug_logging.log_status("Provided texture node name is blank when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if not texture_node:
            debug_logging.log_status("Can't find the specified texture node when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        # Select and then reload the image in the texture node.
        if texture_node.image:
            context.scene.tool_settings.image_paint.canvas = texture_node.image
            bpy.ops.image.reload()
            debug_logging.log_status("Reloaded {0}.".format(texture_node.image.name), self, type='INFO')
        return {'FINISHED'}

class MATLAYER_OT_delete_texture_node_image(Operator):
    bl_idname = "matlayer.delete_texture_node_image"
    bl_label = "Delete Texture Node Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the texture image stored in the texture node from blenders data, and it's saved file on disk if one exists"

    node_tree_name: StringProperty(default="")
    node_name: StringProperty(default="")

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status("Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        if self.node_name == "":
            debug_logging.log_status("Provided texture node name is blank when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if not texture_node:
            debug_logging.log_status("Can't find the specified texture node when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        # Delete the image in the texture node from the blend data if one exists.
        if texture_node.image:
            image_name = texture_node.image.name
            bpy.data.images.remove(texture_node.image)
            debug_logging.log_status("Deleted " + image_name, self, type='INFO')
        else:
            debug_logging.log_status("No image to delete.", self, type='INFO')

        return {'FINISHED'}