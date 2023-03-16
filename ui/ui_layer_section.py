# This file handles drawing the user interface for the layers section.

import bpy
from .import ui_section_tabs
from ..layers import coater_materials
from ..layers import material_channel_nodes
from ..layers import layer_nodes
from ..layers import layer_stack as ls

SCALE_Y = 1.4

def draw_layers_section_ui(self, context):
    layout = self.layout
    ui_section_tabs.draw_section_tabs(self, context)
    draw_material_selector(self, context)
    draw_layer_operations(self)

    if context.active_object:
        active_material = context.active_object.active_material
        if active_material:
            if coater_materials.verify_material(context):
                draw_material_channel(self, context)
                
                # Don't draw inactive material channels.
                selected_material_channel = context.scene.coater_layer_stack.selected_material_channel
                selected_material_channel_active = True
                texture_set_settings = context.scene.coater_texture_set_settings
                if selected_material_channel == "COLOR" and texture_set_settings.color_channel_toggle == False:
                    selected_material_channel_active = False

                if selected_material_channel == "METALLIC" and texture_set_settings.metallic_channel_toggle == False:
                    selected_material_channel_active = False

                if selected_material_channel == "ROUGHNESS" and texture_set_settings.roughness_channel_toggle == False:
                    selected_material_channel_active = False

                if selected_material_channel == "NORMAL" and texture_set_settings.normal_channel_toggle == False:
                    selected_material_channel_active = False

                if selected_material_channel == "HEIGHT" and texture_set_settings.height_channel_toggle == False:
                    selected_material_channel_active = False

                if selected_material_channel == "SCATTERING" and texture_set_settings.scattering_channel_toggle == False:
                    selected_material_channel_active = False

                if selected_material_channel == "EMISSION" and texture_set_settings.emission_channel_toggle == False:
                    selected_material_channel_active = False

                if selected_material_channel_active:
                    layers = context.scene.coater_layers
                    draw_layer_stack(self, context)
                    
                    row = layout.row(align=True)
                    row.prop_enum(context.scene.coater_layer_stack, "layer_properties_tab", 'MATERIAL', text="MATERIAL")
                    row.prop_enum(context.scene.coater_layer_stack, "layer_properties_tab", 'MASKS', text="MASK")
                    row.prop_enum(context.scene.coater_layer_stack, "layer_properties_tab", 'FILTERS', text="FILTER")
                    

                    if len(layers) > 0:
                        layer_stack = context.scene.coater_layer_stack

                        if layer_stack.layer_properties_tab == "MATERIAL":
                            selected_layer_index = context.scene.coater_layer_stack.layer_index
                            layer_stack_index_exists = ls.verify_layer_stack_index(selected_layer_index, context)
                            if layer_stack_index_exists:
                                draw_layer_properties(self, context)

                        elif layer_stack.layer_properties_tab == "FILTERS":
                            row = layout.row(align=True)
                            row.scale_y = 2
                            row.scale_x = 10
                            row.operator("coater.add_layer_filter_menu", icon='FILTER', text="")
                            row.operator("coater.move_filter_up", icon='TRIA_UP', text="")
                            row.operator("coater.move_filter_down", icon='TRIA_DOWN', text="")
                            row.operator("coater.delete_layer_filter", icon='TRASH', text="")

                            layer_filter_stack = context.scene.coater_layer_filter_stack
                            row = layout.row(align=True)
                            row.scale_y = 2
                            row.template_list("COATER_UL_layer_filter_stack", "Layers", context.scene, "coater_layer_filters", layer_filter_stack, "selected_filter_index", sort_reverse=True)
                            
                        elif layer_stack.layer_properties_tab == "MASKS":
                            row = layout.row(align=True)
                            row.scale_y = 2
                            row.scale_x = 10
                            row.operator("coater.add_mask", icon='ADD', text="")
                            row.operator("coater.add_layer_mask_filter_menu", icon='FILTER', text="")
                            row.operator("coater.move_layer_mask_up", icon='TRIA_UP', text="")
                            row.operator("coater.move_layer_mask_down", icon='TRIA_DOWN', text="")
                            row.operator("coater.delete_layer_mask", icon='TRASH', text="")

                            mask_stack = context.scene.coater_mask_stack
                            row = layout.row(align=True)
                            row.scale_y = 2
                            row.template_list("COATER_UL_mask_stack", "Masks", context.scene, "coater_masks", mask_stack, "selected_mask_index", sort_reverse=True)
    else:
        layout = self.layout
        layout.label(text="Select an object.")


def draw_material_selector(self, context):
    '''Draws a material selector and layer stack refresh button.'''
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
            row.operator("coater.read_layer_nodes", text="", icon='FILE_REFRESH')
    row.scale_y = 1.5

def draw_layer_operations(self):
    layout = self.layout
    row = layout.row(align=True)
    row.scale_y = 2.0
    row.scale_x = 10
    row.operator("coater.add_layer", icon="ADD", text="")
    row.operator("coater.move_layer_up", icon="TRIA_UP", text="")
    row.operator("coater.move_layer_down", icon="TRIA_DOWN", text="")
    row.operator("coater.duplicate_layer", icon="DUPLICATE", text="")
    #row.operator("coater.merge_layer", icon="AUTOMERGE_OFF", text="")
    #row.operator("coater.bake_layer", icon="RENDER_STILL", text="")
    #row.operator("coater.image_editor_export", icon="EXPORT", text="")
    row.operator("coater.delete_layer", icon="TRASH", text="")

def draw_material_channel(self, context):
    '''Draws the currently selected material channel.'''
    layout = self.layout
    row = layout.row(align=True)
    row.prop(context.scene.coater_layer_stack, "selected_material_channel", text="")
    if context.scene.coater_layer_stack.material_channel_preview == False:
        row.operator("coater.toggle_channel_preview", text="", icon='MATERIAL')

    elif context.scene.coater_layer_stack.material_channel_preview == True:
        row.operator("coater.toggle_channel_preview", text="", icon='MATERIAL', depress=True)

    row.scale_x = 2
    row.scale_y = 1.4

def draw_layer_stack(self, context):
    layout = self.layout
    row = layout.row(align=True)
    layer_stack = context.scene.coater_layer_stack
    row.template_list("COATER_UL_layer_list", "Layers", context.scene, "coater_layers", layer_stack, "layer_index", sort_reverse=True)
    row.scale_y = 2



#----------------- DRAW LAYER PROPERTIES ----------------------#
def draw_material_projection_settings(self, context):
    '''Draws material projection settings.'''
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    layout = self.layout

    row = layout.row()
    row.alignment = 'CENTER'
    row.label(text="-------------------------------------------------------------------------------------------------------------")
    
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

def draw_material_channel_toggles(self, context):
    '''Draws options to quickly toggle material channels on and off.'''
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    texture_set_settings = context.scene.coater_texture_set_settings
    layout = self.layout

    row = layout.row()
    row = layout.row(align=False)
    row.scale_y = 1.4

    if texture_set_settings.color_channel_toggle:
        row.prop(layers[selected_layer_index], "color_channel_toggle", text="Color", toggle=1)

    if texture_set_settings.metallic_channel_toggle:
        row.prop(layers[selected_layer_index], "metallic_channel_toggle", text="Metal", toggle=1)

    if texture_set_settings.roughness_channel_toggle:
        row.prop(layers[selected_layer_index], "roughness_channel_toggle", text="Rough", toggle=1)

    if texture_set_settings.normal_channel_toggle:
        row.prop(layers[selected_layer_index], "normal_channel_toggle", text="Nrm", toggle=1)

    if texture_set_settings.height_channel_toggle:
        row.prop(layers[selected_layer_index], "height_channel_toggle", text="Height", toggle=1)

    if texture_set_settings.emission_channel_toggle:
        row.prop(layers[selected_layer_index], "emission_channel_toggle", text="Emit", toggle=1)

    if texture_set_settings.scattering_channel_toggle:
        row.prop(layers[selected_layer_index], "scattering_channel_toggle", text="Scatt", toggle=1)

def draw_material_channel_texture_settings(layout, context):
    '''Draws settings for the currently selected texture node in the each active material channel.'''
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    texture_set_settings = context.scene.coater_texture_set_settings

    # Get a list of all the material channels.
    material_channels = material_channel_nodes.get_material_channel_list()

    # Draw the texture node settings for every material channel.
    for i in range(0, len(material_channels)):
        texture_node = layer_nodes.get_layer_node("TEXTURE", material_channels[i], selected_layer_index, context)

        # If the texture node exists in the material channel, draw the texture settings.
        if texture_node:
            # TODO: If the texture node types can be stored in a list / array, this code can be greatly simplified.
            # Get the texture node type.
            if material_channels[i] == "COLOR":
                if layers[selected_layer_index].color_channel_toggle:
                    if texture_set_settings.color_channel_toggle:
                        # Draw a divider between texture node settings.
                        draw_divider(layout)

                        # Draw the material channel name.
                        row = layout.row(align=True)
                        row.scale_y = SCALE_Y
                        row.label(text=material_channels[i])

                        # Draw the texture settings.
                        texture_node_type = layers[selected_layer_index].color_texture_node_type
                        row.prop(layers[selected_layer_index], "color_texture_node_type", text="")
                        draw_texture_settings(layout, texture_node, texture_node_type, "COLOR", layers[selected_layer_index], "COLOR")

            if material_channels[i] == "METALLIC":
                if layers[selected_layer_index].metallic_channel_toggle:
                    if texture_set_settings.metallic_channel_toggle:
                        # Draw a divider between texture node settings.
                        draw_divider(layout)

                        # Draw the material channel name.
                        row = layout.row(align=True)
                        row.scale_y = SCALE_Y
                        row.label(text=material_channels[i])

                        # Draw the texture node settings
                        texture_node_type = layers[selected_layer_index].metallic_texture_node_type
                        row.prop(layers[selected_layer_index], "metallic_texture_node_type", text="")
                        draw_texture_settings(layout, texture_node, texture_node_type, "METALLIC", layers[selected_layer_index], "METALLIC")

            if material_channels[i] == "ROUGHNESS":
                if layers[selected_layer_index].roughness_channel_toggle:
                    if texture_set_settings.roughness_channel_toggle:
                        # Draw a divider between texture node settings.
                        draw_divider(layout)

                        # Draw the material channel name.
                        row = layout.row(align=True)
                        row.scale_y = SCALE_Y
                        row.label(text=material_channels[i])

                        # Draw the texture node settings
                        texture_node_type = layers[selected_layer_index].roughness_texture_node_type
                        row.prop(layers[selected_layer_index], "roughness_texture_node_type", text="")
                        draw_texture_settings(layout, texture_node, texture_node_type, "ROUGHNESS", layers[selected_layer_index], "ROUGHNESS")

            if material_channels[i] == "NORMAL":
                if layers[selected_layer_index].normal_channel_toggle:
                    if texture_set_settings.normal_channel_toggle:
                        # Draw a divider between texture node settings.
                        draw_divider(layout)

                        # Draw the material channel name.
                        row = layout.row(align=True)
                        row.scale_y = SCALE_Y
                        row.label(text=material_channels[i])

                        # Draw the texture node settings
                        texture_node_type = layers[selected_layer_index].normal_texture_node_type
                        row.prop(layers[selected_layer_index], "normal_texture_node_type", text="")
                        draw_texture_settings(layout, texture_node, texture_node_type, "NORMAL", layers[selected_layer_index], "NORMAL")

            if material_channels[i] == "HEIGHT":
                if layers[selected_layer_index].height_channel_toggle:
                    if texture_set_settings.height_channel_toggle:
                        # Draw a divider between texture node settings.
                        draw_divider(layout)

                        # Draw the material channel name.
                        row = layout.row(align=True)
                        row.scale_y = SCALE_Y
                        row.label(text=material_channels[i])

                        # Draw the texture node settings.
                        texture_node_type = layers[selected_layer_index].height_texture_node_type
                        row.prop(layers[selected_layer_index], "height_texture_node_type", text="")
                        draw_texture_settings(layout, texture_node, texture_node_type, "HEIGHT", layers[selected_layer_index], "HEIGHT")

            if material_channels[i] == "EMISSION":
                if layers[selected_layer_index].emission_channel_toggle:
                    if texture_set_settings.emission_channel_toggle:
                        # Draw a divider between texture node settings.
                        draw_divider(layout)

                        # Draw the material channel name.
                        row = layout.row(align=True)
                        row.scale_y = SCALE_Y
                        row.label(text=material_channels[i])

                        # Draw the texture node settings
                        texture_node_type = layers[selected_layer_index].emission_texture_node_type
                        row.prop(layers[selected_layer_index], "emission_texture_node_type", text="")
                        draw_texture_settings(layout, texture_node, texture_node_type, "EMISSION", layers[selected_layer_index], "EMISSION")

            if material_channels[i] == "SCATTERING":
                if layers[selected_layer_index].scattering_channel_toggle:
                    if texture_set_settings.scattering_channel_toggle:
                        # Draw a divider between texture node settings.
                        draw_divider(layout)

                        # Draw the material channel name.
                        row = layout.row(align=True)
                        row.scale_y = SCALE_Y
                        row.label(text=material_channels[i])

                        # Draw the texture node settings
                        texture_node_type = layers[selected_layer_index].scattering_texture_node_type
                        row.prop(layers[selected_layer_index], "scattering_texture_node_type", text="")
                        draw_texture_settings(layout, texture_node, texture_node_type, "SCATTERING", layers[selected_layer_index], "SCATTERING")

def draw_texture_settings(layout, texture_node, texture_node_type, material_channel, layer, material_channel_name):
    '''Draws the texture setting based on the given texture node type.'''
    if texture_node_type == "COLOR":
        row = layout.row(align=True)
        row.scale_y = SCALE_Y
        match material_channel_name:
            case "COLOR":
                row.prop(layer, "color_layer_color_preview", text="")

            case "METTALIC":
                row.prop(layer, "metallic_layer_color_preview", text="")

            case "ROUGHNESS":
                row.prop(layer, "roughness_layer_color_preview", text="")

            case "NORMAL":
                row.prop(layer, "normal_layer_color_preview", text="")

            case "HEIGHT":
                row.prop(layer, "height_layer_color_preview", text="")

            case "EMISSION":
                row.prop(layer, "emission_layer_color_preview", text="")

            case "SCATTERING":
                row.prop(layer, "scattering_layer_color_preview", text="")

            case _:
                # Show an error, the color preview can't be properly displayed.
                row.template_icon(2, scale=1)
            
    if texture_node_type == "VALUE":
        row = layout.row(align=True)
        row.scale_y = SCALE_Y
        match material_channel_name:
            case "COLOR":
                row.prop(layer, "uniform_color_value", text="", slider=True)

            case "ROUGHNESS":
                row.prop(layer, "uniform_roughness_value", text="", slider=True)

            case "METALLIC":
                row.prop(layer, "uniform_metallic_value", text="", slider=True)

            case "NORMAL":
                row.prop(layer, "uniform_normal_value", text="", slider=True)

            case "HEIGHT":
                row.prop(layer, "uniform_height_value", text="", slider=True)

            case "SCATTERING":
                row.prop(layer, "uniform_scattering_value", text="", slider=True)

            case "EMISSION":
                row.prop(layer, "uniform_emission_value", text="", slider=True)

            case _:
                row.prop(texture_node.outputs[0], "default_value", text="")

    if texture_node_type == "TEXTURE":
        row = layout.row(align=True)
        row.scale_y = SCALE_Y
        row.prop(texture_node, "image", text="")

        # Draw buttons to add / import / delete image textures quickly.
        add_layer_image_operator = row.operator("coater.add_layer_image", icon="ADD", text="")
        import_texture_operator = row.operator("coater.import_texture", icon="IMPORT", text="")
        unlink_image_operator = row.operator("coater.unlink_layer_image", icon="UNLINKED", text="")
        delete_layer_image_operator = row.operator("coater.delete_layer_image", icon="TRASH", text="")

        # Notify the operators the desired material channel work for the specified material channel.
        add_layer_image_operator.material_channel = material_channel
        import_texture_operator.material_channel = material_channel
        unlink_image_operator.material_channel = material_channel
        delete_layer_image_operator.material_channel = material_channel

    if texture_node_type == "NOISE":
        row = layout.row(align=True)
        row.scale_y = SCALE_Y
        row.prop(texture_node.inputs[2], "default_value", text="Scale", slider=True)
        row = layout.row(align=True)
        row.scale_y = SCALE_Y
        row.prop(texture_node.inputs[3], "default_value", text="Detail", slider=True)
        row = layout.row(align=True)
        row.scale_y = SCALE_Y
        row.prop(texture_node.inputs[4], "default_value", text="Roughness", slider=True)
        row = layout.row(align=True)
        row.scale_y = SCALE_Y
        row.prop(texture_node.inputs[5], "default_value", text="Distortion", slider=True)

    if texture_node_type == "VORONOI":
        row = layout.row(align=True)
        row.scale_y = SCALE_Y
        row.prop(texture_node.inputs[2], "default_value", text="Scale", slider=True)

        row = layout.row(align=True)
        row.scale_y = SCALE_Y
        row.prop(texture_node.inputs[3], "default_value", text="Randomness", slider=True)

    if texture_node_type == "MUSGRAVE":
        row = layout.row(align=True)
        row.scale_y = SCALE_Y
        row.prop(texture_node.inputs[2], "default_value", text="Scale", slider=True)
        row = layout.row(align=True)
        row.scale_y = SCALE_Y
        row.prop(texture_node.inputs[3], "default_value", text="Detail", slider=True)
        row = layout.row(align=True)
        row.scale_y = SCALE_Y
        row.prop(texture_node.inputs[4], "default_value", text="Dimension", slider=True)
        row = layout.row(align=True)
        row.scale_y = SCALE_Y
        row.prop(texture_node.inputs[5], "default_value", text="Lacunarity", slider=True)

def draw_divider(layout):
    row = layout.row()
    row.alignment = 'CENTER'
    row.label(text="-------------------------------------------------------------------------------------------------------------")

def draw_layer_properties(self, context):
    '''Draws layer properties such as projection settings, active material channels, and texture settings.'''
    draw_material_channel_toggles(self, context)
    draw_material_channel_texture_settings(self.layout, context)
    draw_material_projection_settings(self, context)

    