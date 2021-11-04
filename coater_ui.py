# Copyright (c) 2021 Logan Fairbairn
# logan-fairbairn@outlook.com
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# This file handles the coater user interface.

import bpy
from . import layer_functions

class COATER_panel_properties(bpy.types.PropertyGroup):
    sections: bpy.props.EnumProperty(
        items=[('SECTION_LAYERS', "Layers", "This section contains a layer stack for the active material"),
               ('SECTION_BAKE', "Bake", "This section contains operations to quickly bake common texture maps for your model"),
               ('SECTION_EXPORT', "Export", "This section contains operations to quickly export textures made with Coater")],
        name="Coater Sections",
        description="Current coater category",
        default='SECTION_LAYERS'
    )

class COATER_PT_Panel(bpy.types.Panel):
    bl_label = "Coater " + "0.1"
    bl_idname = "COATER_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Coater"

    def draw(self, context):
        panel_properties = context.scene.coater_panel_properties

        if panel_properties.sections == "SECTION_LAYERS":
            draw_layers_section_ui(self, context)

        if panel_properties.sections == "SECTION_BAKE":
            draw_baking_section_ui(self, context)

        if panel_properties.sections == 'SECTION_EXPORT':
            draw_export_section_ui(self, context)

def draw_layers_section_ui(self, context):
    layout = self.layout
    scene = context.scene
    panel_properties = context.scene.coater_panel_properties
    active_object = context.active_object
    addon_preferences = context.preferences.addons["Coater"].preferences
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Draw add-on section buttons.
    row = layout.row(align=True)
    row.prop(panel_properties, "sections", expand=True)
    row.operator("coater.open_settings", text="", icon='SETTINGS')
    row.scale_y = 2.0

    # Layer Folder
    layout.prop(addon_preferences, "layer_folder")

    # Draw Color Picker
    if addon_preferences.show_color_picker:
        row = layout.row()
        row.template_color_picker(bpy.context.scene.tool_settings.unified_paint_settings, "color")

    # Draw Color Palette
    if addon_preferences.show_color_palette:
        if context.tool_settings.image_paint.palette:
            layout.template_palette(context.tool_settings.image_paint, "palette", color=True)

    # Draw Primary & Secondary Colors
    if addon_preferences.show_brush_colors:
        row = layout.row(align=True)
        row.prop(scene.tool_settings.unified_paint_settings, "color", text="")
        row.prop(scene.tool_settings.unified_paint_settings, "secondary_color", text="")
        row.operator("coater.swap_primary_color", icon='UV_SYNC_SELECT')

    # TODO: Draw Brush *Presets*

    # Draw curently selected material AND dropdown list of attached materials.
    row = layout.row(align=True)


    if active_object != None:
        if active_object.active_material != None:
            row.template_ID(active_object, "active_material")

        else:
            layout.label(text="No active material")

    else:
        layout.label(text="No object selected.")

    if active_object.active_material != None:
        row.operator("coater.refresh_layers", icon='FILE_REFRESH')

    row.scale_y = 1.4

    # Layer Operations
    row = layout.row(align=True)
    row.operator("coater.add_layer_menu", icon="ADD")
    row.operator("coater.add_mask_menu", icon="MOD_MASK")
    row.operator("coater.move_layer_up", icon="TRIA_UP")
    row.operator("coater.move_layer_down", icon="TRIA_DOWN")
    row.operator("coater.duplicate_layer", icon="DUPLICATE")
    row.operator("coater.merge_layer", icon="AUTOMERGE_OFF")
    row.operator("coater.image_editor_export", icon="EXPORT")
    row.operator("coater.delete_layer", icon="TRASH")
    row.scale_y = 2.0
    row.scale_x = 2

    # Draw material channels.
    row = layout.row(align=True)
    row.prop(scene.coater_layer_stack, "channel")
    if scene.coater_layer_stack.channel_preview == False:
        row.operator("coater.toggle_channel_preview", text="", icon='MATERIAL')

    elif scene.coater_layer_stack.channel_preview == True:
        row.operator("coater.toggle_channel_preview", text="", icon='MATERIAL', depress=True)

    row.scale_x = 2
    row.scale_y = 1.4
    
    # Draw layer blending mode and layer opacity.
    if len(layers) > 0:
        row = layout.row(align=True)
        row.prop(layers[layer_index], "blend_mode")
        row.prop(layers[layer_index], "layer_opacity")
    row.scale_y = 1.4

    # Draw Layer Base Values
    draw_base_channel_value(self, context)

    # Draw Layer Properties
    if len(layers) > 0:
        # Draw Layer Stack
        row = layout.row(align=True)
        row.template_list("COATER_UL_layer_list", "The_List", scene, "coater_layers", scene.coater_layer_stack, "layer_index")
        row.scale_y = 2

        draw_layer_properties(self, context)
        #draw_effect_properties(self, context)
        #draw_mask_properties(self, context)

def draw_baking_section_ui(self, context):
    layout = self.layout
    panel_properties = context.scene.coater_panel_properties
    addon_preferences = context.preferences.addons["Coater"].preferences

    # Draw add-on section buttons.
    row = layout.row()
    row.prop(panel_properties, "sections", expand=True)
    row.scale_y = 2.0

    layout.prop(addon_preferences, "bake_folder")

    # Bake
    row = layout.row()
    row.operator("coater.bake")
    row.scale_y = 2.0

    # Toggles
    layout.prop(addon_preferences, "bake_ao")
    layout.prop(addon_preferences, "bake_curvature")
    layout.prop(addon_preferences, "bake_edges")
    layout.prop(addon_preferences, "bake_normals")

def draw_export_section_ui(self, context):
    layout = self.layout
    panel_properties = context.scene.coater_panel_properties
    addon_preferences = context.preferences.addons["Coater"].preferences

    # Draw add-on section buttons.
    row = layout.row()
    row.prop(panel_properties, "sections", expand=True)
    row.scale_y = 2.0

    layout.prop(addon_preferences, "export_folder")

    row = layout.row()
    row.operator("coater.export")
    row.scale_y = 2.0

    layout.prop(addon_preferences, "export_base_color")
    layout.prop(addon_preferences, "export_roughness")
    layout.prop(addon_preferences, "export_metallic")
    layout.prop(addon_preferences, "export_normals")
    layout.prop(addon_preferences, "export_emission")
    layout.prop(addon_preferences, "export_ao")

def draw_base_channel_value(self, context):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    material_nodes = context.active_object.active_material.node_tree.nodes
    
    layout = self.layout
    row = layout.row()

    if len(layers) == 0:
        principled_bsdf = material_nodes.get('Principled BSDF')

        if layer_stack.channel == 'BASE_COLOR':
            row.prop(principled_bsdf.inputs[0], "default_value", text="")

        if layer_stack.channel == 'METALLIC':
            row.prop(principled_bsdf.inputs[4], "default_value", text="")

        if layer_stack.channel == 'ROUGHNESS':
            row.prop(principled_bsdf.inputs[7], "default_value", text="")

    else:
        channel_node = layer_functions.get_channel_node(self, context)
        
        if layer_stack.channel == 'BASE_COLOR':
            row.prop(channel_node.inputs[0], "default_value", text="")

def draw_layer_properties(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node = layer_functions.get_channel_node(self, context)

    layout = self.layout
    row = layout.row()
    row.label(text="Layer Properties")
    
    # Image Layer Properties
    if(layers[layer_index].layer_type == 'IMAGE_LAYER'):
        color_node = channel_node.node_tree.nodes.get(layers[layer_index].color_node_name)
        mapping_node = channel_node.node_tree.nodes.get(layers[layer_index].mapping_node_name)

        if color_node != None:
            row = layout.row()
            row.prop(color_node, "image")

            row = layout.row()
            row.prop(color_node, "extension")

            row = layout.row()
            row.prop(color_node, "interpolation")

            row = layout.row()
            row.prop(color_node, "projection")

            if color_node.projection == 'BOX':
                row = layout.row()
                row.prop(color_node, "projection_blend")

        if mapping_node != None:
            row = layout.row()
            row.prop(mapping_node.inputs[1], "default_value", text="Location")
            
            row = layout.row()
            row.prop(mapping_node.inputs[2], "default_value", text="Rotation")
            
            row = layout.row()
            row.prop(mapping_node.inputs[3], "default_value", text="Scale")

    # Color Layer Properties
    if(layers[layer_index].layer_type == 'COLOR_LAYER'):
        color_node = channel_node.node_tree.nodes.get(layers[layer_index].color_node_name)

        row = layout.row()
        row.prop(color_node.outputs[0], "default_value", text="Color")

def draw_effect_properties(self, context):
    layout = self.layout
    row = layout.row()
    row.label(text="Effect Properties")

def draw_mask_properties(self, context):
    layout = self.layout
    row = layout.row()
    row.label(text="Mask Properties")