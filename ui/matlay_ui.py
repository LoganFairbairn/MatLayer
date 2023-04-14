# Draws the matlay user interface.

import bpy
from .import ui_layer_section
from .import ui_baking_section
from .import ui_export_section
from .import ui_texture_set_section

class MATLAY_panel_properties(bpy.types.PropertyGroup):
    sections: bpy.props.EnumProperty(
        items=[('SECTION_TEXTURE_SET', "TEXTURE SET", "This section contains texture set settings and mesh map baking options."),
               ('SECTION_BAKING', "BAKING", "This section contains operations to quickly bake mesh maps for your models."),
               ('SECTION_LAYERS', "LAYERS", "This section contains a layer stack for the active material."),
               ('SECTION_EXPORT', "EXPORT", "This section contains operations to quickly export textures made with MatLay.")],
        name="MatLay Sections",
        description="Current matlay category",
        default='SECTION_LAYERS'
    )

class MATLAY_PT_Panel(bpy.types.Panel):
    bl_label = "MatLay " + "0.98" + " Development Build"
    bl_idname = "MATLAY_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MatLay"

    def draw(self, context):
        panel_properties = context.scene.matlay_panel_properties
        self.layout.label(text="Something here")
        if check_blend_saved():
            if panel_properties.sections == 'SECTION_TEXTURE_SET':
                ui_texture_set_section.draw_texture_set_section_ui(self, context)

            if panel_properties.sections == 'SECTION_BAKING':
                ui_baking_section.draw_baking_section_ui(self, context)
                
            if panel_properties.sections == "SECTION_LAYERS":
                ui_layer_section.draw_layers_section_ui(self, context)

            if panel_properties.sections == 'SECTION_EXPORT':
                ui_export_section.draw_export_section_ui(self, context)

        else:
            layout = self.layout
            layout.label(text="Save your .blend file to use MatLay.")
            layout.label(text="The .blend path is used to find correct paths for image folders,")
            layout.label(text="where textures, baked mesh maps, or exported textures created ")
            layout.label(text="using this add-on are saved.")
            
def check_blend_saved():
    if bpy.path.abspath("//") == "":
        return False
    else:
        return True