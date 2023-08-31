# This file handles drawing the user interface for the layers section.

import bpy
from bpy.types import Operator, Menu
from ..core import material_layers
from ..core import layer_masks
from ..core import baking
from ..ui import ui_section_tabs
import re

DEFAULT_UI_SCALE_Y = 1

MATERIAL_LAYER_PROPERTY_TABS = [
    ("MATERIAL", "MATERIAL", "Properties for the selected material layer"),
    ("MASKS", "MASKS", "Properties for masks applied to the selected material layer")
]

def draw_layers_section_ui(self, context):
    '''Draws the layer section user interface to the add-on side panel.'''
    ui_section_tabs.draw_section_tabs(self, context)
    layout = self.layout

    split = layout.split()

    column_one = split.column()
    draw_material_property_tabs(column_one)
    match bpy.context.scene.matlayer_material_property_tabs:
        case 'MATERIAL':
            draw_layer_projection(column_one)
            draw_layer_material_channel_toggles(column_one)
            draw_material_channel_properties(column_one)
            draw_material_filters(column_one)

        case 'MASKS':
            draw_layer_masks(column_one)

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
        second_column.operator("object.material_slot_add", text="", icon='ADD')
        second_column.operator("object.material_slot_remove", text="-")
        operator = second_column.operator("object.material_slot_move", text="", icon='TRIA_UP')
        operator.direction = 'UP'
        operator = second_column.operator("object.material_slot_move", text="", icon='TRIA_DOWN')
        operator.direction = 'DOWN'
        second_column.operator("object.material_slot_assign", text="", icon='MATERIAL_DATA')
        second_column.operator("object.material_slot_select", text="", icon='SELECT_SET')

        row = layout.row(align=True)
        row.template_ID(active_object, "active_material", new="matlayer.add_layer", live_icon=True)

def draw_selected_material_channel(layout):
    '''Draws the selected material channel.'''
    subrow = layout.row(align=True)
    subrow.scale_x = 2
    subrow.scale_y = 1.4
    subrow.prop(bpy.context.scene.matlayer_layer_stack, "selected_material_channel", text="")
    if bpy.context.scene.matlayer_layer_stack.material_channel_preview == False:
        subrow.operator("matlayer.toggle_material_channel_preview", text="", icon='MATERIAL')

    elif bpy.context.scene.matlayer_layer_stack.material_channel_preview == True:
        subrow.operator("matlayer.toggle_material_channel_preview", text="", icon='MATERIAL', depress=True)

def draw_layer_operations(layout):
    '''Draws layer operation buttons.'''
    row = layout.row(align=True)
    row.scale_y = 2.0
    row.scale_x = 10
    row.operator("matlayer.add_material_layer_menu", icon="ADD", text="")
    row.operator("matlayer.add_material_effects_menu", icon="SHADERFX", text="")
    row.operator("matlayer.move_material_layer_up", icon="TRIA_UP", text="")
    row.operator("matlayer.move_material_layer_down", icon="TRIA_DOWN", text="")
    row.operator("matlayer.duplicate_layer", icon="DUPLICATE", text="")
    row.operator("matlayer.delete_layer", icon="TRASH", text="")

def draw_layer_stack(layout):
    '''Draws the material layer stack along with it's operators and material channel.'''
    if len(bpy.context.scene.matlayer_layers) > 0:
        row = layout.row(align=True)
        row.template_list("MATLAYER_UL_layer_list", "Layers", bpy.context.scene, "matlayer_layers", bpy.context.scene.matlayer_layer_stack, "selected_layer_index", sort_reverse=True)
        row.scale_y = 2

def draw_material_property_tabs(layout):
    '''Draws tabs to change between editing the material layer and the masks applied to the material layer.'''
    row = layout.row(align=True)
    row.scale_y = 1.5
    row.prop_enum(bpy.context.scene, "matlayer_material_property_tabs", 'MATERIAL')
    row.prop_enum(bpy.context.scene, "matlayer_material_property_tabs", 'MASKS')

def draw_layer_material_channel_toggles(layout):
    '''Draws on / off toggles for individual material channels.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    row = layout.row()
    row.separator()

    row = layout.row()
    row.alignment = 'LEFT'
    row.label(text="CHANNEL TOGGLES")

    row = layout.row()
    row.scale_y = 1.4
    drawn_toggles = 0
    for material_channel_name in material_layers.MATERIAL_CHANNEL_LIST:
        mix_node = material_layers.get_material_layer_node('MIX', selected_layer_index, material_channel_name)
        if mix_node:
            row.prop(mix_node, "mute", text=material_channel_name, toggle=True, invert_checkbox=True)
            drawn_toggles += 1
            if drawn_toggles > 4:
                row = layout.row()
                row.scale_y = 1.4
                drawn_toggles = 0

def draw_material_channel_properties(layout):
    '''Draws properties for all active material channels on selected material layer.'''
    row = layout.row()
    row.separator()
    row.scale_y = 2.5
    row = layout.row()
    row.label(text="CHANNEL PROPERTIES")

    layers = bpy.context.scene.matlayer_layers
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index

    # Avoid drawing material channel properties for invalid layers.
    if material_layers.get_material_layer_node('LAYER', selected_layer_index) == None or len(layers) <= 0:
        return

    for material_channel_name in material_layers.MATERIAL_CHANNEL_LIST:

        # Do not draw properties for globally inactive material channels.
        texture_set_settings = bpy.context.scene.matlayer_texture_set_settings
        material_channel_active = getattr(texture_set_settings.global_material_channel_toggles, "{0}_channel_toggle".format(material_channel_name.lower()))
        if not material_channel_active:
            continue

        # Do no draw properties for material channels inactive on this material layer.
        mix_node = material_layers.get_material_layer_node('MIX', selected_layer_index, material_channel_name)
        if mix_node:
            if mix_node.mute:
                continue

        row = layout.row()
        row.scale_y = DEFAULT_UI_SCALE_Y
        row.label(text=material_channel_name)
        row.prop(layers[selected_layer_index].material_channel_node_types, material_channel_name.lower() + "_node_type", text="")

        value_node = material_layers.get_material_layer_node('VALUE', selected_layer_index, material_channel_name)
        if value_node:

            # Draw values based on the node type used to represent the material channel value.
            match value_node.bl_static_type:
                case 'GROUP':
                    row = layout.row()
                    row.scale_y = DEFAULT_UI_SCALE_Y
                    row.template_ID(value_node, "node_tree")

                    # For group nodes used to represent default material channel values, draw only the first value.
                    if value_node.node_tree.name.startswith('ML_Default'):
                        row = layout.row()
                        row.scale_y = DEFAULT_UI_SCALE_Y
                        row.prop(value_node.inputs[0], "default_value", text="")

                    # For custom group nodes, draw all properties to the interface.
                    else:
                        for i in range(0, len(value_node.inputs)):
                            row = layout.row()
                            row.scale_y = DEFAULT_UI_SCALE_Y
                            row.prop(value_node.inputs[i], "default_value", text=value_node.inputs[i].name)

                case 'TEX_IMAGE':
                    row = layout.row(align=True)
                    row.scale_y = DEFAULT_UI_SCALE_Y
                    row.prop(value_node, "image", text="")
                    add_layer_image_operator = row.operator("matlayer.add_material_channel_image", icon="ADD", text="")
                    add_layer_image_operator.material_channel_name = material_channel_name
                    import_texture_operator = row.operator("matlayer.import_texture", icon="IMPORT", text="")
                    import_texture_operator.material_channel_name = material_channel_name
                    export_image_operator = row.operator("matlayer.edit_image_externally", icon="TPAINT_HLT", text="")
                    export_image_operator.material_channel_name = material_channel_name
                    reload_image_operator = row.operator("matlayer.reload_material_channel_image", icon="FILE_REFRESH", text="")
                    reload_image_operator.material_channel_name = material_channel_name
                    delete_layer_image_operator = row.operator("matlayer.delete_material_channel_image", icon="TRASH", text="")
                    delete_layer_image_operator.material_channel_name = material_channel_name

def draw_layer_projection(layout):
    row = layout.row()
    row.alignment = 'LEFT'
    row.scale_y = DEFAULT_UI_SCALE_Y
    row.label(text="LAYER PROJECTION")

    layers = bpy.context.scene.matlayer_layers
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index

    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.scale_y = DEFAULT_UI_SCALE_Y
    row.label(text="Mode")
    row = second_column.row()
    row.scale_y = DEFAULT_UI_SCALE_Y
    row.prop(layers[selected_layer_index].projection, "mode", text="", slider=True, index=0)

    projection_node = material_layers.get_material_layer_node('PROJECTION', selected_layer_index)
    if projection_node:
        match layers[selected_layer_index].projection.mode:
            case 'UV':
                row = first_column.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.label(text="Offset")
                row = second_column.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.prop(projection_node.inputs.get('Offset'), "default_value", text="X", slider=True, index=0)
                row.prop(layers[selected_layer_index].projection, "sync_projection_scale", text="", icon='LOCKED')
                row.prop(projection_node.inputs.get('Offset'), "default_value", text="Y", slider=True, index=1)

                row = first_column.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.label(text="Rotation")
                row = second_column.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.prop(projection_node.inputs.get('Rotation'), "default_value", text="", slider=True)

                row = first_column.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.label(text="Scale")
                row = second_column.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.prop(projection_node.inputs.get('Scale'), "default_value", text="X", slider=True, index=0)
                row.prop(projection_node.inputs.get('Scale'), "default_value", text="Y", slider=True, index=1)

            case 'TRIPLANAR':
                row = first_column.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.label(text="Offset")
                row = second_column.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.prop(projection_node.inputs.get('Offset'), "default_value", text="", slider=True, index=0)
                row.prop(projection_node.inputs.get('Offset'), "default_value", text="", slider=True, index=1)
                row.prop(projection_node.inputs.get('Offset'), "default_value", text="", slider=True, index=2)
                row.prop(layers[selected_layer_index].projection, "sync_projection_scale", text="", icon='LOCKED')

                row = first_column.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.label(text="Rotation")
                row = second_column.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.prop(projection_node.inputs.get('Rotation'), "default_value", text="", slider=True, index=0)
                row.prop(projection_node.inputs.get('Rotation'), "default_value", text="", slider=True, index=1)
                row.prop(projection_node.inputs.get('Rotation'), "default_value", text="", slider=True, index=2)

                row = first_column.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.label(text="Scale")
                row = second_column.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.prop(projection_node.inputs.get('Scale'), "default_value", text="", slider=True, index=0)
                row.prop(projection_node.inputs.get('Scale'), "default_value", text="", slider=True, index=1)
                row.prop(projection_node.inputs.get('Scale'), "default_value", text="", slider=True, index=2)

def draw_material_filters(layout):
    row = layout.row()
    row.scale_y = 2.5
    row.separator()
    row = layout.row()
    row.alignment = 'LEFT'
    row.scale_y = DEFAULT_UI_SCALE_Y
    row.label(text="MATERIAL FILTERS")
    row = layout.row(align=True)
    row.scale_x = 10
    row.scale_y = DEFAULT_UI_SCALE_Y + 0.6
    row.operator("matlayer.add_material_filter_menu", icon="ADD", text="")
    row.operator("matlayer.move_material_filter_up", icon="TRIA_UP", text="")
    row.operator("matlayer.move_material_filter_down", icon="TRIA_DOWN", text="")
    row.operator("matlayer.duplicate_material_filter", icon="DUPLICATE", text="")
    row.operator("matlayer.delete_material_filter", icon="TRASH", text="")
    row = layout.row(align=True)
    row.template_list("MATLAYER_UL_material_filter_list", "Material Filters", bpy.context.scene, "matlayer_material_filters", bpy.context.scene.matlayer_material_filter_stack, "selected_index", sort_reverse=True)
    row.scale_y = 2

def draw_layer_masks(layout):
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
    masks = bpy.context.scene.matlayer_masks
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    selected_mask_index = bpy.context.scene.matlayer_mask_stack.selected_index
    mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, selected_mask_index)
    if mask_node:
        row = layout.row()
        row.scale_y = DEFAULT_UI_SCALE_Y
        row.label(text="MASK PROPERTIES")
        for i in range(0, len(mask_node.inputs)):
            if mask_node.inputs[i].name != 'Mix':
                row = layout.row()
                row.scale_y = DEFAULT_UI_SCALE_Y
                row.prop(mask_node.inputs[i], "default_value", text=mask_node.inputs[i].name)

        for node in mask_node.node_tree.nodes:
            if node.bl_static_type == 'TEX_IMAGE':
                if node.projection == 'BOX':
                    row = layout.row()
                    row.prop(node, "projection_blend", text=node.label + " Blending")

        # Draw properties for any (non-mesh map) textures used in the mask.
        for node in mask_node.node_tree.nodes:
            if node.bl_static_type == 'TEX_IMAGE' and node.name not in baking.MESH_MAP_TYPES:
                split = layout.split(factor=0.4)
                first_column = split.column()
                second_column = split.column()

                row = first_column.row()
                texture_display_name = node.label.replace('_', ' ')
                texture_display_name = re.sub(r'\b[a-z]', lambda m: m.group().upper(), texture_display_name.capitalize())
                row.label(text=texture_display_name)

                row = second_column.row(align=True)
                row.prop(node, "image", text="")
                row.menu("MATLAYER_MT_image_utility_sub_menu", text="", icon='DOWNARROW_HLT')

        # Draw mask projection options if it exists.
        row = layout.row()
        row.separator()
        row = layout.row()
        row.scale_y = DEFAULT_UI_SCALE_Y
        row.label(text="MASK PROJECTION")
        mask_projection_node = layer_masks.get_mask_node('PROJECTION', selected_layer_index, selected_mask_index)
        if mask_projection_node:
            split = layout.split(factor=0.25)
            first_column = split.column()
            second_column = split.column()

            row = first_column.row()
            row.scale_y = DEFAULT_UI_SCALE_Y
            row.label(text="Offset")
            row = second_column.row()
            row.scale_y = DEFAULT_UI_SCALE_Y
            row.prop(mask_projection_node.inputs.get('Offset'), "default_value", text="X", slider=True, index=0)
            row.prop(masks[selected_mask_index], "sync_projection_scale", text="", icon='LOCKED')
            row.prop(mask_projection_node.inputs.get('Offset'), "default_value", text="Y", slider=True, index=1)

            row = first_column.row()
            row.label(text="Rotation")
            row = second_column.row()
            row.prop(mask_projection_node.inputs.get('Rotation'), "default_value", text="", slider=True)

            row = first_column.row()
            row.scale_y = DEFAULT_UI_SCALE_Y
            row.label(text="Scale")
            row = second_column.row()
            row.scale_y = DEFAULT_UI_SCALE_Y
            row.prop(mask_projection_node.inputs.get('Scale'), "default_value", text="X", slider=True, index=0)
            row.prop(mask_projection_node.inputs.get('Scale'), "default_value", text="Y", slider=True, index=1)

        # Draw any mesh maps used for this mask.
        row = layout.row()
        row.separator()
        row = layout.row()
        row.scale_y = DEFAULT_UI_SCALE_Y
        row.label(text="MESH MAPS")

        for mesh_map_name in baking.MESH_MAP_TYPES:
            mesh_map_texture_node = layer_masks.get_mask_node(mesh_map_name, selected_layer_index, selected_mask_index)
            if mesh_map_texture_node:
                split = layout.split(factor=0.4)
                first_column = split.column()
                second_column = split.column()

                row = first_column.row()
                mesh_map_display_name = mesh_map_texture_node.label.replace('_', ' ')
                mesh_map_display_name = re.sub(r'\b[a-z]', lambda m: m.group().upper(), mesh_map_display_name.capitalize())
                row.label(text=mesh_map_display_name)

                row = second_column.row(align=True)
                row.prop(mesh_map_texture_node, "image", text="")

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
        col.operator("matlayer.add_material_layer", text="Add Material Layer", icon='MATERIAL_DATA')
        col.operator("matlayer.add_paint_material_layer", text="Add Paint Layer", icon='BRUSHES_ALL')
        col.operator("matlayer.add_decal_material_layer", text="Add Decal Layer", icon='OUTLINER_OB_FONT')

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
        split = layout.split()
        col = split.column(align=True)
        col.scale_y = 1.4
        col.operator("matlayer.add_black_layer_mask", text="Black")
        col.operator("matlayer.add_white_layer_mask", text="White")
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

class MATLAYER_OT_add_material_effects_menu(Operator):
    bl_label = ""
    bl_idname = "matlayer.add_material_effects_menu"

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
        col.operator("matlayer.add_edge_wear")
        col.operator("matlayer.add_grunge")
        col.operator("matlayer.add_dust")
        col.operator("matlayer.add_drips")

class ImageUtilitySubMenu(Menu):
    bl_idname = "MATLAYER_MT_image_utility_sub_menu"
    bl_label = "Image Utility Sub Menu"

    def draw(self, context):
        layout = self.layout
        add_layer_image_operator = layout.operator("matlayer.add_material_channel_image", icon="ADD", text="New Image")
        import_texture_operator = layout.operator("matlayer.import_texture", icon="IMPORT", text="Import Image")
        export_image_operator = layout.operator("matlayer.edit_image_externally", icon="TPAINT_HLT", text="Edit Image Externally")
        reload_image_operator = layout.operator("matlayer.reload_material_channel_image", icon="FILE_REFRESH", text="Reload Image")
        delete_layer_image_operator = layout.operator("matlayer.delete_material_channel_image", icon="TRASH", text="Delete Image")