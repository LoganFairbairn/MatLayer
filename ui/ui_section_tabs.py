# This file handles drawing Coater's main section tabs.

import bpy

def draw_section_tabs(self, context):
    layout = self.layout
    panel_properties = context.scene.coater_panel_properties

    # Draw add-on section buttons.
    row = layout.row(align=True)
    row.prop_enum(panel_properties, "sections", 'SECTION_BAKE')
    row.prop_enum(panel_properties, "sections", 'SECTION_LAYERS')
    row.prop_enum(panel_properties, "sections", 'SECTION_EXPORT')
    row.scale_y = 2.0