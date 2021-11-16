import bpy

def get_channel_nodes(context):
    active_material = context.active_object.active_material
    material_nodes = context.active_object.active_material.node_tree.nodes

    base_color_group = material_nodes.get(active_material.name + "_" + "BASE_COLOR")
    metallic_group = material_nodes.get(active_material.name + "_" + "METALLIC")
    roughness_group = material_nodes.get(active_material.name + "_" + "ROUGHNESS")
    height_group = material_nodes.get(active_material.name + "_" + "HEIGHT")
    emission_group = material_nodes.get(active_material.name + "_" + "EMISSION")

    group_nodes = []
    if base_color_group != None:
        group_nodes.append(base_color_group)
        
    if metallic_group != None:
        group_nodes.append(metallic_group)

    if roughness_group != None:
        group_nodes.append(roughness_group)

    if height_group != None:
        group_nodes.append(height_group)

    if emission_group != None:
        group_nodes.append(emission_group)

    return group_nodes

def get_channel_node_group(context):
    layer_stack = context.scene.coater_layer_stack
    active_material = context.active_object.active_material

    if active_material != None:
        group_node_name = active_material.name + "_" + str(layer_stack.channel)
        node_group = bpy.data.node_groups.get(group_node_name)
        return node_group
    
    else:
        return None

def get_channel_node(context):
    active_material = context.active_object.active_material

    if active_material != None:
        material_nodes = context.active_object.active_material.node_tree.nodes
        layer_stack = context.scene.coater_layer_stack

        return material_nodes.get(active_material.name + "_" + str(layer_stack.channel))

    return None

def get_layer_nodes(context, layer_index):
    node_group = get_channel_node_group(context)
    nodes = []

    # Color nodes.
    color_node = node_group.nodes.get("Color_" + str(layer_index))
    if color_node != None:
        nodes.append(color_node)

    coord_node_name = node_group.nodes.get("Coord_" + str(layer_index))
    if coord_node_name != None:
        nodes.append(coord_node_name)

    mapping_node = node_group.nodes.get("Mapping_" + str(layer_index))
    if mapping_node != None:
        nodes.append(mapping_node)

    opacity_node = node_group.nodes.get("Opacity_" + str(layer_index))
    if opacity_node != None:
        nodes.append(opacity_node)

    mix_node = node_group.nodes.get("MixLayer_" + str(layer_index))
    if mix_node != None:
        nodes.append(mix_node)

    # Mask Nodes
    mask_node = node_group.nodes.get("Mask_" + str(layer_index))
    if mask_node != None:
        nodes.append(mask_node)

    mask_coord_node = node_group.nodes.get("MaskCoords_" + str(layer_index))
    if mask_coord_node != None:
        nodes.append(mask_coord_node)

    mask_mapping_node = node_group.nodes.get("MaskMapping_" + str(layer_index))
    if mask_mapping_node != None:
        nodes.append(mask_mapping_node)

    mask_levels_node = node_group.nodes.get("MaskLevels_" + str(layer_index))
    if mask_levels_node != None:
        nodes.append(mask_levels_node)

    mask_mix_node = node_group.nodes.get("MaskMix_" + str(layer_index))
    if mask_mix_node != None:
        nodes.append(mask_mix_node)

    return nodes

def get_node(context, node_name):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node_group = get_channel_node_group(context)

    if channel_node_group != None:
        if node_name == 'COLOR':
            return channel_node_group.nodes.get(layers[layer_index].color_node_name)

        if node_name == 'OPACITY':
            return channel_node_group.nodes.get(layers[layer_index].opacity_node_name)

        if node_name == 'MIX':
            return channel_node_group.nodes.get(layers[layer_index].mix_layer_node_name)
        
        if node_name == 'MASK':
            return channel_node_group.nodes.get(layers[layer_index].mask_node_name)

    else:
        return None

def get_node(context, node_name, index):
    layers = context.scene.coater_layers
    channel_node_group = get_channel_node_group(context)

    if channel_node_group != None:
        if node_name == 'COLOR':
            return channel_node_group.nodes.get(layers[index].color_node_name)

        if node_name == 'OPACITY':
            return channel_node_group.nodes.get(layers[index].opacity_node_name)

        if node_name == 'MIX':
            return channel_node_group.nodes.get(layers[index].mix_layer_node_name)
        
        if node_name == 'MASK':
            return channel_node_group.nodes.get(layers[index].mask_node_name)

    else:
        return None

def get_layer_image(context):
    color_node = get_node(context, 'COLOR')

    if color_node != None:
        if color_node.bl_static_type == 'TEX_IMAGE':
            return color_node.image
        else:
            return None
    else:
        return None

def get_layer_image(context, index):
    color_node = get_node(context, 'COLOR', index)

    if color_node != None:
        if color_node.bl_static_type == 'TEX_IMAGE':
            return color_node.image
        else:
            return None
    else:
        return None

def update_node_labels(context):
    '''Update the labels for all layer nodes.'''
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    group_node_name = context.active_object.active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)

    # Rename all layer nodes with their appropriate index.
    for x in range(2):
        for i in range(len(layers), 0, -1):
                index = i - 1
                layers = context.scene.coater_layers
                layer_stack = context.scene.coater_layer_stack
                group_node_name = context.active_object.active_material.name + "_" + str(layer_stack.channel)
                node_group = bpy.data.node_groups.get(group_node_name)

                # Update every nodes name and label only if they exist.
                frame = node_group.nodes.get(layers[index].frame_name)
                if frame != None:
                    frame.name = layers[index].layer_name  + "_" + str(index)
                    frame.label = frame.name
                    layers[index].frame_name = frame.name

                # Color Nodes
                color_node = node_group.nodes.get(layers[index].color_node_name)
                if color_node != None:
                    color_node.name = "Color_" + str(index)
                    color_node.label = color_node.name
                    layers[index].color_node_name = color_node.name

                coord_node_name = node_group.nodes.get(layers[index].coord_node_name)
                if coord_node_name != None:
                    coord_node_name.name = "Coord_" + str(index)
                    coord_node_name.label = coord_node_name.name
                    layers[index].coord_node_name = coord_node_name.name

                mapping_node = node_group.nodes.get(layers[index].mapping_node_name)
                if mapping_node != None:
                    mapping_node.name = "Mapping_" + str(index)
                    mapping_node.label = mapping_node.name
                    layers[index].mapping_node_name = mapping_node.name

                opacity_node = node_group.nodes.get(layers[index].opacity_node_name)
                if opacity_node != None:
                    opacity_node.name = "Opacity_" + str(index)
                    opacity_node.label = opacity_node.name
                    layers[index].opacity_node_name = opacity_node.name

                mix_layer_node = node_group.nodes.get(layers[index].mix_layer_node_name)
                if mix_layer_node != None:
                    mix_layer_node.name = "MixLayer_" + str(index)
                    mix_layer_node.label = mix_layer_node.name
                    layers[index].mix_layer_node_name = mix_layer_node.name

                # Mask Nodes
                mask_node = node_group.nodes.get(layers[index].mask_node_name)
                if mask_node != None:
                    mask_node.name = "Mask_" + str(index)
                    mask_node.label = mask_node.name
                    layers[index].mask_node_name = mask_node.name

                mask_mix_node = node_group.nodes.get(layers[index].mask_mix_node_name)
                if mask_mix_node != None:
                    mask_mix_node.name = "MaskMix_" + str(index)
                    mask_mix_node.label = mask_mix_node.name
                    layers[index].mask_mix_node_name = mask_mix_node.name

                mask_coord_node = node_group.nodes.get(layers[index].mask_coord_node_name)
                if mask_coord_node != None:
                    mask_coord_node.name = "MaskCoords_" + str(index)
                    mask_coord_node.label = mask_coord_node.name
                    layers[index].mask_coord_node_name = mask_coord_node.name

                mask_mapping_node = node_group.nodes.get(layers[index].mask_mapping_node_name)
                if mask_mapping_node != None:
                    mask_mapping_node.name = "MaskMapping_" + str(index)
                    mask_mapping_node.label = mask_mapping_node.name
                    layers[index].mask_mapping_node_name = mask_mapping_node.name

                mask_levels_node = node_group.nodes.get(layers[index].mask_levels_node_name)
                if mask_levels_node != None:
                    mask_levels_node.name = "MaskLevels_" + str(index)
                    mask_levels_node.label = mask_levels_node.name
                    layers[index].mask_levels_node_name = mask_levels_node.name

def set_material_shading(context):
    if context.space_data.type == 'VIEW_3D':
        context.space_data.shading.type = 'MATERIAL'

def link_layers(context):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    active_material = context.active_object.active_material
    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)
    group_input_node = node_group.nodes.get('Group Input')
    group_output_node = node_group.nodes.get('Group Output')

    # Remove all existing output links for mix layer or mix mask nodes.
    group_input = node_group.nodes.get('Group Input')
    output = group_input.outputs[0]
    for l in output.links:
        if l != 0:
            node_group.links.remove(l)

    group_output = node_group.nodes.get('Group Output')
    output = group_output.inputs[0]

    for l in output.links:
        if l != 0:
            node_group.links.remove(l)

    number_of_layers = len(layers)
    for x in range(number_of_layers - 1):
        mix_layer_node = node_group.nodes.get(layers[x].mix_layer_node_name)
        if mix_layer_node != None:
            output = mix_layer_node.outputs[0]
            for l in output.links:
                if l != 0:
                    node_group.links.remove(l)

        mix_mask_node = node_group.nodes.get(layers[x].mask_mix_node_name)
        if mix_mask_node != None:
            output = mix_mask_node.outputs[0]
            for l in output.links:
                if l != 0:
                    node_group.links.remove(l)
    
    # Connect mix layer nodes.
    for x in range(number_of_layers, 0, -1):
        current_layer_index = x - 1
        next_layer_index = x - 2

        # Connect the group input value to the first mix layer node or mix mask node (prioritize mask node connections).
        if x == number_of_layers:
            for i in range(number_of_layers, 0, -1):
                mix_mask_node = node_group.nodes.get(layers[i - 1].mask_mix_node_name)
                if layers[i - 1].hidden == False:
                    if mix_mask_node != None:
                        mix_layer_node = node_group.nodes.get(layers[i - 1].mix_layer_node_name)
                        mix_mask_node = node_group.nodes.get(layers[i - 1].mask_mix_node_name)
                        node_group.links.new(group_input_node.outputs[0], mix_layer_node.inputs[1])
                        node_group.links.new(group_input_node.outputs[0], mix_mask_node.inputs[1])
                    else:
                        mix_layer_node = node_group.nodes.get(layers[i - 1].mix_layer_node_name)
                        node_group.links.new(group_input_node.outputs[0], mix_layer_node.inputs[1])
                    break

        # Only connect layers that are not hidden.
        if layers[current_layer_index].hidden == False:
            mix_layer_node = node_group.nodes.get(layers[current_layer_index].mix_layer_node_name)
            mix_mask_node = node_group.nodes.get(layers[current_layer_index].mask_mix_node_name)
            next_mix_layer_node = node_group.nodes.get(layers[next_layer_index].mix_layer_node_name)
            next_mix_mask_node = node_group.nodes.get(layers[next_layer_index].mask_mix_node_name)

            # Deal with hidden layers.
            while layers[next_layer_index].hidden:
                next_layer_index -= 1

                if next_layer_index < 0:
                    next_mix_layer_node = None
                    next_mix_mask_node = None
                    break

                else:
                    next_mix_layer_node = node_group.nodes.get(layers[next_layer_index].mix_layer_node_name)
                    next_mix_mask_node = node_group.nodes.get(layers[next_layer_index].mask_mix_node_name)

            # Connect to the next mix layer node or mix mask node (prioritize mask node connections).
            if next_layer_index >= 0:
                if mix_mask_node != None:
                    if next_mix_mask_node != None:
                        node_group.links.new(mix_mask_node.outputs[0], next_mix_layer_node.inputs[1])
                        node_group.links.new(mix_mask_node.outputs[0], next_mix_mask_node.inputs[1])

                    else:
                        node_group.links.new(mix_mask_node.outputs[0], next_mix_layer_node.inputs[1])

                else:
                    if next_mix_mask_node != None:
                        node_group.links.new(mix_layer_node.outputs[0], next_mix_layer_node.inputs[1])
                        node_group.links.new(mix_layer_node.outputs[0], next_mix_mask_node.inputs[1])

                    else:
                        node_group.links.new(mix_layer_node.outputs[0], next_mix_layer_node.inputs[1])

            # For the last layer, connect the layer mix node or the mask mix node to the output (prioritize mask node connections).
            else:
                # If the channel is a Height channel, connect to the bump node first before connecting to the output.
                if layer_stack.channel == 'HEIGHT':
                    bump_node = node_group.nodes.get("Bump")

                    if bump_node != None:
                        if mix_mask_node != None:
                            node_group.links.new(mix_mask_node.outputs[0], bump_node.inputs[2])
                            node_group.links.new(mix_mask_node.outputs[0], group_output_node.inputs[1])
                            node_group.links.new(bump_node.outputs[0], group_output_node.inputs[0])

                        else:
                            node_group.links.new(mix_layer_node.outputs[0], bump_node.inputs[2])
                            node_group.links.new(mix_layer_node.outputs[0], group_output_node.inputs[1])
                            node_group.links.new(bump_node.outputs[0], group_output_node.inputs[0])
                else:
                    if mix_mask_node != None:
                        node_group.links.new(mix_mask_node.outputs[0], group_output_node.inputs[0])

                    else:
                        node_group.links.new(mix_layer_node.outputs[0], group_output_node.inputs[0])

            # Connect the mix layer node to the mix mask node if a mask exists.
            if mix_mask_node != None:
                node_group.links.new(mix_layer_node.outputs[0], mix_mask_node.inputs[2])

        # TODO: Link to alpha to calculate alpha nodes if required.

def organize_nodes(context):
    '''Organizes all coater nodes in the material node editor.'''
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    node_spacing = layer_stack.node_spacing

    # Organize channel nodes.
    channel_nodes = get_channel_nodes(context)
    header_position = [0.0, 0.0]
    for node in channel_nodes:
        if node != None:
            node.location = (-node.width + -node_spacing, header_position[1])
            header_position[1] -= (node.height + (layer_stack.node_spacing * 0.5))


    # Organize all layer nodes.
    channel_node = get_channel_node(context)
    header_position = [0.0, 0.0]
    for i in range(0, len(layers)):
        header_position[0] -= layer_stack.node_default_width + node_spacing
        header_position[1] = 0.0

        node_list = get_layer_nodes(context, i)
        for node in node_list:
            node.width = layer_stack.node_default_width
            node.location = (header_position[0], header_position[1])
            header_position[1] -= (node.dimensions.y) + node_spacing

    # Organize group input node.
    if channel_node != None:
        header_position[0] -= layer_stack.node_default_width + node_spacing
        group_input_node = channel_node.node_tree.nodes.get('Group Input')
        group_input_node.location = (header_position[0], 0.0)
    
    # Organize group output node.
    if channel_node != None:
        group_output_node = channel_node.node_tree.nodes.get('Group Output')
        group_output_node.location = (0.0, 0.0)

    # TODO: If the current channel is a height channel, organize the bump node too.
    if layer_stack.channel == 'HEIGHT':
        if channel_node != None:
            bump_node = channel_node.node_tree.nodes.get('Bump')

            if bump_node != None:
                bump_node.location = (0.0, -group_input_node.dimensions.y - node_spacing)

def move_layer(context, direction):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    layer_index = context.scene.coater_layer_stack.layer_index

    index_to_move_to = max(0, min(layer_index + (-1 if direction == "Up" else 1), len(layers) - 1))
    layers.move(layer_index, index_to_move_to)
    layer_stack.layer_index = index_to_move_to

    update_node_labels(context)   # Re-name nodes.
    organize_nodes(context)       # Re-organize nodes.
    link_layers(context)          # Re-connect layers.

def ready_coater_material(context):
    active_object = context.active_object
    active_material = context.active_object.active_material

    # Add a new Coater material if there is none.
    if active_object != None:

        # There is no active material, make one.
        if active_material == None:
            remove_all_material_slots()
            create_coater_material(context, active_object)

        # There is a material, make sure it's a Coater material.
        else:
            # If the material is a coater material, it's good to go!
            if check_coater_material(context):
                return {'FINISHED'}

            # If the material isn't a coater material, make a new material.
            else:
                remove_all_material_slots()
                create_coater_material(context, active_object)
            
    else:
        self.report({'WARNING'}, "There is no active object, select an object.")
        return {'FINISHED'}

def remove_all_material_slots():
    for x in bpy.context.object.material_slots:
        bpy.context.object.active_material_index = 0
        bpy.ops.object.material_slot_remove()

def create_coater_material(context, active_object):
    new_material = bpy.data.materials.new(name=active_object.name)
    active_object.data.materials.append(new_material)
    layer_stack = context.scene.coater_layer_stack
    
    # The active material MUST use nodes.
    new_material.use_nodes = True

    # Use alpha clip blend mode to make the material transparent.
    new_material.blend_method = 'CLIP'

    # Make a new emission node (used for channel previews).
    material_nodes = new_material.node_tree.nodes
    emission_node = material_nodes.new(type='ShaderNodeEmission')
    emission_node.width = layer_stack.node_default_width

    # Get the principled BSDF & material output node.
    principled_bsdf_node = material_nodes.get('Principled BSDF')
    principled_bsdf_node.width = layer_stack.node_default_width
    material_output_node = material_nodes.get('Material Output')

    # Set the label of the Principled BSDF node (allows this material to be identified as a Coater material).
    principled_bsdf_node.label = "Coater PBR"

    # Set the default value for emission to 5, this makes the emission easier to see.
    principled_bsdf_node.inputs[18].default_value = 5

    # Turn Eevee bloom on, this also makes emission easier to see.
    context.scene.eevee.use_bloom = True

    # Adjust nodes locations.
    node_spacing = context.scene.coater_layer_stack.node_spacing
    principled_bsdf_node.location = (0.0, 0.0)
    material_output_node.location = (principled_bsdf_node.width + node_spacing, 0.0)
    emission_node.location = (0.0, emission_node.height + node_spacing)

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
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[4])

            if layer_stack.channel == "ROUGHNESS":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[7])

            if layer_stack.channel == "EMISSION":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[17])

            if layer_stack.channel == "HEIGHT":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[20])

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
    update_node_labels(context)

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
    layer_nodes = get_layer_nodes(context, layer_index)
    for n in layer_nodes:
        n.parent = frame

    # Store the frame.
    frame.name = layers[layer_index].layer_name + "_" + str(layer_index)
    frame.label = frame.name
    layers[layer_index].frame_name = frame.name

    # TODO: If there is another layer already, add a group node to help calculate alpha blending.
    #if len(layers) > 1:
    #    create_calculate_alpha_node(self, context)

def create_calculate_alpha_node(context):
    layer_stack = context.scene.coater_layer_stack
    channel_node = get_channel_node(context)

    group_node_name = "Coater Calculate Alpha"
    if bpy.data.node_groups.get(group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(group_node_name, 'ShaderNodeTree')

        # Create Nodes
        input_node = new_node_group.nodes.new('NodeGroupInput')
        output_node = new_node_group.nodes.new('NodeGroupOutput')
        subtract_node = new_node_group.nodes.new(type='ShaderNodeMath')
        multiply_node = new_node_group.nodes.new(type='ShaderNodeMath')
        add_node = new_node_group.nodes.new(type='ShaderNodeMath')

        # Add Sockets
        new_node_group.inputs.new('NodeSocketFloat', 'Alpha 1')
        new_node_group.inputs.new('NodeSocketFloat', 'Alpha 2')
        new_node_group.outputs.new('NodeSocketFloat', 'Alpha')

        # Set node values.
        subtract_node.operation = 'SUBTRACT'
        multiply_node.operation = 'MULTIPLY'
        add_node.operation = 'ADD'
        subtract_node.inputs[0].default_value = 1

        # Link nodes.
        link = new_node_group.links.new
        link(input_node.outputs[0], subtract_node.inputs[1])
        link(subtract_node.outputs[0], multiply_node.inputs[0])
        link(input_node.outputs[0], multiply_node.inputs[1])
        link(multiply_node.outputs[0], add_node.inputs[1])
        link(input_node.outputs[1], add_node.inputs[0])
        link(add_node.outputs[0], output_node.inputs[0])

        calculate_alpha_node = channel_node.node_tree.nodes.new('ShaderNodeGroup')
        calculate_alpha_node.node_tree = bpy.data.node_groups[group_node_name]
        calculate_alpha_node.name = group_node_name
        calculate_alpha_node.label = group_node_name
        calculate_alpha_node.width = layer_stack.node_default_width

        # Organize nodes.
        nodes = []
        nodes.append(input_node)
        nodes.append(subtract_node)
        nodes.append(multiply_node)
        nodes.append(add_node)
        nodes.append(output_node)

        header_position = [0.0, 0.0]
        for n in nodes:
            n.width = layer_stack.node_default_width
            n.location = (header_position[0], header_position[1])
            header_position[0] -= (layer_stack.node_default_width + layer_stack.node_spacing)

def add_layer_slot(context):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    layer_index = context.scene.coater_layer_stack.layer_index

    # Add a new layer slot.
    layers.add()

    # Assign the layer a unique name.
    new_layer_name = "Layer 0"
    layer_number = 0
    name_exists = True
    number_of_layers = len(layers)

    while (name_exists):
        for i in range(number_of_layers):
            if layers[i].layer_name == new_layer_name:
                layer_number += 1
                new_layer_name = "Layer " + str(layer_number)
                break

            if i == (number_of_layers - 1):
                name_exists = False
                layers[len(layers) - 1].layer_name = new_layer_name

    # Moves the new layer above the currently selected layer and selects it.
    if(layer_index != -1):
        move_index = len(layers) - 1
        move_to_index = max(0, min(layer_index, len(layers) - 1))
        layers.move(move_index, move_to_index)
        layer_stack.layer_index = move_to_index

    # If there is no layer selected, move the layer to the top of the stack.
    else:
        move_index = len(layers) - 1
        move_to_index = 0
        layers.move(move_index, move_to_index)
        layer_stack.layer_index = move_to_index

def check_coater_material(context):
    active_material = context.active_object.active_material

    principled_bsdf = active_material.node_tree.nodes.get('Principled BSDF')

    if principled_bsdf != None:
        if principled_bsdf.label == "Coater PBR":
            return True
        else:
            return False
    else:
        return False

def delete_layer_image(context, image):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    layer_exist = False
    for l in range(0, layers):
        if l != layer_index:
            if get_layer_image(context, l):
                layer_exist = True
                break

    if layer_exist == False:
        bpy.data.images.remove(image)