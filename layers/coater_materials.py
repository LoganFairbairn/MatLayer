# This file contains functions for creating and verifying materials made with this add-on.

import bpy

# Returns true if the material on the active object is compatible with this add-on.
def verify_material(context):
    active_object = context.active_object
    if active_object == None:
        return False
    
    active_material = context.active_object.active_material
    if active_material == None:
        return False

    principled_bsdf = active_material.node_tree.nodes.get('Principled BSDF')
    if principled_bsdf != None:
        if principled_bsdf.label == "Coater Material":
            return True
        else:
            return False
    else:
        return False

def create_normal_mixing_group_node(context):
    '''Create a node group with a function for mixing normal maps.'''
    layer_stack = context.scene.coater_layer_stack
    active_material = context.active_object.active_material
    node_name = "COATER_NORMALMIX"
    if bpy.data.node_groups.get(node_name) == None:
        new_node_group = bpy.data.node_groups.new(node_name, 'ShaderNodeTree')

        # Create group node input sockets.
        group_input_node = new_node_group.nodes.new('NodeGroupInput')
        group_input_node.width = layer_stack.node_default_width
        new_node_group.inputs.new('NodeSocketVector', 'Normal1')
        new_node_group.inputs.new('NodeSocketVector', 'Normal2')

        # Create output nodes and sockets.
        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        group_output_node.width = layer_stack.node_default_width
        new_node_group.outputs.new('NodeSocketVector', 'Normal')

        # Create nodes used for mixing normal formula.
        separate_xyz_node_1 = new_node_group.nodes.new('ShaderNodeSeparateXYZ')
        separate_xyz_node_2 = new_node_group.nodes.new('ShaderNodeSeparateXYZ')
        add_node_1 = new_node_group.nodes.new('ShaderNodeMath')
        add_node_2 = new_node_group.nodes.new('ShaderNodeMath')
        combine_xyz_node = new_node_group.nodes.new('ShaderNodeCombineXYZ')
        normalize_node = new_node_group.nodes.new('ShaderNodeVectorMath')

        # Set new node settings.
        add_node_1.operation = 'ADD'
        add_node_2.operation = 'ADD'
        normalize_node.operation = 'NORMALIZE'

        # Connect nodes used for mixing normals.
        new_node_group.links.new(group_input_node.outputs[0], separate_xyz_node_1.inputs[0])
        new_node_group.links.new(group_input_node.outputs[1], separate_xyz_node_2.inputs[0])

        new_node_group.links.new(separate_xyz_node_1.outputs[0], add_node_1.inputs[0])
        new_node_group.links.new(separate_xyz_node_1.outputs[1], add_node_2.inputs[0])
        new_node_group.links.new(separate_xyz_node_1.outputs[2], combine_xyz_node.inputs[2])

        new_node_group.links.new(separate_xyz_node_2.outputs[0], add_node_1.inputs[1])
        new_node_group.links.new(separate_xyz_node_2.outputs[0], add_node_2.inputs[1])

        new_node_group.links.new(add_node_1.outputs[0], combine_xyz_node.inputs[0])
        new_node_group.links.new(add_node_2.outputs[0], combine_xyz_node.inputs[1])

        new_node_group.links.new(combine_xyz_node.outputs[0], normalize_node.inputs[0])
        new_node_group.links.new(normalize_node.outputs[0], group_output_node.inputs[0])

# Creates and prepares a Coater specific material.
def create_material(context, active_object):
    new_material = bpy.data.materials.new(name=active_object.name)
    active_object.data.materials.append(new_material)
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack

    # Clear all layers.
    layers.clear()
    layer_stack.layer_index = -1
    
    new_material.use_nodes = True           # The active material MUST use nodes (as of Blender version 2.8).
    new_material.blend_method = 'CLIP'      # Use alpha clip blend mode to make the material transparent.

    # Make a new emission node (used for channel previews).
    material_nodes = new_material.node_tree.nodes
    emission_node = material_nodes.new(type='ShaderNodeEmission')
    emission_node.width = layer_stack.node_default_width

    # Update the principled bsdf node.
    principled_bsdf_node = material_nodes.get('Principled BSDF')
    principled_bsdf_node.width = layer_stack.node_default_width

    # Make a new mix normal group node for mixing normal and height material channels.
    create_normal_mixing_group_node(context)
    normal_mix_node = material_nodes.new('ShaderNodeGroup')
    normal_mix_node.node_tree = bpy.data.node_groups["COATER_NORMALMIX"]
    normal_mix_node.name = "COATER_NORMALMIX"
    normal_mix_node.label = normal_mix_node.name
    normal_mix_node.location = (0.0, -700.0)
    new_material.node_tree.links.new(normal_mix_node.outputs[0], principled_bsdf_node.inputs[22])

    # Set the label of the Principled BSDF node (allows this material to be identified as a material made with this add-on).
    principled_bsdf_node.label = "Coater Material"

    # Adjust nodes locations.
    node_spacing = context.scene.coater_layer_stack.node_spacing
    principled_bsdf_node.location = (0.0, 0.0)
    material_output_node = material_nodes.get('Material Output')
    material_output_node.location = (principled_bsdf_node.width + node_spacing, 0.0)
    emission_node.location = (0.0, emission_node.height + node_spacing)

def prepare_material(context):
    active_object = context.active_object
    active_material = context.active_object.active_material

    # Add a new Coater material if there is none.
    if active_object != None:

        # There is no active material, make one.
        if active_material == None:
            remove_all_material_slots()
            create_material(context, active_object)

        # There is a material, make sure it's a Coater material.
        else:
            # If the material is a coater material, it's good to go!
            if verify_material(context):
                return {'FINISHED'}

            # If the material isn't a coater material, make a new material.
            else:
                remove_all_material_slots()
                create_material(context, active_object)
    return {'FINISHED'}

def remove_all_material_slots():
    '''Removes all material slots for the selected mesh.'''

    # TODO: Verify the selected object is a mesh before attempting to remove material slots.
    for x in bpy.context.object.material_slots:
        bpy.context.object.active_material_index = 0
        bpy.ops.object.material_slot_remove()
