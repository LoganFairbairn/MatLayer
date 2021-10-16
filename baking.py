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

# Baking settings.
class COATER_baking_properties(bpy.types.PropertyGroup):
    ao_bake_image_name: bpy.props.StringProperty(
        name="",
        description="The baking AO image",
        default="")

class COATER_OT_apply_color_grid(bpy.types.Operator):
    bl_idname = "coater.apply_color_grid"
    bl_label = "Apply Color Grid"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Applied a color grid to the selected object."

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        # Store the active object.
        active_object = bpy.context.active_object

        # Check to see if there is an existing image.
        color_grid_image = bpy.data.images.get("ColorGrid")
        if color_grid_image != None:
            bpy.data.images.remove(color_grid_image)

        # Create a a new color grid texture.
        color_grid_image = bpy.ops.image.new(name='ColorGrid', width=2048, height=2048, color=(
            0.0, 0.0, 0.0, 1.0), alpha=False, generated_type='COLOR_GRID', float=False, use_stereo_3d=False, tiled=False)

        # Remove existing material slots from the object.
        for x in bpy.context.object.material_slots:
            bpy.context.object.active_material_index = 0
            bpy.ops.object.material_slot_remove()

        # Check to see if there is a material with the name ColorGrid.
        color_grid_material = bpy.data.materials.get("ColorGrid")
        if color_grid_material != None:
            bpy.data.materials.remove(color_grid_material)

        # Create a new material.
        color_grid_material = bpy.data.materials.new(name="ColorGrid")
        color_grid_material.use_nodes = True

        # Add the color grid material to the object's material list.
        active_object.data.materials.append(color_grid_material)
        nodes = color_grid_material.node_tree.nodes

        material_output = nodes.get("Material Output")

        # Remove Principaled BSDF
        bsdf_node = nodes.get("Principled BSDF")
        if bsdf_node != None:
            nodes.remove(bsdf_node)

        # Add an emission node.
        node_emission = nodes.new(type='ShaderNodeEmission')

        # Add an color grid image texture as an image node.
        color_grid_image_node = nodes.new(type='ShaderNodeTexImage')
        color_grid_image_node.image = bpy.data.images["ColorGrid"]

        # Link nodes.
        links = color_grid_material.node_tree.links
        links.new(node_emission.outputs[0], material_output.inputs[0])
        links.new(color_grid_image_node.outputs[0], node_emission.inputs[0])

        # Change viewport shading to material mode.
        bpy.context.space_data.shading.type = 'MATERIAL'

        return {'FINISHED'}

class COATER_OT_bake_common_maps(bpy.types.Operator):
    bl_idname = "coater.bake_common_maps"
    bl_label = "Bake common maps"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bpy.ops.coater.bake_ambient_occlusion()
        bpy.ops.coater.bake_curvature()
        return {'FINISHED'}

# Bakes ambient occlusion for the active object.
class COATER_OT_bake_ambient_occlusion(bpy.types.Operator):
    bl_idname = "coater.bake_ambient_occlusion"
    bl_label = "Bake Ambient Occlusion"
    bl_options = {'REGISTER', 'UNDO'}

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

# Bakes low poly curvature texture map for the active object.
class COATER_OT_bake_curvature(bpy.types.Operator):
    bl_idname = "coater.bake_curvature"
    bl_label = "Bake Curvature"
    bl_options = {'REGISTER', 'UNDO'}

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
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'

        return {'FINISHED'}

# Bakes low poly curvature texture map for the active object.
class COATER_OT_bake_edges(bpy.types.Operator):
    bl_idname = "coater.bake_edges"
    bl_label = "Bake Edges"
    bl_options = {'REGISTER', 'UNDO'}

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
        geometry_node = nodes.new(type='ShaderNodeNewGeometry')
        invert_node = nodes.new(types='ShaderNodeInvert')
        bevel_node = nodes.new(types='ShaderNodeBevel')

        # Set node values.
        image_node.image = bpy.data.images[bake_image_name]


        # Link Nodes
        links = bake_material.node_tree.links

        links.new(emission_node.outputs[0], material_output_node.inputs[0])

        # Bake
        image_node.select = True
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.bake_type = 'EMIT'
        bpy.ops.object.bake(type='EMIT')

        # Remove the material.
        bpy.data.materials.remove(bake_material)
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'

        return {'FINISHED'}
