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
                    row.prop_enum(layer_stack, "layer_properties_tab", 'PROJECTION')

                    if layer_stack.layer_properties_tab == "PROJECTION":
                        draw_projection_settings(self, context)

                    if layer_stack.layer_properties_tab == "MATERIAL":
                        draw_material_channels(self, context)
                        draw_layer_properties(self, context)
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

def draw_projection_settings(self, context):
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
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    # Draw layer properties for each active channel.
    draw_channel_node_value("Color", "COLOR", layout, context)
    draw_channel_node_value("Metallic", "METALLIC", layout, context)
    draw_channel_node_value("Roughness", "ROUGHNESS", layout, context)
    draw_channel_node_value("Normal", "NORMAL", layout, context)
    draw_channel_node_value("Height", "HEIGHT", layout, context)
    draw_channel_node_value("Scattering", "SCATTERING", layout, context)
    draw_channel_node_value("Emission", "EMISSION", layout, context)

'''
def draw_mask_properties(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    scale_y = 1.4

    if layers[layer_index].mask_node_name != "":
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index
        channel_node = layer_nodes.get_channel_node(context)

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
        row.operator("coater.delete_layer_image_mask", text="", icon="REMOVE")
        row.operator("coater.import_mask_image", text="", icon="IMPORT")

        #row = layout.row()
        #row.scale_y = scale_y
        #row.prop(mask_node, "extension")

        #row = layout.row()
        #row.scale_y = scale_y
        #row.prop(mask_node, "interpolation")

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
            

            # Draw Mask Scale
            split = layout.split()
            col = split.column()
            col.ui_units_x = 1
            col.scale_y = scale_y
            col.prop(layers[layer_index], "projected_mask_scale_x")

            col = split.column()
            col.ui_units_x = 0.1
            col.scale_y = scale_y
            layer_settings = context.scene.coater_layer_settings
            if layer_settings.match_layer_mask_scale:
                col.prop(layer_settings, "match_layer_mask_scale", text="", icon="LOCKED")

            else:
                col.prop(layer_settings, "match_layer_mask_scale", text="", icon="UNLOCKED")
           
            col = split.column()
            col.ui_units_x = 2
            col.scale_y = scale_y
            if layer_settings.match_layer_mask_scale:
                col.enabled = False
            col.prop(layers[layer_index], "projected_mask_scale_y")

        levels_node = channel_node.node_tree.nodes.get(layers[layer_index].mask_levels_node_name)
        row = layout.row()
        layout.template_color_ramp(levels_node, "color_ramp")

'''

def draw_channel_node_value(name, channel, layout, context):
    '''Draws the channels node value.'''
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    texture_node = layer_nodes.get_layer_node("TEXTURE", channel, selected_layer_index, context)

    if texture_node:
        row = layout.row(align=True)
        row.scale_y = SCALE_Y

        row.label(text=name)
        
        if channel == "COLOR":
            row.prop(layers[selected_layer_index], "color_texture_node_type", text="")

            row = layout.row()
            row.scale_y = SCALE_Y
            row.prop(texture_node.outputs[0], "default_value", text="")

        if channel == "METALLIC":
            row.prop(layers[selected_layer_index], "metallic_texture_node_type", text="")

            row = layout.row()
            row.scale_y = SCALE_Y

            if layers[selected_layer_index].metallic_texture_node_type == 'VALUE':
                row.prop(texture_node.inputs[0], "default_value", slider=True, text="")

            else:
                row.prop(texture_node.outputs[0], "default_value", text="")

        if channel == "ROUGHNESS":
            row.prop(layers[selected_layer_index], "roughness_texture_node_type", text="")

            row = layout.row()
            row.scale_y = SCALE_Y
            if layers[selected_layer_index].roughness_texture_node_type == 'VALUE':
                row.prop(texture_node.inputs[0], "default_value", slider=True, text="")

            else:
                row.prop(texture_node.outputs[0], "default_value", text="")

        if channel == "NORMAL":
            row.prop(layers[selected_layer_index], "normal_texture_node_type", text="")

            row = layout.row()
            row.scale_y = SCALE_Y
            row.prop(texture_node.outputs[0], "default_value", text="")  

        if channel == "HEIGHT":
            row.prop(layers[selected_layer_index], "height_texture_node_type", text="")

            row = layout.row()
            row.scale_y = SCALE_Y
            if layers[selected_layer_index].height_texture_node_type == 'VALUE':
                row.prop(texture_node.inputs[0], "default_value", slider=True, text="")

            else:
                row.prop(texture_node.outputs[0], "default_value", text="")

        if channel == "SCATTERING":
            row.prop(layers[selected_layer_index], "scattering_texture_node_type", text="")

            row = layout.row()
            row.scale_y = SCALE_Y
            row.prop(texture_node.outputs[0], "default_value", text="")  

        if channel == "EMISSION":
            row.prop(layers[selected_layer_index], "emission_texture_node_type", text="")

            row = layout.row()
            row.scale_y = SCALE_Y
            row.prop(texture_node.outputs[0], "default_value", text="")