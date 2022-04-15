# This file contains functions for creating and verifying Coater materials.

import bpy

# Makes sure the material on the active object is Coater compatible.
# Returns true if the material is compatable with Coater, returns false if not.
def check_coater_material(context):
    active_object = context.active_object
    if active_object == None:
        return False
    
    active_material = context.active_object.active_material
    if active_material == None:
        return False

    principled_bsdf = active_material.node_tree.nodes.get('Principled BSDF')
    if principled_bsdf != None:
        if principled_bsdf.label == "Coater PBR":
            return True
        else:
            return False
    else:
        return False

# Creates and prepares a Coater specific material.
def create_coater_material(context, active_object):
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

    # Get the principled BSDF & material output node.
    principled_bsdf_node = material_nodes.get('Principled BSDF')
    principled_bsdf_node.width = layer_stack.node_default_width
    material_output_node = material_nodes.get('Material Output')

    # Set the label of the Principled BSDF node (allows this material to be identified as a Coater material).
    principled_bsdf_node.label = "Coater PBR"

    # Set the default value for emission to 5, this makes the emission easier to see.
    principled_bsdf_node.inputs[20].default_value = 5

    # Turn Eevee bloom on, this also makes emission easier to see.
    context.scene.eevee.use_bloom = True

    # Adjust nodes locations.
    node_spacing = context.scene.coater_layer_stack.node_spacing
    principled_bsdf_node.location = (0.0, 0.0)
    material_output_node.location = (principled_bsdf_node.width + node_spacing, 0.0)
    emission_node.location = (0.0, emission_node.height + node_spacing)

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
    return {'FINISHED'}

def remove_all_material_slots():
    for x in bpy.context.object.material_slots:
        bpy.context.object.active_material_index = 0
        bpy.ops.object.material_slot_remove()
