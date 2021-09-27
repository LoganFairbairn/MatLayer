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
# All layer functionality is handled here.

import bpy


class LayerProperties(bpy.types.PropertyGroup):
    '''Layer stack item.'''
    current_material_name: bpy.props.StringProperty(
        name="",
        description="The name of the currently selected material",
        default=""
    )

    layer_name: bpy.props.StringProperty(
        name="",
        description="The name of the layer",
        default="Layer naming error")

    layer_hidden: bpy.props.BoolProperty(name="")

    layer_type: bpy.props.EnumProperty(
        items=[('COLOR_LAYER', "", ""),
               ('FILL_LAYER', "", "")],
        name="",
        description="Type of the layer",
        default=None,
        options={'HIDDEN'}
    )

    layer_masked: bpy.props.BoolProperty(name="")

    layer_opacity: bpy.props.FloatProperty(name="",
                                           description="Opacity of the currently selected layer.",
                                           default=1.0,
                                           min=0.0,
                                           max=1.0,
                                           subtype='FACTOR')


class COATER_UL_layer_list(bpy.types.UIList):
    '''Draws the layer stack.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Draw the layer hide icon.
            if item.layer_hidden == True:
                layout.prop(item, "layer_hidden", text="",
                            emboss=False, icon='HIDE_ON')

            elif item.layer_hidden == False:
                layout.prop(item, "layer_hidden", text="",
                            emboss=False, icon='HIDE_OFF')

            # Draw the layer's name.
            layout.prop(item, "layer_name", text="",
                        emboss=False, icon_value=icon)

            # Draw the layer mask icon.
            if (item.layer_masked == True):
                layout.prop(item, "layer_masked", text="",
                            emboss=False, icon='MOD_MASK')

            # Draw the layer type.
            if (item.layer_type == "COLOR_LAYER"):
                layout.prop(item, "layer_type", text="",
                            emboss=False, icon='COLOR')

            elif item.layer_type == "FILL_LAYER":
                layout.prop(item, "layer_type", text="", emboss=False, icon='')

            # Draw the layers opacity.
            layout.prop(item, "layer_opacity")


class COATER_OT_add_layer(bpy.types.Operator):
    '''Add a new layer to the layer stack.'''
    bl_idname = "coater.add_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds a new layer."

    def execute(self, context):
        # Adds the layer to the list.
        context.scene.my_list.add()
        new_layer_name = "layer " + str(len(context.scene.my_list) - 1)
        context.scene.my_list[len(
            context.scene.my_list) - 1].layer_name = new_layer_name

        # Make a new image.
        layer_image = bpy.ops.image.new(name=new_layer_name, width=2048, height=2048, color=(
            0.0, 0.0, 0.0, 1.0), alpha=False, generated_type='BLANK', float=False, use_stereo_3d=False, tiled=False)
        return {'FINISHED'}


class COATER_OT_add_color_layer(bpy.types.Operator):
    '''Adds a new color layer to the layer stack'''
    bl_idname = "coater.add_color_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds a new color layer"

    def execute(self, context):
        # Store the active object.
        selected_object = bpy.context.active_object

        # TODO: Make sure there is a material on the selected object.
        if len(selected_object.material_slots) == -1:
            coater_material = bpy.data.materials.new(name="coater_Material")
            selected_object.data.materials.append(coater_material)
            coater_material.use_nodes = True

        # Adds the layer to the list.
        context.scene.my_list.add()
        new_layer_name = "layer " + str(len(context.scene.my_list) - 1)
        context.scene.my_list[len(
            context.scene.my_list) - 1].layer_name = new_layer_name

        # TODO: Set up color layer nodes.

        return {'FINISHED'}


class COATER_OT_delete_layer(bpy.types.Operator):
    '''Deletes the currently selected layer from the layer stack.'''
    bl_idname = "coater.delete_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the currently selected layer"

    @ classmethod
    def poll(cls, context):
        return context.scene.my_list

    def execute(self, context):
        my_list = context.scene.my_list
        index = context.scene.layer_index

        my_list.remove(index)
        context.scene.layer_index = min(max(0, index - 1), len(my_list) - 1)

        # TODO: Disconnect and reconnect nodes.

        return {'FINISHED'}


class COATER_OT_move_layer(bpy.types.Operator):
    """Moves the selecter layer up on the layer stack."""
    bl_idname = "coater.move_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the currently selected layer"

    # Use enums, to go up or down in the list.
    direction = bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))

    # Poll tests if the operator can be called or not.
    @ classmethod
    def poll(cls, context):
        return context.scene.my_list

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        index = bpy.context.scene.layer_index
        list_length = len(bpy.context.scene.my_list) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        bpy.context.scene.layer_index = max(0, min(new_index, list_length))

    def execute(self, context):
        my_list = context.scene.my_list
        index = context.scene.layer_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        my_list.move(neighbor, index)
        self.move_index()

        # TODO: Disconnect and reconnect nodes.

        return{'FINISHED'}


class COATER_OT_merge_layer(bpy.types.Operator):
    """Merges the selected layer with the layer below."""
    bl_idname = "coater.merge_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Merges the selected layer with the layer below."

    def execute(self, context):
        return{'FINISHED'}


class COATER_OT_duplicate_layer(bpy.types.Operator):
    """Duplicates the selected layer."""
    bl_idname = "coater.duplicate_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Duplicates the selected layer."

    def execute(self, context):
        return{'FINISHED'}
