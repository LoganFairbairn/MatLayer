# This file handles drawing the user interface for the layers section.

import bpy
from bpy.types import Operator
from ..core import material_layers
from ..ui import ui_section_tabs

SCALE_Y = 1.4

def draw_layers_section_ui(self, context):
    '''Draws the layer section user interface to the add-on side panel.'''
    ui_section_tabs.draw_section_tabs(self, context)
    layout = self.layout

    split = layout.split()

    column_one = split.column()
    draw_layer_material_channel_toggles(column_one)
    draw_material_channel_properties(column_one)

    column_two = split.column()
    draw_material_selector(column_two)
    draw_layer_operations(column_two)
    draw_layer_stack(column_two)

def draw_material_selector(layout):
    '''Draws a material selector and layer stack refresh button.'''
    active_object = bpy.context.active_object
    if active_object:
        split = layout.split(factor=0.90, align=True)
        first_column = split.column(align=True)
        second_column = split.column(align=True)
        second_column.scale_x = 0.1

        first_column.template_list("MATERIAL_UL_matslots", "Layers", bpy.context.active_object, "material_slots", bpy.context.active_object, "active_material_index")
        second_column.operator("object.material_slot_add", text="", icon='ADD')
        second_column.operator("object.material_slot_remove", text="-")
        operator = second_column.operator("object.material_slot_move", text="", icon='TRIA_UP')
        operator.direction = 'UP'
        operator = second_column.operator("object.material_slot_move", text="", icon='TRIA_DOWN')
        operator.direction = 'DOWN'
        second_column.operator("object.material_slot_assign", text="", icon='MATERIAL_DATA')
        second_column.operator("object.material_slot_select", text="", icon='SELECT_SET')

        row = layout.row(align=True)
        row.template_ID(active_object, "active_material", new="matlayer.add_layer", live_icon=True)

class MATLAYER_OT_add_material_layer_menu(Operator):
    bl_label = ""
    bl_idname = "matlayer.add_material_layer_menu"
    bl_description = "Opens a menu of material layer types that can be added to the active material"

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

    # Opens the popup when the add layer button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=150)

    # Draws the properties in the popup.
    def draw(self, context):
        layout = self.layout
        split = layout.split()
        col = split.column(align=True)
        col.scale_y = 1.4
        col.operator("matlayer.add_material_layer", text="Add Material Layer", icon='MATERIAL_DATA')
        col.operator("matlayer.add_paint_material_layer", text="Add Paint Layer", icon='BRUSHES_ALL')
        col.operator("matlayer.add_decal_material_layer", text="Add Decal Layer", icon='OUTLINER_OB_FONT')

def draw_layer_operations(layout):
    '''Draws layer operation buttons.'''
    subrow = layout.row(align=True)
    subrow.scale_y = 2.0
    subrow.scale_x = 10
    subrow.operator("matlayer.add_material_layer_menu", icon="ADD", text="")
    operator = subrow.operator("matlayer.move_material_layer", icon="TRIA_UP", text="")
    operator.direction = 'UP'
    operator = subrow.operator("matlayer.move_material_layer", icon="TRIA_DOWN", text="")
    operator.direction = 'DOWN'
    subrow.operator("matlayer.duplicate_layer", icon="DUPLICATE", text="")
    subrow.operator("matlayer.delete_layer", icon="TRASH", text="")

def draw_layer_stack(layout):
    '''Draws the material layer stack along with it's operators and material channel.'''
    if len(bpy.context.scene.matlayer_layers) > 0:
        subrow = layout.row(align=True)
        subrow.template_list("MATLAYER_UL_layer_list", "Layers", bpy.context.scene, "matlayer_layers", bpy.context.scene.matlayer_layer_stack, "selected_layer_index", sort_reverse=True)
        subrow.scale_y = 2

def draw_layer_material_channel_toggles(layout):
    '''Draws on / off toggles for individual material channels.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    row = layout.row()
    row.scale_y = 1.4
    drawn_toggles = 0
    for material_channel_name in material_layers.MATERIAL_CHANNEL_LIST:
        mix_node = material_layers.get_material_layer_node('MIX', selected_layer_index, material_channel_name)
        if mix_node:
            row.prop(mix_node, "mute", text=material_channel_name, toggle=True, invert_checkbox=True)
            drawn_toggles += 1
            if drawn_toggles > 4:
                row = layout.row()
                row.scale_y = 1.4
                drawn_toggles = 0

def draw_material_channel_properties(layout):
    '''Draws properties for all active material channels on selected material layer.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    for material_channel_name in material_layers.MATERIAL_CHANNEL_LIST:
        row = layout.row()
        row.label(text=material_channel_name)

        value_node = material_layers.get_material_layer_node('VALUE', selected_layer_index, material_channel_name)
        if value_node:
            row = layout.row()
            row.scale_y = 1.4

            # Draw values based on the node type used to represent the material channel value.
            match value_node.bl_static_type:
                case 'GROUP':
                    # For group nodes used to represent default material channel values, draw only the first value.
                    if value_node.node_tree.name.startswith('ML_Default'):
                        row.prop(value_node.inputs[0], "default_value", text="")

                    # For custom group nodes, draw all properties to the interface.
                    else:
                        for i in range(0, len(value_node.inputs)):
                            row = layout.row()
                            row.scale_y = 1.4
                            row.prop(value_node.inputs[i], "default_value", text=value_node.inputs[i].name)
