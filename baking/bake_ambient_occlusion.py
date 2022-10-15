import json     # For reading resolution mapping.
import bpy
from bpy.types import Operator
from .import bake_functions

# Bakes ambient occlusion for the active object.
class COATER_OT_bake_ambient_occlusion(Operator):
    bl_idname = "coater.bake_ambient_occlusion"
    bl_label = "Bake Ambient Occlusion"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bake_type = "AO"
        if bake_functions.verify_bake_object(self, context):
            bake_image_name = bake_functions.create_bake_image(context, bake_type)
            original_material = bake_functions.empty_material_slots(context)
            bake_material = bake_functions.add_new_bake_material(context, "Coater_AmbientOcclusion")
            add_ambient_occlusion_nodes(context, bake_material, bake_image_name)
            bake_functions.start_bake()
            bake_functions.set_output_quality()
            bake_functions.end_bake(bake_material, original_material)
            bake_functions.save_bake(bake_image_name)
            return {'FINISHED'}

class COATER_OT_delete_ao_map(Operator):
    bl_idname = "coater.delete_ao_map"
    bl_label = "Delete Ambient Occlusion Map"
    bl_description = "Deletes the baked ambient occlusion map for the active object if one exists"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}

def add_ambient_occlusion_nodes(context, material, image_name):
    # Add nodes.
    nodes = material.node_tree.nodes

    bsdf_node = nodes.get("Principled BSDF")
    if bsdf_node != None:
        nodes.remove(bsdf_node)

    material_output_node = nodes.get("Material Output")
    image_node = nodes.new(type='ShaderNodeTexImage')
    emission_node = nodes.new(type='ShaderNodeEmission')
    ao_node = nodes.new(type='ShaderNodeAmbientOcclusion')
    color_ramp_node = nodes.new(type='ShaderNodeValToRGB')

    # Set node values.
    baking_settings = context.scene.coater_baking_settings
    if image_name != "":
        image_node.image = bpy.data.images[image_name]
    ao_node.only_local = baking_settings.ambient_occlusion_local
    ao_node.samples = baking_settings.ambient_occlusion_samples
    ao_node.inside = baking_settings.ambient_occlusion_inside
    color_ramp_node.color_ramp.elements[0].position = baking_settings.ambient_occlusion_intensity
    color_ramp_node.color_ramp.interpolation = 'EASE'

    # Link Nodes
    links = material.node_tree.links
    links.new(ao_node.outputs[0], color_ramp_node.inputs[0])
    links.new(color_ramp_node.outputs[0], emission_node.inputs[0])
    links.new(emission_node.outputs[0], material_output_node.inputs[0])