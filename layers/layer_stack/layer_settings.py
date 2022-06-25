import bpy

def update_match_layer_scale(self, context):
    layer_settings = context.scene.coater_layer_settings

    if layer_settings.match_layer_scale:
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.selected_layer_index

        layers[layer_index].projected_scale_y = layers[layer_index].projected_scale_x

def update_match_layer_mask_scale(self, context):
    layer_settings = context.scene.coater_layer_settings

    if layer_settings.match_layer_mask_scale:
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.selected_layer_index

        layers[layer_index].projected_mask_scale_y = layers[layer_index].projected_mask_scale_x

class COATER_layer_settings(bpy.types.PropertyGroup):
    match_layer_scale: bpy.props.BoolProperty(name="Match Layer Scale", default=True,update=update_match_layer_scale)
    match_layer_mask_scale: bpy.props.BoolProperty(name="Match Layer Mask Scale", default=True, update=update_match_layer_mask_scale)