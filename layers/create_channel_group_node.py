import bpy

# Creates a channel group node.
def create_channel_group_node(context):
    active_material = context.active_object.active_material
    material_nodes = context.active_object.active_material.node_tree.nodes
    layer_stack = context.scene.coater_layer_stack

    # Create a node group for the selected channel if one does not exist.
    group_node_name = active_material.name + "_" + str(layer_stack.channel)

    if bpy.data.node_groups.get(group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(group_node_name, 'ShaderNodeTree')

        group_input_node = new_node_group.nodes.new('NodeGroupInput')
        group_input_node.width = layer_stack.node_default_width
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = layer_stack.node_default_width

        # Add a socket based on channel
        if layer_stack.channel == 'BASE_COLOR':
            new_node_group.inputs.new('NodeSocketColor', 'Base Color')
            new_node_group.outputs.new('NodeSocketColor', 'Base Color')
            new_node_group.outputs.new('NodeSocketFloat', 'Alpha')
        
        if layer_stack.channel == 'METALLIC':
            new_node_group.inputs.new('NodeSocketFloat', 'Metallic')
            new_node_group.outputs.new('NodeSocketFloat', 'Metallic')

        if layer_stack.channel == 'ROUGHNESS':
            new_node_group.inputs.new('NodeSocketFloat', 'Roughness')
            new_node_group.outputs.new('NodeSocketFloat', 'Roughness')

        if layer_stack.channel == 'HEIGHT':
            new_node_group.outputs.new('NodeSocketVector', 'Height (Vector)')
            new_node_group.outputs.new('NodeSocketFloat', 'Height')
            new_node_group.nodes.new('ShaderNodeBump')

        if layer_stack.channel == 'EMISSION':
            new_node_group.inputs.new('NodeSocketColor', 'Emission')
            new_node_group.outputs.new('NodeSocketColor', 'Emission')
            
    # Add the group node to the active material if there is there isn't a group node already.
    if material_nodes.get(group_node_name) == None:
        group_node = material_nodes.new('ShaderNodeGroup')
        group_node.node_tree = bpy.data.node_groups[group_node_name]
        group_node.name = group_node_name
        group_node.label = group_node_name
        group_node.width = layer_stack.node_default_width * 1.2

        # Link the group node with the Principled BSDF node.
        principled_bsdf_node = material_nodes.get('Principled BSDF')

        if principled_bsdf_node != None:
            node_links = active_material.node_tree.links

            if layer_stack.channel == "BASE_COLOR":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[0])

            if layer_stack.channel == "METALLIC":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[6])

            if layer_stack.channel == "ROUGHNESS":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[9])

            if layer_stack.channel == "EMISSION":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[19])

            if layer_stack.channel == "HEIGHT":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[22])