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
# This file contains operators that quickly bake common texture maps.

import bpy
from bpy.types import Operator

# Baking settings.
class COATER_baking_properties(bpy.types.PropertyGroup):
    bake_type: bpy.props.EnumProperty(
        items=[('AMBIENT_OCCLUSION', "Ambient Occlusion", ""),
               ('CURVATURE', "Curvature", ""),
               ('EDGES', 'Edges', "")],
        name="Bake Types",
        description="Projection type of the image attached to the selected layer",
        default='AMBIENT_OCCLUSION',
    )

    ambient_occlusion_image_name: bpy.props.StringProperty(name="", description="The baking AO image", default="")
    ambient_occlusion_intensity: bpy.props.FloatProperty(default=1.0, name="Ambient Occlusion Intensity")

    curvature_image_name: bpy.props.StringProperty(name="", description="The baked curvature for object", default="")
    curvature_edge_intensity: bpy.props.FloatProperty(default=1.0, name="Curvature Edge Radius")
    curvature_edge_radius: bpy.props.FloatProperty(default=0.01, name="Curvature Edge Radius")

    edge_image_name: bpy.props.StringProperty(name="Edge Image", description="Edge texture map.", default="")
    edge_intensity: bpy.props.FloatProperty(default=1.0, name="Edge Intensity")
    edge_radius: bpy.props.FloatProperty(default=0.01, name="Edge Radius")

# Bakes all selected texture maps.
class COATER_OT_bake(Operator):
    bl_idname = "coater.bake"
    bl_label = "Bake"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bpy.ops.coater.bake_ambient_occlusion()
        bpy.ops.coater.bake_curvature()
        return {'FINISHED'}

# Bakes ambient occlusion for the active object.
class COATER_OT_bake_ambient_occlusion(Operator):
    bl_idname = "coater.bake_ambient_occlusion"
    bl_label = "Bake Ambient Occlusion"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        # Store the active object.
        active_object = bpy.context.active_object

        bake_image_name = active_object.name + "_AO"

        # Delete existing bake image if it exists.
        image = bpy.data.images.get(bake_image_name)
        if image != None:
            bpy.data.images.remove(image)

        # Make a new bake image.
        image = bpy.ops.image.new(name=bake_image_name,
                                  width=1024,
                                  height=1024,
                                  color=(0.0, 0.0, 0.0, 1.0),
                                  alpha=False,
                                  generated_type='BLANK',
                                  float=False,
                                  use_stereo_3d=False,
                                  tiled=False)

        # Create a material for baking.
        bake_material_name = "Coater_Bake_AmbientOcclusion"
        bake_material = bpy.data.materials.get(bake_material_name)

        if bake_material != None:
            bpy.data.materials.remove(bake_material)

        bake_material = bpy.data.materials.new(name=bake_material_name)
        bake_material.use_nodes = True

        # Remove existing material slots from the object.
        for x in context.object.material_slots:
            context.object.active_material_index = 0
            bpy.ops.object.material_slot_remove()

        # Add the bake material to the active object's material slots.
        active_object.data.materials.append(bake_material)

        # Add nodes.
        nodes = bake_material.node_tree.nodes

        bsdf_node = nodes.get("Principled BSDF")
        if bsdf_node != None:
            nodes.remove(bsdf_node)

        material_output_node = nodes.get("Material Output")
        image_node = nodes.new(type='ShaderNodeTexImage')
        emission_node = nodes.new(type='ShaderNodeEmission')
        ao_node = nodes.new(type='ShaderNodeAmbientOcclusion')
        color_ramp_node = nodes.new(type='ShaderNodeValToRGB')
        intensity_node = nodes.new(type='ShaderNodeMath')

        # Set node values.
        image_node.image = bpy.data.images[bake_image_name]
        intensity_node.inputs[1].default_value = 3
        intensity_node.operation = 'MULTIPLY'
        color_ramp_node.color_ramp.elements[0].position = 0.4

        # Link Nodes
        links = bake_material.node_tree.links
        links.new(ao_node.outputs[0], color_ramp_node.inputs[0])
        links.new(color_ramp_node.outputs[0], intensity_node.inputs[0])
        links.new(intensity_node.outputs[0], emission_node.inputs[0])
        links.new(emission_node.outputs[0], material_output_node.inputs[0])

        # Bake
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.bake_type = 'EMIT'
        bpy.ops.object.bake(type='EMIT')

        # Remove the material.
        bpy.data.materials.remove(bake_material)
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'

        return {'FINISHED'}

class COATER_OT_preview_ambient_occlusion(Operator):
    bl_idname = "coater.preview_ambient_occlusion"
    bl_label = "Preview Coater"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}

# Bakes low poly curvature texture map for the active object.
class COATER_OT_bake_curvature(Operator):
    bl_idname = "coater.bake_curvature"
    bl_label = "Bake Curvature"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        # Store the active object.
        active_object = bpy.context.active_object

        bake_image_name = active_object.name + "_Curvature"

        # Delete existing bake image if it exists.
        image = bpy.data.images.get(bake_image_name)
        if image != None:
            bpy.data.images.remove(image)

        # Make a new bake image.
        image = bpy.ops.image.new(name=bake_image_name,
                                  width=1024,
                                  height=1024,
                                  color=(0.0, 0.0, 0.0, 1.0),
                                  alpha=False,
                                  generated_type='BLANK',
                                  float=False,
                                  use_stereo_3d=False,
                                  tiled=False)

        # Create a material for baking.
        bake_material_name = "Coater_Bake_Curvature"
        bake_material = bpy.data.materials.get(bake_material_name)
        

        if bake_material != None:
            bpy.data.materials.remove(bake_material)

        bake_material = bpy.data.materials.new(name=bake_material_name)
        bake_material.use_nodes = True

        # Remove existing material slots from the object.
        for x in context.object.material_slots:
            context.object.active_material_index = 0
            bpy.ops.object.material_slot_remove()

        # Add the bake material to the active object's material slots.
        active_object.data.materials.append(bake_material)

        # Add nodes.
        nodes = bake_material.node_tree.nodes

        bsdf_node = nodes.get("Principled BSDF")
        if bsdf_node != None:
            nodes.remove(bsdf_node)

        material_output_node = nodes.get("Material Output")
        image_node = nodes.new(type='ShaderNodeTexImage')
        emission_node = nodes.new(type='ShaderNodeEmission')
        geometry_node = nodes.new(type='ShaderNodeNewGeometry')
        color_ramp_node = nodes.new(type='ShaderNodeValToRGB')

        # Set node values.
        image_node.image = bpy.data.images[bake_image_name]
        color_ramp_node.color_ramp.elements[0].position = 0.4
        color_ramp_node.color_ramp.elements[0].color = (0.132868, 0.132868, 0.132868, 1.0)

        # Link Nodes
        links = bake_material.node_tree.links
        links.new(geometry_node.outputs[7], color_ramp_node.inputs[0])
        links.new(color_ramp_node.outputs[0], emission_node.inputs[0])
        links.new(emission_node.outputs[0], material_output_node.inputs[0])

        # Bake
        image_node.select = True
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.bake_type = 'EMIT'
        bpy.ops.object.bake(type='EMIT')

        # Remove the material.
        bpy.data.materials.remove(bake_material)
        context.scene.render.engine = 'BLENDER_EEVEE'

        return {'FINISHED'}

# Bakes low poly curvature texture map for the active object.
class COATER_OT_bake_edges(Operator):
    bl_idname = "coater.bake_edges"
    bl_label = "Bake Edges"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        # Store the active object.
        active_object = bpy.context.active_object

        bake_image_name = active_object.name + "_Edges"

        # Delete existing bake image if it exists.
        image = bpy.data.images.get(bake_image_name)
        if image != None:
            bpy.data.images.remove(image)

        # Make a new bake image.
        image = bpy.ops.image.new(name=bake_image_name,
                                  width=1024,
                                  height=1024,
                                  color=(0.0, 0.0, 0.0, 1.0),
                                  alpha=False,
                                  generated_type='BLANK',
                                  float=False,
                                  use_stereo_3d=False,
                                  tiled=False)

        # Create a material for baking.
        bake_material_name = "Coater_Bake_Edges"
        bake_material = bpy.data.materials.get(bake_material_name)
        

        if bake_material != None:
            bpy.data.materials.remove(bake_material)

        bake_material = bpy.data.materials.new(name=bake_material_name)
        bake_material.use_nodes = True

        # Remove existing material slots from the object.
        for x in context.object.material_slots:
            context.object.active_material_index = 0
            bpy.ops.object.material_slot_remove()

        # Add the bake material to the active object's material slots.
        active_object.data.materials.append(bake_material)

        # Add nodes.
        nodes = bake_material.node_tree.nodes

        bsdf_node = nodes.get("Principled BSDF")
        if bsdf_node != None:
            nodes.remove(bsdf_node)

        material_output_node = nodes.get("Material Output")
        image_node = nodes.new(type='ShaderNodeTexImage')
        emission_node = nodes.new(type='ShaderNodeEmission')
        vector_math_node = nodes.new(type='ShaderNodeVectorMath')
        math_node = nodes.new(type='ShaderNodeMath')
        geometry_node = nodes.new(type='ShaderNodeNewGeometry')
        invert_node = nodes.new(type='ShaderNodeInvert')
        bevel_node = nodes.new(type='ShaderNodeBevel')

        # Set node values.
        image_node.image = bpy.data.images[bake_image_name]
        bevel_node.inputs[0].default_value = 0.01
        math_node.operation = 'MULTIPLY'
        math_node.inputs[0].default_value = 1.0
        vector_math_node.operation = 'DOT_PRODUCT'

        # Link Nodes
        links = bake_material.node_tree.links

        links.new(material_output_node.inputs[0], emission_node.outputs[0])
        links.new(emission_node.inputs[0], invert_node.outputs[0])
        links.new(invert_node.inputs[1], math_node.outputs[0])

        # This node never links to math node.
        links.new(math_node.inputs[1], vector_math_node.outputs[1])
        links.new(vector_math_node.inputs[1], geometry_node.outputs[1])
        links.new(vector_math_node.inputs[0], bevel_node.outputs[0])
        
        # Bake
        image_node.select = True
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.bake_type = 'EMIT'
        bpy.ops.object.bake(type='EMIT')

        # Remove the material.
        bpy.data.materials.remove(bake_material)
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'

        return {'FINISHED'}
