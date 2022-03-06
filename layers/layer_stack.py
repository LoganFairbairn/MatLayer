import bpy
from bpy.types import PropertyGroup
from .import coater_node_info

def update_layer_channel(self, context):
    bpy.ops.coater.refresh_layers()

def update_layer_index(self, context):
    layer_index = context.scene.coater_layer_stack.layer_index
    
    bpy.context.scene.tool_settings.image_paint.mode = 'IMAGE'
    
    layer_image = coater_node_info.get_layer_image(context, layer_index)
    if layer_image != None:
        context.scene.tool_settings.image_paint.canvas = layer_image

class COATER_layer_stack(PropertyGroup):
    '''Properties for the layer stack.'''
    layer_index: bpy.props.IntProperty(default=-1, update=update_layer_index)
    channel_preview: bpy.props.BoolProperty(name="", default=False)
    node_default_width: bpy.props.IntProperty(default=250)
    node_spacing: bpy.props.IntProperty(default=80)
    channel: bpy.props.EnumProperty(
        items=[('BASE_COLOR', "Base Color", "Set to show all layers for the base color channel"),
               ('ROUGHNESS', "Roughness", "Set to show all layers in the roughness channel"),
               ('METALLIC', "Metallic", "Set to show all layers in the metallic channel"),
               ('HEIGHT', "Height", "Set to show all layers in the height channel"),
               ('EMISSION', 'Emission', "Set to show all layers in the emission channel")],
        name="Layer Stack",
        description="Type of the layer",
        default=None,
        options={'HIDDEN'},
        update=update_layer_channel
    )