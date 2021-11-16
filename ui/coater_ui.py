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
from ..import layer_functions

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
    bl_label = "Coater " + "0.5"
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

# Sections
def draw_layers_section_ui(self, context):
    draw_section_buttons(self, context)             # Draw add-on section buttons.
    draw_layer_folder(self, context)                # Draw the layer folder location.
    draw_tools(self, context)                       # Draw coater specific tools.
    draw_material_selector(self, context)           # Draw a material selector.
    draw_layer_operations(self)                     # Draw layer operations.

    if context.active_object != None:
        active_material = context.active_object.active_material
        if active_material != None:
            if layer_functions.check_coater_material(context):
                draw_material_channel(self, context)            # Draw material channel.
                draw_opacity_and_blending(self, context)        # Draw layer blending mode and layer opacity.
            
                layers = context.scene.coater_layers
                if len(layers) > 0:
                    draw_layer_stack(self, context)         # Draw layer stack

                draw_base_channel_value(self, context)          # Draw Layer Base Values

                if len(layers) > 0:
                    draw_layer_properties(self, context)    # Draw layer properties
                    draw_mask_properties(self, context)     # Draw mask properties.
            
        

def draw_baking_section_ui(self, context):
    layout = self.layout
    addon_preferences = context.preferences.addons["Coater"].preferences

    draw_section_buttons(self, context)             # Draw section buttons.
    layout.prop(addon_preferences, "bake_folder")   # Draw the bake folder.

    # Bake
    row = layout.row()
    row.operator("coater.bake")
    row.scale_y = 2.0

    row = layout.row()
    row.operator("coater.bake_edges")

    # Toggles
    layout.prop(addon_preferences, "bake_ao")
    layout.prop(addon_preferences, "bake_curvature")
    layout.prop(addon_preferences, "bake_edges")
    layout.prop(addon_preferences, "bake_normals")

def draw_export_section_ui(self, context):
    layout = self.layout
    addon_preferences = context.preferences.addons["Coater"].preferences

    # Draw add-on section buttons.
    draw_section_buttons(self, context)

    layout.prop(addon_preferences, "export_folder")

    row = layout.row()
    row.operator("coater.export")
    row.scale_y = 2.0

    layout.prop(addon_preferences, "export_base_color")
    layout.prop(addon_preferences, "export_roughness")
    layout.prop(addon_preferences, "export_metallic")
    layout.prop(addon_preferences, "export_normals")
    layout.prop(addon_preferences, "export_emission")
    #layout.prop(addon_preferences, "export_ao")

# Sub-sections.
def draw_section_buttons(self, context):
    layout = self.layout
    panel_properties = context.scene.coater_panel_properties

    # Draw add-on section buttons.
    row = layout.row(align=True)
    row.prop(panel_properties, "sections", expand=True)
    row.operator("coater.open_settings", text="", icon='SETTINGS')
    row.scale_y = 2.0

def draw_layer_folder(self, context):
    layout = self.layout
    addon_preferences = context.preferences.addons["Coater"].preferences
    layout.prop(addon_preferences, "layer_folder")

def draw_tools(self, context):
    layout = self.layout

    addon_preferences = context.preferences.addons["Coater"].preferences
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
        row.prop(context.scene.tool_settings.unified_paint_settings, "color", text="")
        row.prop(context.scene.tool_settings.unified_paint_settings, "secondary_color", text="")
        row.operator("coater.swap_primary_color", icon='UV_SYNC_SELECT')

def draw_material_selector(self, context):
    active_object = context.active_object
    layout = self.layout

    row = layout.row(align=True)
    if active_object != None:
        if active_object.active_material != None:
            row.template_ID(active_object, "active_material")

        else:
            layout.label(text="No active material")

    else:
        layout.label(text="No object selected.")

    if active_object != None:
        if active_object.active_material != None:
            row.operator("coater.refresh_layers", icon='FILE_REFRESH')
    row.scale_y = 1.5

def draw_layer_operations(self):
    layout = self.layout
    row = layout.row(align=True)
    row.operator("coater.add_layer_menu", icon="ADD", text="")
    row.operator("coater.add_mask_menu", icon="MOD_MASK", text="")
    row.operator("coater.move_layer_up", icon="TRIA_UP", text="")
    row.operator("coater.move_layer_down", icon="TRIA_DOWN", text="")
    row.operator("coater.duplicate_layer", icon="DUPLICATE", text="")
    row.operator("coater.merge_layer", icon="AUTOMERGE_OFF", text="")
    row.operator("coater.image_editor_export", icon="EXPORT", text="")
    row.operator("coater.delete_layer", icon="TRASH", text="")
    row.scale_y = 2.0
    row.scale_x = 2

def draw_material_channel(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.prop(context.scene.coater_layer_stack, "channel", text="")
    if context.scene.coater_layer_stack.channel_preview == False:
        row.operator("coater.toggle_channel_preview", text="", icon='MATERIAL')

    elif context.scene.coater_layer_stack.channel_preview == True:
        row.operator("coater.toggle_channel_preview", text="", icon='MATERIAL', depress=True)

    row.scale_x = 2
    row.scale_y = 1.4

def draw_opacity_and_blending(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    layout = self.layout
    row = layout.row()

    opacity_node = layer_functions.get_node(context, 'OPACITY', layer_index)
    mix_node = layer_functions.get_node(context, 'MIX', layer_index)

    if opacity_node != None and mix_node != None:
        row = layout.row(align=True)
        row.prop(layers[layer_index], "layer_opacity")
        row.prop(mix_node, "blend_type", text="")

    row.scale_y = 1.4

def draw_layer_stack(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.template_list("COATER_UL_layer_list", "The_List", context.scene, "coater_layers", context.scene.coater_layer_stack, "layer_index")
    row.scale_y = 2

def draw_base_channel_value(self, context):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    material_nodes = context.active_object.active_material.node_tree.nodes
    
    layout = self.layout
    row = layout.row()

    principled_bsdf = material_nodes.get('Principled BSDF')
    if len(layers) == 0:
        if layer_stack.channel == 'BASE_COLOR':
            row.prop(principled_bsdf.inputs[0], "default_value", text="")

        if layer_stack.channel == 'METALLIC':
            row.prop(principled_bsdf.inputs[4], "default_value", text="")

        if layer_stack.channel == 'ROUGHNESS':
            row.prop(principled_bsdf.inputs[7], "default_value", text="")

        if layer_stack.channel == 'EMISSION':
            row.prop(principled_bsdf.inputs[17], "default_value", text="")

    else:
        channel_node = layer_functions.get_channel_node(context)

        if layer_stack.channel == 'BASE_COLOR':
            row.prop(channel_node.inputs[0], "default_value", text="")

    if layer_stack.channel == 'EMISSION':
        row.prop(principled_bsdf.inputs[18], "default_value", text="")

def draw_layer_properties(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node = layer_functions.get_channel_node(context)

    layout = self.layout
    row = layout.row()
    row.label(text="Layer Properties")
    
    # Image Layer Properties
    if(layers[layer_index].layer_type == 'IMAGE_LAYER'):
        color_node = channel_node.node_tree.nodes.get(layers[layer_index].color_node_name)
        mapping_node = channel_node.node_tree.nodes.get(layers[layer_index].mapping_node_name)

        if color_node != None:
            row = layout.row(align=True)
            row.prop(color_node, "image")
            row.operator("coater.import_color_image", text="", icon="IMPORT")

            row = layout.row()
            row.prop(color_node, "extension")

            row = layout.row()
            row.prop(color_node, "interpolation")

            row = layout.row()
            row.prop(layers[layer_index], "layer_projection")

            if layers[layer_index].layer_projection == 'BOX':
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

def draw_mask_properties(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    if layers[layer_index].mask_node_name != "":
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index
        channel_node = layer_functions.get_channel_node(context)

        layout = self.layout
        row = layout.row()
        row.label(text="Mask Properties")
        row.operator("coater.delete_layer_mask", icon="X", text="")

        mask_node = channel_node.node_tree.nodes.get(layers[layer_index].mask_node_name)

        row = layout.row(align=True)
        row.prop(mask_node, "image")
        row.operator("coater.select_layer_mask", icon="MOD_MASK", text="")
        row.operator("coater.import_mask_image", text="", icon="IMPORT")

        row = layout.row()
        row.prop(mask_node, "extension")

        row = layout.row()
        row.prop(mask_node, "interpolation")

        row = layout.row()
        row.prop(layers[layer_index], "mask_projection")

        if layers[layer_index].mask_projection == 'BOX':
            row = layout.row()
            row.prop(mask_node, "projection_blend")

        mask_mapping_node = channel_node.node_tree.nodes.get(layers[layer_index].mask_mapping_node_name)
        if mask_mapping_node != None:
            row = layout.row()
            row.prop(mask_mapping_node.inputs[1], "default_value", text="Location")
                
            row = layout.row()
            row.prop(mask_mapping_node.inputs[2], "default_value", text="Rotation")
                
            row = layout.row()
            row.prop(mask_mapping_node.inputs[3], "default_value", text="Scale")

        levels_node = channel_node.node_tree.nodes.get(layers[layer_index].mask_levels_node_name)
        row = layout.row()
        layout.template_color_ramp(levels_node, "color_ramp")