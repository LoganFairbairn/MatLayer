# This file handles drawing the user interface for the layers section.

import bpy
from bpy.types import Operator, Menu, Panel
from ..core import material_layers
from ..core import layer_masks
from ..core import mesh_map_baking
from ..core import blender_addon_utils
from ..core import texture_set_settings as tss
from ..core import shaders
from ..core import blender_addon_utils as bau
from ..core import material_filters
from .. import preferences

STANDARD_UI_SPLIT = 0.4

# Tabs to help organize the user interface and help limit the number of properties displayed at one time.
MATERIAL_LAYER_PROPERTY_TABS = [
    ("MATERIAL_CHANNELS", "CHANNELS", "Properties of material channels for the selected layer"),
    ("PROJECTION", "PROJECTION", "Projection properties for the selected layer"),
    ("MASKS", "MASKS", "Properties for masks applied to the selected material layer"),
    ("UNLAYERED", "UNLAYERED", "Unlayered properties of the shader node")
]

# User interface labels for group nodes.
GROUP_NODE_UI_LABELS = {
    "RY_UVProjection": "UV",
    "RY_TriplanarProjection": "Triplanar",
    "RY_TriplanarHexGridProjection": "Triplanar Hex Grid",
    "RY_DecalProjection": "Decal Projection"
}

def update_material_properties_tab(self, context):
    '''Callback function for when the material properties tab is changed.'''
    selected_tab = bpy.context.scene.rymat_material_property_tabs

    match selected_tab:
        case 'MATERIAL_CHANNELS':
            selected_layer_index = bpy.context.scene.rymat_layer_stack.selected_layer_index
            selected_material_channel = bpy.context.scene.rymat_layer_stack.selected_material_channel
            value_node = material_layers.get_material_layer_node('VALUE', selected_layer_index, selected_material_channel)
            if value_node:
                if value_node.bl_static_type == 'TEX_IMAGE':
                    bau.set_texture_paint_image(value_node.image)

        case 'MASKS':
            selected_layer_index = context.scene.rymat_layer_stack.selected_layer_index
            selected_mask_index = context.scene.rymat_mask_stack.selected_index
            mask_texture_node = layer_masks.get_mask_node('TEXTURE', selected_layer_index, selected_mask_index)
            if mask_texture_node:
                bau.set_texture_paint_image(mask_texture_node.image)

def draw_edit_layers_ui(self, context):
    '''Draws the layer section user interface to the add-on side panel.'''
    layout = self.layout

    # Print info when there is no active object.
    active_object = bpy.context.view_layer.objects.active
    if not active_object:
        bau.print_aligned_text(layout, "No Active Object", alignment='CENTER')
        return
    
    # Print user info about hidden objects.
    if active_object.hide_get():
        bau.print_aligned_text(layout, "Active Object Hidden", alignment='CENTER')
        return
    
    # Draw user interface for when a shader node group is not defined.
    shader_info = bpy.context.scene.rymat_shader_info
    if shader_info.shader_node_group == None:
        bau.print_aligned_text(layout, "No Shader Group Node", alignment='CENTER')
        bau.print_aligned_text(layout, "Define a shader group node to edit layers.", alignment='CENTER')

        # Draw an operator that applies a defaul shader setup.
        row = layout.row()
        row.alignment = 'CENTER'
        column = row.column()
        column.operator("rymat.apply_default_shader")

        # Draw a button to open shader settings.
        column.prop_enum(context.scene.rymat_panel_properties, "sections", 'SECTION_SHADER_SETTINGS', text="Open Shader Settings")
        return

    # Print info for when there is no active material.
    active_material = active_object.active_material
    if active_material == None:
        bau.print_aligned_text(layout, "No Active Material", alignment='CENTER')
        return

    # Print info for when the active material isn't made with this add-on.
    elif bau.verify_addon_material(active_material) == False:
        bau.print_aligned_text(layout, "Material Invalid", alignment='CENTER')
        bau.print_aligned_text(layout, "Materials must be created with this add-on.", alignment='CENTER')
        bau.print_aligned_text(layout, "Node format must remain unchanged.", alignment='CENTER')
        return

    # Print info for when the shader in the active material isn't defined in shader settings.
    elif shaders.validate_active_shader(active_material) == False:
        bau.print_aligned_text(layout, "Shader Not Defined", alignment='CENTER')
        bau.print_aligned_text(layout, "Define the active shader in setup tab.")
        return

def draw_value_node_properties(layout, material_channel_name, layer_node_tree, selected_layer_index, value_node, mix_node):
    '''Draws properties for the provided value node.'''

    # Use a two column layout.
    split = layout.split(factor=STANDARD_UI_SPLIT)
    first_column = split.column(align=True)
    second_column = split.column(align=True)

    match value_node.bl_static_type:
        case 'GROUP':
            row = first_column.row()
            row.label(text="Node Tree")
            row = second_column.row(align=True)
            row.prop(value_node, "node_tree", text="")
            for input in value_node.inputs:
                row = first_column.row()
                row.label(text=input.name)
                row = second_column.row()
                row.prop(input, "default_value", text="")
        
        case 'TEX_IMAGE':
            row = first_column.row()
            row.label(text="Image")
            row = second_column.row(align=True)
            row.prop(value_node, "image", text="")
            image = value_node.image
            if image:
                row.prop(image, "use_fake_user", text="")

            # Draw a custom sub-menu for image utility operators.
            row.context_pointer_set("node_tree", layer_node_tree)
            row.context_pointer_set("node", value_node)
            row.menu("RYMAT_MT_image_utility_sub_menu", text="", icon='DOWNARROW_HLT')
            
            # Draw a toggle for image alpha blending.
            row = first_column.row()
            row.label(text="Blend Image Alpha")
            row = second_column.row()
            mix_image_alpha_node = material_layers.get_material_layer_node('MIX_IMAGE_ALPHA', selected_layer_index, material_channel_name)
            if mix_image_alpha_node:
                operator = row.operator(
                    "rymat.toggle_image_alpha_blending", 
                    text=str(not mix_image_alpha_node.mute),
                    depress=not mix_image_alpha_node.mute
                )
                operator.material_channel_name = material_channel_name

            # Draw CRGB channel output options (mainly for channel packing).
            row = first_column.row()
            row.label(text="Output")
            row = second_column.row()
            row.context_pointer_set("mix_node", mix_node)
            output_channel_name = material_layers.get_material_channel_crgba_output(material_channel_name)
            if len(output_channel_name) > 0:
                output_channel_name = bau.capitalize_by_space(output_channel_name)
                row.menu("RYMAT_MT_material_channel_output_sub_menu", text=output_channel_name)

            # Draw texture interpolation.
            row = first_column.row()
            row.label(text="Interpolation")
            row = second_column.row()
            row.prop(value_node, "interpolation", text="")

            # Draw texture color-space and alpha settings.
            if value_node.image:
                row = first_column.row()
                row.label(text="Color Space")
                row = second_column.row()
                row.prop(value_node.image.colorspace_settings, "name", text="")

                row = first_column.row()
                row.label(text="Alpha Mode")
                row = second_column.row()
                row.prop(value_node.image, "alpha_mode", text="")

def draw_material_filter_name(layout, material_channel_name, filter_index, filter_node):
    split = layout.split(factor=STANDARD_UI_SPLIT)
    first_column = split.column(align=True)
    second_column = split.column(align=True)
    row = first_column.row()
    row.label(text="Filter " + str(filter_index))
    row = second_column.row()
    row.prop(filter_node, "label", text="")
    op = row.operator("rymat.delete_material_filter", text="", icon="TRASH")
    op.filter_index = filter_index
    op.material_channel = material_channel_name
    op.filter_type = 'NORMAL'

def draw_filter_properties(layout, material_channel_name, selected_layer_index):
    '''Draws material channel filter node properties to the user interface.'''
    layer_node = material_layers.get_material_layer_node('LAYER', selected_layer_index)
    static_channel_name = bau.format_static_matchannel_name(material_channel_name)

    # Draw properties specifically for blur filters.
    split = layout.split(factor=STANDARD_UI_SPLIT)
    first_column = split.column(align=True)
    second_column = split.column(align=True)
    blur_node = material_layers.get_material_layer_node('BLUR', selected_layer_index, material_channel_name)
    if blur_node:
        row = first_column.row()
        row.label(text="Blur Amount")
        row = second_column.row()
        row.prop(blur_node.inputs.get('Blur Amount'), "default_value", slider=True, text="")
        op = row.operator("rymat.delete_material_filter", text="", icon="TRASH")
        op.material_channel = material_channel_name
        op.filter_type = 'BLUR'

    # Draw specific properties for all filters applied to the material channel.
    filter_index = 1
    filter_node_name = static_channel_name + "_FILTER_" + str(filter_index)
    filter_node = layer_node.node_tree.nodes.get(filter_node_name)
    while filter_node:
        filter_type = material_filters.get_filter_type(filter_node)
        ui_sockets = material_filters.get_filter_info(filter_type, "ui_sockets")

        match filter_type:
            case 'CURVE_RGB':
                draw_material_filter_name(layout, material_channel_name, filter_index, filter_node)
                layout.template_curve_mapping(filter_node, "mapping")

            case 'VALTORGB':
                draw_material_filter_name(layout, material_channel_name, filter_index, filter_node)
                layout.template_color_ramp(filter_node, "color_ramp", expand=False)

            case _:
                draw_material_filter_name(layout, material_channel_name, filter_index, filter_node)
                split = layout.split(factor=STANDARD_UI_SPLIT)
                first_column = split.column(align=True)
                second_column = split.column(align=True)
                for i, input in enumerate(filter_node.inputs):
                    if i in ui_sockets:
                        match filter_type:
                            case _:
                                row = first_column.row()
                                row.label(text=input.name)
                                row = second_column.row()
                                row.prop(input, "default_value", text="")

        # Increment the filter index to draw the next filter properties.
        filter_index += 1
        filter_node_name = static_channel_name + "_FILTER_" + str(filter_index)
        filter_node = layer_node.node_tree.nodes.get(filter_node_name)

def draw_material_channel_properties(layout):
    '''Draws properties for all active material channels on selected material layer.'''
    selected_layer_index = bpy.context.scene.rymat_layer_stack.selected_layer_index
    layout.separator()

    # Use a two column layout so the user interface aligns better.
    split = layout.split(factor=STANDARD_UI_SPLIT)
    first_column = split.column()
    second_column = split.column()

    # Draw material channels add menu.
    row = first_column.row()
    row.label(text="CHANNELS")
    row = second_column.row()
    row.menu("RYMAT_MT_add_material_channel_sub_menu", text="Add Channel", icon='ADD')

    # Avoid drawing material channel properties for invalid layers.
    if material_layers.get_material_layer_node('LAYER', selected_layer_index) == None:
        return
    
    # Draw properties for all active material channels.
    shader_info = bpy.context.scene.rymat_shader_info
    for channel in shader_info.material_channels:

        # Do not draw properties for globally inactive material channels.
        if not tss.get_material_channel_active(channel.name):
            continue

        # Draw properties for all active material channels.
        layer_node_tree = material_layers.get_layer_node_tree(selected_layer_index)
        mix_node = material_layers.get_material_layer_node('MIX', selected_layer_index, channel.name)
        value_node = material_layers.get_material_layer_node('VALUE', selected_layer_index, channel.name)
        if value_node and mix_node:
            if not mix_node.mute:
                layout.separator()

                # Use a three column layout.
                split = layout.split(factor=STANDARD_UI_SPLIT)
                first_column = split.column(align=True)
                second_column = split.column(align=True)
                
                # Draw the channel name and operators for editing the material channel.
                row = first_column.row()
                row.label(text="{0}".format(channel.name.upper()))
                row = second_column.row()
                row.alignment = 'RIGHT'
                row.context_pointer_set("mix_node", mix_node)
                row.menu('RYMAT_MT_material_channel_value_node_sub_menu', text="", icon='NODE')
                operator = row.operator("rymat.delete_material_channel_nodes", text="", icon='X')
                operator.material_channel_name = channel.name

                draw_value_node_properties(layout, channel.name, layer_node_tree, selected_layer_index, value_node, mix_node)
                draw_filter_properties(layout, channel.name, selected_layer_index)

def draw_layer_projection(layout):
    '''Draws layer projection settings.'''
    selected_layer_index = bpy.context.scene.rymat_layer_stack.selected_layer_index

    # Only draw layer projection if a projection node exists.
    projection_node = material_layers.get_material_layer_node('PROJECTION', selected_layer_index)
    if not projection_node:
        return

    # Use a two column layout for neatness.
    split = layout.split(factor=STANDARD_UI_SPLIT)
    first_column = split.column()
    second_column = split.column()

    # Draw the projection mode submenu.
    row = first_column.row()
    row.label(text="Method")
    row = second_column.row()
    projection_method_dropdown_label = GROUP_NODE_UI_LABELS[projection_node.node_tree.name]
    row.menu('RYMAT_MT_layer_projection_submenu', text=projection_method_dropdown_label)

    # Draw adjustment settings for the selected projection method.
    match projection_node.node_tree.name:
        case 'RY_DecalProjection':
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="USING DECAL PROJECTION")
        
        case _:
            for input in projection_node.inputs:
                row = first_column.row()
                row.label(text=input.name)
                row = second_column.row()
                row.prop(input, "default_value", text="", slider=True)

def draw_unlayered_shader_properties(layout):
    '''Draws unlayered properties of the shader node.'''
    # Use a two column layout for neatness.
    split = layout.split(factor=STANDARD_UI_SPLIT)
    first_column = split.column()
    second_column = split.column()

    active_object = bpy.context.active_object
    if not active_object:
        return

    active_material = bpy.context.active_object.active_material
    if not active_material:
        return

    shader_node = active_material.node_tree.nodes.get('SHADER_NODE')
    if not shader_node:
        return

    shader_info = bpy.context.scene.rymat_shader_info
    for input in shader_node.inputs:
        if input.name not in shader_info.material_channels:
            row = first_column.row()
            row.label(text=input.name)
            row = second_column.row()
            row.prop(input, "default_value", text="")

def draw_image_texture_property(layout, node_tree, texture_node):
    '''Draws an image texture property with this add-ons image utility sub-menu.'''
    split = layout.split(factor=STANDARD_UI_SPLIT)
    first_column = split.column()
    second_column = split.column()
    row = first_column.row()
    texture_display_name = texture_node.label.replace('_', ' ')
    texture_display_name = blender_addon_utils.capitalize_by_space(texture_display_name)
    row.label(text=texture_display_name)

    row = second_column.row(align=True)
    row.prop(texture_node, "image", text="")
    image = texture_node.image
    if image:
        row.prop(image, "use_fake_user", text="")
    row.context_pointer_set("node_tree", node_tree)
    row.context_pointer_set("node", texture_node)
    row.menu("RYMAT_MT_image_utility_sub_menu", text="", icon='DOWNARROW_HLT')

    row = first_column.row()
    row.label(text="Interpolation")
    row = second_column.row()
    row.prop(texture_node, "interpolation", text="")

def draw_mask_properties(layout, mask_node, mask_type, selected_layer_index, selected_mask_index):
    '''Draws group node properties for the selected mask.'''

    # Draw properties for texture nodes in masks based on mask type.
    match mask_type:
        case 'IMAGE_MASK':
            texture_node = layer_masks.get_mask_node('TEXTURE', selected_layer_index, selected_mask_index, node_number=1)
            draw_image_texture_property(layout, mask_node.node_tree, texture_node)

        case _:
            for node in mask_node.node_tree.nodes:
                if node.bl_static_type == 'TEX_IMAGE' and node.name not in mesh_map_baking.MESH_MAP_TYPES:
                    draw_image_texture_property(layout, mask_node.node_tree, node)

    # Draw mask group node input properties, excluding those that will be auto-connected.
    split = layout.split(factor=STANDARD_UI_SPLIT)
    first_column = split.column()
    second_column = split.column()
    for i in range(0, len(mask_node.inputs)):
        if mask_node.inputs[i].name != 'Mix' and mask_node.inputs[i].name != 'Blur Noise':
            row = first_column.row()
            row.label(text=mask_node.inputs[i].name)
            row = second_column.row()
            row.prop(mask_node.inputs[i], "default_value", text="")

    # Draw CRGBA channel properties for compatable masks.
    separate_rgb_node = layer_masks.get_mask_node('SEPARATE_RGB', selected_layer_index, selected_mask_index)
    if separate_rgb_node:
        mask_crgba_channel_name = layer_masks.get_mask_crgba_channel()
        row = first_column.row()
        row.label(text="Channel")
        row = second_column.row()
        row.menu(
            "RYMAT_MT_mask_channel_sub_menu", 
            text=bau.capitalize_by_space(mask_crgba_channel_name)
        )

    # Draw mask color ramp properties.
    for node in mask_node.node_tree.nodes:
        if node.bl_static_type == 'VALTORGB':
            layout.label(text=node.label)
            layout.template_color_ramp(node, "color_ramp", expand=True)

def draw_mask_projection(layout):
    '''Draws projection settings for the selected mask.'''
    row = layout.row()
    row.scale_y = 2.5
    row.separator()

    # If no mask projection node exists, abort drawing properties for it.
    selected_layer_index = bpy.context.scene.rymat_layer_stack.selected_layer_index
    selected_mask_index = bpy.context.scene.rymat_mask_stack.selected_index
    mask_projection_node = layer_masks.get_mask_node('PROJECTION', selected_layer_index, selected_mask_index)
    if not mask_projection_node:
        return

    # Draw the projection title & method drop-down.
    row = layout.row()
    row.label(text="PROJECTION")
    row = layout.row()
    projection_method_dropdown_label = GROUP_NODE_UI_LABELS[mask_projection_node.node_tree.name]
    row.menu('RYMAT_MT_mask_projection_sub_menu', text=projection_method_dropdown_label)

    # Use a two column layout for neatness.
    split = layout.split(factor=STANDARD_UI_SPLIT)
    first_column = split.column()
    second_column = split.column()

    # Draw all properties for the mask.
    for input in mask_projection_node.inputs:
        row = first_column.row()
        row.label(text=input.name)
        row = second_column.row()
        row.prop(input, "default_value", text="")

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
                row.label(text="MESH MAPS")
                drew_title = True

            split = layout.split(factor=STANDARD_UI_SPLIT)
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

def draw_masks_tab(layout):
    row = layout.row(align=True)
    row.scale_x = 10
    row.scale_y = 2
    row.operator("rymat.add_layer_mask_menu", icon="ADD", text="")
    row.operator("rymat.move_layer_mask_up", icon="TRIA_UP", text="")
    row.operator("rymat.move_layer_mask_down", icon="TRIA_DOWN", text="")
    row.operator("rymat.duplicate_layer_mask", icon="DUPLICATE", text="")
    row.operator("rymat.delete_layer_mask", icon="TRASH", text="")
    row = layout.row(align=True)
    row.template_list(
        "RYMAT_UL_mask_list", 
        "Masks", 
        bpy.context.scene, 
        "rymat_masks", 
        bpy.context.scene.rymat_mask_stack, 
        "selected_index", 
        sort_reverse=True
    )
    row.scale_y = 2

    # Draw properties for the selected mask.
    selected_layer_index = bpy.context.scene.rymat_layer_stack.selected_layer_index
    selected_mask_index = bpy.context.scene.rymat_mask_stack.selected_index
    mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, selected_mask_index)
    mask_type = layer_masks.get_mask_type(selected_layer_index, selected_mask_index)
    if mask_node:
        row = layout.row()
        row.label(text="PROPERTIES")
        draw_mask_properties(layout, mask_node, mask_type, selected_layer_index, selected_mask_index)
        draw_mask_projection(layout)
        draw_mask_mesh_maps(layout, selected_layer_index, selected_mask_index)

class MaterialSelectorPanel(Panel):
    bl_label = "Material Selector"
    bl_idname = "RYMAT_PT_material_selector_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RyMat"

    # Only draw this panel when the edit materials section is selected.
    @ classmethod
    def poll(cls, context):
        return context.scene.rymat_panel_properties.sections == 'SECTION_EDIT_MATERIALS'

    def draw(self, context):
        panel_properties = context.scene.rymat_panel_properties
        if not panel_properties.sections == 'SECTION_EDIT_MATERIALS':
            return
        
        layout = self.layout
        active_object = bpy.context.active_object
        if not active_object:
            return

        # Draw the active material.
        split = layout.split(factor=STANDARD_UI_SPLIT)
        first_column = split.column()
        second_column = split.column()
        row = first_column.row()
        row.label(text="Active Material")
        row = second_column.row()
        row.prop(bpy.context.active_object, "active_material", text="")

        # Draw the shader node detected the active material.
        active_material = bpy.context.active_object.active_material
        row = first_column.row()
        row.label(text="Active Shader Node")
        row = second_column.row()
        if active_material:
            shader_node = active_material.node_tree.nodes.get('SHADER_NODE')
            if shader_node:
                row.enabled = False
                row.prop(shader_node.node_tree, "name", text="")
            else:
                row.label(text="NONE")
        else:
            row.label(text="NONE")

        # Draw material slots on the active object.
        split = layout.split(factor=0.925)
        first_column = split.column(align=True)
        second_column = split.column(align=True)
        second_column.scale_x = 0.1
        first_column.template_list("MATERIAL_UL_matslots", "Layers", bpy.context.active_object, "material_slots", bpy.context.active_object, "active_material_index")
        second_column.operator("rymat.add_material_slot", text="", icon='ADD')
        second_column.operator("rymat.remove_material_slot", text="-")
        second_column.operator("rymat.move_material_slot_up", text="", icon='TRIA_UP')
        second_column.operator("rymat.move_material_slot_down", text="", icon='TRIA_DOWN')
        second_column.operator("object.material_slot_assign", text="", icon='MATERIAL_DATA')
        second_column.operator("object.material_slot_select", text="", icon='SELECT_SET')
        
        # TODO: Deprecate this if drag 'n drop material merging is implemented.
        '''
        split = layout.split(factor=0.70)
        first_column = split.column()
        second_column = split.column()
        col = first_column.column()
        if bpy.context.active_object:
            col.prop(bpy.context.active_object, "active_material", text="")
            col.prop(bpy.context.scene, "rymat_merge_material", text="")
            col = second_column.column()
            col.scale_y = 2.0
            col.operator("rymat.merge_materials", text="Merge")
        '''

class LayerStackPanel(Panel):
    bl_label = "Layer Stack"
    bl_idname = "RYMAT_PT_layer_stack_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RyMat"

    # Only draw this panel when the edit materials section is selected.
    @ classmethod
    def poll(cls, context):
        return context.scene.rymat_panel_properties.sections == 'SECTION_EDIT_MATERIALS'

    def draw(self, context):
        panel_properties = context.scene.rymat_panel_properties
        if panel_properties.sections == 'SECTION_EDIT_MATERIALS':
            layout = self.layout

            # Use a two column layout.
            split = layout.split(factor=0.5)
            first_column = split.column()
            second_column = split.column()

            # Draw layer operations.
            row = first_column.row(align=True)
            row.scale_y = 1.5
            row.scale_x = 10
            row.operator("rymat.add_material_layer_menu", icon='ADD', text="")
            row.operator("rymat.import_texture_set", icon='IMPORT', text="")
            row.operator("rymat.move_material_layer_up", icon='TRIA_UP', text="")
            row.operator("rymat.move_material_layer_down", icon='TRIA_DOWN', text="")
            row.operator("rymat.duplicate_layer", icon='DUPLICATE', text="")
            row.operator("rymat.merge_with_layer_below", icon='TRIA_DOWN_BAR', text="")
            row.operator("rymat.delete_layer", icon='TRASH', text="")

            # Draw the selected material channel.
            row = second_column.row(align=True)
            row.scale_y = 1.5
            selected_material_channel = bpy.context.scene.rymat_layer_stack.selected_material_channel
            row.menu("RYMAT_MT_material_channel_sub_menu", text=selected_material_channel)
            row.operator("rymat.isolate_material_channel", text="", icon='MATERIAL')
            row.operator("rymat.show_compiled_material", text="", icon='SHADING_RENDERED')

            # Draw the layer stack.
            row = layout.row(align=True)
            row.template_list(
                "RYMAT_UL_layer_list", 
                "Layers", 
                bpy.context.scene, 
                "rymat_layers", 
                bpy.context.scene.rymat_layer_stack, 
                "selected_layer_index", 
                sort_reverse=True
            )

class ColorPalettePanel(Panel):
    bl_label = "Color Palette"
    bl_idname = "RYMAT_PT_color_palette"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RyMat"

    # Only draw this panel when the edit materials section is selected.
    @ classmethod
    def poll(cls, context):
        return context.scene.rymat_panel_properties.sections == 'SECTION_EDIT_MATERIALS'

    def draw(self, context):
        panel_properties = context.scene.rymat_panel_properties
        if panel_properties.sections == 'SECTION_EDIT_MATERIALS':
            layout = self.layout

            tool_settings = context.tool_settings
            if tool_settings.image_paint.palette:
                row = layout.row(align=True)
                row.template_ID(tool_settings.image_paint, "palette")
                layout.template_palette(tool_settings.image_paint, "palette", color=True)

class MaterialPropertiesPanel(Panel):
    bl_label = "Material Properties"
    bl_idname = "RYMAT_PT_material_properties_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RyMat"

    # Only draw this panel when the edit materials section is selected.
    @ classmethod
    def poll(cls, context):
        return context.scene.rymat_panel_properties.sections == 'SECTION_EDIT_MATERIALS'

    def draw(self, context):
        panel_properties = context.scene.rymat_panel_properties
        if panel_properties.sections == 'SECTION_EDIT_MATERIALS':
            layout = self.layout

            # Draw properties for the selected material layer.
            layer_count = material_layers.count_layers()
            if layer_count > 0:
                row = layout.row(align=True)
                row.scale_y = 1.5
                row.prop_enum(bpy.context.scene, "rymat_material_property_tabs", 'MATERIAL_CHANNELS', text="CHANNELS")
                row.prop_enum(bpy.context.scene, "rymat_material_property_tabs", 'PROJECTION', text="PROJECTION")
                row.prop_enum(bpy.context.scene, "rymat_material_property_tabs", 'MASKS', text="MASKS")
                row.prop_enum(bpy.context.scene, "rymat_material_property_tabs", 'UNLAYERED', text="UNLAYERED")
                match bpy.context.scene.rymat_material_property_tabs:
                    case 'MATERIAL_CHANNELS':
                        draw_material_channel_properties(layout)
                    case 'MASKS':
                        draw_masks_tab(layout)
                    case 'PROJECTION':
                        draw_layer_projection(layout)
                    case 'UNLAYERED':
                        draw_unlayered_shader_properties(layout)
            else:
                bau.print_aligned_text(layout, "No Layer Selected", alignment='CENTER')

class RYMAT_OT_add_material_layer_menu(Operator):
    bl_label = ""
    bl_idname = "rymat.add_material_layer_menu"
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
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Add Layer")
        split = layout.split()
        col = split.column(align=True)
        col.scale_y = 1.4
        col.operator("rymat.add_material_layer", text="Material")
        col.operator("rymat.add_image_layer", text="Image")
        col.operator("rymat.add_decal_material_layer", text="Decal")

class RYMAT_OT_add_layer_mask_menu(Operator):
    bl_label = "Add Mask"
    bl_idname = "rymat.add_layer_mask_menu"

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

    # Opens the popup when the add layer button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=150)

    # Draws the properties in the popup.
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Add Mask")
        row = layout.row(align=True)
        col = row.column(align=True)
        col.scale_y = 1.4
        col.operator("rymat.add_empty_layer_mask", text="Empty Image")
        col.operator("rymat.add_black_layer_mask", text="Black Image")
        col.operator("rymat.add_white_layer_mask", text="White Image")
        col.operator("rymat.add_linear_gradient_mask", text="Linear Gradient")

        selected_layer_index = bpy.context.scene.rymat_layer_stack.selected_layer_index
        projection_node = material_layers.get_material_layer_node('PROJECTION', selected_layer_index)
        if projection_node.node_tree.name == 'RY_DecalProjection':
            col.operator("rymat.add_decal_mask", text="Decal")
        
        col.operator("rymat.add_grunge_mask", text="Grunge")
        col.operator("rymat.add_edge_wear_mask", text="Edge Wear")
        col.operator("rymat.add_ambient_occlusion_mask", text="Ambient Occlusion")
        col.operator("rymat.add_curvature_mask", text="Curvature")
        col.operator("rymat.add_thickness_mask", text="Thickness")
        col.operator("rymat.add_world_space_normals_mask", text="World Space Normals")

class AddMaterialChannelSubMenu(Menu):
    bl_idname = "RYMAT_MT_add_material_channel_sub_menu"
    bl_label = "Add Material Channel Sub Menu"

    def draw(self, context):
        layout = self.layout
        shader_info = bpy.context.scene.rymat_shader_info
        for channel in shader_info.material_channels:
            operator = layout.operator("rymat.add_material_channel_nodes", text=channel.name)
            operator.material_channel_name = channel.name

class MaterialChannelSubMenu(Menu):
    bl_idname = "RYMAT_MT_material_channel_sub_menu"
    bl_label = "Material Channel Sub Menu"

    def draw(self, context):
        layout = self.layout
        shader_info = bpy.context.scene.rymat_shader_info
        for channel in shader_info.material_channels:
            operator = layout.operator("rymat.set_material_channel", text=channel.name)
            operator.material_channel_name = channel.name

class ImageUtilitySubMenu(Menu):
    bl_idname = "RYMAT_MT_image_utility_sub_menu"
    bl_label = "Image Utility Sub Menu"

    def draw(self, context):
        layout = self.layout
        if context.node and context.node_tree:
            material_channel_name = context.node.name.split('_')[0]

            operator = layout.operator("rymat.add_texture_node_image", text="Add New Image", icon='NONE')
            operator.node_tree_name = context.node_tree.name
            operator.node_name = context.node.name
            operator.material_channel_name = material_channel_name

            operator = layout.operator("rymat.import_texture_node_image", text="Import Image", icon='NONE')
            operator.node_tree_name = context.node_tree.name
            operator.node_name = context.node.name
            operator.material_channel_name = material_channel_name

            operator = layout.operator("rymat.rename_texture_node_image", text="Rename Image", icon='NONE')
            operator.node_tree_name = context.node_tree.name
            operator.node_name = context.node.name
            operator.material_channel_name = material_channel_name

            operator = layout.operator("rymat.edit_texture_node_image_externally", text="Edit Image Externally", icon='NONE')
            operator.node_tree_name = context.node_tree.name
            operator.node_name = context.node.name
            
            operator = layout.operator("rymat.image_edit_uvs", text="Externally Image Edit UVs", icon='NONE')

            operator = layout.operator("rymat.reload_texture_node_image", text="Reload Image", icon='NONE')
            operator.node_tree_name = context.node_tree.name
            operator.node_name = context.node.name

            operator = layout.operator("rymat.duplicate_texture_node_image", text="Duplicate Image", icon='NONE')
            operator.node_tree_name = context.node_tree.name
            operator.node_name = context.node.name

            operator = layout.operator("rymat.delete_texture_node_image", text="Delete Image", icon='NONE')
            operator.node_tree_name = context.node_tree.name
            operator.node_name = context.node.name

class LayerProjectionModeSubMenu(Menu):
    bl_idname = "RYMAT_MT_layer_projection_submenu"
    bl_label = "Layer Projection Sub Menu"

    def draw(self, context):
        layout = self.layout
        op = layout.operator("rymat.set_layer_projection", text="UV")
        op.projection_method = 'UV'
        op = layout.operator("rymat.set_layer_projection", text="Triplanar")
        op.projection_method = 'TRIPLANAR'

        # Experimental anti-repetition projection method.
        addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
        if addon_preferences.experimental_features:
            op = layout.operator("rymat.set_layer_projection", text="Triplanar Hex Grid")
            op.projection_method = 'TRIPLANAR_HEX_GRID'

class MaskProjectionModeSubMenu(Menu):
    bl_idname = "RYMAT_MT_mask_projection_sub_menu"
    bl_label = "Mask Projection Sub Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("rymat.set_mask_projection_uv", text="UV")
        layout.operator("rymat.set_mask_projection_triplanar", text="Triplanar")

class MaterialChannelValueNodeSubMenu(Menu):
    bl_idname = "RYMAT_MT_material_channel_value_node_sub_menu"
    bl_label = "Material Channel Value Node Sub Menu"

    def draw(self, context):
        layout = self.layout

        # This is a work-around for not being able (or not knowing how) to pass a string to this sub-menu from the draw layout call.
        # Get the material channel name from the mix node being drawn.
        material_channel_name = context.mix_node.name.replace('-MIX', '')

        operator = layout.operator("rymat.change_material_channel_value_node", text="Use Group Node", icon='NODETREE')
        operator.material_channel_name = material_channel_name
        operator.node_type = 'GROUP'

        operator = layout.operator("rymat.change_material_channel_value_node", text="Use Texture", icon='IMAGE_DATA')
        operator.material_channel_name = material_channel_name
        operator.node_type = 'TEXTURE'

        # Draw operators to add available material filters.
        op = layout.operator("rymat.add_material_filter", text="Add Blur", icon='FILTER')
        op.material_channel = material_channel_name
        op.filter_type = 'BLUR'
        op = layout.operator("rymat.add_material_filter", text="Add HSV Filter", icon='FILTER')
        op.material_channel = material_channel_name
        op.filter_type = 'HUE_SAT'
        op = layout.operator("rymat.add_material_filter", text="Add Invert Filter", icon='FILTER')
        op.material_channel = material_channel_name
        op.filter_type = 'INVERT'
        op = layout.operator("rymat.add_material_filter", text="Add Brightness / Contrast Filter", icon='FILTER')
        op.material_channel = material_channel_name
        op.filter_type = 'BRIGHTCONTRAST'
        op = layout.operator("rymat.add_material_filter", text="Add Gamma Filter", icon='FILTER')
        op.material_channel = material_channel_name
        op.filter_type = 'GAMMA'
        op = layout.operator("rymat.add_material_filter", text="Add RGB Curves Fitler", icon='FILTER')
        op.material_channel = material_channel_name
        op.filter_type = 'CURVE_RGB'
        op = layout.operator("rymat.add_material_filter", text="Add RGB to BW Fitler", icon='FILTER')
        op.material_channel = material_channel_name
        op.filter_type = 'RGBTOBW'
        op = layout.operator("rymat.add_material_filter", text="Add Color Ramp Fitler", icon='FILTER')
        op.material_channel = material_channel_name
        op.filter_type = 'VALTORGB'
        op = layout.operator("rymat.add_material_filter", text="Add Cheap Contrast Filter", icon='FILTER')
        op.material_channel = material_channel_name
        op.filter_type = 'CHEAP_CONTRAST'
        op = layout.operator("rymat.add_material_filter", text="Add Normal Intensity Filter", icon='FILTER')
        op.material_channel = material_channel_name
        op.filter_type = 'NORMAL_INTENSITY'

class MaskChannelSubMenu(Menu):
    bl_idname = "RYMAT_MT_mask_channel_sub_menu"
    bl_label = "Mask Channel Sub Menu"

    def draw(self, context):
        layout = self.layout
        operator = layout.operator("rymat.set_mask_crgba_channel", text="Color")
        operator.channel_name = 'COLOR'
        operator = layout.operator("rymat.set_mask_crgba_channel", text="Alpha")
        operator.channel_name = 'ALPHA'
        operator = layout.operator("rymat.set_mask_crgba_channel", text="Red")
        operator.channel_name = 'RED'
        operator = layout.operator("rymat.set_mask_crgba_channel", text="Green")
        operator.channel_name = 'GREEN'
        operator = layout.operator("rymat.set_mask_crgba_channel", text="Blue")
        operator.channel_name = 'BLUE'

class MaterialChannelOutputSubMenu(Menu):
    bl_idname = "RYMAT_MT_material_channel_output_sub_menu"
    bl_label = "Material Channel Output Sub Menu"

    def draw(self, context):
        material_channel_name = context.mix_node.name.replace('-MIX', '')
        layout = self.layout
        operator = layout.operator("rymat.set_material_channel_crgba_output", text="Color")
        operator.output_channel_name = 'COLOR'
        operator.material_channel_name = material_channel_name
        operator = layout.operator("rymat.set_material_channel_crgba_output", text="Alpha")
        operator.output_channel_name = 'ALPHA'
        operator.material_channel_name = material_channel_name
        operator = layout.operator("rymat.set_material_channel_crgba_output", text="Red")
        operator.output_channel_name = 'RED'
        operator.material_channel_name = material_channel_name
        operator = layout.operator("rymat.set_material_channel_crgba_output", text="Green")
        operator.output_channel_name = 'GREEN'
        operator.material_channel_name = material_channel_name
        operator = layout.operator("rymat.set_material_channel_crgba_output", text="Blue")
        operator.output_channel_name = 'BLUE'
        operator.material_channel_name = material_channel_name
