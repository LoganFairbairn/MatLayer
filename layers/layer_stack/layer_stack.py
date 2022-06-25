# This file contains properties for the layer stack.

import bpy
from bpy.types import PropertyGroup
from ..nodes import material_channel_nodes
from ..nodes import layer_nodes

# TODO: This should be imported from a file rather than duplicated here.
MATERIAL_CHANNEL_NAMES = ("COLOR", "METALLIC", "ROUGHNESS", "NORMAL", "HEIGHT", "EMISSION", "SCATTERING")

def update_selected_material_channel(self, context):
    

    # Opacity values are stored in the layer so they can be assigned a correct min / max value.
    # TODO: For all layers, update opacity values.
    layers = context.scene.coater_layers
    selected_material_channel = context.scene.coater_layer_stack.selected_material_channel


    number_of_layers = len(layers)
    for i in range(0, len(layers)):
        opacity_node = layer_nodes.get_layer_node("OPACITY", selected_material_channel, i, context)
        layers[i].opacity = opacity_node.inputs[1].default_value

    bpy.ops.coater.refresh_layers()


def update_layer_index(self, context):
    '''Runs when the layer index is updated.'''
    layer_index = context.scene.coater_layer_stack.selected_layer_index
    
    # TODO: Select the current layer image.
    '''
    bpy.context.scene.tool_settings.image_paint.mode = 'IMAGE'
    layer_image = layer_nodes.get_layer_image(context, layer_index)
    if layer_image != None:
        context.scene.tool_settings.image_paint.canvas = layer_image
    '''

class COATER_layer_stack(PropertyGroup):
    '''Properties for the layer stack.'''
    selected_layer_index: bpy.props.IntProperty(default=-1, update=update_layer_index)
    channel_preview: bpy.props.BoolProperty(name="", default=False)
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
               ('MASK', "MASK", "Layer Mask Properties"),
               ('FILTERS', "FILTERS", "Layer Filter Properties")],
        name="Layer Properties Tab",
        description="Currently selected layer properties user interface tab to display",
        default=None,
        options={'HIDDEN'},
    )