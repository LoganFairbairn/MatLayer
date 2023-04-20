def draw_section_tabs(self, context):
    '''Draws tabs for swapping to different sections in this add-on.'''
    layout = self.layout
    panel_properties = context.scene.matlay_panel_properties

    # Draw add-on section buttons.
    row = layout.row(align=True)
    row.prop_enum(panel_properties, "sections", 'SECTION_TEXTURE_SET')
    row.prop_enum(panel_properties, "sections", "SECTION_BAKING")
    row.prop_enum(panel_properties, "sections", 'SECTION_LAYERS')
    row.prop_enum(panel_properties, "sections", 'SECTION_EXPORT')
    row.prop_enum(panel_properties, "sections", 'SECTION_SETTINGS', text="", icon='SETTINGS')
    row.scale_y = 2.0