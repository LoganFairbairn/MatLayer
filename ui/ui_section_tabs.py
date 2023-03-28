# This file handles drawing MatLay's main section tabs.

import bpy

def draw_section_tabs(self, context):
    layout = self.layout
    panel_properties = context.scene.matlay_panel_properties

    # Draw add-on section buttons.
    row = layout.row(align=True)
    row.prop_enum(panel_properties, "sections", 'SECTION_TEXTURE_SET')
    row.prop_enum(panel_properties, "sections", "SECTION_BAKING")
    row.prop_enum(panel_properties, "sections", 'SECTION_LAYERS')
    row.prop_enum(panel_properties, "sections", 'SECTION_EXPORT')
    row.scale_y = 2.0