# This file handles drawing the user interface for the layers section.

import bpy
from bpy.types import Operator, Menu
from ..core import material_layers
from ..core import layer_masks
from ..core import mesh_map_baking
from ..core import blender_addon_utils
from ..core import texture_set_settings as tss
from ..ui import ui_section_tabs

DEFAULT_UI_SCALE_Y = 1

MATERIAL_LAYER_PROPERTY_TABS = [
    ("LAYER", "LAYER", "Properties for the selected material layer."),
    ("MASKS", "MASKS", "Properties for masks applied to the selected material layer."),
    ("GLOBAL", "GLOBAL", "Properties that affect all layers that comprise the active material")
]

def draw_layers_section_ui(self, context):
    '''Draws the layer section user interface to the add-on side panel.'''
    ui_section_tabs.draw_section_tabs(self, context)
    layout = self.layout

    split = layout.split()

    column_one = split.column()
    if bpy.context.active_object == None:
        row = column_one.row()
        row.label(text="No active object / selecting hidden object.")

    else:
        layer_count = material_layers.count_layers()
        if layer_count > 0:
            draw_material_property_tabs(column_one)
            match bpy.context.scene.matlayer_material_property_tabs:
                case 'LAYER':
                    draw_layer_projection(column_one)
                    draw_layer_material_channel_toggles(column_one)
                    draw_material_channel_properties(column_one)
                    draw_layer_properties(column_one)

                case 'MASKS':
                    draw_masks(column_one)

                case 'GLOBAL':
                    draw_global_material_properties(column_one)

    column_two = split.column()
    draw_material_selector(column_two)
    draw_selected_material_channel(column_two)
    draw_layer_operations(column_two)
    draw_layer_stack(column_two)

def draw_material_selector(layout):
    '''Draws a material selector and layer stack refresh button.'''
    active_object = bpy.context.active_object
    if active_object:
        split = layout.split(factor=0.90, align=True)
        first_column = split.column(align=True)
        second_column = split.column(align=True)
        second_column.scale_x = 0.1

        first_column.template_list("MATERIAL_UL_matslots", "Layers", bpy.context.active_object, "material_slots", bpy.context.active_object, "active_material_index")
        second_column.operator("matlayer.add_material_slot", text="", icon='ADD')
        second_column.operator("matlayer.remove_material_slot", text="-")
        second_column.operator("matlayer.move_material_slot_up", text="", icon='TRIA_UP')
        second_column.operator("matlayer.move_material_slot_down", text="", icon='TRIA_DOWN')
        second_column.operator("object.material_slot_assign", text="", icon='MATERIAL_DATA')
        second_column.operator("object.material_slot_select", text="", icon='SELECT_SET')

        split = layout.split(factor=0.70)
        first_column = split.column()
        second_column = split.column()
        col = first_column.column()
        if bpy.context.active_object:
            col.prop(bpy.context.active_object, "active_material", text="")
            col.prop(bpy.context.scene, "matlayer_merge_material", text="")
            col = second_column.column()
            col.scale_y = 2.0
            col.operator("matlayer.merge_materials", text="Merge")

def draw_selected_material_channel(layout):
    '''Draws the selected material channel.'''
    row = layout.row(align=True)
    row.scale_x = 2
    row.scale_y = 1.4
    row.prop(bpy.context.scene.matlayer_layer_stack, "selected_material_channel", text="")
    row.operator("matlayer.isolate_material_channel", text="", icon='MATERIAL')

def draw_layer_operations(layout):
    '''Draws layer operation buttons.'''
    row = layout.row(align=True)
    row.scale_y = 2.0
    row.scale_x = 10
    row.operator("matlayer.add_material_layer_menu", icon="ADD", text="")
    row.operator("matlayer.move_material_layer_up", icon="TRIA_UP", text="")
    row.operator("matlayer.move_material_layer_down", icon="TRIA_DOWN", text="")
    row.operator("matlayer.duplicate_layer", icon="DUPLICATE", text="")
    row.operator("matlayer.delete_layer", icon="TRASH", text="")

def draw_layer_stack(layout):
    '''Draws the material layer stack along with it's operators and material channel.'''
    row = layout.row(align=True)
    row.template_list("MATLAYER_UL_layer_list", "Layers", bpy.context.scene, "matlayer_layers", bpy.context.scene.matlayer_layer_stack, "selected_layer_index", sort_reverse=True)
    row.scale_y = 2

def draw_material_property_tabs(layout):
    '''Draws tabs to change between editing the material layer and the masks applied to the material layer.'''
    row = layout.row(align=True)
    row.scale_y = 1.5
    row.prop_enum(bpy.context.scene, "matlayer_material_property_tabs", 'LAYER')
    row.prop_enum(bpy.context.scene, "matlayer_material_property_tabs", 'MASKS')
    row.prop_enum(bpy.context.scene, "matlayer_material_property_tabs", 'GLOBAL')
    row.menu("MATLAYER_MT_layer_utility_sub_menu", text="", icon='MODIFIER_ON')

def draw_layer_material_channel_toggles(layout):
    '''Draws on / off toggles for individual material channels.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index

    row = layout.row()
    row.separator()
    row.scale_y = 2
    row = layout.row()
    row.label(text="CHANNEL TOGGLES")

    row = layout.row()
    row.scale_y = DEFAULT_UI_SCALE_Y
    drawn_toggles = 0
    
    for material_channel_name in material_layers.MATERIAL_CHANNEL_LIST:

        # Do not draw toggles for globally inactive material channels.
        if not tss.get_material_channel_active(material_channel_name):
            continue

        mix_node = material_layers.get_material_layer_node('MIX', selected_layer_index, material_channel_name)
        if mix_node:
            row.prop(mix_node, "mute", text=material_layers.get_shorthand_material_channel_name(material_channel_name), toggle=True, invert_checkbox=True)
            drawn_toggles += 1
            if drawn_toggles > 4:
                row = layout.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                drawn_toggles = 0

def draw_value_node(layout, value_node, mix_node, layer_node_tree, selected_layer_index, material_channel_name):
    '''Draws the value node type to the UI.'''

    match value_node.bl_static_type:
        case 'GROUP':
            row = layout.row(align=True)
            row.context_pointer_set("mix_node", mix_node)
            row.menu('MATLAYER_MT_material_channel_value_node_sub_menu', text="", icon='NODETREE')
            row.prop(value_node, "node_tree", text="")

        case 'TEX_IMAGE':
            split = layout.split(factor=0.825)
            first_column = split.column()
            second_column = split.column()

            row = first_column.row(align=True)
            row.context_pointer_set("mix_node", mix_node)
            row.menu('MATLAYER_MT_material_channel_value_node_sub_menu', text="", icon='IMAGE_DATA')
            row.prop(value_node, "image", text="")
            row.context_pointer_set("node_tree", layer_node_tree)
            row.context_pointer_set("node", value_node)
            row.menu("MATLAYER_MT_image_utility_sub_menu", text="", icon='DOWNARROW_HLT')

            row = second_column.row(align=True)
            mix_image_alpha_node = material_layers.get_material_layer_node('MIX_IMAGE_ALPHA', selected_layer_index, material_channel_name)
            if mix_image_alpha_node.mute:
                operator = row.operator("matlayer.toggle_image_alpha_blending", text="", icon='IMAGE_ALPHA')
            else:
                operator = row.operator("matlayer.toggle_image_alpha_blending", text="", icon='IMAGE_ALPHA', depress=True)
            operator.material_channel_name = material_channel_name
            row.context_pointer_set("mix_node", mix_node)
            output_channel_name = material_layers.get_material_channel_output_channel(material_channel_name)
            if len(output_channel_name) > 0:
                row.menu("MATLAYER_MT_material_channel_output_sub_menu", text=output_channel_name[0])

def draw_material_channel_filter_node(layout, material_channel_name, selected_layer_index):
    '''Draws the material channel filter toggle and group node used to filter the material channel.'''
    filter_node = material_layers.get_material_layer_node('FILTER', selected_layer_index, material_channel_name)
    if filter_node:
        split = layout.split(align=True, factor=0.08)
        row = split.column(align=True)

        if blender_addon_utils.get_node_active(filter_node) == True:
            operator = row.operator("matlayer.toggle_material_channel_filter", text='', icon='FILTER', depress=True)
        else:
            operator = row.operator("matlayer.toggle_material_channel_filter", text='', icon='FILTER')
        operator.material_channel_name = material_channel_name
        row = split.column(align=True)
        if filter_node.mute:
            row.enabled = False
        row.prop(filter_node, "node_tree", text="")

def draw_material_channel_filter_properties(layout, selected_layer_index, material_channel_name):
    '''Draws properties for material channel filter group node.'''
    filter_node = material_layers.get_material_layer_node('FILTER', selected_layer_index, material_channel_name)
    if filter_node:
        split = layout.split(factor=0.25)
        first_column = split.column()
        second_column = split.column()
    
        if blender_addon_utils.get_node_active(filter_node) == True:

            # Draw all group node input properties.
            for i in range(0, len(filter_node.inputs)):
                if i == 0:
                    continue
                row = first_column.row()
                row.label(text=filter_node.inputs[i].name)
                row = second_column.row()
                row.prop(filter_node.inputs[i], "default_value", text="")
            
            # Draw all color ramp properties from within node groups.
            for node in filter_node.node_tree.nodes:
                if node.bl_static_type == 'VALTORGB':
                    layout.template_color_ramp(node, "color_ramp", expand=True)

def draw_group_node_properties(layout, value_node):
    '''Draws properties for the provided value node.'''
    match value_node.bl_static_type:
        case 'GROUP':
            for i in range(0, len(value_node.inputs)):
                row = layout.row()
                if value_node.inputs[i].type == 'RGBA':
                    row.prop(value_node.inputs[i], "default_value", text="")
                else:
                    row.prop(value_node.inputs[i], "default_value", text=value_node.inputs[i].name)

def draw_material_channel_properties(layout):
    '''Draws properties for all active material channels on selected material layer.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index

    # Avoid drawing material channel properties for invalid layers.
    if material_layers.get_material_layer_node('LAYER', selected_layer_index) == None:
        return
    
    # Draw properties for all active material channels.
    for material_channel_name in material_layers.MATERIAL_CHANNEL_LIST:

        # Do not draw properties for globally inactive material channels.
        if not tss.get_material_channel_active(material_channel_name):
            continue

        layer_node_tree = material_layers.get_layer_node_tree(selected_layer_index)
        mix_node = material_layers.get_material_layer_node('MIX', selected_layer_index, material_channel_name)
        value_node = material_layers.get_material_layer_node('VALUE', selected_layer_index, material_channel_name)
        if value_node:
            
            # Only draw properties for material channels that are active in this layer.
            if not mix_node.mute:
                row = layout.row()
                row.separator()
                row = layout.row()
                row.label(text="• {0}".format(material_channel_name))
                draw_value_node(layout, value_node, mix_node, layer_node_tree, selected_layer_index, material_channel_name)
                draw_material_channel_filter_node(layout, material_channel_name, selected_layer_index)
                draw_group_node_properties(layout, value_node)
                draw_material_channel_filter_properties(layout, selected_layer_index, material_channel_name)

def draw_layer_projection(layout):
    '''Draws layer projection settings.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    
    # Draw the projection mode.
    projection_node = material_layers.get_material_layer_node('PROJECTION', selected_layer_index)
    if projection_node:
        match projection_node.node_tree.name:
            case 'ML_UVProjection':
                row = layout.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.label(text="LAYER PROJECTION")

                row = layout.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.menu('MATLAYER_MT_layer_projection_sub_menu', text="UV Projection")

                split = layout.split()
                col = split.column()
                col.scale_y = DEFAULT_UI_SCALE_Y
                col.prop(projection_node.inputs.get('OffsetX'), "default_value", text="Offset X", slider=True)
                col.prop(projection_node.inputs.get('OffsetY'), "default_value", text="Offset Y", slider=True)

                col = split.column()
                col.scale_y = DEFAULT_UI_SCALE_Y
                col.prop(projection_node.inputs.get('ScaleX'), "default_value", text="Scale X")
                col.prop(projection_node.inputs.get('ScaleY'), "default_value", text="Scale Y")

                row = layout.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.prop(projection_node.inputs.get('Rotation'), "default_value", text="Rotation", slider=True)

            case 'ML_TriplanarProjection':
                row = layout.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.label(text="LAYER PROJECTION")

                row = layout.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.menu('MATLAYER_MT_layer_projection_sub_menu', text="Triplanar Projection")

                split = layout.split()
                col = split.column()
                col.scale_y = DEFAULT_UI_SCALE_Y
                col.prop(projection_node.inputs.get('OffsetX'), "default_value", text="Offset X", slider=True)
                col.prop(projection_node.inputs.get('OffsetY'), "default_value", text="Offset Y", slider=True)
                col.prop(projection_node.inputs.get('OffsetZ'), "default_value", text="Offset Z", slider=True)

                col = split.column()
                col.scale_y = DEFAULT_UI_SCALE_Y
                col.prop(projection_node.inputs.get('RotationX'), "default_value", text="Rotation X", slider=True)
                col.prop(projection_node.inputs.get('RotationY'), "default_value", text="Rotation Y", slider=True)
                col.prop(projection_node.inputs.get('RotationZ'), "default_value", text="Rotation Z", slider=True)

                col = split.column()
                col.scale_y = DEFAULT_UI_SCALE_Y
                col.prop(projection_node.inputs.get('ScaleX'), "default_value", text="Scale X")
                col.prop(projection_node.inputs.get('ScaleY'), "default_value", text="Scale Y")
                col.prop(projection_node.inputs.get('ScaleZ'), "default_value", text="Scale Z")

                row = layout.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.prop(projection_node.inputs.get('Blending'), "default_value", text="Blending")
                row.menu("MATLAYER_MT_triplanar_projection_sub_menu", text="", icon='DOWNARROW_HLT')

def draw_mask_projection(layout):
    '''Draws projection settings for the selected mask.'''
    row = layout.row()
    row.scale_y = 2.5
    row.separator()

    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    selected_mask_index = bpy.context.scene.matlayer_mask_stack.selected_index
    mask_projection_node = layer_masks.get_mask_node('PROJECTION', selected_layer_index, selected_mask_index)
    mask_id_name = layer_masks.get_mask_id_name(selected_layer_index, selected_mask_index)
    if mask_projection_node:
        match mask_projection_node.node_tree.name:
            case 'ML_UVProjection':
                row = layout.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.label(text="MASK PROJECTION")

                if mask_id_name == 'IMAGE_MASK':
                    row = layout.row()
                    row.scale_y = DEFAULT_UI_SCALE_Y
                    row.menu('MATLAYER_MT_mask_projection_sub_menu', text="UV Projection")

                split = layout.split()
                col = split.column()
                col.scale_y = DEFAULT_UI_SCALE_Y
                col.prop(mask_projection_node.inputs.get('OffsetX'), "default_value", text="Offset X", slider=True)
                col.prop(mask_projection_node.inputs.get('OffsetY'), "default_value", text="Offset Y", slider=True)

                col = split.column()
                col.scale_y = DEFAULT_UI_SCALE_Y
                col.prop(mask_projection_node.inputs.get('ScaleX'), "default_value", text="Scale X")
                col.prop(mask_projection_node.inputs.get('ScaleY'), "default_value", text="Scale Y")

                row = layout.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.prop(mask_projection_node.inputs.get('Rotation'), "default_value", text="Rotation", slider=True)

            case 'ML_TriplanarProjection':
                row = layout.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.label(text="MASK PROJECTION")

                if mask_id_name == 'IMAGE_MASK':
                    row = layout.row()
                    row.scale_y = DEFAULT_UI_SCALE_Y
                    row.menu('MATLAYER_MT_mask_projection_sub_menu', text="Triplanar Projection")

                split = layout.split()
                col = split.column()
                col.scale_y = DEFAULT_UI_SCALE_Y
                col.prop(mask_projection_node.inputs.get('OffsetX'), "default_value", text="Offset X", slider=True)
                col.prop(mask_projection_node.inputs.get('OffsetY'), "default_value", text="Offset Y", slider=True)
                col.prop(mask_projection_node.inputs.get('OffsetZ'), "default_value", text="Offset Z", slider=True)

                col = split.column()
                col.scale_y = DEFAULT_UI_SCALE_Y
                col.prop(mask_projection_node.inputs.get('RotationX'), "default_value", text="Rotation X", slider=True)
                col.prop(mask_projection_node.inputs.get('RotationY'), "default_value", text="Rotation Y", slider=True)
                col.prop(mask_projection_node.inputs.get('RotationZ'), "default_value", text="Rotation Z", slider=True)

                col = split.column()
                col.scale_y = DEFAULT_UI_SCALE_Y
                col.prop(mask_projection_node.inputs.get('ScaleX'), "default_value", text="Scale X")
                col.prop(mask_projection_node.inputs.get('ScaleY'), "default_value", text="Scale Y")
                col.prop(mask_projection_node.inputs.get('ScaleZ'), "default_value", text="Scale Z")

                row = layout.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.prop(mask_projection_node.inputs.get('Blending'), "default_value", text="Blending")

def draw_mask_channel(layout, selected_layer_index, selected_mask_index):
    '''Draws the mask channel and sub menu to change the mask channel used.'''
    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()

    mask_filter_node = layer_masks.get_mask_node("FILTER", selected_layer_index, selected_mask_index)
    if mask_filter_node:
        row = first_column.row()
        row.label(text="Channel")

        if len(mask_filter_node.inputs[0].links) > 0:
            menu_label = mask_filter_node.inputs[0].links[0].from_socket.name
            row = second_column.row()
            row.menu("MATLAYER_MT_mask_channel_sub_menu", text=menu_label)

def draw_mask_properties(layout, mask_node, selected_layer_index, selected_mask_index):
    '''Draws group node properties for the selected mask.'''
    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()

    # Draw primary mask texture property ('TEXTURE_1').
    mask_texture_node = layer_masks.get_mask_node('TEXTURE', selected_layer_index, selected_mask_index, node_number=1)
    if mask_texture_node:
        row = first_column.row()
        texture_display_name = mask_texture_node.label.replace('_', ' ')
        texture_display_name = blender_addon_utils.capitalize_by_space(texture_display_name)
        row.label(text=texture_display_name)

        row = second_column.row(align=True)
        row.prop(mask_texture_node, "image", text="")
        row.context_pointer_set("node_tree", mask_node.node_tree)
        row.context_pointer_set("node", mask_texture_node)
        row.menu("MATLAYER_MT_image_utility_sub_menu", text="", icon='DOWNARROW_HLT')

    # Draw custom mask texture properties (if any exist).
    for node in mask_node.node_tree.nodes:
        if node.bl_static_type == 'TEX_IMAGE' and node.name not in mesh_map_baking.MESH_MAP_TYPES:
            if not node.name.startswith('TEXTURE_'):
                row = first_column.row()
                texture_display_name = node.label.replace('_', ' ')
                texture_display_name = blender_addon_utils.capitalize_by_space(texture_display_name)
                row.label(text=texture_display_name)

                row = second_column.row(align=True)
                row.prop(node, "image", text="")
                row.context_pointer_set("node_tree", mask_node.node_tree)
                row.context_pointer_set("node", node)
                row.menu("MATLAYER_MT_image_utility_sub_menu", text="", icon='DOWNARROW_HLT')

    # Draw mask group node input properties.
    for i in range(0, len(mask_node.inputs)):
        if mask_node.inputs[i].name != 'Mix':
            row = layout.row()
            row.scale_y = DEFAULT_UI_SCALE_Y
            row.prop(mask_node.inputs[i], "default_value", text=mask_node.inputs[i].name)

    # Draw blurring properties.
    blur_node = layer_masks.get_mask_node('BLUR', selected_layer_index, selected_mask_index)
    if blur_node:
        split = layout.split(factor=0.085)
        first_column = split.column()
        second_column = split.column()

        row = first_column.row()
        blur_value_row = second_column.row()
        if blender_addon_utils.get_node_active(blur_node):
            row.operator("matlayer.toggle_mask_blur", text="", icon='CHECKBOX_HLT', depress=True)
            blur_value_row.enabled = True
        else:
            row.operator("matlayer.toggle_mask_blur", text="", icon='CHECKBOX_DEHLT')
            blur_value_row.enabled = False

        blur_value_row.prop(blur_node.inputs.get('Blur Amount'), "default_value", text="Blur", slider=True)

    # Draw mask color ramp properties.
    mask_filter_node = layer_masks.get_mask_node('FILTER', selected_layer_index, selected_mask_index)
    if mask_filter_node:
        layout.template_color_ramp(mask_filter_node, "color_ramp", expand=True)

def draw_mask_mesh_maps(layout, selected_layer_index, selected_mask_index):
    '''Draws un-editable mesh maps used in the selected mask.'''
    drew_title = False
    for mesh_map_name in mesh_map_baking.MESH_MAP_TYPES:
        mesh_map_texture_node = layer_masks.get_mask_node(mesh_map_name, selected_layer_index, selected_mask_index)
        if mesh_map_texture_node:
            if not drew_title:
                row = layout.row()
                row.separator()
                row = layout.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.label(text="MESH MAPS")
                drew_title = True

            split = layout.split(factor=0.4)
            first_column = split.column()
            second_column = split.column()

            row = first_column.row()
            mesh_map_display_name = mesh_map_texture_node.label.replace('_', ' ')
            mesh_map_display_name = blender_addon_utils.capitalize_by_space(mesh_map_display_name)
            row.label(text=mesh_map_display_name)

            # Users should never be able to edit mesh maps, mesh maps are applied automatically when a mask requires them.
            row = second_column.row(align=True)
            row.enabled = False
            if mesh_map_texture_node.image:
                row.prop(mesh_map_texture_node.image, "name", text="")
            else:
                row.label(text="Not Baked")

def draw_masks(layout):
    row = layout.row(align=True)
    row.scale_x = 10
    row.scale_y = DEFAULT_UI_SCALE_Y + 1.0
    row.operator("matlayer.add_layer_mask_menu", icon="ADD", text="")
    row.operator("matlayer.move_layer_mask_up", icon="TRIA_UP", text="")
    row.operator("matlayer.move_layer_mask_down", icon="TRIA_DOWN", text="")
    row.operator("matlayer.duplicate_layer_mask", icon="DUPLICATE", text="")
    row.operator("matlayer.delete_layer_mask", icon="TRASH", text="")
    row = layout.row(align=True)
    row.template_list("MATLAYER_UL_mask_list", "Masks", bpy.context.scene, "matlayer_masks", bpy.context.scene.matlayer_mask_stack, "selected_index", sort_reverse=True)
    row.scale_y = 2

    # Draw properties for the selected mask.
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    selected_mask_index = bpy.context.scene.matlayer_mask_stack.selected_index
    mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, selected_mask_index)
    if mask_node:
        row = layout.row()
        row.scale_y = DEFAULT_UI_SCALE_Y
        row.label(text="MASK PROPERTIES")

        draw_mask_channel(layout, selected_layer_index, selected_mask_index)
        draw_mask_properties(layout, mask_node, selected_layer_index, selected_mask_index)
        draw_mask_projection(layout)
        draw_mask_mesh_maps(layout, selected_layer_index, selected_mask_index)

def draw_layer_blur_settings(layout):
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    blur_node = material_layers.get_material_layer_node('BLUR', selected_layer_index)

    if blur_node:
        split = layout.row()
        column_1 = split.column()
        column_2 = split.column()

        row = column_1.row()

        if blender_addon_utils.get_node_active(blur_node):
            row.operator("matlayer.toggle_layer_blur", text="", icon='CHECKBOX_HLT', depress=True)
            row = column_2.row()
            row.enabled = True

        else:
            row.operator("matlayer.toggle_layer_blur", text="", icon='CHECKBOX_DEHLT', depress=False)
            row = column_2.row()
            row.enabled = False

        row.prop(blur_node.inputs.get('Blur Amount'), "default_value", text="Blur Amount")

        if blender_addon_utils.get_node_active(blur_node):
            row = layout.row()
            drawn_toggles = 0
            for material_channel_name in material_layers.MATERIAL_CHANNEL_LIST:

                # Do not draw blur toggles for material channels not active in the texture set.
                if not tss.get_material_channel_active(material_channel_name):
                    continue

                blur_toggle_property_name = "{0}BlurToggle".format(material_channel_name.capitalize())
                if blur_node.inputs.get(blur_toggle_property_name).default_value == 1:
                    operator = row.operator("matlayer.toggle_material_channel_blur", text=material_layers.get_shorthand_material_channel_name(material_channel_name), depress=True)
                    operator.material_channel_name = material_channel_name
                if blur_node.inputs.get(blur_toggle_property_name).default_value == 0:
                    operator = row.operator("matlayer.toggle_material_channel_blur", text=material_layers.get_shorthand_material_channel_name(material_channel_name), depress=False)
                    operator.material_channel_name = material_channel_name
                
                drawn_toggles += 1
                if drawn_toggles >= 5:
                    row = layout.row()
                    drawn_toggles = 0

def draw_layer_properties(layout):
    '''Draws properties specific to the selected layer such as blurring, or decal properties.'''
    row = layout.row()
    row.separator()
    row.scale_y = 2

    row = layout.row()
    row.label(text="LAYER PROPERTIES")

    # Draw blur settings.
    draw_layer_blur_settings(layout)

def draw_global_material_properties(layout):
    '''Draws properties for the material.'''
    active_object = bpy.context.active_object
    if active_object:
        if active_object.active_material:
            row = layout.row()
            row.separator()
            row.scale_y = 2

            row = layout.row()
            row.label(text="GLOBAL PROPERTIES")

            split = layout.split(factor=0.4)
            first_column = split.column()
            second_column = split.column()

            # Draw the global base height value.
            normal_height_mix_node = material_layers.get_material_layer_node('NORMAL_HEIGHT_MIX')
            if normal_height_mix_node:
                row = first_column.row()
                row.label(text="Base Height")
                row = second_column.row()
                row.prop(normal_height_mix_node.inputs.get('Base Height'), "default_value", text="", slider=True)

            # Draw the global alpha clip value.
            if tss.get_material_channel_active('ALPHA'):
                row = first_column.row()
                row.label(text="Alpha Clip")
                row = second_column.row()
                row.prop(active_object.active_material, "alpha_threshold", text="")

            # Draw the global emission strength value.
            principled_bsdf_node = active_object.active_material.node_tree.nodes.get('MATLAYER_BSDF')
            if principled_bsdf_node:

                row = first_column.row()
                row.label(text="IOR")
                row = second_column.row()
                row.prop(principled_bsdf_node.inputs.get('IOR'), "default_value", text="", slider=True)

                row = first_column.row()
                row.label(text="Transmission Weight")
                row = second_column.row()
                row.prop(principled_bsdf_node.inputs.get('Transmission Weight'), "default_value", text="", slider=True)

                row = first_column.row()
                row.label(text="Transmission Roughness")
                row = second_column.row()
                row.prop(principled_bsdf_node.inputs.get('Transmission Roughness'), "default_value", text="", slider=True)

                row = first_column.row()
                row.label(text="Anisotropic")
                row = second_column.row()
                row.prop(principled_bsdf_node.inputs.get('Anisotropic'), "default_value", text="", slider=True)

                row = first_column.row()
                row.label(text="Anisotropic Rotation")
                row = second_column.row()
                row.prop(principled_bsdf_node.inputs.get('Anisotropic Rotation'), "default_value", text="", slider=True)

                row = first_column.row()
                row.label(text="Coat Weight")
                row = second_column.row()
                row.prop(principled_bsdf_node.inputs.get('Coat Weight'), "default_value", text="", slider=True)

                row = first_column.row()
                row.label(text="Coat Roughness")
                row = second_column.row()
                row.prop(principled_bsdf_node.inputs.get('Coat Roughness'), "default_value", text="", slider=True)

                row = first_column.row()
                row.label(text="Sheen Weight")
                row = second_column.row()
                row.prop(principled_bsdf_node.inputs.get('Sheen Weight'), "default_value", text="", slider=True)

                row = first_column.row()
                row.label(text="Sheen Tint")
                row = second_column.row()
                row.prop(principled_bsdf_node.inputs.get('Sheen Tint'), "default_value", text="", slider=True)

                if tss.get_material_channel_active('EMISSION'):
                    row = first_column.row()
                    row.label(text="Emission Strength")
                    row = second_column.row()
                    row.prop(principled_bsdf_node.inputs.get('Emission Strength'), "default_value", text="", slider=True)

                # Draw the global subsurface color value.
                if tss.get_material_channel_active('SUBSURFACE'):
                    row = first_column.row()
                    row.label(text="Subsurface Color")
                    row = second_column.row()
                    row.prop(principled_bsdf_node.inputs.get('Subsurface Color'), "default_value", text="", slider=True)

class MATLAYER_OT_add_material_layer_menu(Operator):
    bl_label = ""
    bl_idname = "matlayer.add_material_layer_menu"
    bl_description = "Opens a menu of material layer types that can be added to the active material"

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

    # Opens the popup when the add layer button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=150)

    # Draws the properties in the popup.
    def draw(self, context):
        layout = self.layout
        split = layout.split()
        col = split.column(align=True)
        col.scale_y = 1.4
        col.operator("matlayer.add_material_layer", text="Add Material")
        col.operator("matlayer.add_paint_material_layer", text="Add Paint")
        col.operator("matlayer.add_decal_material_layer", text="Add Decal")

class MATLAYER_OT_add_layer_mask_menu(Operator):
    bl_label = "Add Mask"
    bl_idname = "matlayer.add_layer_mask_menu"

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

    # Opens the popup when the add layer button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=150)

    # Draws the properties in the popup.
    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        col = row.column(align=True)
        col.scale_y = 1.4
        col.operator("matlayer.add_empty_layer_mask", text="Empty")
        col.operator("matlayer.add_black_layer_mask", text="Black")
        col.operator("matlayer.add_white_layer_mask", text="White")
        col.operator("matlayer.add_linear_gradient_mask", text="Linear Gradient")

        row = layout.row(align=True)
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        layer_projection_node = material_layers.get_material_layer_node('PROJECTION', selected_layer_index)
        if layer_projection_node:
            if layer_projection_node.node_tree.name != 'ML_DecalProjection':
                row.enabled = False
        col = row.column(align=True)
        col.scale_y = 1.4
        col.operator("matlayer.add_decal_mask", text="Decal")

        row = layout.row(align=True)
        col = row.column(align=True)
        col.scale_y = 1.4
        col.operator("matlayer.add_grunge_mask", text="Grunge")
        col.operator("matlayer.add_edge_wear_mask", text="Edge Wear")

class MATLAYER_OT_add_material_filter_menu(Operator):
    bl_label = ""
    bl_idname = "matlayer.add_material_filter_menu"

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

    # Opens the popup when the add layer button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=150)
    
    # Draws the properties in the popup.
    def draw(self, context):
        layout = self.layout
        split = layout.split()
        col = split.column(align=True)
        col.scale_y = 1.4
        col.operator("matlayer.add_material_filter_hsv", text="Add HSV")
        col.operator("matlayer.add_material_filter_color_ramp", text="Add Color Ramp")
        col.operator("matlayer.add_material_filter_invert", text="Add Invert")

class ImageUtilitySubMenu(Menu):
    bl_idname = "MATLAYER_MT_image_utility_sub_menu"
    bl_label = "Image Utility Sub Menu"

    def draw(self, context):
        layout = self.layout
        if context.node and context.node_tree:
            material_channel_name = context.node.name.split('_')[0]

            operator = layout.operator("matlayer.add_texture_node_image", icon="ADD", text="Add New Image")
            operator.node_tree_name = context.node_tree.name
            operator.node_name = context.node.name
            operator.material_channel_name = material_channel_name

            operator = layout.operator("matlayer.import_texture_node_image", icon="IMPORT", text="Import Image")
            operator.node_tree_name = context.node_tree.name
            operator.node_name = context.node.name
            operator.material_channel_name = material_channel_name

            operator = layout.operator("matlayer.edit_texture_node_image_externally", icon="TPAINT_HLT", text="Edit Image Externally")
            operator.node_tree_name = context.node_tree.name
            operator.node_name = context.node.name
            
            operator = layout.operator("matlayer.image_edit_uvs", icon="UV", text="Externally Image Edit UVs")
            operator = layout.operator("matlayer.export_uvs", icon="UV_DATA", text="Export UVs")

            operator = layout.operator("matlayer.reload_texture_node_image", icon="FILE_REFRESH", text="Reload Image")
            operator.node_tree_name = context.node_tree.name
            operator.node_name = context.node.name

            operator = layout.operator("matlayer.delete_texture_node_image", icon="TRASH", text="Delete Image")
            operator.node_tree_name = context.node_tree.name
            operator.node_name = context.node.name

class LayerProjectionModeSubMenu(Menu):
    bl_idname = "MATLAYER_MT_layer_projection_sub_menu"
    bl_label = "Layer Projection Sub Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("matlayer.set_layer_projection_uv", text="UV")
        layout.operator("matlayer.set_layer_projection_triplanar", text="Triplanar")

class MaskProjectionModeSubMenu(Menu):
    bl_idname = "MATLAYER_MT_mask_projection_sub_menu"
    bl_label = "Mask Projection Sub Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("matlayer.set_mask_projection_uv", text="UV")
        layout.operator("matlayer.set_mask_projection_triplanar", text="Triplanar")

class MaterialChannelValueNodeSubMenu(Menu):
    bl_idname = "MATLAYER_MT_material_channel_value_node_sub_menu"
    bl_label = "Material Channel Value Node Sub Menu"

    def draw(self, context):
        layout = self.layout

        # This is a work-around for not being able (or not knowing how) to pass a string to this sub-menu from the draw layout call.
        # Get the material channel name from the mix node being drawn.
        material_channel_name = context.mix_node.name.replace('_MIX', '')

        operator = layout.operator("matlayer.change_material_channel_value_node", text='GROUP', icon='NODETREE')
        operator.material_channel_name = material_channel_name
        operator.node_type = 'GROUP'

        operator = layout.operator("matlayer.change_material_channel_value_node", text='TEXTURE', icon='IMAGE_DATA')
        operator.material_channel_name = material_channel_name
        operator.node_type = 'TEXTURE'

class LayerUtilitySubMenu(Menu):
    bl_idname = "MATLAYER_MT_layer_utility_sub_menu"
    bl_label = "Layer Utility Sub Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("matlayer.import_texture_set", text="Import Texture Set")

class LayerTriplanarProjectionSubMenu(Menu):
    bl_idname = "MATLAYER_MT_triplanar_projection_sub_menu"
    bl_label = "Layer Projection Sub Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("matlayer.toggle_triplanar_flip_correction", text="Toggle Triplanar Axis Correction Flip")

class MaskChannelSubMenu(Menu):
    bl_idname = "MATLAYER_MT_mask_channel_sub_menu"
    bl_label = "Mask Channel Sub Menu"

    def draw(self, context):
        layout = self.layout
        operator = layout.operator("matlayer.set_mask_output_channel", text="Color")
        operator.channel_name = 'COLOR'
        operator = layout.operator("matlayer.set_mask_output_channel", text="Alpha")
        operator.channel_name = 'ALPHA'
        operator = layout.operator("matlayer.set_mask_output_channel", text="Red")
        operator.channel_name = 'RED'
        operator = layout.operator("matlayer.set_mask_output_channel", text="Green")
        operator.channel_name = 'GREEN'
        operator = layout.operator("matlayer.set_mask_output_channel", text="Blue")
        operator.channel_name = 'BLUE'

class MaterialChannelOutputSubMenu(Menu):
    bl_idname = "MATLAYER_MT_material_channel_output_sub_menu"
    bl_label = "Material Channel Output Sub Menu"

    def draw(self, context):
        material_channel_name = context.mix_node.name.replace('_MIX', '')

        layout = self.layout
        operator = layout.operator("matlayer.set_material_channel_output_channel", text="Color")
        operator.output_channel_name = 'COLOR'
        operator.material_channel_name = material_channel_name
        operator = layout.operator("matlayer.set_material_channel_output_channel", text="Alpha")
        operator.output_channel_name = 'ALPHA'
        operator.material_channel_name = material_channel_name
        operator = layout.operator("matlayer.set_material_channel_output_channel", text="Red")
        operator.output_channel_name = 'RED'
        operator.material_channel_name = material_channel_name
        operator = layout.operator("matlayer.set_material_channel_output_channel", text="Green")
        operator.output_channel_name = 'GREEN'
        operator.material_channel_name = material_channel_name
        operator = layout.operator("matlayer.set_material_channel_output_channel", text="Blue")
        operator.output_channel_name = 'BLUE'
        operator.material_channel_name = material_channel_name