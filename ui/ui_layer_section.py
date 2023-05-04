# This file handles drawing the user interface for the layers section.

import bpy
from ..core import matlay_materials
from ..core import material_channels
from ..core import material_layers
from ..core import layer_nodes
from ..core import layer_masks
from ..core import material_filters as mf
from ..core import texture_set_settings as tss
from ..ui import ui_section_tabs

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
        if bpy.context.active_object.type == 'MESH':
            if context.active_object.active_material:
                if matlay_materials.verify_material(context):
                    if material_layers.validate_material_layer_stack_index(context.scene.matlay_layer_stack.layer_index, context):
                        draw_layer_properties(column1, context, layout)
            else:
                column1.label(text="No active material, add a layer to begin editing.")

        # Layer stack (second column).
        column2 = split.column()
        draw_material_selector(column2, context)
        draw_layer_operations(column2)
        draw_selected_material_channel(column2, context)
            
        selected_material_channel = context.scene.matlay_layer_stack.selected_material_channel

        selected_material_channel_active = get_material_channel_active(context, selected_material_channel)
        if bpy.context.active_object.type == 'MESH':
            if len(context.scene.matlay_layers) > 0:
                if selected_material_channel_active:
                    draw_layer_stack(column2, context)
                else:
                    subrow = column2.row(align=True)
                    subrow.label(text="Selected material channel inactive in texture set.")
            else:
                subrow = column2.row(align=True)
                subrow.label(text="No layers, add a layer to see the layer stack.")
        else:
            subrow = column2.row(align=True)
            subrow.label(text="Select a mesh to be able to edit materials.")

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
        row.template_ID(active_object, "active_material", new="matlay.add_layer", live_icon=True)
        row.operator("matlay.read_layer_nodes", text="", icon='FILE_REFRESH')
    row.scale_y = 1.5

def draw_layer_operations(column):
    '''Draws layer operation buttons.'''
    subrow = column.row(align=True)
    subrow.scale_y = 2.0
    subrow.scale_x = 10
    subrow.operator("matlay.add_layer_menu", icon="ADD", text="")
    operator = subrow.operator("matlay.move_material_layer", icon="TRIA_UP", text="")
    operator.direction = 'UP'
    operator = subrow.operator("matlay.move_material_layer", icon="TRIA_DOWN", text="")
    operator.direction = 'DOWN'
    subrow.operator("matlay.duplicate_layer", icon="DUPLICATE", text="")
    subrow.operator("matlay.delete_layer", icon="TRASH", text="")

def draw_selected_material_channel(column, context):
    '''Draws the selected material channel.'''
    subrow = column.row(align=True)
    subrow.scale_x = 2
    subrow.scale_y = 1.4
    subrow.prop(context.scene.matlay_layer_stack, "selected_material_channel", text="")
    if context.scene.matlay_layer_stack.material_channel_preview == False:
        subrow.operator("matlay.toggle_material_channel_preview", text="", icon='MATERIAL')

    elif context.scene.matlay_layer_stack.material_channel_preview == True:
        subrow.operator("matlay.toggle_material_channel_preview", text="", icon='MATERIAL', depress=True)

def draw_layer_stack(column, context):
    '''Draws the material layer stack along with it's operators and material channel.'''
    if len(context.scene.matlay_layers) > 0:
        subrow = column.row(align=True)
        subrow.template_list("MATLAY_UL_layer_list", "Layers", context.scene, "matlay_layers", context.scene.matlay_layer_stack, "layer_index", sort_reverse=True)
        subrow.scale_y = 2


#----------------- DRAW MATERIAL EDITING UI ----------------------#

def draw_divider(column):
    '''Draws a horizontal divider to provide visual spacing between elements.'''
    # Blender doesn't seem to support drawing a horizontal divider with the standard ui drawing tools, this is a work-around using a label.
    # Alternatively to this solution this could be used: layout.row().separator()
    subrow = column.row()
    subrow.alignment = 'CENTER'
    subrow.ui_units_x = 10
    subrow.label(text="----------------------------------------------------------------------------------------")

def draw_layer_utility_buttons(column, context):
    '''Draws buttons with helpful utility functions for the selected layer.'''
    material_layers = context.scene.matlay_layers
    selected_material_layer_index = context.scene.matlay_layer_stack.layer_index

    column.label(text="LAYER UTILITY FUNCTIONS")
    subrow = column.row(align=True)
    subrow.scale_y = 1.4
    subrow.operator("matlay.import_texture_set", icon='MATERIAL')
    
    if material_layers[selected_material_layer_index].type == 'DECAL':
        subrow.operator("matlay.set_decal_layer_snapping", icon='SNAP_ON', text="Decal Snapping")
    draw_divider(column)

def draw_layer_material_channel_toggles(column, context):
    '''Draws options to quickly toggle material channels on and off.'''
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    texture_set_settings = context.scene.matlay_texture_set_settings

    subrow = column.row()
    subrow.scale_y = 1.4
    material_channel_list = material_channels.get_material_channel_list()

    # Determine the number of active material channels in the texture set settings so the material channel toggles can be drawn on two user interface lines rather than one in case there are too many.
    number_of_active_material_channels = tss.get_active_material_channel_count()

    number_of_drawn_channel_toggles = 0
    for i in range(len(material_channel_list)):
        attribute_name = material_channel_list[i].lower() + "_channel_toggle"
        if getattr(texture_set_settings.global_material_channel_toggles, attribute_name, None):
            material_channel_name_abbreviation = material_channels.get_material_channel_abbreviation(material_channel_list[i])
            subrow.prop(layers[selected_layer_index].material_channel_toggles, attribute_name, text=material_channel_name_abbreviation, toggle=1)

            # Add an additional row in the user interface for material channel toggles if there are a lot of active material channels.
            number_of_drawn_channel_toggles += 1
            if number_of_drawn_channel_toggles >= number_of_active_material_channels / 2 and number_of_active_material_channels >= 6:
                subrow = column.row()
                subrow.scale_y = 1.4
                number_of_drawn_channel_toggles = 0

def draw_texture_node_settings(column, texture_node, texture_node_type, layer, material_channel_name, context):
    '''Draws the texture node setting based on the given texture node type.'''
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
            add_layer_image_operator.material_channel_name = material_channel_name
            import_texture_operator = subrow.operator("matlay.import_texture", icon="IMPORT", text="")
            import_texture_operator.material_channel_name = material_channel_name
            export_image_operator = subrow.operator("matlay.edit_image_externally", icon="TPAINT_HLT", text="")
            export_image_operator.material_channel_name = material_channel_name
            export_image_operator.image_type = 'LAYER'
            reload_image_operator = subrow.operator("matlay.reload_image", icon="FILE_REFRESH", text="")
            reload_image_operator.material_channel_name = material_channel_name
            delete_layer_image_operator = subrow.operator("matlay.delete_layer_image", icon="TRASH", text="")
            delete_layer_image_operator.material_channel_name = material_channel_name

        case "GROUP_NODE":
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.template_ID(texture_node, "node_tree")

        case "NOISE":
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node, "noise_dimensions", text="", slider=True)
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
            subrow.prop(texture_node, "voronoi_dimensions", text="", slider=True)
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node, "feature", text="", slider=True)
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node, "distance", text="", slider=True)
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node.inputs[2], "default_value", text="Scale", slider=True)
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node.inputs[3], "default_value", text="Randomness", slider=True)

        case "MUSGRAVE":
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node, "musgrave_dimensions", text="", slider=True)
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node, "musgrave_type", text="", slider=True)
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
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node.inputs[6], "default_value", text="Offset", slider=True)
            subrow = column.row(align=True)
            subrow.scale_y = SCALE_Y
            subrow.prop(texture_node.inputs[7], "default_value", text="Gain", slider=True)

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

    material_channel_names = material_channels.get_material_channel_list()
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
    if layers[selected_layer_index].projection.projection_mode != 'FLAT':
        row.prop(layers[selected_layer_index].projection, "projection_offset_z")
            
    row = column.row()
    row.scale_y = SCALE_Y
    row.prop(layers[selected_layer_index].projection, "projection_rotation", slider=True)

    row = column.row()

    row.scale_y = SCALE_Y
    col = row.split()
    col.prop(layers[selected_layer_index].projection, "projection_scale_x")

    col = row.split()
    if layers[selected_layer_index].projection.match_layer_scale:
        col.enabled = False
    col.prop(layers[selected_layer_index].projection, "projection_scale_y")

    if layers[selected_layer_index].projection.projection_mode != 'FLAT':
        col = row.split()
        if layers[selected_layer_index].projection.match_layer_scale:
            col.enabled = False
        col.prop(layers[selected_layer_index].projection, "projection_scale_z")

    col = row.split()
    if layers[selected_layer_index].projection.match_layer_scale:
        col.prop(layers[selected_layer_index].projection, "match_layer_scale", icon="LOCKED", icon_only=True)
    else:
        col.prop(layers[selected_layer_index].projection, "match_layer_scale", icon="UNLOCKED", icon_only=True)

def draw_filter_material_channel_toggles(column, context):
    '''Draws material channel toggles for material filters.'''
    subrow = column.row()
    subrow.scale_y = 1.4
    material_channel_list = material_channels.get_material_channel_list()
    texture_set_settings = context.scene.matlay_texture_set_settings
    filters = context.scene.matlay_material_filters
    selected_filter_index = context.scene.matlay_material_filter_stack.selected_filter_index
    number_of_active_material_channels = tss.get_active_material_channel_count()

    number_of_drawn_channel_toggles = 0
    for i in range(len(material_channel_list)):
        attribute_name = material_channel_list[i].lower() + "_channel_toggle"
        if getattr(texture_set_settings.global_material_channel_toggles, attribute_name, None):
            material_channel_name_abbreviation = material_channels.get_material_channel_abbreviation(material_channel_list[i])
            subrow.prop(filters[selected_filter_index].material_channel_toggles, attribute_name, text=material_channel_name_abbreviation, toggle=1)

            # Add an additional row in the user interface for material channel toggles if there are a lot of active material channels.
            number_of_drawn_channel_toggles += 1
            if number_of_drawn_channel_toggles >= number_of_active_material_channels / 2 and number_of_active_material_channels >= 6:
                subrow = column.row()
                subrow.scale_y = 1.4
                number_of_drawn_channel_toggles = 0

def draw_material_filters(column, context, layout):
    '''Draws a layer stack of filters applied to the selected material layer and their settings.'''
    row = column.row(align=True)
    row.scale_y = 2
    row.scale_x = 10
    row.operator("matlay.add_layer_filter_menu", icon='ADD', text="")
    row.operator("matlay.move_filter_up", icon='TRIA_UP', text="")
    row.operator("matlay.move_filter_down", icon='TRIA_DOWN', text="")
    row.operator("matlay.delete_layer_filter", icon='TRASH', text="")

    # Draw filter stack.
    layer_filter_stack = context.scene.matlay_material_filter_stack
    row = column.row(align=True)
    row.template_list("MATLAY_UL_layer_filter_stack", "Layers", context.scene, "matlay_material_filters", layer_filter_stack, "selected_filter_index", sort_reverse=True)

    # Only draw filter settings if filters exist on the selected layer.
    material_filters = context.scene.matlay_material_filters
    if len(material_filters) <= 0:
        return
    
    row = column.row()
    row.separator()

    # Draw filter material channel toggles.
    draw_filter_material_channel_toggles(column, context)

    row = column.row()
    row.separator()

    # Draw filter settings.
    selected_material_channel = context.scene.matlay_layer_stack.selected_material_channel
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    selected_filter_index = context.scene.matlay_material_filter_stack.selected_filter_index
    filter_node = mf.get_material_filter_node(selected_material_channel, selected_layer_index, selected_filter_index)
    if filter_node:
        match filter_node.bl_static_type:
            case 'INVERT':
                row = column.row()
                row.scale_y = 1.4
                row.prop(filter_node.inputs[0], "default_value", text="Invert")

            case 'VALTORGB':
                row = column.row()
                row.scale_y = 1.4
                column.template_color_ramp(filter_node, "color_ramp")

            case 'HUE_SAT':
                row = column.row()
                row.scale_y = 1.4
                row.prop(filter_node.inputs[0], "default_value", text="Hue", slider=True)
                row = column.row()
                row.scale_y = 1.4
                row.prop(filter_node.inputs[1], "default_value", text="Saturation", slider=True)
                row = column.row()
                row.scale_y = 1.4
                row.prop(filter_node.inputs[2], "default_value", text="Value", slider=True)
                row = column.row()
                row.scale_y = 1.4
                row.prop(filter_node.inputs[3], "default_value", text="Fac", slider=True)

            case 'CURVE_RGB':
                row = column.row()
                row.scale_y = 1.4
                row.prop(filter_node.inputs[0], "default_value", text="Fac")
                column.template_curve_mapping(filter_node, "mapping", type='COLOR')

            case 'BRIGHTCONTRAST':
                row = column.row()
                row.scale_y = 1.4
                row.prop(filter_node.inputs[1], "default_value", text="Brightness")
                row = column.row()
                row.scale_y = 1.4
                row.prop(filter_node.inputs[2], "default_value", text="Contrast")

#----------------- DRAW MASK EDITING UI ----------------------#

def draw_mask_stack(column):
    '''Draw layer mask operations and stack.'''
    subrow = column.row(align=True)
    subrow.scale_y = 2
    subrow.scale_x = 10
    subrow.operator("matlay.open_layer_mask_menu", icon='ADD', text="")
    subrow.operator("matlay.move_layer_mask_up", icon='TRIA_UP', text="")
    subrow.operator("matlay.move_layer_mask_down", icon='TRIA_DOWN', text="")
    subrow.operator("matlay.delete_layer_mask", icon='TRASH', text="")

    mask_stack = bpy.context.scene.matlay_mask_stack
    subrow = column.row(align=True)
    subrow.scale_y = 2
    subrow.template_list("MATLAY_UL_mask_stack", "Masks", bpy.context.scene, "matlay_masks", mask_stack, "selected_mask_index", sort_reverse=True)

def draw_mask_node_properties(column):
    selected_mask_index = bpy.context.scene.matlay_mask_stack.selected_mask_index
    selected_layer_index = bpy.context.scene.matlay_layer_stack.layer_index
    selected_material_channel = bpy.context.scene.matlay_layer_stack.selected_material_channel
    masks = bpy.context.scene.matlay_masks

    subrow = column.row(align=True)
    subrow.scale_y = 1.4
    subrow.label(text="Mask Node Type")
    subrow.prop(masks[selected_mask_index], "node_type", text="")

    # Draw node properties based on mask node type.
    mask_node = layer_masks.get_mask_node('MaskTexture', selected_material_channel, selected_layer_index, selected_mask_index)
    if mask_node:
        subrow = column.row(align=True)
        subrow.scale_y = 1.4
        match mask_node.bl_static_type:
            case 'TEX_IMAGE':
                selected_mask_index = bpy.context.scene.matlay_mask_stack.selected_mask_index
                masks = bpy.context.scene.matlay_masks

                subrow.prop(masks[selected_mask_index], 'mask_image', text="")

                # Draw buttons to add / import / delete image masks quickly.
                subrow.operator("matlay.add_mask_image", icon="ADD", text="")
                subrow.operator("matlay.import_mask_image", icon="IMPORT", text="")
                export_image_operator = subrow.operator("matlay.edit_image_externally", icon="TPAINT_HLT", text="")
                export_image_operator.image_type = 'MASK'
                reload_image_operator = subrow.operator("matlay.reload_image", icon="FILE_REFRESH", text="")
                reload_image_operator.reload_mask = True
                subrow.prop(masks[selected_mask_index], 'use_alpha', icon='IMAGE_ALPHA', icon_only=True, toggle=True)
                subrow.operator("matlay.delete_mask_image", icon="TRASH", text="")

            case 'GROUP':
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.template_ID(mask_node, "node_tree") 

            case "TEX_NOISE":
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node, "noise_dimensions", text="", slider=True)
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node.inputs[2], "default_value", text="Scale", slider=True)
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node.inputs[3], "default_value", text="Detail", slider=True)
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node.inputs[4], "default_value", text="Roughness", slider=True)
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node.inputs[5], "default_value", text="Distortion", slider=True)

            case "TEX_VORONOI":
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node, "voronoi_dimensions", text="", slider=True)
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node, "feature", text="", slider=True)
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node, "distance", text="", slider=True)
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node.inputs[2], "default_value", text="Scale", slider=True)
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node.inputs[3], "default_value", text="Randomness", slider=True)

            case "TEX_MUSGRAVE":
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node, "musgrave_dimensions", text="", slider=True)
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node, "musgrave_type", text="", slider=True)
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node.inputs[2], "default_value", text="Scale", slider=True)
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node.inputs[3], "default_value", text="Detail", slider=True)
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node.inputs[4], "default_value", text="Dimension", slider=True)
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node.inputs[5], "default_value", text="Lacunarity", slider=True)
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node.inputs[6], "default_value", text="Offset", slider=True)
                subrow = column.row(align=True)
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_node.inputs[7], "default_value", text="Gain", slider=True)

def draw_mask_projection_settings(column):
    selected_material_layer_index = bpy.context.scene.matlay_layer_stack.layer_index
    selected_mask_index = bpy.context.scene.matlay_mask_stack.selected_mask_index
    masks = bpy.context.scene.matlay_masks

    # Decal layers can't swap their projection modes, don't draw this option in the user interface.
    if not layer_nodes.check_decal_layer(selected_material_layer_index):
        subrow = column.row(align=True)
        subrow.scale_y = 1.4
        row = column.row()
        row.scale_y = SCALE_Y
        row.prop(masks[selected_mask_index].projection, "projection_mode", text="Projection")

    row = column.row()
    row.scale_y = SCALE_Y
    row.prop(masks[selected_mask_index].projection, "texture_interpolation", text="Interpolation")

    row = column.row()
    row.scale_y = SCALE_Y
    row.prop(masks[selected_mask_index].projection, "texture_extension", text="Extension")

    if masks[selected_mask_index].projection.projection_mode == 'BOX':
        row = column.row()
        row.scale_y = SCALE_Y
        row.prop(masks[selected_mask_index].projection, "projection_blend")

    row = column.row()
    row.scale_y = SCALE_Y
    row.prop(masks[selected_mask_index].projection, "projection_offset_x")
    row.prop(masks[selected_mask_index].projection, "projection_offset_y")
    if masks[selected_mask_index].projection.projection_mode != 'FLAT':
        row.prop(masks[selected_mask_index].projection, "projection_offset_z")

    row = column.row()
    row.scale_y = SCALE_Y
    row.prop(masks[selected_mask_index].projection, "projection_rotation", slider=True)

    row = column.row()
    row.scale_y = SCALE_Y
    col = row.split()
    col.prop(masks[selected_mask_index].projection, "projection_scale_x")

    col = row.split()
    if masks[selected_mask_index].projection.match_layer_mask_scale:
        col.enabled = False
    col.prop(masks[selected_mask_index].projection, "projection_scale_y")

    if masks[selected_mask_index].projection.projection_mode != 'FLAT':
        col = row.split()
        if masks[selected_mask_index].projection.match_layer_mask_scale:
            col.enabled = False
        col.prop(masks[selected_mask_index].projection, "projection_scale_z")

    col = row.split()
    if masks[selected_mask_index].projection.match_layer_mask_scale:
        col.prop(masks[selected_mask_index].projection, "match_layer_mask_scale", text="", icon="LOCKED")

    else:
        col.prop(masks[selected_mask_index].projection, "match_layer_mask_scale", text="", icon="UNLOCKED")

def draw_mask_filters(column):
    '''Draws the mask filter stack with operators for material layer masks.'''
    subrow = column.row(align=True)
    subrow.scale_y = 2
    subrow.scale_x = 10
    subrow.operator("matlay.add_layer_mask_filter_menu", text="", icon='ADD')
    operator = subrow.operator("matlay.move_layer_mask_filter", text="", icon='TRIA_UP')
    operator.direction = 'UP'
    operator = subrow.operator("matlay.move_layer_mask_filter", text="", icon='TRIA_DOWN')
    operator.direction = 'DOWN'
    subrow.operator("matlay.delete_mask_filter", text="", icon='TRASH')

    mask_filter_stack = bpy.context.scene.matlay_mask_filter_stack
    subrow = column.row(align=True)
    subrow.template_list("MATLAY_UL_mask_filter_stack", "Masks", bpy.context.scene, "matlay_mask_filters", mask_filter_stack, "selected_mask_filter_index", sort_reverse=True)

    # Draw node settings based on the node type.
    selected_material_index = bpy.context.scene.matlay_layer_stack.layer_index
    selected_mask_index = bpy.context.scene.matlay_mask_stack.selected_mask_index
    selected_mask_filter_index = bpy.context.scene.matlay_mask_filter_stack.selected_mask_filter_index
    mask_filter_node = layer_masks.get_mask_filter_node('COLOR', selected_material_index, selected_mask_index, selected_mask_filter_index, False)
    if mask_filter_node:
        match mask_filter_node.bl_static_type:
            case 'INVERT':
                subrow = column.row()
                subrow.scale_y = SCALE_Y
                subrow.prop(mask_filter_node.inputs[0], "default_value", text="Invert")
            case 'VALTORGB':
                subrow = column.row()
                subrow.scale_y = SCALE_Y
                column.template_color_ramp(mask_filter_node, "color_ramp")

def draw_mask_properties(column):
    '''Draws tabs and properties for the seelcted layer mask.'''
    masks = bpy.context.scene.matlay_masks

    # Only draw masks properties if there's at least one mask.
    if len(masks) <= 0:
        return
    
    mask_stack = bpy.context.scene.matlay_mask_stack
    selected_mask_index = bpy.context.scene.matlay_mask_stack.selected_mask_index

    subrow = column.row(align=True)
    subrow.scale_y = 1.4
    subrow.prop_enum(mask_stack, "mask_property_tab", 'MASK', text='Mask')
    if masks[selected_mask_index].node_type == 'TEXTURE':
        subrow.prop_enum(mask_stack, "mask_property_tab", 'PROJECTION', text='Projection')
    subrow.prop_enum(mask_stack, "mask_property_tab", 'FILTERS', text='Mask Filters')

    match mask_stack.mask_property_tab:
        case 'MASK':
            draw_mask_node_properties(column)
    
        case 'PROJECTION':
            draw_mask_projection_settings(column)
    
        case 'FILTERS':
            draw_mask_filters(column)

#----------------- DRAW (ALL) LAYER PROPERTIES ----------------------#

def draw_layer_properties(column, context, layout):
    '''Draws material and mask properties for the selected layer based on the selected tab.'''
    layer_property_tab = context.scene.matlay_layer_stack.layer_property_tab
    selected_material_layer_index = context.scene.matlay_layer_stack.layer_index

    subrow = column.row(align=True)
    subrow.scale_y = 1.4
    subrow.prop_enum(context.scene.matlay_layer_stack, "layer_property_tab", 'MATERIAL', text='EDIT MATERIAL', icon='MATERIAL')
    subrow.prop_enum(context.scene.matlay_layer_stack, "layer_property_tab", 'MASK', text='EDIT MASK', icon='MOD_MASK')

    # Draw layer materials based on the selected tab.
    match layer_property_tab:
        case 'MATERIAL':
            subrow = column.row(align=True)
            subrow.scale_y = 1.4
            subrow.prop_enum(context.scene.matlay_layer_stack, "material_property_tab", 'MATERIAL', text="Material")
            if not layer_nodes.check_decal_layer(selected_material_layer_index):
                subrow.prop_enum(context.scene.matlay_layer_stack, "material_property_tab", 'PROJECTION', text="Projection")
            subrow.prop_enum(context.scene.matlay_layer_stack, "material_property_tab", 'FILTERS', text="Filters")
            subrow = column.column()
            subrow.separator()
            
            if material_layers.validate_material_layer_stack_index(selected_material_layer_index, context):
                material_property_tab = context.scene.matlay_layer_stack.material_property_tab
                match material_property_tab:
                    case 'MATERIAL':
                        draw_layer_utility_buttons(column, context)
                        draw_layer_material_channel_toggles(column, context)
                        draw_material_channel_node_properties(column, context)

                    case 'PROJECTION':
                        draw_material_projection_settings(column, context)

                    case 'FILTERS':
                        draw_material_filters(column, context, layout)
                        
        case 'MASK':
            draw_mask_stack(column)
            draw_mask_properties(column)

