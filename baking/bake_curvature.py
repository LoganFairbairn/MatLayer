import bpy
from bpy.types import Operator
from .import bake_functions

# Bakes low poly curvature texture map for the active object.
class COATER_OT_bake_curvature(Operator):
    bl_idname = "coater.bake_curvature"
    bl_label = "Bake Curvature"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bake_type = "Curvature"
        if bake_functions.verify_bake_object(self, context):
            bake_image_name = bake_functions.create_bake_image(context, bake_type)
            original_material = bake_functions.empty_material_slots(context)
            bake_material = bake_functions.add_new_bake_material(context, "Coater_Curvature")
            add_curvature_nodes(context, bake_material, bake_image_name)
            bake_functions.start_bake()
            bake_functions.set_output_quality()
            bake_functions.end_bake(bake_material, original_material)
            bake_functions.save_bake(bake_image_name)
            return {'FINISHED'}

class COATER_OT_delete_curvature_map(Operator):
    bl_idname = "coater.delete_curvature_map"
    bl_label = "Delete Curvature Map"
    bl_description = "Deletes the baked curvature map for the active object if one exists"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}

def add_curvature_nodes(context, material, image_name):
    nodes = material.node_tree.nodes

    bsdf_node = nodes.get("Principled BSDF")
    if bsdf_node != None:
        nodes.remove(bsdf_node)

    # Required Nodes
    material_output_node = nodes.get("Material Output")
    image_node = nodes.new(type='ShaderNodeTexImage')
    emission_node = nodes.new(type='ShaderNodeEmission')

    # Ambient Occlusion Mask Nodes
    ao_node = nodes.new(type='ShaderNodeAmbientOcclusion')
    ao_color_ramp_node = nodes.new(type='ShaderNodeValToRGB')
    ao_invert_node = nodes.new(type='ShaderNodeInvert')
    ao_masking_node = nodes.new(type='ShaderNodeMath')

    # Edge Nodes
    edge_bevel_node = nodes.new(type='ShaderNodeBevel')
    edge_geometry_node = nodes.new(type='ShaderNodeNewGeometry')
    edge_vector_math_node = nodes.new(type='ShaderNodeVectorMath')
    edge_invert_node = nodes.new(type='ShaderNodeInvert')
    edge_intensity_node = nodes.new(type='ShaderNodeMath')

    # Ambient Occlusion Masking
    ao_mix_mask_node = nodes.new(type='ShaderNodeMixRGB')

    # Pointiness Nodes
    curvature_geometry_node = nodes.new(type='ShaderNodeNewGeometry')
    curvature_color_ramp_node = nodes.new(type='ShaderNodeValToRGB')

    # Pointiness Edges Mix
    pointiness_mix_node = nodes.new(type='ShaderNodeMixRGB')

    # Set node values.
    baking_settings = context.scene.coater_baking_settings

    if image_name != "":
        image_node.image = bpy.data.images[image_name]

    ao_node.only_local = True
    ao_node.samples = baking_settings.ambient_occlusion_samples
    ao_masking_node.operation = 'MULTIPLY'

    edge_bevel_node.inputs[0].default_value = baking_settings.curvature_edge_radius
    edge_vector_math_node.operation = 'DOT_PRODUCT'
    edge_intensity_node.operation = 'MULTIPLY'
    edge_intensity_node.inputs[1].default_value = baking_settings.curvature_edge_intensity

    ao_masking_node.inputs[1].default_value = baking_settings.curvature_ao_masking
    ao_mix_mask_node.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
    ao_color_ramp_node.color_ramp.elements[0].position = 0.2
    ao_color_ramp_node.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)

    curvature_color_ramp_node.color_ramp.elements[0].position = 0.5
    curvature_color_ramp_node.color_ramp.elements[0].color = (0.25, 0.25, 0.25, 1.0)

    pointiness_mix_node.blend_type = 'SCREEN'
    pointiness_mix_node.inputs[0].default_value = 1

    # Link Nodes
    links = material.node_tree.links

    links.new(material_output_node.inputs[0], emission_node.outputs[0])
    links.new(emission_node.inputs[0], pointiness_mix_node.outputs[0])
        
    links.new(pointiness_mix_node.inputs[1], curvature_color_ramp_node.outputs[0])
    links.new(pointiness_mix_node.inputs[2], ao_mix_mask_node.outputs[0])

    links.new(curvature_color_ramp_node.inputs[0], curvature_geometry_node.outputs[7])

    links.new(ao_mix_mask_node.inputs[0], ao_masking_node.outputs[0])
    links.new(ao_mix_mask_node.inputs[1], edge_intensity_node.outputs[0])

    links.new(ao_masking_node.inputs[0], ao_invert_node.outputs[0])
    links.new(ao_invert_node.inputs[1], ao_color_ramp_node.outputs[0])
    links.new(ao_color_ramp_node.inputs[0], ao_node.outputs[0])

    links.new(edge_intensity_node.inputs[0], edge_invert_node.outputs[0])
    links.new(edge_invert_node.inputs[1], edge_vector_math_node.outputs[1])
    links.new(edge_vector_math_node.inputs[0], edge_bevel_node.outputs[0])
    links.new(edge_vector_math_node.inputs[1], edge_geometry_node.outputs[1])