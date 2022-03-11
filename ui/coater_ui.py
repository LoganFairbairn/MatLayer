# Draws the coater user interface.

import bpy
from .import ui_layer_section
from .import ui_baking_section
from .import ui_export_section
from .import ui_texture_set_section

class COATER_panel_properties(bpy.types.PropertyGroup):
    sections: bpy.props.EnumProperty(
        items=[('SECTION_TEXTURE_SET', "TEXTURE SET", "This section contains texture set settings and mesh map baking options."),
               ('SECTION_BAKING', "BAKING", "This section contains operations to quickly bake mesh maps for your models."),
               ('SECTION_LAYERS', "LAYERS", "This section contains a layer stack for the active material."),
               ('SECTION_EXPORT', "EXPORT", "This section contains operations to quickly export textures made with Coater.")],
        name="Coater Sections",
        description="Current coater category",
        default='SECTION_LAYERS'
    )

class COATER_PT_Panel(bpy.types.Panel):
    bl_label = "Coater " + "0.71"
    bl_idname = "COATER_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Coater"

    def draw(self, context):
        panel_properties = context.scene.coater_panel_properties

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
            layout.label(text="Save your .blend file to use Coater.")

def check_blend_saved():
    if bpy.path.abspath("//") == "":
        return False
    else:
        return True