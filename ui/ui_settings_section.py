import bpy
from . import ui_section_tabs

def draw_ui_settings_section(self, context):
    ui_section_tabs.draw_section_tabs(self, context)