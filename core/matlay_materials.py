# This file contains functions for creating and verifying materials made with this add-on.

import bpy
from ..utilities import logging

def verify_material(context):
    '''Returns true if the material is a valid material created using this add-on.'''
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

def create_matlay_material(context):
    '''Creates a new material in the active (selected) material index / slot for the active object.'''
    node_spacing = context.scene.matlay_layer_stack.node_spacing

    # Create a new material for the active material slot in the active object.
    active_object = context.active_object
    object_material_index = 1
    new_material_name = "{0}_{1}".format(active_object.name, str(object_material_index))
    while bpy.data.materials.get(new_material_name):
        object_material_index += 1
        new_material_name = "{0}_{1}".format(active_object.name, str(object_material_index))
    new_material = bpy.data.materials.new(name=new_material_name)
    new_material.use_nodes = True

    if len(active_object.material_slots) == 0:
        active_object.data.materials.append(new_material)
    else:
        active_object.material_slots[active_object.active_material_index].material = new_material

    # Clear all layers and reset the layer index.
    layers = context.scene.matlay_layers
    layer_stack = context.scene.matlay_layer_stack
    layers.clear()
    layer_stack.layer_index = -1

    # Make a new emission node (used for channel previews).
    material_nodes = new_material.node_tree.nodes
    emission_node = material_nodes.new(type='ShaderNodeEmission')
    emission_node.width = layer_stack.node_default_width
    emission_node.location = (0.0, emission_node.height + node_spacing)

    # Update the principled bsdf node.
    principled_bsdf_node = material_nodes.get('Principled BSDF')
    principled_bsdf_node.width = layer_stack.node_default_width
    principled_bsdf_node.label = "MatLay Material"
    principled_bsdf_node.location = (0.0, 0.0)

    # Make a new mix normal group node for mixing normal and height material channels.
    normal_mix_node = material_nodes.new('ShaderNodeMix')
    normal_mix_node.data_type = 'VECTOR'
    normal_mix_node.name = "MATLAY_NORMALMIX"
    normal_mix_node.label = normal_mix_node.name
    normal_mix_node.location = (0.0, -700.0)
    new_material.node_tree.links.new(normal_mix_node.outputs[0], principled_bsdf_node.inputs[22])

    # Adjust material output node location.
    material_output_node = material_nodes.get('Material Output')
    material_output_node.location = (principled_bsdf_node.width + node_spacing, 0.0)

def prepare_material(context, self):
    '''Ensures a valid material exists in the active material slot for the active object.'''

    # Verify there in an active object.
    active_object = context.active_object
    if not active_object:
        self.report({'INFO'}, "No active object selected, please select an object.")
        return False

    # Verify the active object is a mesh.
    if active_object.type != 'MESH':
        self.report({'INFO'}, "Selected object must be a mesh to create materials for.")
        return False

    # If there is a material in the active material index of the active object, the material is ready for editing.
    if verify_material(context):
        return True
    
    # If the material in the active material slot of the active object doesn't exist, or isn't made with this add-on, create a new material for that slot.
    else:
        create_matlay_material(context)
        return True
