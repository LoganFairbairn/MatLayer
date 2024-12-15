# Draws the matlayer user interface.

import bpy
from . import ui_edit_tab
from . import ui_mesh_map_tab
from . import ui_settings_tab
from . import ui_export_tab
from . import ui_viewport_tab
from ..core import export_textures
from ..core import shaders

def check_blend_saved():
    if bpy.path.abspath("//") == "":
        return False
    else:
        return True

def update_main_ui_tabs(self, context):
    '''Callback function for updating data when the main user interface tab is changed.'''

    # Read json data for available shaders when the shader tab is selected.
    if context.scene.matlayer_panel_properties.sections == 'SECTION_SETTINGS':
        shaders.update_shader_list()

    # Read the available export templates when the export tab is selected.
    if context.scene.matlayer_panel_properties.sections == 'SECTION_EXPORT':
        export_textures.read_export_template_names()

class MATLAYER_panel_properties(bpy.types.PropertyGroup):
    sections: bpy.props.EnumProperty(
        items=[('SECTION_EDIT', "EDIT", "This section contains operators to edit material layers."),
               ('SECTION_MESH_MAPS', "MESH MAPS", "This section contains operations to quickly bake mesh map textures for your models. Baking mesh maps transfer 3D data such as shadows, curvature, sharp edges and extra detail from higher polycount objects to image textures. Baked mesh map textures can be used as textures in layers in many different ways to make the texturing process faster. One example of where baked mesh maps could be used is to mask dirt by using the baked ambient occlusion as a mask."),
               ('SECTION_EXPORT', "EXPORT", "This section contains operations to quickly export textures made with MatLayer."),
               ('SECTION_SETTINGS', "SETTINGS", "Settings that defined how materials and textures are created by this add-on."),
               ('SECTION_VIEWPORT_SETTINGS', "VIEWPORT", "This section contains select viewport render settings to help preview materials")],
        name="MatLayer Sections",
        description="Current matlayer category",
        default='SECTION_EDIT',
        update=update_main_ui_tabs
    )

class MATLAYER_PT_Panel(bpy.types.Panel):
    bl_label = "MatLayer 3.0.0"
    bl_idname = "MATLAYER_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MatLayer"

    def draw(self, context):
        layout = self.layout
        panel_properties = context.scene.matlayer_panel_properties
        if check_blend_saved():
            match panel_properties.sections:
                case "SECTION_EDIT":
                    ui_edit_tab.draw_layers_tab_ui(self, context)

                case 'SECTION_MESH_MAPS':
                    ui_mesh_map_tab.draw_baking_tab_ui(self, context)

                case 'SECTION_EXPORT':
                    ui_export_tab.draw_export_tab_ui(self, context)

                case 'SECTION_SETTINGS':
                    ui_settings_tab.draw_settings_tab(self, context)

                case 'SECTION_VIEWPORT_SETTINGS':
                    ui_viewport_tab.draw_ui_settings_tab(self, context)

        else:
            layout.label(text="Save your .blend file to use MatLayer.")
            layout.label(text="The .blend path is used to find correct paths for image folders,")
            layout.label(text="where textures, baked mesh maps, or exported textures created ")
            layout.label(text="using this add-on are saved.")
