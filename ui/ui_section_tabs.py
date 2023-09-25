import bpy
from bpy.types import Menu

def draw_section_tabs(self, context):
    '''Draws tabs for swapping to different sections in this add-on.'''
    layout = self.layout
    panel_properties = context.scene.matlayer_panel_properties

    # Draw add-on section buttons.
    row = layout.row(align=True)
    row.scale_y = 2.0
    row.prop_enum(panel_properties, "sections", 'SECTION_TEXTURE_SET')
    row.prop_enum(panel_properties, "sections", "SECTION_MESH_MAPS")
    row.prop_enum(panel_properties, "sections", 'SECTION_LAYERS')
    row.prop_enum(panel_properties, "sections", 'SECTION_EXPORT')
    row.prop_enum(panel_properties, "sections", 'SECTION_SETTINGS', text="", icon='SETTINGS')
    row.menu("MATLAYER_MT_utility_sub_menu", text="", icon='TOOL_SETTINGS')

class UtilitySubMenu(Menu):
    bl_idname = "MATLAYER_MT_utility_sub_menu"
    bl_label = "Utility Sub Menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("matlayer.append_workspace", text="Append Workspace")
        layout.operator("matlayer.append_basic_brushes", text="Append Basic Brushes")