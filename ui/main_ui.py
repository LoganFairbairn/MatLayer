# Draws the matlayer user interface.

import bpy
from . import ui_layer_section
from . import ui_baking_section
from . import ui_export_section
from . import ui_texture_set_section
from . import ui_utils_section
from . import ui_settings_section
from .. import matlayer_utils

def check_blend_saved():
    if bpy.path.abspath("//") == "":
        return False
    else:
        return True

class MATLAYER_panel_properties(bpy.types.PropertyGroup):
    sections: bpy.props.EnumProperty(
        items=[('SECTION_TEXTURE_SET', "TEXTURE SET", "This section contains settings for the materials textures."),
               ('SECTION_BAKING', "BAKING", "This section contains operations to quickly bake mesh map textures for your models. Baking mesh maps transfer 3D data such as shadows, curvature, sharp edges and extra detail from higher polycount objects to image textures. Baked mesh map textures can be used as textures in layers in many different ways to make the texturing process faster. One example of where baked mesh maps could be used is to mask dirt by using the baked ambient occlusion as a mask."),
               ('SECTION_LAYERS', "LAYERS", "This section contains a layer stack for the selected object's active material. In this section you can add, edit and blend multiple materials together."),
               ('SECTION_EXPORT', "EXPORT", "This section contains operations to quickly export textures made with MatLay."),
               ('SECTION_UTILS', "UTILS", "This section contains helpful operators."),
               ('SECTION_SETTINGS', "SETTINGS", "This section contains general add-on settings for this add-on.")],
        name="MatLay Sections",
        description="Current matlayer category",
        default='SECTION_LAYERS'
    )

class MATLAYER_PT_Panel(bpy.types.Panel):
    bl_label = "MatLayer " + "1.0.4"
    bl_idname = "MATLAYER_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MatLayer"

    def draw(self, context):
        layout = self.layout
        panel_properties = context.scene.matlayer_panel_properties
        if check_blend_saved():
            match panel_properties.sections:
                case 'SECTION_TEXTURE_SET':
                    ui_texture_set_section.draw_texture_set_section_ui(self, context)

                case 'SECTION_BAKING':
                    ui_baking_section.draw_baking_section_ui(self, context)
                
                case "SECTION_LAYERS":
                    ui_layer_section.draw_layers_section_ui(self, context)
                    settings = context.scene.matlayer_settings
                    row = layout.row()
                    row.alignment = 'CENTER'
                    row.label(text="Active nodes: {0} Nodes links: {1}".format(settings.total_node_count, settings.total_node_link_count))    

                case 'SECTION_EXPORT':
                    ui_export_section.draw_export_section_ui(self, context)

                case 'SECTION_UTILS':
                    ui_utils_section.draw_ui_utils_section(self, context)

                case 'SECTION_SETTINGS':
                    ui_settings_section.draw_ui_settings_section(self, context)

        else:
            layout.label(text="Save your .blend file to use MatLayer.")
            layout.label(text="The .blend path is used to find correct paths for image folders,")
            layout.label(text="where textures, baked mesh maps, or exported textures created ")
            layout.label(text="using this add-on are saved.")
