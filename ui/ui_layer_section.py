# This file handles drawing the user interface for the layers section.

import bpy
from ..ui import ui_section_tabs

SCALE_Y = 1.4

def draw_layers_section_ui(self, context):
    '''Draws the layer section.'''
    ui_section_tabs.draw_section_tabs(self, context)
    layout = self.layout

    split = layout.split()
    column_one = split.column()
    column_two = split.column()

    row = column_one.row()
    row.label(text="Column One...")

    row = column_two.row()
    row.label(text="Thing...")