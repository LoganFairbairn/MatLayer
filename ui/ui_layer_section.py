# This file handles drawing the user interface for the layers section.

import bpy
from .import ui_section_tabs
from ..layers import matlay_materials
from ..layers import material_channel_nodes
from ..layers import layer_nodes
from ..layers import layer_stack as ls

SCALE_Y = 1.4

def draw_layers_section_ui(self, context):
    '''Draws the layer section.'''
    ui_section_tabs.draw_section_tabs(self, context)
    layout = self.layout
    
    # Only draw if there is a selected object.
    if context.active_object:
        
        # Create a 2 column layout (to give lots of space for add-on ui).
        split = layout.split()

        # Layer properties (first column).
        column1 = split.column()
        if context.active_object.active_material:
            if matlay_materials.verify_material(context):
                if ls.verify_layer_stack_index(context.scene.matlay_layer_stack.layer_index, context):
                    draw_layer_properties(column1, context)

        else:
            column1.label(text="No active material.")

        # Layer stack (second column).
        column2 = split.column()
        draw_material_selector(column2, context)
        draw_layer_operations(column2)
        draw_selected_material_channel(column2, context)
            
        selected_material_channel = context.scene.matlay_layer_stack.selected_material_channel


        selected_material_channel_active = get_material_channel_active(context, selected_material_channel)
        if selected_material_channel_active and len(context.scene.matlay_layers) > 0:
            draw_layer_stack(column2, context)

    else:
        layout = self.layout
        layout.label(text="Select an object.")

def get_material_channel_active(context, material_channel_name):
    '''Returns true if the given material channel is active in both the texture set settings and the layer material channel toggles.'''
    texture_set_settings = context.scene.matlay_texture_set_settings
    return getattr(texture_set_settings.global_material_channel_toggles, material_channel_name.lower() + "_channel_toggle", None)

def draw_material_selector(column, context):
    '''Draws a material selector and layer stack refresh button.'''
    active_object = context.active_object
    row = column.row(align=True)
    if active_object:
        if active_object.active_material:
            row.template_ID(active_object, "active_material", new="matlay.add_color_layer", live_icon=True)

        else:
            row.template_ID(active_object, "active_material", new="matlay.add_color_layer", live_icon=True)

    if active_object:
        if active_object.active_material:
            row.operator("matlay.refresh_layer_nodes", text="", icon='FILE_REFRESH')
    row.scale_y = 1.5

def draw_layer_operations(column):
    # Draw the layer stack operator buttons.
    subrow = column.row(align=True)
    subrow.scale_y = 2.0
    subrow.scale_x = 10
    subrow.operator("matlay.add_layer", icon="ADD", text="")
    subrow.operator("matlay.move_layer_up", icon="TRIA_UP", text="")
    subrow.operator("matlay.move_layer_down", icon="TRIA_DOWN", text="")
    subrow.operator("matlay.duplicate_layer", icon="DUPLICATE", text="")
    #subrow.operator("matlay.merge_layer", icon="AUTOMERGE_OFF", text="")
    #subrow.operator("matlay.bake_layer", icon="RENDER_STILL", text="")
    #subrow.operator("matlay.image_editor_export", icon="EXPORT", text="")
    subrow.operator("matlay.delete_layer", icon="TRASH", text="")

def draw_selected_material_channel(column, context):
    '''Draws the selected material channel.'''
    subrow = column.row(align=True)
    subrow.scale_x = 2
    subrow.scale_y = 1.4
    subrow.prop(context.scene.matlay_layer_stack, "selected_material_channel", text="")
    if context.scene.matlay_layer_stack.material_channel_preview == False:
        subrow.operator("matlay.toggle_channel_preview", text="", icon='MATERIAL')

    elif context.scene.matlay_layer_stack.material_channel_preview == True:
        subrow.operator("matlay.toggle_channel_preview", text="", icon='MATERIAL', depress=True)

def draw_layer_stack(column, context):
    '''Draws the material layer stack along with it's operators and material channel.'''
    subrow = column.row(align=True)
    subrow.template_list("MATLAY_UL_layer_list", "Layers", context.scene, "matlay_layers", context.scene.matlay_layer_stack, "layer_index", sort_reverse=True)
    subrow.scale_y = 2



#----------------- DRAW MATERIAL PROPERTIES ----------------------#

def draw_divider(column):
    '''Draws a horizontal divider to provide visual spacing between elements.'''
    # Blender doesn't seem to support drawing a horizontal divider with the standard ui drawing tools, this is a work-around using a label.
    # Alternatively to this solution this could be used: layout.row().separator()
    subrow = column.row()
    subrow.alignment = 'CENTER'
    subrow.ui_units_x = 10
    subrow.label(text="----------------------------------------------------------------------------------------")

def draw_layer_material_channel_toggles(column, context):
    '''Draws options to quickly toggle material channels on and off.'''
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    texture_set_settings = context.scene.matlay_texture_set_settings

    subrow = column.row()
    subrow.scale_y = 1.4
    material_channel_list = material_channel_nodes.get_material_channel_list()

    # Determine the number of active material channels in the texture set settings so the material channel toggles
    # can be drawn on two user interface lines rather than one in case there are too many.
    number_of_active_material_channels = 0
    for material_channel_name in material_channel_list:
        attribute_name = material_channel_name.lower() + "_channel_toggle"
        if getattr(texture_set_settings.global_material_channel_toggles, attribute_name, None):
            number_of_active_material_channels += 1

    number_of_drawn_channel_toggles = 0
    for i in range(len(material_channel_list)):
        attribute_name = material_channel_list[i].lower() + "_channel_toggle"
        if getattr(texture_set_settings.global_material_channel_toggles, attribute_name, None):
            material_channel_name_abbreviation = material_channel_nodes.get_material_channel_abbreviation(material_channel_list[i])
            subrow.prop(layers[selected_layer_index].material_channel_toggles, attribute_name, text=material_channel_name_abbreviation, toggle=1)

            # Add an additional row in the user interface for material channel toggles if there are a lot of active material channels.
            number_of_drawn_channel_toggles += 1
            if number_of_drawn_channel_toggles >= number_of_active_material_channels / 2 and number_of_active_material_channels >= 6:
                subrow = column.row()
                subrow.scale_y = 1.4
                number_of_drawn_channel_toggles = 0

def draw_texture_node_settings(column, texture_node, texture_node_type, layer, material_channel_name, context):
    '''Draws the texture setting based on the given texture node type.'''
    principled_bsdf_node = context.active_object.active_material.node_tree.nodes.get('Principled BSDF')

    match texture_node_type:
        case "VALUE":
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(layer.uniform_channel_values, "uniform_" + material_channel_name.lower() + "_value", text="", slider=True)

        case "COLOR":
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(layer.color_channel_values, material_channel_name.lower() + "_channel_color", text="")

        case "TEXTURE":
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node, "image", text="")

            # Draw buttons to add / import / delete image textures quickly.
            add_layer_image_operator = subrow.operator("matlay.add_layer_image", icon="ADD", text="")
            import_texture_operator = subrow.operator("matlay.import_texture", icon="IMPORT", text="")
            delete_layer_image_operator = subrow.operator("matlay.delete_layer_image", icon="TRASH", text="")

            # Notify the operators the desired material channel work for the specified material channel.
            add_layer_image_operator.material_channel_name = material_channel_name
            import_texture_operator.material_channel_name = material_channel_name
            delete_layer_image_operator.material_channel_name = material_channel_name

        case "GROUP_NODE":
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.template_ID(texture_node, "node_tree")

        case "NOISE":
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node.inputs[2], "default_value", text="Scale", slider=True)
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node.inputs[3], "default_value", text="Detail", slider=True)
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node.inputs[4], "default_value", text="Roughness", slider=True)
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node.inputs[5], "default_value", text="Distortion", slider=True)

        case "VORONOI":
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node.inputs[2], "default_value", text="Scale", slider=True)

            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node.inputs[3], "default_value", text="Randomness", slider=True)

        case "MUSGRAVE":
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node.inputs[2], "default_value", text="Scale", slider=True)
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node.inputs[3], "default_value", text="Detail", slider=True)
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node.inputs[4], "default_value", text="Dimension", slider=True)
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node.inputs[5], "default_value", text="Lacunarity", slider=True)

    # Draw additional settings for specific material channels.
    subrow = column.row()
    subrow.scale_y = SCALE_Y
    match material_channel_name:
        case "EMISSION":
            subrow.label(text="Emission Strength")
            subrow.prop(principled_bsdf_node.inputs[20], "default_value", text="")

        case "SCATTERING":
            subrow.label(text="Subsurface Color")
            subrow.prop(principled_bsdf_node.inputs[3], "default_value", text="")

def draw_material_channel_node_properties(column, context):
    '''Draws user interface for layer nodes representing material channels based on their type.'''
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    texture_set_settings = context.scene.matlay_texture_set_settings

    material_channel_names = material_channel_nodes.get_material_channel_list()
    for i in range(0, len(material_channel_names)):
        texture_node = layer_nodes.get_layer_node("TEXTURE", material_channel_names[i], selected_layer_index, context)
        attribute_name = material_channel_names[i].lower() + "_channel_toggle"
        if texture_node and getattr(texture_set_settings.global_material_channel_toggles, attribute_name, None) and getattr(layers[selected_layer_index].material_channel_toggles, material_channel_names[i].lower() + "_channel_toggle", None):
            draw_divider(column)
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.label(text=material_channel_names[i].replace("_", " "))

            # Draw the node type (allows users to see the selected node type for each material channel and easily switch it).
            subrow.prop(layers[selected_layer_index].channel_node_types, material_channel_names[i].lower() + "_node_type", text="")
            
            # Draw user interface settings for the material channel node based on it's type.
            texture_node_type = getattr(layers[selected_layer_index].channel_node_types, material_channel_names[i].lower() + "_node_type", None)
            draw_texture_node_settings(column, texture_node, texture_node_type, layers[selected_layer_index], material_channel_names[i], context)

def draw_material_projection_settings(column, context):
    '''Draws material projection settings.'''
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    
    row = column.row()
    row.scale_y = SCALE_Y
    row.prop(layers[selected_layer_index].projection, "projection_mode", text="Projection")

    row = column.row()
    row.scale_y = SCALE_Y
    row.prop(layers[selected_layer_index].projection, "texture_interpolation", text="Interpolation")

    row = column.row()
    row.scale_y = SCALE_Y
    row.prop(layers[selected_layer_index].projection, "texture_extension", text="Extension")

    if layers[selected_layer_index].projection.projection_mode == 'BOX':
        row = column.row()
        row.scale_y = SCALE_Y
        row.prop(layers[selected_layer_index].projection, "projection_blend")

    row = column.row()
    row.scale_y = SCALE_Y
    row.prop(layers[selected_layer_index].projection, "projection_offset_x")
    row.prop(layers[selected_layer_index].projection, "projection_offset_y")
            
    row = column.row()
    row.scale_y = SCALE_Y
    row.prop(layers[selected_layer_index].projection, "projection_rotation", slider=True)

    split = column.split()
    col = split.column()
    col.ui_units_x = 1
    col.scale_y = SCALE_Y
    col.prop(layers[selected_layer_index].projection, "projection_scale_x")

    col = split.column()
    col.ui_units_x = 0.1
    col.scale_y = SCALE_Y
    if layers[selected_layer_index].projection.match_layer_scale:
        col.prop(layers[selected_layer_index].projection, "match_layer_scale", text="", icon="LOCKED")

    else:
        col.prop(layers[selected_layer_index].projection, "match_layer_scale", text="", icon="UNLOCKED")
           
    col = split.column()
    col.ui_units_x = 2
    col.scale_y = SCALE_Y
    if layers[selected_layer_index].projection.match_layer_scale:
        col.enabled = False
    col.prop(layers[selected_layer_index].projection, "projection_scale_y")

def draw_material_filters(column, context):
    '''Draws a layer stack of filters applied to the selected material layer.'''
    row = column.row(align=True)
    row.scale_y = 2
    row.scale_x = 10
    row.operator("matlay.add_layer_filter_menu", icon='FILTER', text="")
    row.operator("matlay.move_filter_up", icon='TRIA_UP', text="")
    row.operator("matlay.move_filter_down", icon='TRIA_DOWN', text="")
    row.operator("matlay.delete_layer_filter", icon='TRASH', text="")

    layer_filter_stack = context.scene.matlay_layer_filter_stack
    row = column.row(align=True)
    row.scale_y = 2
    row.template_list("MATLAY_UL_layer_filter_stack", "Layers", context.scene, "matlay_layer_filters", layer_filter_stack, "selected_filter_index", sort_reverse=True)

#----------------- DRAW MASK PROPERTIES ----------------------#




#----------------- DRAW (ALL) LAYER PROPERTIES ----------------------#

def draw_layer_properties(column, context):
    '''Draws material and mask properties for the selected layer based on the selected tab.'''
    layer_property_tab = context.scene.matlay_layer_stack.layer_property_tab

    # Draw material channel toggles.
    draw_layer_material_channel_toggles(column, context)
    
    # Draw layer materials based on the selected tab.
    match layer_property_tab:
        case 'MATERIAL':
            draw_divider(column)
            subrow = column.row(align=True)
            subrow.scale_y = 1.2
            subrow.prop_enum(context.scene.matlay_layer_stack, "material_property_tab", 'MATERIAL', text='MATERIAL')
            subrow.prop_enum(context.scene.matlay_layer_stack, "material_property_tab", 'PROJECTION', text='PROJECTION')
            subrow.prop_enum(context.scene.matlay_layer_stack, "material_property_tab", 'FILTERS', text='FILTERS')

            selected_layer_index = context.scene.matlay_layer_stack.layer_index
            if ls.verify_layer_stack_index(selected_layer_index, context):
                material_property_tab = context.scene.matlay_layer_stack.material_property_tab
                match material_property_tab:
                    case 'MATERIAL':
                        draw_material_channel_node_properties(column, context)

                    case 'PROJECTION':
                        draw_material_projection_settings(column, context)

                    case 'FILTERS':
                        draw_material_filters(column, context)
                        
        case 'MASKS':
            subrow = column.row(align=True)
            subrow.scale_y = 2
            subrow.scale_x = 10
            subrow.operator("matlay.add_mask", icon='ADD', text="")
            subrow.operator("matlay.add_layer_mask_filter_menu", icon='FILTER', text="")
            subrow.operator("matlay.move_layer_mask_up", icon='TRIA_UP', text="")
            subrow.operator("matlay.move_layer_mask_down", icon='TRIA_DOWN', text="")
            subrow.operator("matlay.delete_layer_mask", icon='TRASH', text="")

            mask_stack = context.scene.matlay_mask_stack
            subrow = column.row(align=True)
            subrow.scale_y = 2
            subrow.template_list("MATLAY_UL_mask_stack", "Masks", context.scene, "matlay_masks", mask_stack, "selected_mask_index", sort_reverse=True)

            # Draw mask proprty tabs.
            subrow = column.row(align=True)
            subrow.prop_enum(context.scene.matlay_layer_stack, "material_property_tab", 'SETTINGS', text='SETTINGS')
            subrow.prop_enum(context.scene.matlay_layer_stack, "material_property_tab", 'PROJECTION', text='PROJECTION')

            #mask_property_tab = context.scene.matlay_layer_stack.mask_property_tab
            #match material_property_tab:
            #    case 'PROJECTION':

            #    case 'FILTERS':

