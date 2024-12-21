from bpy.types import Menu

def draw_addon_tabs(self, context):
    '''Draws tabs for swapping to different sections in this add-on.'''
    layout = self.layout
    panel_properties = context.scene.matlayer_panel_properties

    # Draw add-on section tabs.
    row = layout.row(align=True)
    row.scale_y = 2.0
    row.prop_enum(panel_properties, "sections", 'SECTION_EDIT', text="EDIT LAYERS")
    row.prop_enum(panel_properties, "sections", "SECTION_MESH_MAPS", text="MESH MAPS")
    row.prop_enum(panel_properties, "sections", 'SECTION_EXPORT', text="EXPORT TEXTURES")
    row.prop_enum(panel_properties, "sections", 'SECTION_SETTINGS', text="SETTINGS")
    row.prop_enum(panel_properties, "sections", 'SECTION_VIEWPORT_SETTINGS', text="VIEW")

class UtilitySubMenu(Menu):
    bl_idname = "MATLAYER_MT_utility_sub_menu"
    bl_label = "Utility Sub Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("matlayer.append_workspace", text="Append Workspace")
        layout.operator("matlayer.append_material_ball", text="Append Material Ball")
        layout.operator("matlayer.append_basic_brushes", text="Append Basic Brushes")
        layout.operator("matlayer.remove_unused_textures", text="Remove Unused Textures")
        layout.operator("matlayer.apply_default_shader", text="Apply Default Shader")