import bpy
from bpy.types import Operator

# COLOR GRID
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