# This file handles drawing the user interface for the layers section.

import bpy
from bpy.types import Operator, Menu
from ..core import material_layers
from ..core import layer_masks
from ..core import mesh_map_baking
from ..core import blender_addon_utils
from ..core import texture_set_settings as tss
from ..core import shaders
from ..core import blender_addon_utils as bau
from . import ui_tabs
from .. import preferences

DEFAULT_UI_SCALE_Y = 1

MATERIAL_LAYER_PROPERTY_TABS = [
    ("LAYER", "LAYER", "Properties for the selected material layer."),
    ("MASKS", "MASKS", "Properties for masks applied to the selected material layer."),
    ("UNLAYERED", "UNLAYERED", "Properties for the selected material that are not layered.")
]
    
def draw_layers_tab_ui(self, context):
    '''Draws the layer section user interface to the add-on side panel.'''
    ui_tabs.draw_addon_tabs(self, context)
    layout = self.layout

    # Draw setup prompts to help new users of the add-on.
    draw_workspace_prompt(layout)

    # Use a two column layout.
    split = layout.split()
    column_one = split.column()
    column_two = split.column()

    # Print info when there is no active object.
    active_object = bpy.context.view_layer.objects.active
    if not active_object:
        bau.print_aligned_text(layout, "No Active Object", alignment='CENTER')
        return
    
    # Print user info about hidden objects.
    if active_object.hide_get():
        bau.print_aligned_text(layout, "Active Object Hidden", alignment='CENTER')
        return
    
    # Print user info for when a shader node group is not defined.
    shader_info = bpy.context.scene.matlayer_shader_info
    if shader_info.shader_node_group == None:
        bau.print_aligned_text(layout, "No Shader Group Node", alignment='CENTER')
        bau.print_aligned_text(layout, "Define a shader group node to edit layers.", alignment='CENTER')
        return

    # Print info for when there is no active material.
    active_material = active_object.active_material
    if active_material == None:
        bau.print_aligned_text(column_one, "No Active Material", alignment='CENTER')

    # Print info for when the active material isn't made with this add-on.
    elif bau.verify_addon_material(active_material) == False:
        bau.print_aligned_text(column_one, "Material Invalid", alignment='CENTER')
        bau.print_aligned_text(column_one, "Possible Reasons:")
        bau.print_aligned_text(column_one, "• Material isn't created with this add-on.")
        bau.print_aligned_text(column_one, "• Material node format is corrupted.")
        bau.print_aligned_text(column_one, "Solution:")
        bau.print_aligned_text(column_one, "• Add a new layer to an empty material slot.")
        draw_material_selector(column_two)
        return

    # Print info for when the shader in the active material isn't defined in shader settings.
    elif shaders.validate_active_shader(active_material) == False:
        bau.print_aligned_text(column_one, "Shader Not Defined", alignment='CENTER')
        bau.print_aligned_text(column_one, "Define the active shader in setup tab.")
        draw_material_selector(column_two)
        return

    # Draw layer user interface.
    layer_count = material_layers.count_layers()
    if layer_count > 0:
        draw_material_property_tabs(column_one)
        match bpy.context.scene.matlayer_material_property_tabs:
            case 'LAYER':
                draw_layer_projection(column_one)
                draw_layer_material_channel_toggles(column_one)
                draw_material_channel_properties(column_one)
            case 'MASKS':
                draw_masks(column_one)
            case 'UNLAYERED':
                draw_unlayered_material_properties(column_one)

    draw_material_selector(column_two)
    draw_selected_material_channel(column_two)
    draw_layer_operations(column_two)
    draw_layer_stack(column_two)
    draw_selected_image_name(column_two)

def draw_workspace_prompt(layout):
    '''Draws a prompt to load the suggested workspace to help new users of the add-on.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    if addon_preferences.beginner_help:
        workspace = bpy.data.workspaces.get('Matlayer')
        if not workspace:
            row = layout.row()
            row.scale_y = 1.5
            row.separator()
            row = layout.row()
            row.scale_y = 1.5
            row.alignment = 'CENTER'
            row.operator("matlayer.append_workspace", text="Load Suggested Workspace")
            row = layout.row()
            row.scale_y = 1.5
            row.separator()

def draw_material_selector(layout):
    '''Draws a material selector.'''
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

        layout.prop(bpy.context.active_object, "active_material", text="")
        
        # TODO: Deprecate this if drag 'n drop material merging is implemented.
        '''
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
        '''

def draw_selected_material_channel(layout):
    '''Draws the selected material channel.'''
    row = layout.row(align=True)
    row.scale_x = 2
    row.scale_y = 1.4
    selected_material_channel = bpy.context.scene.matlayer_layer_stack.selected_material_channel
    row.menu("MATLAYER_MT_material_channel_sub_menu", text=selected_material_channel)
    row.operator("matlayer.isolate_material_channel", text="", icon='MATERIAL')

def draw_layer_operations(layout):
    '''Draws layer operation buttons.'''
    row = layout.row(align=True)
    row.scale_y = 2.0
    row.scale_x = 10
    row.operator("matlayer.add_material_layer_menu", icon='ADD', text="")
    #row.operator("matlayer.merge_layers", icon='TRIA_DOWN_BAR', text="")
    row.operator("matlayer.import_texture_set", icon='IMPORT', text="")
    row.operator("matlayer.move_material_layer_up", icon='TRIA_UP', text="")
    row.operator("matlayer.move_material_layer_down", icon='TRIA_DOWN', text="")
    row.operator("matlayer.duplicate_layer", icon='DUPLICATE', text="")
    row.operator("matlayer.delete_layer", icon='TRASH', text="")

def draw_layer_stack(layout):
    '''Draws the material layer stack along with it's operators and material channel.'''
    row = layout.row(align=True)
    row.template_list("MATLAYER_UL_layer_list", "Layers", bpy.context.scene, "matlayer_layers", bpy.context.scene.matlayer_layer_stack, "selected_layer_index", sort_reverse=True)
    row.scale_y = 2

def draw_selected_image_name(layout):
    '''Draws the selected image name.'''
    row = layout.row(align=True)
    if bpy.context.scene.tool_settings.image_paint.canvas:
        row.label(text="Selecting: {0}".format(bpy.context.scene.tool_settings.image_paint.canvas.name))

def draw_material_property_tabs(layout):
    '''Draws tabs to change between editing the material layer and the masks applied to the material layer.'''
    row = layout.row(align=True)
    row.scale_y = 1.5
    row.prop_enum(bpy.context.scene, "matlayer_material_property_tabs", 'LAYER')
    row.prop_enum(bpy.context.scene, "matlayer_material_property_tabs", 'MASKS')
    row.prop_enum(bpy.context.scene, "matlayer_material_property_tabs", 'UNLAYERED')

def draw_layer_material_channel_toggles(layout):
    '''Draws on / off toggles with for individual material channels in the selected material layer.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index

    row = layout.row()
    row.separator()
    row.scale_y = 2
    row = layout.row()
    row.label(text="CHANNELS")

    row = layout.row()
    row.scale_y = DEFAULT_UI_SCALE_Y
    drawn_toggles = 0
    
    shader_info = bpy.context.scene.matlayer_shader_info

    active_material_channels = []
    for channel in shader_info.material_channels:
        if tss.get_material_channel_active(channel.name):
            active_material_channels.append(channel.name)

    for channel_name in active_material_channels:
        mix_node = material_layers.get_material_layer_node('MIX', selected_layer_index, channel_name)
        if mix_node:

            # Draw material channels with shortened names so they are more condensed in the user interface.
            row.prop(mix_node, "mute", text=material_layers.get_shorthand_material_channel_name(channel_name), toggle=True, invert_checkbox=True)
            drawn_toggles += 1
            if len(active_material_channels) > 5:
                if drawn_toggles >= min(4, round(len(active_material_channels) / 2)):
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
            first_column = split.column(align=True)
            second_column = split.column(align=True)

            # Draw the image texture property.
            row = first_column.row(align=True)
            row.context_pointer_set("mix_node", mix_node)
            row.menu('MATLAYER_MT_material_channel_value_node_sub_menu', text="", icon='IMAGE_DATA')
            row.prop(value_node, "image", text="")
            image = value_node.image
            if image:
                row.prop(image, "use_fake_user", text="")

            # Draw a custom sub-menu for editing the image property.
            row.context_pointer_set("node_tree", layer_node_tree)
            row.context_pointer_set("node", value_node)
            row.menu("MATLAYER_MT_image_utility_sub_menu", text="", icon='DOWNARROW_HLT')

            # Draw the toggle image alpha button and the RGBA output channel.
            row = second_column.row(align=True)
            mix_image_alpha_node = material_layers.get_material_layer_node('MIX_IMAGE_ALPHA', selected_layer_index, material_channel_name)
            if mix_image_alpha_node.mute:
                operator = row.operator("matlayer.toggle_image_alpha_blending", text="", icon='IMAGE_ALPHA')
            else:
                operator = row.operator("matlayer.toggle_image_alpha_blending", text="", icon='IMAGE_ALPHA', depress=True)
            operator.material_channel_name = material_channel_name
            row.context_pointer_set("mix_node", mix_node)
            output_channel_name = material_layers.get_material_channel_crgba_output(material_channel_name)
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

def draw_value_node_properties(layout, value_node):
    '''Draws properties for the provided value node.'''
    match value_node.bl_static_type:
        case 'GROUP':
            # Draw input properties for the group node.
            for i in range(0, len(value_node.inputs)):
                row = layout.row(align=True)
                if value_node.inputs[i].type == 'RGBA' or value_node.inputs[i].type == 'VECTOR':
                    row.prop(value_node.inputs[i], "default_value", text="")
                else:
                    row.prop(value_node.inputs[i], "default_value", text=value_node.inputs[i].name)

            # Draw texture properties stored in custom group nodes.
            for node in value_node.node_tree.nodes:
                if node.bl_static_type == 'TEX_IMAGE':
                    row = layout.row(align=True)

                    split = row.split(factor=0.4)
                    first_column = split.row()
                    second_column = split.row(align=True)

                    if node.label == "":
                        first_column.label(text=node.name)
                    else:
                        first_column.label(text=node.label)
                    second_column.prop(node, "image", text="")
                    second_column.context_pointer_set("node_tree", value_node.node_tree)
                    second_column.context_pointer_set("node", node)
                    second_column.menu("MATLAYER_MT_image_utility_sub_menu", text="", icon='DOWNARROW_HLT')

        case 'TEX_IMAGE':
            row = layout.row()
            row.prop(value_node, "interpolation", text="")

def draw_material_channel_properties(layout):
    '''Draws properties for all active material channels on selected material layer.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index

    # Avoid drawing material channel properties for invalid layers.
    if material_layers.get_material_layer_node('LAYER', selected_layer_index) == None:
        return
    
    # Draw properties for all active material channels.
    shader_info = bpy.context.scene.matlayer_shader_info
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
                row = layout.row()
                row.separator()
                row = layout.row()
                row.label(text="• {0}".format(channel.name))
                draw_value_node(layout, value_node, mix_node, layer_node_tree, selected_layer_index, channel.name)
                draw_material_channel_filter_node(layout, channel.name, selected_layer_index)
                draw_value_node_properties(layout, value_node)
                draw_material_channel_filter_properties(layout, selected_layer_index, channel.name)

def draw_layer_projection(layout):
    '''Draws layer projection settings.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    
    # Draw the projection mode.
    projection_node = material_layers.get_material_layer_node('PROJECTION', selected_layer_index)
    if projection_node:
        match projection_node.node_tree.name:
            case 'ML_UVProjection':
                # Draw the projection mode submenu.
                split = layout.split(factor=0.25)
                first_column = split.column()
                second_column = split.column()

                row = first_column.row()
                row.label(text="Projection")
                row = second_column.row()
                row.menu('MATLAYER_MT_layer_projection_submenu', text="UV")

                # Draw the UV map property.
                active_object = bpy.context.active_object
                if active_object:
                    uv_map_node = projection_node.node_tree.nodes.get('UV_MAP')
                    if uv_map_node:
                        row = first_column.row()
                        row.label(text="UV Map")
                        row = second_column.row()
                        row.prop_search(uv_map_node, "uv_map", active_object.data, "uv_layers", text="")

                # In Blender users can edit multiple properties by holding shift and dragging the mouse down over all properties they wish to edit.
                # Rotation, offset and scale values are draw in columns rather than in rows to allow this.
                split = layout.split()
                col = split.column()
                col.prop(projection_node.inputs.get('OffsetX'), "default_value", text="Offset X", slider=True)
                col.prop(projection_node.inputs.get('OffsetY'), "default_value", text="Offset Y", slider=True)

                col = split.column()
                col.prop(projection_node.inputs.get('ScaleX'), "default_value", text="Scale X")
                col.prop(projection_node.inputs.get('ScaleY'), "default_value", text="Scale Y")

                row = layout.row()
                row.prop(projection_node.inputs.get('Rotation'), "default_value", text="Rotation", slider=True)

            case 'ML_TriplanarProjection':
                # Draw the projection mode submenu.
                split = layout.split(factor=0.25)
                first_column = split.column()
                second_column = split.column()

                row = first_column.row()
                row.label(text="Projection")
                row = second_column.row()
                row.menu('MATLAYER_MT_layer_projection_submenu', text="Triplanar")

                # In Blender users can edit multiple properties by holding shift and dragging the mouse down over all properties they wish to edit.
                # Rotation, offset and scale values are draw in columns rather than in rows to allow this.
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

            case 'ML_DecalProjection':
                split = layout.split(factor=0.25)
                first_column = split.column()
                second_column = split.column()

                row = first_column.row()
                row.label(text="Projection")
                row = second_column.row()
                row.label(text="Decal")

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
        image = mask_texture_node.image
        if image:
            row.prop(image, "use_fake_user", text="")
        row.context_pointer_set("node_tree", mask_node.node_tree)
        row.context_pointer_set("node", mask_texture_node)
        row.menu("MATLAYER_MT_image_utility_sub_menu", text="", icon='DOWNARROW_HLT')

        row = first_column.row()
        row.label(text="Interpolation")
        row = second_column.row()
        row.prop(mask_texture_node, "interpolation", text="")

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
                image = mask_node.image
                if image:
                    row.prop(image, "use_fake_user", text="")
                row.context_pointer_set("node_tree", mask_node.node_tree)
                row.context_pointer_set("node", node)
                row.menu("MATLAYER_MT_image_utility_sub_menu", text="", icon='DOWNARROW_HLT')

                row = first_column.row()
                row.label(text="Interpolation")
                row = second_column.row()
                row.prop(node, "interpolation", text="")

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

def draw_unlayered_material_properties(layout):
    '''Draws all unlayered material properties.'''

    # Ensure there is an active object.
    active_object = bpy.context.active_object
    if not active_object:
        row.label(text="No Active Object Selected")
        return

    # Ensure there is an active material.
    active_material = active_object.active_material
    if not active_material:
        row.label(text="No Active Material")
        return

    # Ensure there is a valid shader node.
    matlayer_shader_node = active_material.node_tree.nodes.get('MATLAYER_SHADER')
    if not matlayer_shader_node:
        row.label(text="No Valid Shader Node")
        return

    # Draw all unlayered material properties.
    shader_info = bpy.context.scene.matlayer_shader_info
    split = layout.split(factor=0.6)
    first_column = split.column()
    second_column = split.column()
    for property in shader_info.unlayered_properties:
        shader_property = matlayer_shader_node.inputs.get(property.name)
        row = layout.row()
        if shader_property:
            row = first_column.row()
            row.label(text=property.name)
            row = second_column.row()
            row.prop(shader_property, "default_value", text="")
        else:
            row.label(text="Shader Property Invalid")

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
        col.operator("matlayer.add_material_layer")
        col.operator("matlayer.add_image_layer")
        col.operator("matlayer.add_decal_material_layer")

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

        row = layout.row(align=True)
        col = row.column(align=True)
        col.scale_y = 1.4
        col.operator("matlayer.add_ambient_occlusion_mask", text="Ambient Occlusion")
        col.operator("matlayer.add_curvature_mask", text="Curvature")
        col.operator("matlayer.add_thickness_mask", text="Thickness")
        col.operator("matlayer.add_world_space_normals_mask", text="World Space Normals")

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

class MaterialChannelSubMenu(Menu):
    bl_idname = "MATLAYER_MT_material_channel_sub_menu"
    bl_label = "Material Channel Sub Menu"

    def draw(self, context):
        layout = self.layout
        shader_info = bpy.context.scene.matlayer_shader_info
        for channel in shader_info.material_channels:
            operator = layout.operator("matlayer.set_material_channel", text=channel.name)
            operator.channel_name = channel.name

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
    bl_idname = "MATLAYER_MT_layer_projection_submenu"
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
        operator = layout.operator("matlayer.set_material_channel_crgba_output", text="Color")
        operator.output_channel_name = 'COLOR'
        operator.material_channel_name = material_channel_name
        operator = layout.operator("matlayer.set_material_channel_crgba_output", text="Alpha")
        operator.output_channel_name = 'ALPHA'
        operator.material_channel_name = material_channel_name
        operator = layout.operator("matlayer.set_material_channel_crgba_output", text="Red")
        operator.output_channel_name = 'RED'
        operator.material_channel_name = material_channel_name
        operator = layout.operator("matlayer.set_material_channel_crgba_output", text="Green")
        operator.output_channel_name = 'GREEN'
        operator.material_channel_name = material_channel_name
        operator = layout.operator("matlayer.set_material_channel_crgba_output", text="Blue")
        operator.output_channel_name = 'BLUE'
        operator.material_channel_name = material_channel_name