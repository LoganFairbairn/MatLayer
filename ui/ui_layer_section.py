# This file handles drawing the user interface for the layers section.

import bpy
from ..ui import ui_section_tabs

SCALE_Y = 1.4

def draw_layers_section_ui(self, context):
    '''Draws the layer section user interface to the add-on side panel.'''
    ui_section_tabs.draw_section_tabs(self, context)
    layout = self.layout

    split = layout.split()
    column_one = split.column()
    column_two = split.column()

    row = column_one.row()
    row.label(text="Column One...")

    row = column_two.row()
    draw_material_selector(column_two)

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
        row.operator("matlayer.read_layer_nodes", text="", icon='FILE_REFRESH')
        row.scale_y = 1.5