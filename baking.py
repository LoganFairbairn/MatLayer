import bpy


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

    def execute(self, context):
        # Store the active object.
        selected_object = bpy.context.active_object

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

        # Add the color grid material to the object's material list.
        selected_object.data.materials.append(color_grid_material)
        color_grid_material.use_nodes = True
        nodes = color_grid_material.node_tree.nodes

        material_output = nodes.get("Material Output")

        # Add an emission node.
        node_emission = nodes.new(type='ShaderNodeEmission')

        # Add an color grid image texture as an image node.
        color_grid_image_node = nodes.new(type='ShaderNodeTexImage')
        color_grid_image_node.image = bpy.data.images["ColorGrid"]

        # Link nodes.
        links = color_grid_material.node_tree.links
        new_link = links.new(
            node_emission.outputs[0], material_output.inputs[0])

        links.new(color_grid_image_node.outputs[0], node_emission.inputs[0])

        # Change viewport shading to material mode.
        bpy.context.space_data.shading.type = 'MATERIAL'

        return {'FINISHED'}


class COATER_OT_bake_ambient_occlusion(bpy.types.Operator):
    bl_idname = "coater.bake_ambient_occlusion"
    bl_label = "Bake Ambient Occlusion"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Store the active object.
        selected_object = bpy.context.active_object

        bake_image_name = selected_object.name + "_AO"

        # Delete existing bake images.
        ao_bake_image = bpy.data.images.get("")
        if ao_bake_image != None:
            bpy.data.images.remove(ao_bake_image)

        # Make a new bake image.
        ao_bake_image = bpy.ops.image.new(name="new_bake_image",
                                          width=2048,
                                          height=2048,
                                          color=(0.0, 0.0, 0.0, 1.0),
                                          alpha=False,
                                          generated_type='BLANK',
                                          float=False,
                                          use_stereo_3d=False,
                                          tiled=False)

        return {'FINISHED'}
