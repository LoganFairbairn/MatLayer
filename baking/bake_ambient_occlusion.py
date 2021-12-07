# Copyright (c) 2021 Logan Fairbairn
# logan-fairbairn@outlook.com
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

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

class COATER_OT_toggle_ambient_occlusion_preview(Operator):
    bl_idname = "coater.toggle_ambient_occlusion_preview"
    bl_label = "Preview Ambient Occlusion"
    bl_description = "Previews ambient occlusion bake result on the active object"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        material_name = "Coater_AmbientOcclusion"

        if bake_functions.verify_bake_object(self, context):
            bake_functions.empty_material_slots(context)
            preview_material = bake_functions.add_new_bake_material(context, material_name)
            add_ambient_occlusion_nodes(context, preview_material, "")
            bpy.context.scene.render.engine = 'CYCLES'
            if context.space_data.type == 'VIEW_3D':
                context.space_data.shading.type = 'RENDERED'
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