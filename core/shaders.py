# This file contains properties and functions for editing shader nodes used for lighting calculations in materials created with this add-on.

import bpy
from bpy.utils import resource_path
from bpy.types import PropertyGroup, Operator
from bpy.props import StringProperty, CollectionProperty
import json
from pathlib import Path
from ..core import debug_logging
from .. import preferences

def update_shader_list():
    '''Updates a list of all available shaders as defined in the shader info json data.'''
    templates_path = str(Path(resource_path('USER')) / "scripts/addons" / preferences.ADDON_NAME / "json_data" / "shader_info.json")
    json_file = open(templates_path, "r")
    jdata = json.load(json_file)
    json_file.close()
    shaders = jdata['shaders']
    matlayer_shader_list = bpy.context.scene.matlayer_shader_list
    matlayer_shader_list.clear()
    for shader in shaders:
        shader_name = matlayer_shader_list.add()
        shader_name.name = shader['name']
    debug_logging.log("Updated shader list.")

def set_shader(shader_name):
    '''Sets the shader that will be used in materials created with this add-on.'''

    # Update the list of shaders that are defined in the shader info json file.
    update_shader_list()

    matlayer_shader_list = bpy.context.scene.matlayer_shader_list
    matlayer_shader_info = bpy.context.scene.matlayer_shader_info

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
            matlayer_shader_info.name = shaders[i]['name']
            matlayer_shader_info.author = shaders[i]['author']
            matlayer_shader_info.description = shaders[i]['description']
            matlayer_shader_info.group_node_name = shaders[i]['group_node_name']

            shader_material_channels = shaders[i]['shader_material_channels']
            matlayer_shader_info.material_channels.clear()
            for shader_material_channel in shader_material_channels:
                channel = matlayer_shader_info.material_channels.add()
                channel.name = shader_material_channel

    # TODO: If the shader wasn't found, apply a default shader instead.
    if not shader_exists:
        debug_logging.log("Shader {0} doesn't exist, applying default shader.".format(shader_name))

class MATLAYER_shader_name(PropertyGroup):
    '''Shader name'''
    name: StringProperty()

class MATLAYER_shader_material_channel(PropertyGroup):
    '''List of material channels for a specific shader.'''
    name: StringProperty()

class MATLAYER_shader_info(PropertyGroup):
    name: StringProperty()
    author: StringProperty()
    description: StringProperty()
    group_node_name: StringProperty()
    material_channels: CollectionProperty(type=MATLAYER_shader_material_channel)

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
        
        # Set the shader so new material layers will be created using it.
        set_shader(self.shader_name)

        # DISABLED
        # Replace the shader node in the active material.
        '''
        active_object = bpy.context.active_object
        if active_object:
            active_material = active_object.active_material
            if active_material:
                shader_node = active_material.node_tree.nodes.get('MATLAYER_SHADER')
                if shader_node:
                    shader_node_tree = blender_addon_utils.append_group_node(self.shader)
                    if shader_node_tree:
                        old_node_location = shader_node.location
                        old_node_width = shader_node.width
                        active_material.node_tree.nodes.remove(shader_node)
                        new_shader_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
                        new_shader_node.name = 'MATLAYER_SHADER'
                        new_shader_node.label = new_shader_node.name
                        new_shader_node.node_tree = shader_node_tree
                        new_shader_node.location = old_node_location
                        new_shader_node.width = old_node_width
                        
                        # Link the new shader node.
                        material_output_node = active_material.node_tree.nodes.get('MATERIAL_OUTPUT')
                        if material_output_node:
                            active_material.node_tree.links.new(new_shader_node.outputs[0], material_output_node.inputs[0])

                        normal_height_mix_node = get_material_layer_node('NORMAL_HEIGHT_MIX')
                        if normal_height_mix_node:
                            active_material.node_tree.links.new(normal_height_mix_node.outputs[0], new_shader_node.inputs.get('Normal'))
                        link_layer_group_nodes(self)
        '''
        return {'FINISHED'}