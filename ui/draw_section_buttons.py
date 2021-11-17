import bpy

def draw_section_buttons(self, context):
    layout = self.layout
    panel_properties = context.scene.coater_panel_properties

    # Draw add-on section buttons.
    row = layout.row(align=True)
    row.prop(panel_properties, "sections", expand=True)
    row.scale_y = 2.0