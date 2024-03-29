# This file contains properties and functions for editing shader nodes used for lighting calculations in materials created with this add-on.

import bpy
from bpy.utils import resource_path
from bpy.types import PropertyGroup, Operator
from bpy.props import BoolProperty, StringProperty, CollectionProperty, EnumProperty, FloatProperty, FloatVectorProperty
import json
from pathlib import Path
from ..core import debug_logging
from .. import preferences

LAYER_BLEND_MODES = [
    ('MIX', "Mix", ""),
    ('DARKEN', "Darken", ""),
    ('MULTIPLY', "Multiply", ""),
    ('BURN', "Burn", ""),
    ('LIGHTEN', "Lighten", ""),
    ('SCREEN', "Screen", ""),
    ('DODGE', "Dodge", ""),
    ('ADD', "Add", ""),
    ('OVERLAY', "Overlay", ""),
    ('SOFT_LIGHT', "Soft Light", ""),
    ('LINEAR_LIGHT', "Linear Light", ""),
    ('DIFFERENCE', "Difference", ""),
    ('EXCLUSION', "Exclusion", ""),
    ('SUBTRACT', "Subtract", ""),
    ('DIVIDE', "Divide", ""),
    ('HUE', "Hue", ""),
    ('SATURATION', "Saturation", ""),
    ('COLOR', "Color", ""),
    ('VALUE', "Value", ""),
    ('NORMAL_MAP_COMBINE', "Normal Map Combine", ""),
    ('NORMAL_MAP_DETAIL', "Normal Map Detail", "")
]

# Valid node socket types for shader channels defined for this add-on.
NODE_SOCKET_TYPES = [
    ("NodeSocketFloat", "Float", "Channel contains greyscale (0 - 1) data."),
    ("NodeSocketColor", "Color", "Channel contains RGBA data."),
    ("NodeSocketVector", "Vector", "Channel contains vector data."),
    #("NodeSocketShader", "Shader", "Channel contains shader data.")
]

# Valid node socket subtypes for shader channels defined for this add-on.
NODE_SOCKET_SUBTYPES = [
    ("NONE", "None", "No socket subtype."),
    ("FACTOR", "Factor", "Define the socket property as a factor (makes the property a slider in the interface).")
]

DEFAULT_CHANNEL_FILTERS = [
    ("COLOR", "Color", "Default filter group node designed for fitlering RGBA channels."),
    ("GREYSCALE", "Greyscale", "Default filter group node designed for filtering greyscale channels."),
    ("NORMAL", "Normal", "Default normal filter group node designed for filtering normal channels.")
]

def update_shader_list():
    '''Updates a list of all available shaders for this add-on that are defined in json data.'''
    templates_path = str(Path(resource_path('USER')) / "scripts/addons" / preferences.ADDON_NAME / "json_data" / "shader_info.json")
    json_file = open(templates_path, "r")
    jdata = json.load(json_file)
    json_file.close()
    shaders = jdata['shaders']
    matlayer_shader_list = bpy.context.scene.matlayer_shader_list
    matlayer_shader_list.clear()
    for shader in shaders:
        shader_name = matlayer_shader_list.add()
        shader_name.name = shader['group_node_name']
    debug_logging.log("Updated shader list.")

def set_shader(shader_name):
    '''Sets the shader that will be used in materials created with this add-on.'''

    # Update the list of shaders that are defined in the shader info json file.
    update_shader_list()

    matlayer_shader_list = bpy.context.scene.matlayer_shader_list
    shader_info = bpy.context.scene.matlayer_shader_info

    templates_path = str(Path(resource_path('USER')) / "scripts/addons" / preferences.ADDON_NAME / "json_data" / "shader_info.json")
    json_file = open(templates_path, "r")
    jdata = json.load(json_file)
    json_file.close()
    shaders = jdata['shaders']

    # Set the shader by caching it's info from the json file into Blender's memory.
    shader_exists = False
    for i, shader in enumerate(matlayer_shader_list):
        if shader['name'] == shader_name:
            shader_exists = True
            shader_info.group_node_name = shaders[i]['group_node_name']

            shader_material_channels = shaders[i]['shader_material_channels']
            shader_info.material_channels.clear()
            for shader_material_channel in shader_material_channels:
                channel = shader_info.material_channels.add()
                channel.name = shader_material_channel['name']
                channel.default_active = shader_material_channel['default_active']
                channel.socket_type = shader_material_channel['socket_type']
                channel.socket_subtype = shader_material_channel['socket_subtype']
                channel.default_blend_mode = shader_material_channel['default_blend_mode']

                match channel.socket_type:
                    case 'NodeSocketFloat':
                        channel.socket_float_default = shader_material_channel['socket_default']
                        channel.socket_float_min = shader_material_channel['socket_min']
                        channel.socket_float_max = shader_material_channel['socket_max']
                    case 'NodeSocketColor':
                        channel.socket_color_default = shader_material_channel['socket_default']
                    case 'NodeSocketVector':
                        channel.socket_vector_default = shader_material_channel['socket_default']

            shader_info.global_properties.clear()
            global_properties = shaders[i]['global_properties']
            for property in global_properties:
                global_property = shader_info.global_properties.add()
                global_property.name = property

    # TODO: If the shader wasn't found, apply a default shader instead.
    if not shader_exists:
        debug_logging.log("Shader {0} doesn't exist, applying default shader.".format(shader_name))

    # Set the default channel of the shader to be the first defined channel.
    if len(shader_info.material_channels) > 0:
        bpy.context.scene.matlayer_layer_stack.selected_material_channel = shader_info.material_channels[0].name

class MATLAYER_shader_name(PropertyGroup):
    '''Shader name'''
    name: StringProperty()

class MATLAYER_shader_material_channel(PropertyGroup):
    '''Properties for a shader material channel.'''
    default_active: BoolProperty(
        default=True,
        name="Default Active",
        description="Defines if the shader channel is active by default"
    )
    name: StringProperty(
        name="Shader Channel Name",
        description="The name of the shader channel. The channel name should match an input socket in the defined shader group node.",
        default="New Shader Channel"
    )
    socket_type: EnumProperty(
        name="Shader Channel Type",
        description="Defines the data type for the shader channel",
        items=NODE_SOCKET_TYPES, 
        default='NodeSocketColor'
    )
    socket_subtype: EnumProperty(
        name="Shader Channel Subtype",
        description="Defines the subtype for the shader channel",
        items=NODE_SOCKET_SUBTYPES, 
        default='NONE'
    )
    socket_float_default: FloatProperty(
        name="Channel Float Default",
        description="Defines the default value for the shader channel",
        default=0.0
    )
    socket_float_min: FloatProperty(
        name="Channel Float Min",
        description="Defines the minimum value for the float shader channel",
        default=0.0
    )
    socket_float_max: FloatProperty(
        name="Channel Float Max",
        description="The maximum value for the float shader channel",
        default=1.0
    )
    socket_color_default: FloatVectorProperty(
        name="Channel Color Default",
        description="The shader channels default color value",
        subtype='COLOR',
        default=[0.0, 0.0, 0.0]
    )
    socket_vector_default: FloatVectorProperty(
        name="Channel Vector Default",
        description="The shader channels default vector value",
        default=[0.0, 0.0, 0.0]
    )
    default_blend_mode: EnumProperty(
        name="Default Blend Mode",
        description="The default blend mode for the shader channel",
        default='MIX',
        items=LAYER_BLEND_MODES
    )

class MATLAYER_shader_global_property(PropertyGroup):
    '''Global property for a shader.'''
    name: StringProperty(
        default='New Global Shader Property'
    )

class MATLAYER_shader_info(PropertyGroup):
    name: StringProperty(
        name="Shader Name",
        description="The name of the shader",
        default="ERROR"
    )
    author: StringProperty(
        name="Shader Author",
        description="Defines who created the shader",
        default=""
    )
    description: StringProperty(
        name="Shader Description",
        description="Provides a description of what the shader does, and is used for",
        default=""
    )
    group_node_name: StringProperty(
        name="Shader Group Node Name",
        description="The name of the group node for this shader. The group node must exist in this blend file, or in the add-ons asset blend file",
        default=""
    )
    material_channels: CollectionProperty(type=MATLAYER_shader_material_channel)
    global_properties: CollectionProperty(type=MATLAYER_shader_global_property)

class MATLAYER_OT_set_shader(Operator):
    bl_idname = "matlayer.set_shader"
    bl_label = "Set Shader"
    bl_description = "Reads json shader info data to apply the shader node to use for material lighting calculations when materials are edited with this add-on"
    bl_options = {'REGISTER', 'UNDO'}

    shader_name: StringProperty(default='ERROR')

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        set_shader(self.shader_name)
        return {'FINISHED'}

class MATLAYER_OT_save_shader(Operator):
    bl_idname = "matlayer.save_shader"
    bl_label = "Save Shader"
    bl_description = "Saves the shader to json data. If the shader group node already exists in json data, the shader data will be overwritten"

    shader_name: StringProperty(default='ERROR')

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}
    
class MATLAYER_OT_delete_shader(Operator):
    bl_idname = "matlayer.delete_shader"
    bl_label = "Delete Shader"
    bl_description = "Deletes the shader from json data"

    shader_name: StringProperty(default='ERROR')

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}
    
class MATLAYER_OT_add_shader_channel(Operator):
    bl_idname = "matlayer.add_shader_channel"
    bl_label = "Add Shader Channel"
    bl_description = "Adds a shader channel to the shader info"

    def execute(self, context):
        shader_info = bpy.context.scene.matlayer_shader_info
        shader_info.material_channels.add()
        bpy.context.scene.matlayer_selected_shader_index = len(shader_info.material_channels) - 1
        return {'FINISHED'}
    
class MATLAYER_OT_delete_shader_channel(Operator):
    bl_idname = "matlayer.delete_shader_channel"
    bl_label = "Delete Shader Channel"
    bl_description = "Deletes a shader channel from the shader info"

    def execute(self, context):
        shader_info = bpy.context.scene.matlayer_shader_info
        selected_shader_index = bpy.context.scene.matlayer_selected_shader_index
        shader_info.material_channels.remove(selected_shader_index)
        bpy.context.scene.matlayer_selected_shader_index = min(max(0, selected_shader_index - 1), len(shader_info.material_channels) - 1)
        return {'FINISHED'}
    
class MATLAYER_OT_add_global_shader_property(Operator):
    bl_idname = "matlayer.add_global_shader_property"
    bl_label = "Add Global Shader Property"
    bl_description = "Adds a global shader property to the shader info"

    def execute(self, context):
        shader_info = bpy.context.scene.matlayer_shader_info
        shader_info.global_properties.add()
        bpy.context.scene.matlayer_selected_global_shader_property_index = len(shader_info.global_properties) - 1
        return {'FINISHED'}
    
class MATLAYER_OT_delete_global_shader_property(Operator):
    bl_idname = "matlayer.delete_global_shader_property"
    bl_label = "Delete Global Shader Property"
    bl_description = "Deletes a global shader property to the shader info"

    def execute(self, context):
        shader_info = bpy.context.scene.matlayer_shader_info
        selected_global_shader_property_index = bpy.context.scene.matlayer_selected_global_shader_property_index
        shader_info.global_properties.remove(selected_global_shader_property_index)
        bpy.context.scene.matlayer_selected_global_shader_property_index = min(max(0, selected_global_shader_property_index - 1), len(shader_info.global_properties) - 1)
        return {'FINISHED'}