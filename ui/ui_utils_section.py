from . import ui_section_tabs

def draw_ui_utils_section(self, context):
    ui_section_tabs.draw_section_tabs(self, context)

    # Render engine so users can swap through the interface.
    layout = self.layout
    scale_y = 1.4
    row = layout.row()
    row.scale_y = scale_y
    row.operator("matlayer.append_workspace", icon='IMPORT')

    row = layout.row()
    row.scale_y = scale_y
    row.operator("matlayer.append_basic_brushes", icon='BRUSH_DATA')

    row = layout.row()
    row.scale_y = scale_y
    row.operator("matlayer.delete_unused_external_images", icon='TRASH')

    row = layout.row()
    row.scale_y = scale_y
    row.operator("matlayer.edit_uvs_externally", icon='UV_ISLANDSEL')