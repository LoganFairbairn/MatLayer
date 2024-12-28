# Draws the matlayer user interface.

import bpy
from bpy.types import Menu
from . import ui_edit_layers
from . import ui_mesh_map
from . import ui_settings
from . import ui_export_textures
from . import ui_viewport
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
    if context.scene.matlayer_panel_properties.sections == 'SECTION_EXPORT_TEXTURES':
        export_textures.read_export_template_names()

def draw_addon_dropdown_menu_bar(layout):
    '''Draws a dropdown menu bar for this add-on.'''

    # Split the UI into a two column layout.
    split = layout.split(factor=0.75)
    first_column = split.column()
    second_column = split.column()

    # Draw top row sub-menus.
    row = first_column.row(align=True)
    row.alignment = 'LEFT'
    row.menu("MATLAYER_MT_file_sub_menu", text="File")
    row.menu("MATLAYER_MT_edit_sub_menu", text="Edit")
    row.menu("MATLAYER_MT_utility_sub_menu", text="Utility Operators")
    row.menu("MATLAYER_MT_help_sub_menu", text="Help")

    # Draw a quick access button for the main add-on section.
    panel_properties = bpy.context.scene.matlayer_panel_properties
    row = second_column.row()
    row.alignment = 'RIGHT'
    row.prop_enum(panel_properties, "sections", 'SECTION_EDIT_MATERIALS', text="Edit Materials", icon='MATERIAL')

class FileSubMenu(Menu):
    bl_idname = "MATLAYER_MT_file_sub_menu"
    bl_label = "File Sub Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("matlayer.export", text="Export Textures", icon='EXPORT')
        layout.operator("matlayer.import_texture_set", text="Import Texture Set", icon='IMPORT')

class EditSubMenu(Menu):
    bl_idname = "MATLAYER_MT_edit_sub_menu"
    bl_label = "Edit Sub Menu"

    def draw(self, context):
        layout = self.layout
        panel_properties = context.scene.matlayer_panel_properties
        layout.prop_enum(panel_properties, "sections", 'SECTION_EDIT_MATERIALS', text="Materials")
        layout.prop_enum(panel_properties, "sections", "SECTION_MESH_MAPS", text="Mesh Maps")
        layout.prop_enum(panel_properties, "sections", 'SECTION_TEXTURE_SETTINGS', text="Texture Settings")
        layout.prop_enum(panel_properties, "sections", 'SECTION_SHADER_SETTINGS', text="Shader Settings", icon='MATSHADERBALL')
        layout.prop_enum(panel_properties, "sections", 'SECTION_VIEWPORT_SETTINGS', text="Viewport Settings")
        layout.prop_enum(panel_properties, "sections", 'SECTION_EXPORT_TEXTURES', text="Export Texture Settings", icon='EXPORT')

class HelpSubMenu(Menu):
    bl_idname = "MATLAYER_MT_help_sub_menu"
    bl_label = "Help Sub Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.url_open", text="Documentation", icon='HELP').url = "https://loganfairbairn.github.io/matlayer_documentation.html"

class UtilitySubMenu(Menu):
    bl_idname = "MATLAYER_MT_utility_sub_menu"
    bl_label = "Utility Sub Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("matlayer.append_workspace", text="Append Workspace")
        layout.operator("matlayer.append_material_ball", text="Append Material Ball")
        layout.operator("matlayer.append_basic_brushes", text="Append Basic Brushes")
        layout.operator("matlayer.remove_unused_textures", text="Remove Unused Textures")
        layout.operator("matlayer.apply_default_shader", text="Apply Default Shader")

class MATLAYER_panel_properties(bpy.types.PropertyGroup):
    sections: bpy.props.EnumProperty(
        items=[('SECTION_EDIT_MATERIALS', "Edit Layers", "This section contains operators to edit material layers."),
               ('SECTION_MESH_MAPS', "Mesh Maps", "This section contains operations to quickly bake mesh map textures for your models. Baking mesh maps transfer 3D data such as shadows, curvature, sharp edges and extra detail from higher polycount objects to image textures. Baked mesh map textures can be used as textures in layers in many different ways to make the texturing process faster. One example of where baked mesh maps could be used is to mask dirt by using the baked ambient occlusion as a mask."),
               ('SECTION_EXPORT_TEXTURES', "Export Textures", "This section contains operations to quickly export textures made with MatLayer."),
               ('SECTION_TEXTURE_SETTINGS', "TEXTURE SETTINGS", "Settings that defined how materials and textures are created by this add-on."),
               ('SECTION_SHADER_SETTINGS', "Shader Settings", "Settings for shader node setups."),
               ('SECTION_VIEWPORT_SETTINGS', "VIEWPORT", "This section contains select viewport render settings to help preview materials")],
        name="MatLayer Sections",
        description="Current matlayer category",
        default='SECTION_EDIT_MATERIALS',
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

            # Draw a dropdown menu bar containing options for editing main parts of this add-on.
            draw_addon_dropdown_menu_bar(layout)

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

        else:
            layout.label(text="Save your .blend file to use MatLayer.")
            layout.label(text="The .blend path is used to find correct paths for image folders,")
            layout.label(text="where textures, baked mesh maps, or exported textures created ")
            layout.label(text="using this add-on are saved.")
