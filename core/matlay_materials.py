# This file contains functions for creating and verifying materials made with this add-on.

import bpy
from ..utilities import info_messages

# Returns true if the material on the active object is compatible with this add-on.
def verify_material(context):
    '''Verifies the material is a valid material created using this add-on.'''
    active_object = context.active_object
    if active_object == None:
        return False
    
    active_material = context.active_object.active_material
    if active_material == None:
        return False

    principled_bsdf = active_material.node_tree.nodes.get('Principled BSDF')
    if principled_bsdf != None:
        if principled_bsdf.label == "MatLay Material":
            return True
        else:
            return False
    else:
        return False

def create_matlay_material(context, active_object):
    '''Creates and prepares a MatLay specific material.'''
    new_material = bpy.data.materials.new(name=active_object.name)
    active_object.data.materials.append(new_material)
    layers = context.scene.matlay_layers
    layer_stack = context.scene.matlay_layer_stack

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
    normal_mix_node = material_nodes.new('ShaderNodeMix')
    normal_mix_node.data_type = 'VECTOR'
    normal_mix_node.name = "MATLAY_NORMALMIX"
    normal_mix_node.label = normal_mix_node.name
    normal_mix_node.location = (0.0, -700.0)
    new_material.node_tree.links.new(normal_mix_node.outputs[0], principled_bsdf_node.inputs[22])

    # Set the label of the Principled BSDF node (allows this material to be identified as a material made with this add-on).
    principled_bsdf_node.label = "MatLay Material"

    # Adjust nodes locations.
    node_spacing = context.scene.matlay_layer_stack.node_spacing
    principled_bsdf_node.location = (0.0, 0.0)
    material_output_node = material_nodes.get('Material Output')
    material_output_node.location = (principled_bsdf_node.width + node_spacing, 0.0)
    emission_node.location = (0.0, emission_node.height + node_spacing)

def prepare_material(context):
    active_object = context.active_object
    active_material = context.active_object.active_material

    # Add a new MatLay material if there is none.
    if active_object:

        if active_object.type != 'MESH':
            info_messages.popup_message_box("Selected object must be a mesh to create a material.", title="User Error", icon='ERROR')
            return False

        # There is no active material, make one.
        if active_material == None:
            remove_all_material_slots()
            create_matlay_material(context, active_object)

        # There is a material, make sure it's a MatLay material.
        else:
            # If the material is a matlay material, it's good to go!
            if verify_material(context):
                return True

            # If the material isn't a matlay material, make a new material.
            else:
                remove_all_material_slots()
                create_matlay_material(context, active_object)
    return False

def remove_all_material_slots():
    '''Removes all material slots for the selected mesh.'''
    for x in bpy.context.object.material_slots:
        bpy.context.object.active_material_index = 0
        bpy.ops.object.material_slot_remove()
