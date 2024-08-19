import bpy
from bpy.types import Menu

def draw_addon_tabs(self, context):
    '''Draws tabs for swapping to different sections in this add-on.'''
    layout = self.layout
    panel_properties = context.scene.matlayer_panel_properties

    # Draw add-on section tabs.
    split = layout.split(factor=0.75, align=True)
    first_column = split.column(align=True)
    second_column = split.column(align=True)

    row = first_column.row(align=True)
    row.scale_y = 2.0
    row.prop_enum(panel_properties, "sections", 'SECTION_LAYERS')
    row.prop_enum(panel_properties, "sections", "SECTION_MESH_MAPS")
    row.prop_enum(panel_properties, "sections", 'SECTION_EXPORT')

    row = second_column.row(align=True)
    row.scale_x = 10
    row.scale_y = 2.0
    row.prop_enum(panel_properties, "sections", 'SECTION_SETTINGS', text="", icon='SETTINGS')
    row.prop_enum(panel_properties, "sections", 'SECTION_VIEWPORT_SETTINGS', text="", icon='RESTRICT_VIEW_OFF')
    row.menu("MATLAYER_MT_utility_sub_menu", text="", icon='TOOL_SETTINGS')

class UtilitySubMenu(Menu):
    bl_idname = "MATLAYER_MT_utility_sub_menu"
    bl_label = "Utility Sub Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("matlayer.append_workspace", text="Append Workspace")
        layout.operator("matlayer.append_basic_brushes", text="Append Basic Brushes")
        layout.operator("matlayer.append_hdri_world", text="Append HDRI World")
        layout.operator("matlayer.remove_unused_textures", text="Remove Unused Textures")