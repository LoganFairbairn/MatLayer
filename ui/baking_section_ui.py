import bpy
from .import draw_section_buttons

def draw_baking_section_ui(self, context):
    layout = self.layout
    addon_preferences = context.preferences.addons["Coater"].preferences
    baking_properties = context.scene.coater_baking_properties

    draw_section_buttons.draw_section_buttons(self, context)    # Draw section buttons.
    layout.prop(addon_preferences, "bake_folder")               # Draw the bake folder.

    # Bake
    row = layout.row()
    row.operator("coater.bake")
    row.scale_y = 2.0

    # Toggles
    scale_y = 1.4

    row = layout.row()
    row.prop(addon_preferences, "bake_ao", text="")
    row.prop_enum(baking_properties, "bake_type", 'AMBIENT_OCCLUSION')
    row.operator("coater.bake_ambient_occlusion", text="", icon='RENDER_STILL')
    row.scale_y = scale_y

    row = layout.row()
    row.prop(addon_preferences, "bake_curvature", text="")
    row.prop_enum(baking_properties, "bake_type", 'CURVATURE')
    row.operator("coater.bake_curvature", text="", icon='RENDER_STILL')
    row.scale_y = scale_y

    row = layout.row()
    row.prop(addon_preferences, "bake_edges", text="")
    row.prop_enum(baking_properties, "bake_type", 'EDGES')
    row.operator("coater.bake_edges", text="", icon='RENDER_STILL')
    row.scale_y = scale_y

    # Draw global bake settings.
    layout.label(text="Global Bake Settings:")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(baking_properties, "output_size", text="")
    row.prop(baking_properties, "output_quality", text="")

    row = layout.row()
    row.scale_y = scale_y
    row.prop(bpy.data.scenes["Scene"].cycles, "device", text="")
    row.prop(bpy.data.scenes["Scene"].render.bake, "margin", slider=True)

    # Draw specific bake settings based on selected bake type.
    if baking_properties.bake_type == 'AMBIENT_OCCLUSION':
        layout.label(text="Ambient Occlusion Bake Settings:")
        layout.prop(baking_properties, "ambient_occlusion_intensity", slider=True)
        layout.prop(baking_properties, "ambient_occlusion_samples", slider=True)
        row = layout.row()
        row.prop(baking_properties, "ambient_occlusion_local")
        row.prop(baking_properties, "ambient_occlusion_inside")

    if baking_properties.bake_type == 'CURVATURE':
        layout.label(text="Curvature Bake Settings:")
        layout.prop(baking_properties, "curvature_edge_intensity", slider=True)
        layout.prop(baking_properties, "curvature_edge_radius", slider=True)

    if baking_properties.bake_type == 'EDGES':
        layout.label(text="Edge Bake Settings")
        layout.prop(baking_properties, "edge_intensity", slider=True)
        layout.prop(baking_properties, "edge_radius", slider=True)