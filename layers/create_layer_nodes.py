import bpy
from .import update_node_labels
from .import coater_node_info

def create_layer_nodes(context, layer_type):
    active_material = context.active_object.active_material
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the node group.
    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)

    # Create new nodes based on the layer type.
    if layer_type == 'IMAGE_LAYER':
        color_node = node_group.nodes.new(type='ShaderNodeTexImage')
        coord_node_name = node_group.nodes.new(type='ShaderNodeTexCoord')
        mapping_node = node_group.nodes.new(type='ShaderNodeMapping')

    if layer_type == 'COLOR_LAYER':
        color_node = node_group.nodes.new(type='ShaderNodeRGB')
    opacity_node = node_group.nodes.new(type='ShaderNodeMath')
    mix_layer_node = node_group.nodes.new(type='ShaderNodeMixRGB')

    # Store new nodes in the selected layer.
    layers[layer_index].color_node_name = color_node.name
    layers[layer_index].opacity_node_name = opacity_node.name
    layers[layer_index].mix_layer_node_name = mix_layer_node.name

    if layer_type == 'IMAGE_LAYER':
        layers[layer_index].coord_node_name = coord_node_name.name
        layers[layer_index].mapping_node_name = mapping_node.name

    # Update node labels.
    update_node_labels.update_node_labels(context)

    # Set node default values.
    color_node.outputs[0].default_value = (0, 0, 0, 1.0)
    opacity_node.operation = 'MULTIPLY'
    opacity_node.use_clamp = True
    opacity_node.inputs[0].default_value = 1
    opacity_node.inputs[1].default_value = 1
    mix_layer_node.inputs[0].default_value = 1
    mix_layer_node.use_clamp = True
    mix_layer_node.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0)

    # Link nodes for this layer (based on layer type).
    link = node_group.links.new
    link(color_node.outputs[0], mix_layer_node.inputs[2])
    link(opacity_node.outputs[0], mix_layer_node.inputs[0])

    if layer_type == 'IMAGE_LAYER':
        link(color_node.outputs[1], opacity_node.inputs[0])
        link(coord_node_name.outputs[2], mapping_node.inputs[0])
        link(mapping_node.outputs[0], color_node.inputs[0])

    # Frame nodes.
    frame = node_group.nodes.new(type='NodeFrame')
    layer_nodes = coater_node_info.get_layer_nodes(context, layer_index)
    for n in layer_nodes:
        n.parent = frame

    # Store the frame.
    frame.name = layers[layer_index].name + "_" + str(layers[layer_index].id) + "_" + str(layer_index)
    frame.label = frame.name
    layers[layer_index].frame_name = frame.name

    # TODO: If there is another layer already, add a group node to help calculate alpha blending.
    #if len(layers) > 1:
    #    create_calculate_alpha_node(self, context)