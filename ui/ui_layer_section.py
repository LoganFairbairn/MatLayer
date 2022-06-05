# This file handles drawing the user interface for the layers section.

import bpy
from .import ui_section_tabs
from ..layers.nodes import coater_materials
from ..layers.nodes import layer_nodes

SCALE_Y = 1.4

def draw_layers_section_ui(self, context):
    '''Draws the layer section UI.'''
    layout = self.layout
    ui_section_tabs.draw_section_tabs(self, context)
    draw_material_selector(self, context)
    #draw_paint_tools(layout, context)
    draw_layer_operations(self)

    if context.active_object:
        active_material = context.active_object.active_material
        if active_material:
            if coater_materials.verify_material(context):
                draw_material_channel(self, context)
                
                layers = context.scene.coater_layers
                if len(layers) > 0:
                    draw_layer_stack(self, context)

                if len(layers) > 0:
                    layer_stack = context.scene.coater_layer_stack

                    row = layout.row(align=True)
                    row.scale_y = 2.0
                    row.prop_enum(layer_stack, "layer_properties_tab", 'MATERIAL')
                    row.prop_enum(layer_stack, "layer_properties_tab", 'MASKS')

                    if layer_stack.layer_properties_tab == "MATERIAL":
                        draw_material_projection_settings(self, context)
                        draw_material_channels(self, context)
                        draw_layer_properties(self, context)

                    # TODO: Draw the mask properties here.
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
    row.operator("coater.add_layer", icon="ADD", text="")
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
    '''Draws the currently selected material channel.'''
    layout = self.layout
    row = layout.row(align=True)
    row.prop(context.scene.coater_layer_stack, "channel", text="")
    if context.scene.coater_layer_stack.channel_preview == False:
        row.operator("coater.toggle_channel_preview", text="", icon='MATERIAL')

    elif context.scene.coater_layer_stack.channel_preview == True:
        row.operator("coater.toggle_channel_preview", text="", icon='MATERIAL', depress=True)

    row.scale_x = 2
    row.scale_y = 1.4

def draw_layer_stack(self, context):
    layout = self.layout
    row = layout.row(align=True)
    layers = context.scene.coater_layer_stack
    # TODO: Rename The_List
    row.template_list("COATER_UL_layer_list", "The_List", context.scene, "coater_layers", layers, "layer_index", sort_reverse=True)
    row.scale_y = 2

def draw_material_projection_settings(self, context):
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    layout = self.layout
    
    row = layout.row()
    row.scale_y = SCALE_Y
    row.prop(layers[selected_layer_index], "projection_mode", text="Projection")

    row = layout.row()
    row.scale_y = SCALE_Y
    row.prop(layers[selected_layer_index], "texture_interpolation", text="Interpolation")

    row = layout.row()
    row.scale_y = SCALE_Y
    row.prop(layers[selected_layer_index], "texture_extension", text="Extension")

    if layers[selected_layer_index].projection_mode == 'BOX':
        row = layout.row()
        row.scale_y = SCALE_Y
        row.prop(layers[selected_layer_index], "projection_blend")

    row = layout.row()
    row.scale_y = SCALE_Y
    row.prop(layers[selected_layer_index], "projection_offset_x")
    row.prop(layers[selected_layer_index], "projection_offset_y")
            
    row = layout.row()
    row.scale_y = SCALE_Y
    row.prop(layers[selected_layer_index], "projection_rotation", slider=True)

    split = layout.split()
    col = split.column()
    col.ui_units_x = 1
    col.scale_y = SCALE_Y
    col.prop(layers[selected_layer_index], "projection_scale_x")

    col = split.column()
    col.ui_units_x = 0.1
    col.scale_y = SCALE_Y
    layer_settings = context.scene.coater_layer_settings
    if layer_settings.match_layer_mask_scale:
        col.prop(layer_settings, "match_layer_scale", text="", icon="LOCKED")

    else:
        col.prop(layer_settings, "match_layer_scale", text="", icon="UNLOCKED")
           
    col = split.column()
    col.ui_units_x = 2
    col.scale_y = SCALE_Y

    if layer_settings.match_layer_mask_scale:
        col.enabled = False
        col.prop(layers[selected_layer_index], "projection_scale_y")

    row = layout.row()
    row.label(text="---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

def draw_material_channels(self, context):
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    layout = self.layout

    row = layout.row()
    row = layout.row(align=False)
    row.scale_y = 1.4
    row.prop(layers[selected_layer_index], "color_channel_toggle", text="Color", toggle=1)
    row.prop(layers[selected_layer_index], "metallic_channel_toggle", text="Metal", toggle=1)
    row.prop(layers[selected_layer_index], "roughness_channel_toggle", text="Rough", toggle=1)
    row.prop(layers[selected_layer_index], "normal_channel_toggle", text="Nrm", toggle=1)
    row.prop(layers[selected_layer_index], "height_channel_toggle", text="Height", toggle=1)
    row.prop(layers[selected_layer_index], "scattering_channel_toggle", text="Scatt", toggle=1)

def draw_layer_properties(self, context):
    layout = self.layout

    # Draw layer properties for each active channel.
    draw_channel_texture_settings("Color", "COLOR", layout, context)
    draw_channel_texture_settings("Metallic", "METALLIC", layout, context)
    draw_channel_texture_settings("Roughness", "ROUGHNESS", layout, context)
    draw_channel_texture_settings("Normal", "NORMAL", layout, context)
    draw_channel_texture_settings("Height", "HEIGHT", layout, context)
    draw_channel_texture_settings("Scattering", "SCATTERING", layout, context)
    draw_channel_texture_settings("Emission", "EMISSION", layout, context)






def draw_channel_texture_settings(name, material_channel, layout, context):
    '''Draws settings for the currently selected texture node in the specified material channel.'''
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    texture_node = layer_nodes.get_layer_node("TEXTURE", material_channel, selected_layer_index, context)

    if texture_node:
        row = layout.row(align=True)
        row.scale_y = SCALE_Y

        row.label(text=name)
        
        if material_channel == "COLOR":
            row.prop(layers[selected_layer_index], "color_texture_node_type", text="")

            row = layout.row()
            row.scale_y = 1.4
            row.prop(texture_node, "image", text="")
            


            

        if material_channel == "METALLIC":
            row.prop(layers[selected_layer_index], "metallic_texture_node_type", text="")

            row = layout.row()
            row.scale_y = SCALE_Y

            if layers[selected_layer_index].metallic_texture_node_type == 'VALUE':
                row.prop(texture_node.inputs[0], "default_value", slider=True, text="")

            else:
                row.prop(texture_node.outputs[0], "default_value", text="")

        if material_channel == "ROUGHNESS":
            row.prop(layers[selected_layer_index], "roughness_texture_node_type", text="")

            row = layout.row()
            row.scale_y = SCALE_Y
            if layers[selected_layer_index].roughness_texture_node_type == 'VALUE':
                row.prop(texture_node.inputs[0], "default_value", slider=True, text="")

            else:
                row.prop(texture_node.outputs[0], "default_value", text="")

        if material_channel == "NORMAL":
            row.prop(layers[selected_layer_index], "normal_texture_node_type", text="")

            row = layout.row()
            row.scale_y = SCALE_Y
            row.prop(texture_node.outputs[0], "default_value", text="")  

        if material_channel == "HEIGHT":
            row.prop(layers[selected_layer_index], "height_texture_node_type", text="")

            row = layout.row()
            row.scale_y = SCALE_Y
            if layers[selected_layer_index].height_texture_node_type == 'VALUE':
                row.prop(texture_node.inputs[0], "default_value", slider=True, text="")

            else:
                row.prop(texture_node.outputs[0], "default_value", text="")

        if material_channel == "SCATTERING":
            row.prop(layers[selected_layer_index], "scattering_texture_node_type", text="")

            row = layout.row()
            row.scale_y = SCALE_Y
            row.prop(texture_node.outputs[0], "default_value", text="")  

        if material_channel == "EMISSION":
            row.prop(layers[selected_layer_index], "emission_texture_node_type", text="")

            row = layout.row()
            row.scale_y = SCALE_Y
            row.prop(texture_node.outputs[0], "default_value", text="")