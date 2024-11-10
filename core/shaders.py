# This file contains properties and functions for editing shader nodes used for lighting calculations in materials created with this add-on.

import bpy
import os
import json
import copy
from bpy.utils import resource_path
from bpy.types import PropertyGroup, Operator
from bpy.props import BoolProperty, StringProperty, CollectionProperty, EnumProperty, FloatProperty, FloatVectorProperty, PointerProperty
import json
from pathlib import Path
from ..core import debug_logging
from ..core import blender_addon_utils as bau
from ..core import export_textures
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
]

# Valid float node socket subtypes for shader channels defined for this add-on.
NODE_SOCKET_FLOAT_SUBTYPES = [
    ("PERCENTAGE", "Percentage", ""),
    ("FACTOR", "Factor", "Define the socket property as a factor (makes the property a slider in the interface)."),
    ("ANGLE", "Angle", "Angle"),
    ("TIME", "Time", ""),
    ("DISTANCE", "Distance", "Distance")
]

# Valid vector node socket subtypes for shader channels defined for this add-on.
NODE_SOCKET_VECTOR_SUBTYPES = [
    ("TRANSLATION", "Translation", "Translation"),
    ("DIRECTION", "Direction", "Direction"),
    ("VELOCITY", "Velocity", "Velocity"),
    ("ACCELERATION", "Acceleration", "Acceleration"),
    ("EULER_ANGLE", "Euler Angles", "Euler Angles"),
    ("XYZ", "XYZ", "XYZ")
]

# Internal backup template for the shader json file.
DEFAULT_SHADER_JSON = {
    "shaders": [
        {
            "group_node_name": "PrincipledBSDF",
            "material_channels": [
                {
                    "name": "Color",
                    "default_active": True,
                    "socket_type": "NodeSocketColor",
                    "socket_subtype": "NONE",
                    "socket_default": [0, 0, 0],
                    "socket_min": 0,
                    "socket_max": 1,
                    "default_blend_mode": "MIX"
                }
            ],
            "unlayered_properties": [
                "Emission Strength"
            ]
        }
    ]
}

def update_shader_list():
    '''Updates a list of all available shaders for this add-on that are defined in json data.'''
    shader_info_path = str(Path(resource_path('USER')) / "scripts/addons" / preferences.ADDON_NAME / "json_data" / "shader_info.json")
    json_file = open(shader_info_path, "r")
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
    update_shader_list()
    matlayer_shader_list = bpy.context.scene.matlayer_shader_list
    shader_info = bpy.context.scene.matlayer_shader_info

    # Read shader JSON data into memory.
    templates_path = str(Path(resource_path('USER')) / "scripts/addons" / preferences.ADDON_NAME / "json_data" / "shader_info.json")
    json_file = open(templates_path, "r")
    jdata = json.load(json_file)
    json_file.close()
    shaders = jdata['shaders']

    # Reset the selected shader channel index.
    bpy.context.scene.matlayer_shader_channel_index = 0

    # Set the shader by caching json info into Blender's memory.
    shader_exists = False
    for i, shader in enumerate(matlayer_shader_list):
        if shader['name'] == shader_name:
            shader_exists = True

            # Ensure the defined shader group node is in the blend file.
            shader_nodegroup_name = shaders[i]['group_node_name']
            shader_node_group = bpy.data.node_groups.get(shader_nodegroup_name)
            if shader_node_group:
                shader_info.shader_node_group = shader_node_group
            
            # If the shader node group isn't in the blend file already, attempt to append it from the add-on assets file.
            else:
                shader_node_group = bau.append_group_node(shader_nodegroup_name)
                if shader_node_group:
                    debug_logging.log("Shader node group successfully appended from add-on asset file.")
                    shader_info.shader_node_group = shader_node_group
                else:
                    debug_logging.log("Shader nodetree does not exist and cannot be appended from the add-on assets file.")
                    return
            
            # Set shader info to info from the json data.
            shader_info.group_node_name = shaders[i]['group_node_name']
            shader_material_channels = shaders[i]['material_channels']
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
                        channel.socket_float_min = 0
                        channel.socket_float_max = 1
                    case 'NodeSocketVector':
                        channel.socket_vector_default = shader_material_channel['socket_default']
                        channel.socket_float_min = 0
                        channel.socket_float_max = 1

            shader_info.unlayered_properties.clear()
            unlayered_properties = shaders[i]['unlayered_properties']
            for property in unlayered_properties:
                unlayered_property = shader_info.unlayered_properties.add()
                unlayered_property.name = property

    # Reload the export template to avoid invalid pack texture enums in the export texture settings.
    if shader_exists:
        texture_export_settings = bpy.context.scene.matlayer_texture_export_settings
        export_textures.set_export_template(texture_export_settings.export_template_name)

    # If the shader wasn't found, log an error.
    if not shader_exists:
        debug_logging.log(
            "Shader {0} doesn't exist.".format(shader_name), 
            message_type='ERROR', 
            sub_process=False
        )

    # Set the default selected material channel to be the first defined channel.
    if len(shader_info.material_channels) > 0:
        bpy.context.scene.matlayer_layer_stack.selected_material_channel = shader_info.material_channels[0].name

def read_json_shader_data():
    '''Reads json shader data. Creates a json file if one does not exist.'''
    # Read shader info json data, and ensure the shader info json file exists.
    shader_info_path = str(Path(resource_path('USER')) / "scripts/addons" / preferences.ADDON_NAME / "json_data" / "shader_info.json")
    if os.path.exists(shader_info_path):        
        json_file = open(shader_info_path, "r")
        jdata = json.load(json_file)
        json_file.close()
    
    # If the shader info json file doesn't exist, create a new one.
    else:
        with open(shader_info_path, "w") as f:
            json.dump(DEFAULT_SHADER_JSON, f)

    return jdata

def write_json_shader_data(json_data):
    '''Writes the provided json data to the shader json data file.'''
    shader_info_path = str(Path(resource_path('USER')) / "scripts/addons" / preferences.ADDON_NAME / "json_data" / "shader_info.json")
    json_file = open(shader_info_path, "w")
    json.dump(json_data, json_file)
    json_file.close()

def verify_shader_node_group(self):
    '''Returns true if the shader node group exists within the current blend file.'''
    shader_info = bpy.context.scene.matlayer_shader_info
    if shader_info.shader_node_group:
        debug_logging.log("Shader node group is valid.")
        return True
    else:
        debug_logging.log_status("Invalid shader node group. Set the shader node in the shader tab.", self, type='ERROR')
        return False

def validate_active_shader(active_material):
    '''Checks the shader group node name exists within the cached shader list read from json data.'''
    if active_material:
        shader_node = active_material.node_tree.nodes.get('SHADER_NODE')
        if shader_node:
            shader_list = bpy.context.scene.matlayer_shader_list
            shader_group_node_name = shader_node.node_tree.name

            if shader_group_node_name in shader_list:
                return True
    return False

def read_shader(active_material):
    '''Reads the active material for a valid material / shader setup created with this add-on.'''
    # Check to see if the shader node in the active material contains a valid shader group node.
    shader_node = active_material.node_tree.nodes.get('SHADER_NODE')
    if shader_node:
        shader_list = bpy.context.scene.matlayer_shader_list
        shader_group_node_name = shader_node.node_tree.name

        # If the active material contains a valid shader group node, set that as the shader.
        if shader_group_node_name in shader_list:
            set_shader(shader_group_node_name)
            debug_logging.log(
                "Shader properties updated to match the valid active material shader.", 
                message_type='INFO',
                sub_process=True
            )

def get_static_shader_channel_list():
    '''Returns a list of shader channel name using static formatting.'''
    shader_info = bpy.context.scene.matlayer_shader_info
    static_channel_list = []

    # Add a static channel name for all material channels.
    for channel in shader_info.material_channels:
        channel_name = bau.format_static_matchannel_name(channel.name)
        static_channel_list.append(channel_name)

    return static_channel_list

def get_shader_channel_socket_name(static_material_channel_name):
    '''Returns the shader channel socket name when provided with a static material channel name.'''
    search_channel_name = bau.format_static_matchannel_name(static_material_channel_name)
    shader_info = bpy.context.scene.matlayer_shader_info
    for channel in shader_info.material_channels:
        static_channel_name = bau.format_static_matchannel_name(channel.name)
        if search_channel_name == static_channel_name:
            return channel.name
    
    # Return an error for material channel sockets that don't exist.
    debug_logging.log("Invalid material channel socket name: {0}".format(static_material_channel_name), message_type='ERROR')
    return ""

def get_socket_subtype_enums(scene=None, context=None):
    '''Returns a list of valid socket subtypes in Blender enum format for the selected shader channel.'''
    items = []

    # Add a 'NONE' option for when a node socket subtype isn't defined.
    items += [("NONE", "None", "None")]

    # Return an enum list of either float or vector node socket subtypes based on main node socket type.
    selected_shader_channel_index = bpy.context.scene.matlayer_shader_channel_index
    shader_info = bpy.context.scene.matlayer_shader_info
    selected_shader_channel = shader_info.material_channels[selected_shader_channel_index]
    if selected_shader_channel:
        match selected_shader_channel.socket_type:
            case 'NodeSocketFloat':
                return items + NODE_SOCKET_FLOAT_SUBTYPES
            case 'NodeSocketVector':
                return items + NODE_SOCKET_VECTOR_SUBTYPES

    # If a shader channel isn't selected, return all possible enum values to avoid an error.
    return items + NODE_SOCKET_FLOAT_SUBTYPES + NODE_SOCKET_VECTOR_SUBTYPES

def apply_default_shader():
    '''Applies default shader settings.'''

    # This function doesn't load from JSON file data because it's a constant backup shader setup
    # in the case the user JSON data is missing or damaged.

    shader_info = bpy.context.scene.matlayer_shader_info

    # Ensure the default shader group node is in the blend file.
    shader_nodegroup_name = "MetallicRoughnessPBR"
    shader_node_group = bpy.data.node_groups.get(shader_nodegroup_name)
    if shader_node_group:
        shader_info.shader_node_group = shader_node_group
    
    # If the default shader node group isn't in the blend file already, attempt to append it from the add-on assets file.
    else:
        shader_node_group = bau.append_group_node(shader_nodegroup_name)
        if shader_node_group:
            debug_logging.log("Shader node group successfully appended from add-on asset file.")
            shader_info.shader_node_group = shader_node_group
        else:
            debug_logging.log("Shader nodetree does not exist and cannot be appended from the add-on assets file.")
            return

    shader_info.group_node_name = "MetallicRoughnessPBR"

    # Reset the selected shader channel index.
    bpy.context.scene.matlayer_shader_channel_index = 0

    # Set default material channels.
    shader_info.material_channels.clear()
    channel = shader_info.material_channels.add()
    channel.name = "Base Color"
    channel.default_active = True
    channel.socket_type = "NodeSocketColor"
    channel.socket_color_default = [0, 0.3, 1]
    channel.socket_float_min = 0
    channel.socket_float_max = 1
    channel.default_blend_mode = "MIX"

    channel = shader_info.material_channels.add()
    channel.name = "Metallic"
    channel.default_active = False
    channel.socket_type = "NodeSocketFloat"
    channel.socket_subtype = "FACTOR"
    channel.socket_float_default = 0
    channel.socket_float_min = 0
    channel.socket_float_max = 1
    channel.default_blend_mode = "MIX"

    channel = shader_info.material_channels.add()
    channel.name = "Roughness"
    channel.default_active = False
    channel.socket_type = "NodeSocketFloat"
    channel.socket_subtype = "FACTOR"
    channel.socket_float_default = 0.5
    channel.socket_float_min = 0
    channel.socket_float_max = 1
    channel.default_blend_mode = "MIX"

    channel = shader_info.material_channels.add()
    channel.name = "Alpha"
    channel.default_active = False
    channel.socket_type = "NodeSocketFloat"
    channel.socket_subtype = "FACTOR"
    channel.socket_float_default = 1
    channel.socket_float_min = 0
    channel.socket_float_max = 1
    channel.default_blend_mode = "MIX"

    channel = shader_info.material_channels.add()
    channel.name = "Normal"
    channel.default_active = False
    channel.socket_type = "NodeSocketColor"
    channel.socket_color_default = [0.5, 0.5, 1.0]
    channel.socket_float_min = 0
    channel.socket_float_max = 1
    channel.default_blend_mode = "NORMAL_MAP_COMBINE"

    channel = shader_info.material_channels.add()
    channel.name = "Height"
    channel.default_active = False
    channel.socket_type = "NodeSocketFloat"
    channel.socket_subtype = "FACTOR"
    channel.socket_float_default = 0.0
    channel.socket_float_min = -1.0
    channel.socket_float_max = 1.0
    channel.default_blend_mode = "ADD"

    channel = shader_info.material_channels.add()
    channel.name = "Emission"
    channel.default_active = False
    channel.socket_type = "NodeSocketColor"
    channel.socket_color_default = [0, 0, 0]
    channel.socket_float_min = 0.0
    channel.socket_float_max = 1.0
    channel.default_blend_mode = "MIX"

    # Set default shader unlayered properties.
    shader_info.unlayered_properties.clear()
    unlayered_property = shader_info.unlayered_properties.add()
    unlayered_property.name = "Base Height"

    unlayered_property = shader_info.unlayered_properties.add()
    unlayered_property.name = "Emission Strength"

    # Set the default selected material channel to be the first defined channel.
    if len(shader_info.material_channels) > 0:
        bpy.context.scene.matlayer_layer_stack.selected_material_channel = shader_info.material_channels[0].name
    
    debug_logging.log("Applied default shader settings.", message_type='INFO', sub_process=False)

class MATLAYER_shader_name(PropertyGroup):
    '''Shader name'''
    name: StringProperty()

class MATLAYER_shader_material_channel(PropertyGroup):
    '''Properties for a shader material channel.'''
    name: StringProperty(
        name="Shader Channel Name",
        description="The name of the shader channel. The channel name should match an input socket in the defined shader group node.",
        default="New Shader Channel"
    )
    default_active: BoolProperty(
        default=True,
        name="Default Active",
        description="Defines if the shader channel is active by default"
    )
    socket_type: EnumProperty(
        name="Shader Channel Type",
        description="Defines the data type for the shader channel",
        items=NODE_SOCKET_TYPES, 
        default='NodeSocketColor'
    )
    socket_subtype: EnumProperty(
        items=get_socket_subtype_enums, 
        name="Shader Channel Subtype"
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

class MATLAYER_shader_unlayered_property(PropertyGroup):
    '''Global property for a shader.'''
    name: StringProperty(
        default='New Unlayered Material Property'
    )

class MATLAYER_shader_info(PropertyGroup):
    shader_node_group: PointerProperty(
        type=bpy.types.NodeTree,
        name="Shader Node",
        description="The group node used as the shader node used when creating materials with this add-on"
    )
    material_channels: CollectionProperty(type=MATLAYER_shader_material_channel)
    unlayered_properties: CollectionProperty(type=MATLAYER_shader_unlayered_property)

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

class MATLAYER_OT_new_shader(Operator):
    bl_idname = "matlayer.new_shader"
    bl_label = "New Shader"
    bl_description = "Clears shader data in the shader tab so you can define properties for a new shader"

    def execute(self, context):
        shader_info = bpy.context.scene.matlayer_shader_info
        shader_info.shader_node_group = None
        shader_info.unlayered_properties.clear()
        shader_info.material_channels.clear()
        return {'FINISHED'}

class MATLAYER_OT_save_shader(Operator):
    bl_idname = "matlayer.save_shader"
    bl_label = "Save Shader"
    bl_description = "Saves the shader to json data. If the shader group node already exists in json data, the shader data will be overwritten"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):

        # Verify the shader node group is valid.
        shader_node_group_valid = verify_shader_node_group(self)
        if shader_node_group_valid == False:
            return

        # Check if the shader exists in json data already.
        shader_info = bpy.context.scene.matlayer_shader_info
        shader_group_node = shader_info.shader_node_group
        jdata = read_json_shader_data()
        shader_exists = False
        for i, shader in enumerate(jdata['shaders']):
            if shader['group_node_name'] == shader_group_node.name:
                existing_shader_index = i
                shader_exists = True
                break

        # Create new json data for the shader settings.
        new_shader_info = copy.deepcopy(DEFAULT_SHADER_JSON['shaders'][0])

        # Overwrite the default shader info with the current shader info.
        new_shader_info['group_node_name'] = shader_group_node.name

        new_shader_info['unlayered_properties'].clear()
        for unlayered_property in shader_info.unlayered_properties:
            new_unlayered_property = copy.deepcopy(DEFAULT_SHADER_JSON['shaders'][0]['unlayered_properties'][0])
            new_unlayered_property = unlayered_property.name
            new_shader_info['unlayered_properties'].append(new_unlayered_property)

        new_shader_info['material_channels'].clear()
        for channel in shader_info.material_channels:
            new_channel = copy.deepcopy(DEFAULT_SHADER_JSON['shaders'][0]['material_channels'][0])
            new_channel['name'] = channel.name
            new_channel['default_active'] = channel.default_active
            new_channel['socket_type'] = channel.socket_type
            new_channel['socket_subtype'] = channel.socket_subtype
            match channel.socket_type:
                case 'NodeSocketFloat':
                    new_channel['socket_default'] = channel.socket_float_default
                    new_channel['socket_min'] = channel.socket_float_min
                    new_channel['socket_max'] = channel.socket_float_max
                case 'NodeSocketColor':
                    new_channel['socket_default'] = (channel.socket_color_default[0], channel.socket_color_default[1], channel.socket_color_default[2])
                    new_channel['socket_min'] = 0
                    new_channel['socket_max'] = 1
                case 'NodeSocketVector':
                    new_channel['socket_default'] = (channel.socket_vector_default[0], channel.socket_vector_default[1], channel.socket_vector_default[2])
                    new_channel['socket_min'] = 0
                    new_channel['socket_max'] = 1

            new_channel['default_blend_mode'] = channel.default_blend_mode
            new_shader_info['material_channels'].append(new_channel)
        
        # If the shader already existed, overwrite the existing shader settings in the json file.
        if shader_exists:
            jdata['shaders'][existing_shader_index] = new_shader_info
            write_json_shader_data(jdata)
            debug_logging.log_status("Existing shader settings saved.", self, type='INFO')

        # If the shader didn't already exist, append the json data to the file.
        else:
            jdata['shaders'].append(new_shader_info)
            write_json_shader_data(jdata)
            debug_logging.log_status("New shader data saved.", self, type='INFO')

        # Update the cached list of shader group node names.
        update_shader_list()
        return {'FINISHED'}
    
class MATLAYER_OT_delete_shader(Operator):
    bl_idname = "matlayer.delete_shader"
    bl_label = "Delete Shader"
    bl_description = "Deletes the shader from json data"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):

        # Read the shader json data.
        shader_info = bpy.context.scene.matlayer_shader_info

        # Remove the shader from the json data if it exists.
        if shader_info.shader_node_group:
            jdata = read_json_shader_data()
            for shader in jdata['shaders']:
                if shader['group_node_name'] == shader_info.shader_node_group.name:
                    jdata['shaders'].remove(shader)
                    write_json_shader_data(jdata)
                    debug_logging.log_status("Deleted shader.", self, type='INFO')
        
        # Clear shader info.
        shader_info.shader_node_group = None
        shader_info.unlayered_properties.clear()
        shader_info.material_channels.clear()

        # Update the shader list.
        update_shader_list()

        return {'FINISHED'}
    
class MATLAYER_OT_add_shader_channel(Operator):
    bl_idname = "matlayer.add_shader_channel"
    bl_label = "Add Shader Channel"
    bl_description = "Adds a shader channel to the shader info"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        shader_info = bpy.context.scene.matlayer_shader_info
        shader_info.material_channels.add()
        bpy.context.scene.matlayer_shader_channel_index = len(shader_info.material_channels) - 1
        return {'FINISHED'}
    
class MATLAYER_OT_delete_shader_channel(Operator):
    bl_idname = "matlayer.delete_shader_channel"
    bl_label = "Delete Shader Channel"
    bl_description = "Deletes a shader channel from the shader info"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        shader_info = bpy.context.scene.matlayer_shader_info
        selected_shader_index = bpy.context.scene.matlayer_shader_channel_index
        shader_info.material_channels.remove(selected_shader_index)
        bpy.context.scene.matlayer_shader_channel_index = min(max(0, selected_shader_index - 1), len(shader_info.material_channels) - 1)
        return {'FINISHED'}

class MATLAYER_OT_add_global_shader_property(Operator):
    bl_idname = "matlayer.add_global_shader_property"
    bl_label = "Add Global Shader Property"
    bl_description = "Adds a global shader property to the shader info"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        shader_info = bpy.context.scene.matlayer_shader_info
        shader_info.unlayered_properties.add()
        bpy.context.scene.matlayer_selected_global_shader_property_index = len(shader_info.unlayered_properties) - 1
        return {'FINISHED'}
    
class MATLAYER_OT_delete_global_shader_property(Operator):
    bl_idname = "matlayer.delete_global_shader_property"
    bl_label = "Delete Global Shader Property"
    bl_description = "Deletes a global shader property to the shader info"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        shader_info = bpy.context.scene.matlayer_shader_info
        selected_global_shader_property_index = bpy.context.scene.matlayer_selected_global_shader_property_index
        shader_info.unlayered_properties.remove(selected_global_shader_property_index)
        bpy.context.scene.matlayer_selected_global_shader_property_index = min(max(0, selected_global_shader_property_index - 1), len(shader_info.unlayered_properties) - 1)
        return {'FINISHED'}

class MATLAYER_OT_create_shader_from_nodetree(Operator):
    bl_idname = "matlayer.create_shader_from_nodetree"
    bl_label = "Create Shader From Nodetree"
    bl_description = "Automatically fills in shader info using the selected group node"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        shader_info = bpy.context.scene.matlayer_shader_info

        # Verify the shader group node exists in the blend file.
        if not shader_info.shader_node_group:
            debug_logging.log("Can't create shader from invalid shader group node.")
            return {'FINISHED'}

        # Clear all shader settings.
        shader_info.material_channels.clear()
        shader_info.unlayered_properties.clear()

        # Add a shader channel for all group node inputs.
        for item in shader_info.shader_node_group.interface.items_tree:
            if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
                shader_channel = shader_info.material_channels.add()
                shader_channel.name = item.name

                # Some old group nodes don't define the socket type,
                # assign them a default socket type.
                if item.socket_type == '':
                    item.socket_type = 'NodeSocketFloat'

                else:
                    shader_channel.socket_type = item.socket_type
                    match shader_channel.socket_type:
                        case 'NodeSocketColor':
                            shader_channel.socket_color_default = (item.default_value[0], item.default_value[1], item.default_value[2])

                        case 'NodeSocketFloat':
                            shader_channel.socket_float_default = item.default_value
                            shader_channel.socket_float_min = item.min_value
                            shader_channel.socket_float_max = item.max_value
                            shader_channel.socket_subtype = item.subtype

                        case 'NodeSocketVector':
                            shader_channel.socket_vector_default = item.default_value
                            shader_channel.socket_subtype = item.subtype

                # Guess the ideal default blend mode for the shader channel using the channel name.
                channel_name = shader_channel.name.upper()
                match channel_name:
                    case 'NORMAL':
                        shader_channel.default_blend_mode = 'NORMAL_MAP_COMBINE'
                    case 'HEIGHT':
                        shader_channel.default_blend_mode = 'ADD'
                    case _:
                        shader_channel.default_blend_mode = 'MIX'

        # Reset shader indicies.
        bpy.context.scene.matlayer_shader_channel_index = 0
        bpy.context.scene.matlayer_selected_global_shader_property_index = 0

        debug_logging.log_status("Created shader from selected group node.", self, type='INFO')
        return {'FINISHED'}

class MATLAYER_OT_apply_default_shader(Operator):
    bl_idname = "matlayer.apply_default_shader"
    bl_label = "Apply Default Shader"
    bl_description = "Applies a default shader group node and shader setup"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        apply_default_shader()
        return {'FINISHED'}