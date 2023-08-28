# This file handles drawing the user interface for the layers section.

import bpy
from bpy.types import Operator
from ..core import material_layers
from ..ui import ui_section_tabs

DEFAULT_UI_SCALE_Y = 1

MATERIAL_LAYER_PROPERTY_TABS = [
    ("MATERIAL", "MATERIAL", "Properties for the selected material layer"),
    ("PROJECTION", "PROJECTION", "Projection properties for the selected material layer"),
    ("FILTERS", "FILTERS", "Filter properties for the selected material layer"),
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
            draw_layer_material_channel_toggles(column_one)
            draw_material_channel_properties(column_one)

        case 'PROJECTION':
            draw_layer_projection(column_one)

        case 'FILTERS':
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
    row.prop_enum(bpy.context.scene, "matlayer_material_property_tabs", 'PROJECTION')
    row.prop_enum(bpy.context.scene, "matlayer_material_property_tabs", 'FILTERS')
    row.prop_enum(bpy.context.scene, "matlayer_material_property_tabs", 'MASKS')

def draw_layer_material_channel_toggles(layout):
    '''Draws on / off toggles for individual material channels.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    row = layout.row()
    row.separator()

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
    layers = bpy.context.scene.matlayer_layers
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index

    # Avoid drawing material channel properties for invalid layers.
    if material_layers.get_material_layer_node('LAYER', selected_layer_index) == None or len(layers) <= 0:
        return

    for material_channel_name in material_layers.MATERIAL_CHANNEL_LIST:
        row = layout.row()
        row.scale_y = 2.5
        row.separator()

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
    row.scale_y = DEFAULT_UI_SCALE_Y
    row.label(text="PROJECTION")

def draw_material_filters(layout):
    row = layout.row()
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
    row = layout.row()
    row.scale_y = DEFAULT_UI_SCALE_Y
    row.label(text="MASKS")
    row = layout.row(align=True)
    row.scale_x = 10
    row.scale_y = DEFAULT_UI_SCALE_Y + 0.6
    row.operator("matlayer.add_layer_mask_menu", icon="ADD", text="")
    row.operator("matlayer.move_layer_mask_up", icon="TRIA_UP", text="")
    row.operator("matlayer.move_layer_mask_down", icon="TRIA_DOWN", text="")
    row.operator("matlayer.duplicate_layer_mask", icon="DUPLICATE", text="")
    row.operator("matlayer.delete_layer_mask", icon="TRASH", text="")
    row = layout.row(align=True)
    row.template_list("MATLAYER_UL_mask_list", "Masks", bpy.context.scene, "matlayer_masks", bpy.context.scene.matlayer_mask_stack, "selected_index", sort_reverse=True)
    row.scale_y = 2

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
        col.operator("matlayer.add_empty_layer_mask", text="Empty")
        col.operator("matlayer.add_black_layer_mask", text="Black")
        col.operator("matlayer.add_white_layer_mask", text="White")

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
