# Draws the rymat user interface.

import bpy
from bpy.types import Menu
from . import ui_edit_layers
from . import ui_mesh_map
from . import ui_settings
from . import ui_export_textures
from . import ui_viewport
from ..core import export_textures
from ..core import shaders

def update_main_ui_sections(self, context):
    '''Callback function for updating data when the main user interface tab is changed.'''

    # Read json data for available shaders when the shader tab is selected.
    if context.scene.rymat_panel_properties.sections == 'SECTION_SETTINGS':
        shaders.update_shader_list()

    # Read the available export templates when the export tab is selected.
    if context.scene.rymat_panel_properties.sections == 'SECTION_EXPORT_TEXTURES':
        export_textures.read_export_template_names()

class MiscSubMenu(Menu):
    bl_idname = "RYMAT_MT_misc_sub_menu"
    bl_label = "Main Sub Menu"

    def draw(self, context):
        layout = self.layout
        # May not need this, users could use externally edit UVs instead.
        #layout.operator("rymat.export_uvs", text="Export UV Map", icon='NONE')
        layout.operator("rymat.append_default_workspace", text="Append Default Workspace", icon='NONE')
        layout.operator("rymat.append_material_ball", text="Append Material Ball", icon='NONE')
        layout.operator("rymat.apply_default_shader", text="Apply Default Shader", icon='NONE')
        layout.operator("rymat.add_black_outlines", text="Add Black Outlines", icon='NONE')
        layout.operator("rymat.remove_outlines", text="Remove Black Outlines", icon='NONE')
        layout.operator("wm.url_open", text="Documentation", icon='NONE').url = "https://loganfairbairn.github.io/rymat_documentation.html"

class RYMAT_panel_properties(bpy.types.PropertyGroup):
    sections: bpy.props.EnumProperty(
        items=[('SECTION_EDIT_MATERIALS', "Edit Layers", "This section contains operators to edit material layers."),
               ('SECTION_MESH_MAPS', "Mesh Maps", "This section contains operations to quickly bake mesh map textures for your models. Baking mesh maps transfer 3D data such as shadows, curvature, sharp edges and extra detail from higher polycount objects to image textures. Baked mesh map textures can be used as textures in layers in many different ways to make the texturing process faster. One example of where baked mesh maps could be used is to mask dirt by using the baked ambient occlusion as a mask."),
               ('SECTION_EXPORT_TEXTURES', "Export Textures", "This section contains operations to quickly export textures made with RyMat."),
               ('SECTION_TEXTURE_SETTINGS', "TEXTURE SETTINGS", "Settings that defined how materials and textures are created by this add-on."),
               ('SECTION_SHADER_SETTINGS', "Shader Settings", "Settings for shader node setups."),
               ('SECTION_VIEWPORT_SETTINGS', "VIEWPORT", "This section contains select viewport render settings to help preview materials")],
        name="RyMat Sections",
        description="Current rymat category",
        default='SECTION_EDIT_MATERIALS',
        update=update_main_ui_sections
    )

class RYMAT_PT_Panel(bpy.types.Panel):
    bl_label = "RyMat 1.0.0"
    bl_idname = "RYMAT_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RyMat"

    def draw(self, context):
        layout = self.layout
        panel_properties = context.scene.rymat_panel_properties

        # Split the UI into a two column layout.
        split = layout.split(factor=0.9)
        first_column = split.column()
        second_column = split.column()

        panel_properties = context.scene.rymat_panel_properties

        split = first_column.split(factor=0.1)
        first_sub_column = split.column()
        second_sub_column = split.column()

        # Draw an operator to save all textures in the blend file.
        row = first_sub_column.row()
        row.scale_x = 10
        row.scale_y = 1.5
        row.operator("rymat.save_all_textures", text="", icon='FILE_TICK')
        
        # Draw a top bar with tabs for accessing different menus of the add-on.
        row = second_sub_column.row(align=True)
        row.scale_x = 10
        row.scale_y = 1.5
        row.prop_enum(panel_properties, "sections", 'SECTION_EDIT_MATERIALS', text="", icon='MATERIAL')
        row.prop_enum(panel_properties, "sections", "SECTION_MESH_MAPS", text="", icon='FACE_MAPS')
        row.prop_enum(panel_properties, "sections", 'SECTION_TEXTURE_SETTINGS', text="", icon='TEXTURE')
        row.prop_enum(panel_properties, "sections", 'SECTION_EXPORT_TEXTURES', text="", icon='EXPORT')
        row.prop_enum(panel_properties, "sections", 'SECTION_SHADER_SETTINGS', text="", icon='MATSHADERBALL')
        row.prop_enum(panel_properties, "sections", 'SECTION_VIEWPORT_SETTINGS', text="", icon='VIEW3D')

        # Draw a sub-menu for misc operators.
        row = second_column.row(align=True)
        row.ui_units_x = 10
        row.scale_x = 10
        row.scale_y = 1.5
        row.menu("RYMAT_MT_misc_sub_menu", text="", icon='TOOL_SETTINGS')

        # Draw user interface based on the selected section.
        match panel_properties.sections:
            case "SECTION_EDIT_MATERIALS":
                ui_edit_layers.draw_edit_layers_ui(self, context)

            case 'SECTION_MESH_MAPS':
                ui_mesh_map.draw_mesh_map_section_ui(self, context)

            case 'SECTION_EXPORT_TEXTURES':
                ui_export_textures.draw_export_textures_ui(self, context)

            case 'SECTION_TEXTURE_SETTINGS':
                ui_settings.draw_texture_setting_ui(layout)

            case 'SECTION_SHADER_SETTINGS':
                ui_settings.draw_shader_setting_ui(layout)

            case 'SECTION_VIEWPORT_SETTINGS':
                ui_viewport.draw_viewport_setting_ui(self, context)