import bpy

def update_layer_channel(self, context):
    bpy.ops.coater.refresh_layers()

def update_layer_index(self, context):
    active_material = context.object.active_material
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    
    bpy.context.scene.tool_settings.image_paint.mode = 'MATERIAL'

    if active_material != None:
        for i in range(0, len(active_material.texture_paint_images)):
            if layers[layer_index].color_image == active_material.texture_paint_images[i]:
                active_material.paint_active_slot = i

class COATER_layer_stack(bpy.types.PropertyGroup):
    '''Properties for the layer stack.'''
    layer_index: bpy.props.IntProperty(default=-1, update=update_layer_index)
    channel_preview: bpy.props.BoolProperty(name="", default=False)
    node_default_width: bpy.props.IntProperty(default=250)
    node_spacing: bpy.props.IntProperty(default=50)
    channel: bpy.props.EnumProperty(
        items=[('BASE_COLOR', "Base Color", "Set to show all layers for the base color channel"),
               ('ROUGHNESS', "Roughness", "Set to show all layers in the roughness channel"),
               ('METALLIC', "Metallic", "Set to show all layers in the metallic channel"),
               ('HEIGHT', "Height", "Set to show all layers in the height channel")],
        name="",
        description="Type of the layer",
        default=None,
        options={'HIDDEN'},
        update=update_layer_channel
    )