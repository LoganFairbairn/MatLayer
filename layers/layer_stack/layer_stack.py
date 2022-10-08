# This file contains properties for the layer stack.

import bpy
from bpy.types import PropertyGroup
from ..nodes import material_channel_nodes

MATERIAL_CHANNEL_NAMES = ("COLOR", "METALLIC", "ROUGHNESS", "NORMAL", "HEIGHT", "EMISSION", "SCATTERING")

def update_layer_channel(self, context):
    bpy.ops.coater.refresh_layers()

def update_layer_index(self, context):
    '''Runs when the layer index is updated.'''
    layer_index = context.scene.coater_layer_stack.layer_index
    
    # TODO: Select the current layer image.
    '''
    bpy.context.scene.tool_settings.image_paint.mode = 'IMAGE'
    layer_image = layer_nodes.get_layer_image(context, layer_index)
    if layer_image != None:
        context.scene.tool_settings.image_paint.canvas = layer_image
    '''
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
    channel_preview: bpy.props.BoolProperty(name="", default=False)
    node_default_width: bpy.props.IntProperty(default=250)
    node_spacing: bpy.props.IntProperty(default=80)
    
    selected_material_channel: bpy.props.EnumProperty(
        items=material_channel_nodes.MATERIAL_CHANNELS,
        name="Material Channel",
        description="The currently selected material channel",
        default='COLOR',
        update=update_layer_channel
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