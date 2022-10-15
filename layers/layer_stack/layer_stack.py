# This file contains properties for the layer stack.

import bpy
from bpy.types import PropertyGroup
from ..nodes import material_channel_nodes
from ..nodes import layer_nodes

MATERIAL_CHANNEL_NAMES = ("COLOR", "METALLIC", "ROUGHNESS", "NORMAL", "HEIGHT", "EMISSION", "SCATTERING")

def update_selected_material_channel(self, context):
    '''Updates values when the selected material channel is updated.'''
    layers = context.scene.coater_layers
    selected_material_channel = context.scene.coater_layer_stack.selected_material_channel

    # Update the opacity and blend mode for all layers.
    for i in range(0, len(layers)):
        opacity_node = layer_nodes.get_layer_node("OPACITY", selected_material_channel, i, context)
        if opacity_node:
            layers[i].opacity = opacity_node.inputs[1].default_value

def update_layer_index(self, context):
    '''Selects an image for painting if one exists for the selected material channel.'''
    selected_material_channel = context.scene.coater_layer_stack.selected_material_channel
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    bpy.context.scene.tool_settings.image_paint.mode = 'IMAGE'
    texture_node = layer_nodes.get_layer_node("TEXTURE", selected_material_channel, selected_layer_index, context)

    if texture_node.bl_idname == "ShaderNodeTexImage":
        if texture_node.image:
            context.scene.tool_settings.image_paint.canvas = texture_node.image

def verify_layer_stack_index(layer_stack_index, context):
    '''Verifies the given layer stack index exists.'''
    layers = context.scene.coater_layers
    if layer_stack_index <= len(layers) - 1 and layer_stack_index >= 0:
        return True
    else:
        return False

class COATER_layer_stack(PropertyGroup):
    '''Properties for the layer stack.'''
    # TODO: Rename this to selected_layer_index.
    layer_index: bpy.props.IntProperty(default=-1, update=update_layer_index)
    material_channel_preview: bpy.props.BoolProperty(name="", default=False)
    node_default_width: bpy.props.IntProperty(default=250)
    node_spacing: bpy.props.IntProperty(default=80)
    
    selected_material_channel: bpy.props.EnumProperty(
        items=material_channel_nodes.MATERIAL_CHANNELS,
        name="Material Channel",
        description="The currently selected material channel",
        default='COLOR',
        update=update_selected_material_channel
    )


    # Tabs for layer properties.
    layer_properties_tab: bpy.props.EnumProperty(
        items=[('MATERIAL', "MATERIAL", "Layer Material Properties"),
               ('MASK', "MASKS", "Layer Mask Properties")],
        name="Layer Properties Tab",
        description="Currently selected layer properties user interface tab to display",
        default=None,
        options={'HIDDEN'},
    )