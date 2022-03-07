# This file handles drawing the user interface for the layer section.

import bpy
from .import ui_section_tabs
from ..layers import coater_node_info
from ..layers import coater_material_functions

def draw_layers_section_ui(self, context):
    '''Draws the layer section UI.'''
    layout = self.layout
    ui_section_tabs.draw_section_tabs(self, context)
    draw_material_selector(self, context)
    draw_paint_tools(layout, context)
    draw_layer_operations(self)

    if context.active_object:
        active_material = context.active_object.active_material
        if active_material:
            if coater_material_functions.check_coater_material(context):
                draw_material_channel(self, context)
                
                layers = context.scene.coater_layers
                if len(layers) > 0:
                    draw_layer_stack(self, context)

                if len(layers) > 0:
                    draw_layer_properties(self, context)
                    draw_mask_properties(self, context)
    else:
        layout = self.layout
        layout.label(text="Select an object.")

def draw_paint_tools(layout, context):
    # Only draw paint tools in Texture Paint mode.
    if context.mode == 'PAINT_TEXTURE':
        # Draw brush presets.
        row = layout.row()
        row.template_ID_preview(context.tool_settings.image_paint, "brush", new="brush.add")

def draw_material_selector(self, context):
    '''Draws a material selector and refresh button.'''
    active_object = context.active_object
    layout = self.layout

    row = layout.row(align=True)
    if active_object:
        if active_object.active_material != None:
            row.template_ID(active_object, "active_material", new="coater.add_color_layer", live_icon=True)

        else:
            row.template_ID(active_object, "active_material", new="coater.add_color_layer", live_icon=True)

    if active_object:
        if active_object.active_material != None:
            row.operator("coater.refresh_layers", text="", icon='FILE_REFRESH')
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
    row.operator("coater.bake_layer", icon="RENDER_STILL", text="")
    row.operator("coater.image_editor_export", icon="EXPORT", text="")
    row.operator("coater.delete_layer", icon="TRASH", text="")
    row.scale_y = 2.0
    row.scale_x = 2

def draw_material_channel(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.prop(context.scene.coater_layer_stack, "channel", text="")
    draw_base_channel_value(context, row)
    if context.scene.coater_layer_stack.channel_preview == False:
        row.operator("coater.toggle_channel_preview", text="", icon='MATERIAL')

    elif context.scene.coater_layer_stack.channel_preview == True:
        row.operator("coater.toggle_channel_preview", text="", icon='MATERIAL', depress=True)

    row.scale_x = 2
    row.scale_y = 1.4

def draw_layer_stack(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.template_list("COATER_UL_layer_list", "The_List", context.scene, "coater_layers", context.scene.coater_layer_stack, "layer_index")
    row.scale_y = 2

def draw_base_channel_value(context, row):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    material_nodes = context.active_object.active_material.node_tree.nodes

    principled_bsdf = material_nodes.get('Principled BSDF')
    if len(layers) == 0:
        if layer_stack.channel == 'BASE_COLOR':
            row.prop(principled_bsdf.inputs[0], "default_value", text="")

        if layer_stack.channel == 'METALLIC':
            row.prop(principled_bsdf.inputs[6], "default_value", text="")

        if layer_stack.channel == 'ROUGHNESS':
            row.prop(principled_bsdf.inputs[9], "default_value", text="")

    else:
        channel_node = coater_node_info.get_channel_node(context)

        if layer_stack.channel == 'BASE_COLOR':
            row.prop(channel_node.inputs[0], "default_value", text="")

    if layer_stack.channel == 'EMISSION':
        row.prop(principled_bsdf.inputs[20], "default_value", text="")

def draw_layer_properties(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node = coater_node_info.get_channel_node(context)

    layout = self.layout
    row = layout.row()
    row.label(text="Layer Properties:")
    
    # Draw Image Layer Properties
    if(layers[layer_index].type == 'IMAGE_LAYER'):
        color_node = channel_node.node_tree.nodes.get(layers[layer_index].color_node_name)
        mapping_node = channel_node.node_tree.nodes.get(layers[layer_index].mapping_node_name)

        scale_y = 1.4

        if color_node != None:
            row = layout.row(align=True)
            row.scale_y = scale_y
            row.prop(color_node, "image", text="")
            row.operator("coater.add_layer_image", text="", icon="ADD")
            row.operator("coater.delete_layer_image", text="", icon="REMOVE")
            row.operator("coater.import_color_image", text="", icon="IMPORT")

            row = layout.row()
            row.scale_y = scale_y
            row.prop(color_node, "extension")

            row = layout.row()
            row.scale_y = scale_y
            row.prop(color_node, "interpolation")

            row = layout.row()
            row.scale_y = scale_y
            row.prop(layers[layer_index], "projection")

            if layers[layer_index].projection == 'BOX':
                row = layout.row()
                row.scale_y = scale_y
                row.prop(layers[layer_index], "projection_blend")

        if mapping_node != None:
            row = layout.row()
            row.scale_y = scale_y
            row.prop(layers[layer_index], "projected_offset_x")
            row.prop(layers[layer_index], "projected_offset_y")
            
            row = layout.row()
            row.scale_y = scale_y
            row.prop(layers[layer_index], "projected_rotation", slider=True)
            
            row = layout.row()
            row.scale_y = scale_y
            row.prop(layers[layer_index], "projected_scale_x")
            row.prop(layers[layer_index], "projected_scale_y")

    # Draw Color Layer Properties
    if(layers[layer_index].type == 'COLOR_LAYER'):
        color_node = channel_node.node_tree.nodes.get(layers[layer_index].color_node_name)

        row = layout.row()
        row.scale_y = 1.4
        row.prop(color_node.outputs[0], "default_value", text="Color")

def draw_mask_properties(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    scale_y = 1.4

    if layers[layer_index].mask_node_name != "":
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index
        channel_node = coater_node_info.get_channel_node(context)

        layout = self.layout
        row = layout.row()
        row.scale_y = scale_y
        row.label(text="Mask Properties")
        row.operator("coater.delete_layer_mask", icon="X", text="")

        mask_node = channel_node.node_tree.nodes.get(layers[layer_index].mask_node_name)

        row = layout.row(align=True)
        row.scale_y = scale_y
        row.operator("coater.select_layer_mask", icon="SELECT_SET", text="")
        row.prop(mask_node, "image", text="")
        row.operator("coater.add_layer_image_mask", text="", icon="ADD")
        row.operator("coater.delete_layer_image_mask", text="", icon="REMOVE")
        row.operator("coater.import_mask_image", text="", icon="IMPORT")

        row = layout.row()
        row.scale_y = scale_y
        row.prop(mask_node, "extension")

        row = layout.row()
        row.scale_y = scale_y
        row.prop(mask_node, "interpolation")

        row = layout.row()
        row.scale_y = scale_y
        row.prop(layers[layer_index], "mask_projection")

        if layers[layer_index].mask_projection == 'BOX':
            row = layout.row()
            row.scale_y = scale_y
            row.prop(layers[layer_index], "mask_projection_blend")

        mask_mapping_node = channel_node.node_tree.nodes.get(layers[layer_index].mask_mapping_node_name)
        if mask_mapping_node != None:
            row = layout.row()
            row.scale_y = scale_y
            row.prop(layers[layer_index], "projected_mask_offset_x")
            row.prop(layers[layer_index], "projected_mask_offset_y")
            
            row = layout.row()
            row.scale_y = scale_y
            row.prop(layers[layer_index], "projected_mask_rotation", slider=True)
            
            row = layout.row()
            row.scale_y = scale_y
            row.prop(layers[layer_index], "projected_mask_scale_x")
            row.prop(layers[layer_index], "projected_mask_scale_y")

        levels_node = channel_node.node_tree.nodes.get(layers[layer_index].mask_levels_node_name)
        row = layout.row()
        layout.template_color_ramp(levels_node, "color_ramp")