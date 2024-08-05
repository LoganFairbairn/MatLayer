# This file contains settings and functions the users texture set.

import os
import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import BoolProperty, StringProperty, EnumProperty
from ..core import blender_addon_utils as bau
from ..core import material_layers
from ..core import debug_logging

# Available texture resolutions for texture sets.
TEXTURE_SET_RESOLUTIONS = [
    ("THIRTY_TWO", "32", ""),
    ("SIXTY_FOUR", "64", ""),
    ("ONE_TWENTY_EIGHT", "128", ""),
    ("TWO_FIFTY_SIX", "256", ""),
    ("FIVE_TWELVE", "512", ""),
    ("ONE_K", "1024", ""),
    ("TWO_K", "2048", ""),
    ("FOUR_K", "4096", "")
]

def update_match_image_resolution(self, context):
    texture_set_settings = context.scene.matlayer_texture_set_settings
    if texture_set_settings.match_image_resolution:
        texture_set_settings.image_height = texture_set_settings.image_width

def update_image_width(self, context):
    texture_set_settings = context.scene.matlayer_texture_set_settings
    if texture_set_settings.match_image_resolution:
        if texture_set_settings.image_height != texture_set_settings.image_width:
            texture_set_settings.image_height = texture_set_settings.image_width

#----------------------------- UPDATE GLOBAL MATERIAL CHANNEL TOGGLES (mute / unmute material channels for ALL layers) -----------------------------#

def get_texture_width():
    '''Returns a numeric value based on the enum for texture width.'''
    match bpy.context.scene.matlayer_texture_set_settings.image_width:
        case 'THIRTY_TWO':
            return 32
        case 'SIXTY_FOUR':
            return 64
        case 'ONE_TWENTY_EIGHT':
            return 128
        case 'TWO_FIFTY_SIX':
            return 256
        case 'FIVE_TWELVE':
            return 512
        case 'ONE_K':
            return 1024
        case 'TWO_K':
            return 2048
        case 'FOUR_K':
            return 4096
        case _:
            return 10

def get_texture_height():
    '''Returns a numeric value based on the enum for texture height.'''
    match bpy.context.scene.matlayer_texture_set_settings.image_height:
        case 'THIRTY_TWO':
            return 32
        case 'SIXTY_FOUR':
            return 64
        case 'ONE_TWENTY_EIGHT':
            return 128
        case 'TWO_FIFTY_SIX':
            return 256
        case 'FIVE_TWELVE':
            return 512
        case 'ONE_K':
            return 1024
        case 'TWO_K':
            return 2048
        case 'FOUR_K':
            return 4096
        case _:
            return 10

def get_material_channel_active(channel_name):
    '''Returns if the material channel is active in the active materials texture set.'''

    # Return false if there is no active object.
    active_object = bpy.context.active_object
    if not active_object:
        return False
    
    # Return false if there is no active material.
    active_material = active_object.active_material
    if not active_material:
        return False

    # If the channel toggle node doesn't exist, or is muted, the channel isn't active.
    static_channel_name = bau.format_static_channel_name(channel_name)
    channel_toggle_node_name = "GLOBAL_{0}_TOGGLE".format(static_channel_name)
    channel_toggle_node = active_material.node_tree.nodes.get(channel_toggle_node_name)
    if channel_toggle_node:
        if channel_toggle_node.mute:
            return False
    
    # If the channel toggle node exists, and isn't muted, return true.
    else:
        return True

class MATLAYER_texture_set_settings(PropertyGroup):
    image_width: EnumProperty(
        items=TEXTURE_SET_RESOLUTIONS, 
        name="Image Width", 
        description="Image width in pixels for all images created with this add-on. Changing this value during through creating a material could result in the pixel resolution between textures used in the material not matching, which will cause exported textures to be blurry", 
        default='TWO_K', 
        update=update_image_width
    )

    image_height: EnumProperty(
        items=TEXTURE_SET_RESOLUTIONS, 
        name="Image Height", 
        description="Image height in pixels for all images created with this add-on. Changing this value during through creating a material could result in the pixel resolution between textures used in the material not matching, which will cause exported textures to be blurry", 
        default='TWO_K'
    )

    layer_folder: StringProperty(default="", description="Path to folder location where layer images are saved", name="Image Layer Folder Path")
    match_image_resolution: BoolProperty(name="Match Image Resolution", description="When toggled on, the image width and height will be matched", default=True, update=update_match_image_resolution)

class MATLAYER_OT_toggle_texture_set_material_channel(Operator):
    bl_idname = "matlayer.toggle_texture_set_material_channel"
    bl_label = "Toggle Texture Set Material Channel"
    bl_description = "Toggles the specified material channel on / off for the active materials texture set"
    bl_options = {'REGISTER', 'UNDO'}

    material_channel_name: StringProperty(default='COLOR', name="Material Channel Name")

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bau.verify_material_operation_context(self)
        active_material = bpy.context.active_object.active_material

        # Get the channel toggle node from the material using the formatted name.
        formatted_channel_name = self.material_channel_name.replace(' ', '-')
        formatted_channel_name = formatted_channel_name.upper()
        channel_toggle_node = active_material.node_tree.nodes.get("GLOBAL_{0}_TOGGLE".format(formatted_channel_name))

        # Toggle material channel on.
        if channel_toggle_node:
            if channel_toggle_node.mute:
                channel_toggle_node.mute = False

                # Connect the last active layer node for the toggled material channel to the principled bsdf.
                total_layers = material_layers.count_layers(active_material)
                for i in range(total_layers, 0, -1):
                    layer_node = material_layers.get_material_layer_node('LAYER', i - 1)
                    if bau.get_node_active(layer_node):
                        channel_name = self.material_channel_name
                        shader_node = active_material.node_tree.nodes.get('MATLAYER_SHADER')
                        bau.safe_node_link(
                            layer_node.outputs.get(channel_name),
                            shader_node.inputs.get(channel_name),
                            active_material.node_tree
                        )
                        break

                # Toggle on alpha clip to allow transparency.
                if self.material_channel_name == 'ALPHA':
                    active_material.blend_method = 'CLIP'

                # Toggle on displacement in the material settings.
                if self.material_channel_name == 'DISPLACEMENT':
                    active_material.cycles.displacement_method = 'BOTH'
            
            # Toggle material channel off.
            else:
                channel_toggle_node.mute = True
                disconnect_node = active_material.node_tree.nodes.get('MATLAYER_SHADER')
                channel_name = self.material_channel_name
                disconnect_socket = disconnect_node.inputs.get(channel_name)

                # Disconnect the toggled material channel from the principled bsdf.
                if disconnect_socket:
                    for link in disconnect_socket.links:
                        active_material.node_tree.links.remove(link)

                # Toggle off alpha clip for better shader performance when the channel isn't being used.
                if self.material_channel_name == 'ALPHA':
                    active_material.blend_method = 'OPAQUE'

                # Toggle off displacement in the material settings.
                if self.material_channel_name == 'DISPLACEMENT':
                    active_material.cycles.displacement_method = 'BUMP'

        return {'FINISHED'}

class MATLAYER_OT_set_raw_texture_folder(Operator):
    bl_idname = "matlayer.set_raw_texture_folder"
    bl_label = "Set Raw Texture Folder Path"
    bl_description = "Opens a file explorer to select the folder path where raw textures are externally saved. A raw texture is any image used in the material editing process inside this add-on that isn't a texture being exported"
    bl_options = {'REGISTER'}

    directory: StringProperty()

    # Filters for only folders.
    filter_folder: BoolProperty(
        default=True,
        options={"HIDDEN"}
    )

    def execute(self, context):
        if not os.path.isdir(self.directory):
            debug_logging.log_status("Invalid directory.", self, type='INFO')
        else:
            context.scene.matlayer_raw_textures_folder = self.directory
            debug_logging.log_status("Raw texture folder set to: {0}".format(self.directory), self, type='INFO')
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class MATLAYER_OT_open_raw_texture_folder(Operator):
    bl_idname = "matlayer.open_raw_texture_folder"
    bl_label = "Open Raw Texture Folder"
    bl_description = "Opens the folder in your systems file explorer where raw textures will be saved. Raw textures are considered any image that's used in the material editing process, that's not a mesh map, or a completed texture being exported"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        raw_texture_folder_path = blender_addon_utils.get_texture_folder_path(folder='RAW_TEXTURES')
        blender_addon_utils.open_folder(raw_texture_folder_path, self)
        return {'FINISHED'}