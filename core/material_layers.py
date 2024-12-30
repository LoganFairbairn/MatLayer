# This file contains layer properties and functions for updating layer properties.

import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import IntProperty, StringProperty
from ..core import layer_masks
from ..core import material_filters
from ..core import mesh_map_baking
from ..core import blender_addon_utils as bau
from ..core import debug_logging
from ..core import texture_set_settings as tss
from ..core import shaders
import copy
import random
import time

TRIPLANAR_PROJECTION_INPUTS = [
    'X',
    'Y',
    'Z',
    'UnflippedX',
    'UnflippedY',
    'UnflippedZ',
    'AxisMask',
    'Rotation',
    'SignedGeometryNormals'
]

PROJECTION_TEXTURE_SAMPLE_COUNTS = {
    'UV': 1,
    'TRIPLANAR': 3,
    'TRIPLANAR_HEX_GRID': 9,
    'DECAL': 1
}

#----------------------------- UPDATING PROPERTIES -----------------------------#


def format_material_channel_node_name(material_channel_name, node_name, node_index=-1):
    '''Properly formats the name for a layer node that belongs to a material channel.'''
    static_channel_name = bau.format_static_matchannel_name(material_channel_name)
    if node_index != -1:
        return "{0}-{1}-{2}".format(static_channel_name, node_name, node_index)
    else:
        return "{0}-{1}".format(static_channel_name, node_name)

def format_layer_group_node_name(material_name, layer_index):
    '''Properly formats the layer group node names for this add-on.'''
    return "{0}_{1}".format(material_name, layer_index)

def update_layer_index(self, context):
    '''Updates properties and user interface when a new layer is selected.'''

    # Check that the active object attribute exists within the current Blender context.
    active_object_attribute = getattr(bpy.context, "active_object", None)
    if active_object_attribute == None:
        return
    
    layer_masks.refresh_mask_slots()

    # Select the image for texture painting.
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    selected_material_channel = bpy.context.scene.matlayer_layer_stack.selected_material_channel
    value_node = get_material_layer_node('VALUE', selected_layer_index, selected_material_channel)
    if value_node:
        if value_node.bl_static_type == 'TEX_IMAGE':
            bau.set_texture_paint_image(value_node.image)
    
    active_object = bpy.context.active_object
    if active_object:
        if active_object.active_material:

            # Hide all decal objects excluding the one for this layer (if this layer is a decal layer).
            material_layers = bpy.context.scene.matlayer_layers
            for i in range(0, len(material_layers)):
                decal_coordinates_node = get_material_layer_node('DECAL_COORDINATES', i)
                if decal_coordinates_node:
                    if decal_coordinates_node.object:
                        if i == selected_layer_index:
                            decal_coordinates_node.object.hide_set(False)
                        else:
                            decal_coordinates_node.object.hide_set(True)

def sync_triplanar_nodes():
    '''Updates the image texture used in triplanar texture nodes to match the image being used in the first triplanar node.'''
    # Sync triplanar texture samples for all material channels.
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
    if projection_node:
        if projection_node.node_tree.name == 'ML_TriplanarProjection' or projection_node.node_tree.name == 'ML_TriplanarHexGridProjection':
            shader_info = bpy.context.scene.matlayer_shader_info
            for channel in shader_info.material_channels:
                value_node = get_material_layer_node('VALUE', selected_layer_index, channel.name, node_number=1)
                if value_node:
                    if value_node.bl_static_type == 'TEX_IMAGE':
                        for i in range(2, 10):
                            texture_sample_node = get_material_layer_node('VALUE', selected_layer_index, channel.name, node_number=i)
                            if texture_sample_node:
                                if texture_sample_node.image != value_node.image:
                                    texture_sample_node.image = value_node.image
                                if texture_sample_node.interpolation != value_node.interpolation:
                                    texture_sample_node.interpolation = value_node.interpolation

    # Sync triplanar texture samples for masks.
    selected_mask_index = bpy.context.scene.matlayer_mask_stack.selected_index
    mask_projection_node = layer_masks.get_mask_node('PROJECTION', selected_layer_index, selected_mask_index)
    if mask_projection_node:
        if mask_projection_node.node_tree.name == 'ML_TriplanarProjection':
            texture_sample_1 = layer_masks.get_mask_node('TEXTURE', selected_layer_index, selected_mask_index, node_number=1)
            if texture_sample_1:
                texture_sample_2 = layer_masks.get_mask_node('TEXTURE', selected_layer_index, selected_mask_index, node_number=2)
                texture_sample_3 = layer_masks.get_mask_node('TEXTURE', selected_layer_index, selected_mask_index, node_number=3)

                # Run additional checks to avoid accidentally triggering shader re-compiling by changing the image to the same image.
                if texture_sample_2:
                    if texture_sample_2.image != texture_sample_1.image:
                        texture_sample_2.image = texture_sample_1.image

                    if texture_sample_2.interpolation != texture_sample_1.interpolation:
                        texture_sample_2.interpolation = texture_sample_1.interpolation

                if texture_sample_3:
                    if texture_sample_3.image != texture_sample_1.image:
                        texture_sample_3.image = texture_sample_1.image

                    if texture_sample_3.interpolation != texture_sample_1.interpolation:
                        texture_sample_3.interpolation = texture_sample_1.interpolation

def link_custom_group_nodes():
    '''Links custom group nodes.'''
    shader_info = bpy.context.scene.matlayer_shader_info
    for channel in shader_info.material_channels:
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        value_node = get_material_layer_node('VALUE', selected_layer_index, channel.name)
        if value_node:
            if len(value_node.outputs) > 0:
                if len(value_node.outputs[0].links) == 0:
                    output_channel = get_material_channel_crgba_output(channel.name)
                    relink_material_channel(
                        relink_material_channel_name=channel.name, 
                        original_output_channel=output_channel, 
                        unlink_projection=True
                    )

def shader_node_tree_update():
    '''Updates properties when the shader nodetree is changed.'''

    # If the context isn't correct to edit materials, don't update any properties after a shader nodetree update.
    if bau.verify_material_operation_context(display_message=False) == False:
        return
    
    # Perform updates that should occur after a shader nodetree change is detected.
    sync_triplanar_nodes()
    link_custom_group_nodes()

def parse_layer_index(layer_group_node_name):
    '''Return the layers's index by parsing the layer group node name. Returns -1 if there is no active object'''
    active_object = bpy.context.active_object
    if active_object:
        active_material = active_object.active_material
        if active_material:
            material_name_length = len(active_material.name)
            indicies = layer_group_node_name[material_name_length:]
            indicies = indicies.split('_')
            return int(indicies[1])
    return -1

def parse_material_name(layer_group_node_name):
    '''Returns the layer's associated material name by parsing the layer group node name. Returns -1 if there is no active object, or material.'''
    active_object = bpy.context.active_object
    if active_object:
        active_material = active_object.active_material
        if active_material:
            material_name_length = len(active_material.name)
            material_name = layer_group_node_name[:material_name_length]
            return material_name
    return -1

def get_layer_node_tree(layer_index):
    '''Returns the node group for the specified layer (from Blender data) if it exists'''
    
    if not bpy.context.active_object:
        return None
    
    if not bpy.context.active_object.active_material:
        return None
    
    layer_group_name = format_layer_group_node_name(bpy.context.active_object.active_material.name, layer_index)

    return bpy.data.node_groups.get(layer_group_name)

def get_material_layer_node(layer_node_name, layer_index=0, channel_name='COLOR', node_number=1, get_changed=False):
    '''Returns the desired material node if it exists. Supply the material channel name to get nodes specific to material channels.'''

    # This function fixes a few issues with accessing material layer nodes.
    # 1. It makes it easier to change the name of the material layer node being accessed.
    # 2. It circumnavigates issues with Blender's auto translate feature.
    # 3. It requires less code to access nodes in secondary node groups with the material layer nodes.

    if not getattr(bpy.context, 'active_object'):
        debug_logging.log("Context has no attribute 'active_object'.")
        return

    if bpy.context.active_object == None:
        return
    
    active_material = bpy.context.active_object.active_material
    if active_material == None:
        return
    
    layer_group_node_name = format_layer_group_node_name(active_material.name, layer_index)
    static_channel_name = bau.format_static_matchannel_name(channel_name)

    # TODO: This should use a list lookup, instead of a match statement.
    match layer_node_name:
        case 'LAYER':
            if get_changed:
                return active_material.node_tree.nodes.get(str(layer_index) + "~")
            else:
                return active_material.node_tree.nodes.get(str(layer_index))
        
        case 'MATERIAL_OUTPUT':
            return active_material.node_tree.nodes.get('MATERIAL_OUTPUT')
        
        case 'PROJECTION':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("PROJECTION")
            return None

        case 'GROUP_INPUT':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("GROUP_INPUT")
            return None
        
        case 'GROUP_OUTPUT':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("GROUP_OUTPUT")
            return None

        case 'FRAME':
            frame_name = static_channel_name
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get(frame_name)
            return None

        case 'VALUE':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                node_name = format_material_channel_node_name(static_channel_name, "VALUE", node_number)
                return node_tree.nodes.get(node_name)
            return None

        case 'TRIPLANAR_BLEND':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                node_name = format_material_channel_node_name(static_channel_name, "TRIPLANAR_BLEND")
                return node_tree.nodes.get(node_name)
            return None

        case 'FIX_NORMAL_ROTATION':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("FIX_NORMAL_ROTATION")
            return None

        case 'MIX':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                node_name = format_material_channel_node_name(static_channel_name, "MIX")
                return node_tree.nodes.get(node_name)
            return None
        
        case 'MIX_REROUTE':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                node_name = format_material_channel_node_name(static_channel_name, "MIX_REROUTE")
                return node_tree.nodes.get(node_name)
            return None

        case 'MIX_IMAGE_ALPHA':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                node_name = format_material_channel_node_name(static_channel_name, "MIX_IMAGE_ALPHA")
                return node_tree.nodes.get(node_name)
            return None  

        case 'OPACITY':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                node_name = format_material_channel_node_name(static_channel_name, 'OPACITY')
                return node_tree.nodes.get(node_name)
            return None
        
        case 'IMAGE_ALPHA_REROUTE':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                node_name = format_material_channel_node_name(static_channel_name, 'IMAGE_ALPHA_REROUTE')
                return node_tree.nodes.get(node_name)
        
        case 'FILTER':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                node_name = format_material_channel_node_name(static_channel_name, 'FILTER')
                return node_tree.nodes.get(node_name)
            return None

        case 'DECAL_COORDINATES':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get('DECAL_COORDINATES')
            return None
        
        case 'LINEAR_DECAL_MASK_BLEND':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get('LINEAR_DECAL_MASK_BLEND')
            return None
        
        case 'SEPARATE_RGB':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                node_name = format_material_channel_node_name(static_channel_name, "SEPARATE_RGB")
                return node_tree.nodes.get(node_name)
            return None
        
        case 'EXPORT_UV_MAP':
            return active_material.node_tree.nodes.get('EXPORT_UV_MAP')

        case 'BLUR':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                node_name = format_material_channel_node_name(static_channel_name, 'BLUR')
                return node_tree.nodes.get(node_name)
            return None

        case 'BLUR_NOISE':
            return active_material.node_tree.nodes.get('BLUR_NOISE')

        case _:
            debug_logging.log("Invalid material node name: {0}".format(layer_node_name))
            return None

def get_isolate_node():
    '''Returns a node designed to isolate materials (Emission). If the node doesn't exist already within the active material node tree, a new isolate node will be created.'''
    active_material = bpy.context.active_object.active_material
    isolate_node = active_material.node_tree.nodes.get('ISOLATE_NODE')
    if not isolate_node:
        isolate_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
        isolate_node.name = 'ISOLATE_NODE'
        isolate_node.label = isolate_node.name
        isolate_node.node_tree = bau.append_group_node("ML_IsolateNode", never_auto_delete=True)
        isolate_node.location = [0.0, 200.0]
        isolate_node.width = 250.0
    return isolate_node

def delete_isolate_node():
    '''Deletes the isolation node from the active material's node tree, and the iso late node group from blend data.'''

    # Delete the isolation node from the active material's node tree.
    active_material = bpy.context.active_object.active_material
    isolate_node = active_material.node_tree.nodes.get('ISOLATE_NODE')
    if isolate_node:
        active_material.node_tree.nodes.remove(isolate_node)

    # Deletes the isolation node from blend data.
    isolate_node_tree = bpy.data.node_groups.get("ML_IsolateNode")
    if isolate_node_tree:
        bpy.data.node_groups.remove(isolate_node_tree, do_unlink=True, do_id_user=True, do_ui_user=True)

def get_layer_type():
    '''Determines the type of the selected layer based on the projection node tree.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
    if projection_node:
        match projection_node.node_tree.name:
            case 'ML_DecalProjection':
                return 'DECAL'
            case _:
                return 'NORMAL'
    else:
        debug_logging.log("Projection node not defined.", message_type='ERROR')
        return 'NORMAL'

def add_material_layer_slot():
    '''Adds a new slot to the material layer stack, and returns the index of the new layer slot.'''
    layers = bpy.context.scene.matlayer_layers
    layer_stack = bpy.context.scene.matlayer_layer_stack

    layer_slot = layers.add()

    # Assign a random, unique number to the layer slot. 
    # This allows the layer slot array index to be found using the name of the layer slot as a key.
    unique_random_slot_id = str(random.randrange(0, 999999))
    while layers.find(unique_random_slot_id) != -1:
        unique_random_slot_id = str(random.randrange(0, 999999))
    layer_slot.name = unique_random_slot_id

    # If there is no layer selected, move the layer to the top of the stack.
    if bpy.context.scene.matlayer_layer_stack.selected_layer_index < 0:
        move_index = len(layers) - 1
        move_to_index = 0
        layers.move(move_index, move_to_index)
        layer_stack.layer_index = move_to_index
        bpy.context.scene.matlayer_layer_stack.selected_layer_index = len(layers) - 1

    # Moves the new layer above the currently selected layer and selects it.
    else: 
        move_index = len(layers) - 1
        move_to_index = max(0, min(bpy.context.scene.matlayer_layer_stack.selected_layer_index + 1, len(layers) - 1))
        layers.move(move_index, move_to_index)
        layer_stack.layer_index = move_to_index
        bpy.context.scene.matlayer_layer_stack.selected_layer_index = max(0, min(bpy.context.scene.matlayer_layer_stack.selected_layer_index + 1, len(layers) - 1))

    return bpy.context.scene.matlayer_layer_stack.selected_layer_index

def create_default_material_setup():
    '''Creates a default material setup using the selected shader group node defined in the add-on shader tab.'''

    # Append a blank material template setup from the add-on assets blend file.
    default_material = bau.append_material('BlankMaterialSetup')
    if default_material:
        blank_node_tree = default_material.node_tree
        if blank_node_tree:
            shader_info = bpy.context.scene.matlayer_shader_info
            shader_node = blank_node_tree.nodes.get('SHADER_NODE')
            
            # Replace the shader node in the blank material setup.
            old_node_location = shader_node.location
            old_node_width = shader_node.width
            blank_node_tree.nodes.remove(shader_node)
            new_shader_node = blank_node_tree.nodes.new('ShaderNodeGroup')
            new_shader_node.name = 'SHADER_NODE'
            new_shader_node.label = new_shader_node.name
            new_shader_node.location = old_node_location
            new_shader_node.width = old_node_width
            new_shader_node.node_tree = shader_info.shader_node_group

            # Re-link the main shader node to the material output.
            material_output_node = blank_node_tree.nodes.get('MATERIAL_OUTPUT')
            if material_output_node:
                blank_node_tree.links.new(new_shader_node.outputs[0], material_output_node.inputs[0])
    
    else:
        debug_logging.log("Missing blank material setup.", message_type='ERROR', sub_process=False)

    return default_material

def check_channel_nodes_exist(material_channel_name, node_tree):
    '''Checks if the specified material channel nodes exist by checking for a material channel frame node.'''
    static_channel_name = bau.format_static_matchannel_name(material_channel_name)
    frame_node = node_tree.nodes.get(static_channel_name)
    if frame_node:
        return True
    else:
        return False

def add_material_channel_nodes(material_channel_name, node_tree, layer_type, self=None, log_in_info_window=True):
    '''Creates framed nodes for a material channel.'''
    static_channel_name = bau.format_static_matchannel_name(material_channel_name)
    material_channel_name = shaders.get_shader_channel_socket_name(static_channel_name)

    # If a channel nodes already exist for this material channel, if they do, there's an error, abort.
    channel_nodes_exist = check_channel_nodes_exist(material_channel_name, node_tree)
    if channel_nodes_exist:
        debug_logging.log("Material channel already exists.")
        if self != None:
            info_message = "Material channel already exists."
            if log_in_info_window:
                debug_logging.log_status(info_message, self, type='INFO')
            else:
                debug_logging.log(info_message, message_type='INFO', sub_process=False)
        return

    # Add a frame for the material channel.
    channel_frame_node = node_tree.nodes.new('NodeFrame')
    channel_frame_node.name = static_channel_name
    channel_frame_node.label = static_channel_name

    # Ensure the specified material channel exists in the shader.
    shader_info = bpy.context.scene.matlayer_shader_info
    static_shader_channel_list = shaders.get_static_shader_channel_list()
    if static_channel_name not in static_shader_channel_list:
        debug_logging.log("Shader channel {0} doesn't exist, not adding nodes.".format(material_channel_name))
        return

    # We use group nodes to represent default float, color and vector values for material channels instead of 
    # value, or color nodes because the default ranges and socket types can only be specified for group nodes.
    # Create default group nodes to represent each material channel.
    channel = shader_info.material_channels.get(material_channel_name)
    default_value_group_node_name = "ML_Default{0}".format(material_channel_name.replace(' ', ''))
    default_value_group_node = bpy.data.node_groups.get(default_value_group_node_name)
    if not default_value_group_node:
        default_value_group_node = bpy.data.node_groups.new(default_value_group_node_name, type='ShaderNodeTree')
    
        input_socket = default_value_group_node.interface.new_socket(
            name=channel.name,
            description=channel.name,
            in_out='INPUT',
            socket_type=channel.socket_type
        )

        output_socket = default_value_group_node.interface.new_socket(
            name=channel.name,
            description=channel.name,
            in_out='OUTPUT',
            socket_type=channel.socket_type
        )

        match channel.socket_type:
            case 'NodeSocketFloat':
                input_socket.default_value = channel.socket_float_default
                input_socket.min_value = channel.socket_float_min
                input_socket.max_value = channel.socket_float_max
                output_socket.default_value = channel.socket_float_default
                output_socket.min_value = channel.socket_float_min
                output_socket.max_value = channel.socket_float_max
                input_socket.subtype = channel.socket_subtype

            case 'NodeSocketColor':
                input_socket.default_value = (channel.socket_color_default[0], channel.socket_color_default[1], channel.socket_color_default[2], 1)
                output_socket.default_value = (channel.socket_color_default[0], channel.socket_color_default[1], channel.socket_color_default[2], 1)

            case 'NodeSocketVector':
                input_socket.default_value = channel.socket_vector_default
                input_socket.default_value = channel.socket_vector_default

        # Add input and output nodes so the material channel can pass through the node.
        group_input_node = default_value_group_node.nodes.new('NodeGroupInput')
        group_input_node.name = 'GROUP_INPUT'
        group_input_node.label = group_input_node.name
        group_input_node.location[0] = -1000
        group_input_node.location[1] = 0
        group_input_node.width = 300

        group_output_node = default_value_group_node.nodes.new('NodeGroupOutput')
        group_output_node.name = 'GROUP_OUTPUT'
        group_output_node.label = group_output_node.name
        group_output_node.location[0] = 0
        group_output_node.location[1] = 0
        group_output_node.width = 300

        # Link the input and output nodes.
        default_value_group_node.links.new(group_input_node.outputs[0], group_output_node.inputs[0])

    # Add a value node to represent this material channel.
    value_node = node_tree.nodes.new('ShaderNodeGroup')
    value_node.name = format_material_channel_node_name(static_channel_name, 'VALUE', node_index=1)
    value_node.label = value_node.name
    value_node.location[0] = -1000
    value_node.location[1] = -400
    value_node.parent = channel_frame_node
    value_node.width = 300
    value_node.node_tree = default_value_group_node

    # Add the mix image alpha node.
    image_alpha_node = node_tree.nodes.new('ShaderNodeMath')
    image_alpha_node.name = format_material_channel_node_name(static_channel_name, 'MIX_IMAGE_ALPHA')
    image_alpha_node.label = image_alpha_node.name
    image_alpha_node.location[0] = -500
    image_alpha_node.location[1] = 0
    image_alpha_node.parent = channel_frame_node
    image_alpha_node.operation = 'MULTIPLY'
    image_alpha_node.mute = True
    image_alpha_node.hide = True
    image_alpha_node.use_clamp = True

    # Add a re-route for the image alpha node for better node organization.
    image_alpha_node_reroute = node_tree.nodes.new('NodeReroute')
    image_alpha_node_reroute.name = format_material_channel_node_name(static_channel_name, 'IMAGE_ALPHA_REROUTE')
    image_alpha_node_reroute.label = image_alpha_node_reroute.name
    image_alpha_node_reroute.location[0] = -1000
    image_alpha_node_reroute.location[1] = 0
    image_alpha_node_reroute.parent = channel_frame_node

    # Add an opacity node.
    opacity_node = node_tree.nodes.new('ShaderNodeMix')
    opacity_node.name = format_material_channel_node_name(static_channel_name, 'OPACITY')
    opacity_node.label = opacity_node.name
    opacity_node.location[0] = -300
    opacity_node.location[1] = 0
    opacity_node.parent = channel_frame_node
    opacity_node.width = 250
    opacity_node.data_type = 'FLOAT'
    opacity_node.inputs[0].default_value = 1.0
    opacity_node.inputs[2].default_value = 0.0
    opacity_node.inputs[3].default_value = 1.0

    # Add a separate node for separating RGBA channels.
    separate_node = node_tree.nodes.new('ShaderNodeSeparateColor')
    separate_node.name = format_material_channel_node_name(static_channel_name, 'SEPARATE_RGB')
    separate_node.label = separate_node.name
    separate_node.location[0] = -200
    separate_node.location[1] = -500
    separate_node.parent = channel_frame_node

    # Add re-route nodes for organization.
    mix_node_reroute = node_tree.nodes.new('NodeReroute')
    mix_node_reroute.name = format_material_channel_node_name(static_channel_name, 'MIX_REROUTE')
    mix_node_reroute.label = mix_node_reroute.name
    mix_node_reroute.location[0] = -1000
    mix_node_reroute.location[1] = -177
    mix_node_reroute.parent = channel_frame_node

    # Get group input / output nodes for linking.
    group_input_node = node_tree.nodes.get('GROUP_INPUT')
    group_output_node = node_tree.nodes.get('GROUP_OUTPUT')

    # Change the mix node and it's linking based on the default blend mode.
    if channel.default_blend_mode == 'NORMAL_MAP_COMBINE' or channel.default_blend_mode == 'NORMAL_MAP_DETAIL':
        normal_rotation_fix_node = node_tree.nodes.new('ShaderNodeGroup')
        normal_rotation_fix_node.name = 'FIX_NORMAL_ROTATION'
        normal_rotation_fix_node.label = normal_rotation_fix_node.name
        normal_rotation_fix_node.location[0] = -600
        normal_rotation_fix_node.location[1] = -500
        normal_rotation_fix_node.parent = channel_frame_node
        normal_rotation_fix_node.width = 300
        normal_rotation_fix_node.node_tree = bau.append_group_node('ML_FixNormalRotation')

        mix_node = node_tree.nodes.new('ShaderNodeGroup')
        mix_node.node_tree = bau.append_group_node('ML_ReorientedNormalMapMix')
        node_tree.links.new(mix_node_reroute.outputs[0], mix_node.inputs[1])
        node_tree.links.new(value_node.outputs[0], mix_node.inputs[2])
        node_tree.links.new(mix_node.outputs[0], group_output_node.inputs.get(material_channel_name))

    else:
        mix_node = node_tree.nodes.new('ShaderNodeMix')
        mix_node.data_type = 'RGBA'
        mix_node.clamp_factor = True
        mix_node.clamp_result = True
        mix_node.blend_type = channel.default_blend_mode
        node_tree.links.new(mix_node_reroute.outputs[0], mix_node.inputs[6])
        node_tree.links.new(value_node.outputs[0], mix_node.inputs[7])
        node_tree.links.new(mix_node.outputs[2], group_output_node.inputs.get(material_channel_name))
    
    mix_node.name = format_material_channel_node_name(static_channel_name, 'MIX')
    mix_node.label = mix_node.name
    mix_node.location[0] = 500
    mix_node.location[1] = 0
    mix_node.parent = channel_frame_node

    # The normal mix node output index is different than all other mix node outputs.
    if static_channel_name == 'NORMAL':
        mix_node_output_index = 0
    else:
        mix_node_output_index = 2

    # Link new nodes.
    node_tree.links.new(image_alpha_node_reroute.outputs[0], image_alpha_node.inputs[0])
    node_tree.links.new(image_alpha_node.outputs[0], opacity_node.inputs[3])
    node_tree.links.new(opacity_node.outputs[0], mix_node.inputs[0])
    node_tree.links.new(group_input_node.outputs.get(material_channel_name), mix_node_reroute.inputs[0])
    node_tree.links.new(mix_node.outputs[mix_node_output_index], group_output_node.inputs.get(material_channel_name))

    # Link layer mask nodes based on layer type.
    match layer_type:
        case 'DECAL':
            linear_decal_mask_blend_node = node_tree.nodes.get('LINEAR_DECAL_MASK_BLEND')
            node_tree.links.new(group_input_node.outputs.get('Layer Mask'), linear_decal_mask_blend_node.inputs[0])
            node_tree.links.new(linear_decal_mask_blend_node.outputs[0], image_alpha_node_reroute.inputs[0])
        case _:
            node_tree.links.new(group_input_node.outputs.get('Layer Mask'), image_alpha_node_reroute.inputs[0])

def delete_material_channel_nodes(material_channel_name):
    '''Deletes nodes for the specified material channel.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node_tree = get_material_layer_node("LAYER", selected_layer_index, material_channel_name).node_tree

    # Delete all layer nodes.
    frame_node = get_material_layer_node('FRAME', selected_layer_index, material_channel_name)
    mix_node = get_material_layer_node('MIX', selected_layer_index, material_channel_name)
    mix_image_alpha_node = get_material_layer_node('MIX_IMAGE_ALPHA', selected_layer_index, material_channel_name)
    opacity_node = get_material_layer_node('OPACITY', selected_layer_index, material_channel_name)
    separate_rgb_node = get_material_layer_node('SEPARATE_RGB', selected_layer_index, material_channel_name)
    mix_reroute_node = get_material_layer_node('MIX_REROUTE', selected_layer_index, material_channel_name)
    image_alpha_reroute_node = get_material_layer_node('IMAGE_ALPHA_REROUTE', selected_layer_index, material_channel_name)
    value_node_1 = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, node_number=1)
    value_node_2 = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, node_number=2)
    value_node_3 = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, node_number=3)
    fix_normal_rotation = get_material_layer_node('FIX_NORMAL_ROTATION', selected_layer_index, material_channel_name)
    triplanar_blend = get_material_layer_node('TRIPLANAR_BLEND', selected_layer_index, material_channel_name)
    blur_node = get_material_layer_node('BLUR', selected_layer_index, material_channel_name)

    bau.safe_node_delete(layer_node_tree, frame_node)
    bau.safe_node_delete(layer_node_tree, mix_node)
    bau.safe_node_delete(layer_node_tree, mix_image_alpha_node)
    bau.safe_node_delete(layer_node_tree, opacity_node)
    bau.safe_node_delete(layer_node_tree, separate_rgb_node)
    bau.safe_node_delete(layer_node_tree, mix_reroute_node)
    bau.safe_node_delete(layer_node_tree, image_alpha_reroute_node)
    bau.safe_node_delete(layer_node_tree, value_node_1)
    bau.safe_node_delete(layer_node_tree, value_node_2)
    bau.safe_node_delete(layer_node_tree, value_node_3)
    bau.safe_node_delete(layer_node_tree, fix_normal_rotation)
    bau.safe_node_delete(layer_node_tree, triplanar_blend)
    bau.safe_node_delete(layer_node_tree, blur_node)

    # Delete all filter nodes.
    filter_index = 1
    filter_node = material_filters.get_filter_node(material_channel_name, filter_index)
    while filter_node:
        bau.safe_node_delete(layer_node_tree, filter_node)
        filter_index += 1
        filter_node = material_filters.get_filter_node(material_channel_name, filter_index)

    # Link the input and output nodes so the material channel value is passed through the layer.
    input_node = get_material_layer_node('GROUP_INPUT', selected_layer_index, material_channel_name)
    output_node = get_material_layer_node('GROUP_OUTPUT', selected_layer_index, material_channel_name)
    layer_node_tree.links.new(input_node.outputs.get(material_channel_name),output_node.inputs.get(material_channel_name))

def organize_material_channel_frames(node_tree):
    '''Organizes all material channel frames for the selected layer.'''
    shader_info = bpy.context.scene.matlayer_shader_info
    frame_x = -1000
    frame_y = -500
    frame_spacing = 1000
    for channel in shader_info.material_channels:
        static_channel_name = bau.format_static_matchannel_name(channel.name)
        frame = node_tree.nodes.get(static_channel_name)
        if frame:
            frame.location[0] = frame_x
            frame.location[1] = frame_y
            frame_y -= frame_spacing

def create_new_layer_node(layer_type):
    '''Creates a new layer group node, with a default setup based on the defined shader material channels.'''

    # Create a default node group for the layer, if one exists already, delete it.
    new_layer_node_name = "NewLayerNode"
    new_node_group = bpy.data.node_groups.get(new_layer_node_name)
    if new_node_group:
        bpy.data.node_groups.remove(new_node_group)
    new_node_group = bpy.data.node_groups.new(new_layer_node_name, type='ShaderNodeTree')

    # Add inputs and outputs to the group node for all shader channels.
    shader_info = bpy.context.scene.matlayer_shader_info
    for channel in shader_info.material_channels:
        input_socket = new_node_group.interface.new_socket(
            name=channel.name, 
            description=channel.name,
            in_out='INPUT',
            socket_type=channel.socket_type
        )
        output_socket = new_node_group.interface.new_socket(
            name=channel.name,
            description=channel.name,
            in_out='OUTPUT',
            socket_type=channel.socket_type
        )

        # Define default values for the channel sockets.
        match channel.socket_type:
            case 'NodeSocketFloat':
                input_socket.default_value = channel.socket_float_default
                input_socket.min_value = channel.socket_float_min
                input_socket.max_value = channel.socket_float_max
                output_socket.default_value = channel.socket_float_default
                output_socket.min_value = channel.socket_float_min
                output_socket.max_value = channel.socket_float_max
                input_socket.subtype = channel.socket_subtype
            case 'NodeSocketColor':
                input_socket.default_value = (channel.socket_color_default[0], channel.socket_color_default[1], channel.socket_color_default[2], 1)
                output_socket.default_value = (channel.socket_color_default[0], channel.socket_color_default[1], channel.socket_color_default[2], 1)
            case 'NodeSocketVector':
                input_socket.default_value = channel.socket_vector_default
                output_socket.default_value = channel.socket_vector_default

    # Add an input socket for inputting blur noise (for blurring filters).
    new_node_group.interface.new_socket(
        name="Blur Noise",
        description="Input for noise used in blurring filters",
        in_out='INPUT',
        socket_type='NodeSocketColor'
    )

    # Add an input socket for layer mask input.
    mask_socket = new_node_group.interface.new_socket(
        name="Layer Mask",
        description="Mask input for the layer",
        in_out='INPUT',
        socket_type='NodeSocketFloat'
    )
    mask_socket.subtype = 'FACTOR'
    mask_socket.default_value = 1.0
    mask_socket.min_value = 0.0
    mask_socket.max_value = 1.0

    # Add input and output nodes.
    input_node = new_node_group.nodes.new('NodeGroupInput')
    input_node.name = 'GROUP_INPUT'
    input_node.label = input_node.name
    input_node.location[0] = -3000
    input_node.location[1] = 0
    input_node.width = 300

    output_node = new_node_group.nodes.new('NodeGroupOutput')
    output_node.name = 'GROUP_OUTPUT'
    output_node.label = output_node.name
    output_node.location[0] = 0
    output_node.location[1] = 0
    output_node.width = 300

    # Add a projection node based on the layer type.
    projection_node = new_node_group.nodes.new('ShaderNodeGroup')
    projection_node.name = 'PROJECTION'
    projection_node.label = projection_node.name
    projection_node.location[0] = -3000
    projection_node.location[1] = -1000
    projection_node.width = 300
    match layer_type:
        case 'DECAL':
            projection_node.node_tree = bau.append_group_node('ML_DecalProjection')
            decal_coord_node = new_node_group.nodes.new('ShaderNodeTexCoord')
            decal_coord_node.name = 'DECAL_COORDINATES'
            decal_coord_node.label = decal_coord_node.name
            decal_coord_node.location[0] = -3500
            decal_coord_node.location[1] = -1000
            decal_coord_node.width = 300

            linear_decal_mask_blend_node = new_node_group.nodes.new('ShaderNodeMath')
            linear_decal_mask_blend_node.name = 'LINEAR_DECAL_MASK_BLEND'
            linear_decal_mask_blend_node.label = linear_decal_mask_blend_node.name
            linear_decal_mask_blend_node.location[0] = -2500
            linear_decal_mask_blend_node.location[1] = -1000
            linear_decal_mask_blend_node.width = 150
            linear_decal_mask_blend_node.hide = True
            linear_decal_mask_blend_node.operation = 'MULTIPLY'

            new_node_group.links.new(decal_coord_node.outputs[3], projection_node.inputs[0])
            new_node_group.links.new(projection_node.outputs.get('LinearMask'), linear_decal_mask_blend_node.inputs[1])
        case _:
            projection_node.node_tree = bau.append_group_node('ML_UVProjection')

    # Add material nodes for all active material channels.
    for channel in shader_info.material_channels:
        if channel.default_active == True:
            add_material_channel_nodes(channel.name, new_node_group, layer_type)
        
        # For inactive material channels, skip adding nodes, and instead link the input
        # and output nodes so values from previous layers pass through this layer.
        else:
            new_node_group.links.new(input_node.outputs.get(channel.name),output_node.inputs.get(channel.name))

    # Organize all material channel frame nodes.
    organize_material_channel_frames(new_node_group)

    return new_node_group

def add_material_layer(layer_type, self):
    '''Adds a material layer to the active materials layer stack.'''

    # Append group nodes to help avoid node group duplication from appending.
    bau.append_default_node_groups()

    # Verify standard context is correct.
    if bau.verify_material_operation_context(self, check_active_material=False) == False:
        return
    
    # Verify the shader group node exists, one must be defined to add material layers.
    valid_shader_node_group = shaders.verify_shader_node_group(self)
    if valid_shader_node_group == False:
        return

    # If there are no material slots, or no material in the active material slot...
    # make a new material by appending the default material setup for this add-on.
    active_object = bpy.context.active_object
    if len(active_object.material_slots) == 0:
        new_material = create_default_material_setup()
        new_material_name = bau.get_unique_material_name(active_object.name.replace('_', ''))
        new_material.name = new_material_name
        active_object.data.materials.append(new_material)
        active_object.active_material_index = 0

    # If material slots exist on the object, but the active material slot is empty, add a new material.
    elif active_object.material_slots[active_object.active_material_index].material == None:
        new_material = create_default_material_setup()
        new_material_name = bau.get_unique_material_name(active_object.name.replace('_', ''))
        new_material.name = new_material_name
        active_object.material_slots[active_object.active_material_index].material = new_material

    # If material slots exist on the object, but the active material isn't properly formatted to work with this add-on, display an error.
    else:
        active_material = bpy.context.active_object.active_material
        if bau.verify_addon_material(active_material) == False:
            debug_logging.log_status("Can't add layer, active material format is invalid.", self, type='ERROR')
            return
    
    # Add a new material layer slot.
    new_layer_slot_index = add_material_layer_slot()

    # Create a default layer group node based on shader material channels.
    default_layer_node_group = create_new_layer_node(layer_type)

    # Add the new layer group node to the active material.
    active_material = bpy.context.active_object.active_material
    default_layer_node_group.name = format_layer_group_node_name(active_material.name, str(new_layer_slot_index)) + "~"
    new_layer_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
    new_layer_group_node.node_tree = default_layer_node_group
    new_layer_group_node.name = str(new_layer_slot_index) + "~"

    # Assign a default name to the layer based on the layer type.
    match layer_type:
        case 'NORMAL':
            new_layer_group_node.label = "Material Layer"
        case 'IMAGE':
            new_layer_group_node.label = "Image Layer"
        case 'DECAL':
            new_layer_group_node.label = "Decal Layer"

    # Re-index, organize and link layer nodes together.
    reindex_layer_nodes(change_made='ADDED_LAYER', affected_layer_index=new_layer_slot_index)
    organize_layer_group_nodes()
    link_layer_group_nodes(self)
    layer_masks.organize_mask_nodes()
    layer_masks.refresh_mask_slots()

    # Link layer blur noise inputs so material channels have access to blurring.
    link_material_channel_noise_blur(active_material.node_tree, new_layer_group_node)

    # Perform additional setup steps based on layer type.
    match layer_type:
        case 'MATERIAL':
            debug_logging.log("Added material layer.")

        case 'DECAL':
            # Create a new empty to use as a decal object.
            unique_decal_name = bau.get_unique_object_name("Decal", start_id_number=1)
            decal_object = bpy.data.objects.new(unique_decal_name, None)
            decal_object.empty_display_type = 'CUBE'
            decal_object.scale[2] = 0.1
            bau.add_object_to_collection("Decals", decal_object, color_tag='COLOR_03', unlink_from_other_collections=True)

            # Add the new decal object to the decal coordinate node.
            decal_coordinate_node = get_material_layer_node('DECAL_COORDINATES', new_layer_slot_index)
            if decal_coordinate_node:
                decal_coordinate_node.object = decal_object
            
            # Add a default decal to the base color material channel (if one exists in the shader).
            channel_socket_name = shaders.get_shader_channel_socket_name('BASE_COLOR')
            if channel_socket_name != "":
                default_decal_image = bau.append_image('DefaultDecal')
                replace_material_channel_node('BASE_COLOR', 'TEXTURE')
                texture_node = get_material_layer_node('VALUE', new_layer_slot_index, 'BASE_COLOR')
                if texture_node:
                    if texture_node.bl_static_type == 'TEX_IMAGE':
                        texture_node.image = default_decal_image
                        bau.set_texture_paint_image(default_decal_image)
                        bau.save_image(default_decal_image)

            # Add an image mask to apply a default transparency effect to the decal layer.
            layer_masks.add_layer_mask('DECAL', self)
            mask_texture_node = layer_masks.get_mask_node('TEXTURE', new_layer_slot_index, 0)
            if mask_texture_node:
                mask_texture_node.image = default_decal_image
            layer_masks.set_mask_crgba_channel('ALPHA')
            
            # Apply decal snapping.
            bau.set_snapping('DECAL', snap_on=True)

            debug_logging.log("Added decal layer.")
        
        case 'IMAGE':
            # Toggle off all material channels excluding base color.
            base_color_socket_name = shaders.get_shader_channel_socket_name('BASE_COLOR')
            shader_info = bpy.context.scene.matlayer_shader_info
            for channel in shader_info.material_channels:
                if channel.name != base_color_socket_name:
                    mix_node = get_material_layer_node('MIX', new_layer_slot_index, channel.name)
                    if mix_node:
                        mix_node.mute = True

            # Create a new blank image.
            new_image = bau.create_image(
                new_image_name="Image",
                image_width=tss.get_texture_width(),
                image_height=tss.get_texture_height(),
                base_color=(0,0,0,0),
                generate_type='BLANK',
                alpha_channel=True,
                thirty_two_bit=True,
                add_unique_id=True,
                delete_existing=False
            )

            # Add the new blank image to the base color channel.
            replace_material_channel_node(base_color_socket_name, node_type='TEXTURE')
            value_node = get_material_layer_node('VALUE', new_layer_slot_index, 'BASE_COLOR')
            if value_node:
                if value_node.bl_static_type == 'TEX_IMAGE':
                    value_node.image = new_image

            # Blend the image alpha into the layer.
            toggle_image_alpha_blending('BASE_COLOR')

            # Select the new image for painting.
            bau.set_texture_paint_image(new_image)

            debug_logging.log("Added image layer.")

    # Switch to the layer UI tab after creating a new layer.
    bpy.context.scene.matlayer_material_property_tabs = 'MATERIAL_CHANNELS'

def duplicate_layer(original_layer_index, self):
    '''Duplicates the material layer at the provided layer index.'''

    if bau.verify_material_operation_context(self) == False:
        return
    
    duplicated_decal_object = None

    # Duplicate the node tree and add it to the layer stack.
    layer_node_tree = get_layer_node_tree(original_layer_index)
    if not layer_node_tree:
        debug_logging.log("No layer node tree, can't duplicate layer.")
        return

    duplicated_node_tree = bau.duplicate_node_group(layer_node_tree.name)
    if duplicated_node_tree:
        active_material = bpy.context.active_object.active_material

        new_layer_slot_index = add_material_layer_slot()

        duplicated_node_tree.name = "{0}_{1}".format(active_material.name, str(new_layer_slot_index))
        new_layer_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
        new_layer_group_node.node_tree = duplicated_node_tree
        new_layer_group_node.name = str(new_layer_slot_index) + "~"

        # Copy the name of the original layer.
        original_layer_node = get_material_layer_node('LAYER', original_layer_index)
        new_layer_group_node.label = original_layer_node.label + " Copy"
        
        reindex_layer_nodes(change_made='ADDED_LAYER', affected_layer_index=new_layer_slot_index)
        organize_layer_group_nodes()
        link_layer_group_nodes(self)
        layer_masks.organize_mask_nodes()

        # Link blurring for the duplicated layer.
        link_material_channel_noise_blur(active_material.node_tree, new_layer_group_node)

        # Duplicate decal objects if the original layer was a decal layer.
        decal_coordinate_node = get_material_layer_node('DECAL_COORDINATES', original_layer_index)
        if decal_coordinate_node:
            decal_object = decal_coordinate_node.object
            if decal_object:
                duplicated_decal_object = bau.duplicate_object(decal_object)
                new_decal_coordinate_node = get_material_layer_node('DECAL_COORDINATES', new_layer_slot_index)
                if new_decal_coordinate_node:
                    new_decal_coordinate_node.object = duplicated_decal_object

    # Clear the mask stack from the new layer.
    masks = bpy.context.scene.matlayer_masks
    masks.clear()

    # Duplicate mask node trees and add them as group nodes to the active material.
    mask_count = layer_masks.count_masks(original_layer_index)
    for i in range(0, mask_count):
        original_mask_node = layer_masks.get_mask_node('MASK', original_layer_index, i)
        if original_mask_node:
            duplicated_node_tree = bau.duplicate_node_group(original_mask_node.node_tree.name)
            if duplicated_node_tree:
                new_mask_slot_index = layer_masks.add_mask_slot()
                duplicated_mask_name = layer_masks.format_mask_name(new_layer_slot_index, new_mask_slot_index, bpy.context.active_object.active_material.name) + "~"
                duplicated_node_tree.name = duplicated_mask_name
                new_mask_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
                new_mask_group_node.node_tree = duplicated_node_tree
                new_mask_group_node.name = duplicated_mask_name
                new_mask_group_node.label = original_mask_node.label

                layer_masks.reindex_masks('ADDED_MASK', new_layer_slot_index, affected_mask_index=i)

                if duplicated_decal_object:
                    decal_coordinate_node = layer_masks.get_mask_node('DECAL_COORDINATES', new_layer_slot_index, new_mask_slot_index)
                    if decal_coordinate_node:
                        decal_coordinate_node.object = duplicated_decal_object
                        
    layer_masks.link_mask_nodes(new_layer_slot_index)
    layer_masks.organize_mask_nodes()

    # Log this operation completion for debugging purposes.
    debug_logging.log("Duplicated material layer.")

def delete_layer(self):
    '''Deletes the selected layer'''
    if bau.verify_material_operation_context(self) == False:
        return {'FINISHED'}
    
    layers = bpy.context.scene.matlayer_layers
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    active_material = bpy.context.active_object.active_material

    # For decal layers, delete the accociated empty object if one exists.
    decal_coordinate_node = get_material_layer_node('DECAL_COORDINATES', selected_layer_index)
    if decal_coordinate_node:
        decal_object = decal_coordinate_node.object
        if decal_object:
            bpy.data.objects.remove(decal_object)

    # Remove all mask group nodes and node trees associated with the layer.
    mask_count = layer_masks.count_masks(selected_layer_index)
    for i in range(0, mask_count):
        mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i)
        if mask_node.bl_static_type == 'GROUP' and mask_node.node_tree:
            bpy.data.node_groups.remove(mask_node.node_tree)
        active_material.node_tree.nodes.remove(mask_node)

    # Remove the layer group node (node tree) from Blender's data.
    layer_node_tree = get_layer_node_tree(selected_layer_index)
    if layer_node_tree:
        bpy.data.node_groups.remove(layer_node_tree)

    # Remove the layer node from the active materials node tree.
    layer_group_node = get_material_layer_node('LAYER', selected_layer_index)
    if layer_group_node:
        active_material.node_tree.nodes.remove(layer_group_node)

    reindex_layer_nodes(change_made='DELETED_LAYER', affected_layer_index=selected_layer_index)
    organize_layer_group_nodes()
    link_layer_group_nodes(self)
    layer_masks.organize_mask_nodes()

    # Remove the layer slot and reset the selected layer index.
    layers.remove(selected_layer_index)
    bpy.context.scene.matlayer_layer_stack.selected_layer_index = max(min(selected_layer_index - 1, len(layers) - 1), 0)

    debug_logging.log("Deleted material layer.")

def move_layer(direction, self):
    '''Moves the selected layer up or down on the material layer stack.'''
    if bau.verify_material_operation_context(self) == False:
        return
    
    match direction:
        case 'UP':
            # Swap the layer index for all layer nodes in this layer with the layer above it (if one exists).
            layers = bpy.context.scene.matlayer_layers
            layer_count = len(layers)
            selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
            if not selected_layer_index < layer_count - 1:
                debug_logging.log_status("Can't move layer up. No layers exist above the selected layer.", self, type='INFO')
                return
            
            layer_node = get_material_layer_node('LAYER', selected_layer_index)
            if layer_node:
                layer_node.name += "~"
                if layer_node.node_tree:
                    layer_node.node_tree.name += "~"

            above_layer_node = get_material_layer_node('LAYER', selected_layer_index + 1)
            if above_layer_node:
                above_layer_node.name = str(selected_layer_index)
                if above_layer_node.node_tree:
                    material_name = parse_material_name(above_layer_node.node_tree.name)
                    above_layer_node.node_tree.name = format_layer_group_node_name(material_name, selected_layer_index)

            layer_node.name = str(selected_layer_index + 1)
            material_name = parse_material_name(layer_node.node_tree.name)
            layer_node.node_tree.name = format_layer_group_node_name(material_name, selected_layer_index + 1)

            # Swap the layer index for all mask nodes in this layer with the layer above it.
            selected_layer_mask_count = layer_masks.count_masks(selected_layer_index)
            for i in range(0, selected_layer_mask_count):
                mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i)
                mask_node.name += "~"
                mask_node.node_tree.name = mask_node.name

            above_layer_mask_count = layer_masks.count_masks(selected_layer_index + 1)
            for i in range(0, above_layer_mask_count):
                mask_node = layer_masks.get_mask_node('MASK', selected_layer_index + 1, i)
                mask_node.name = layer_masks.format_mask_name(selected_layer_index, i)
                mask_node.node_tree.name = mask_node.name

            for i in range(0, selected_layer_mask_count):
                mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i, get_changed=True)
                mask_node.name = layer_masks.format_mask_name(selected_layer_index + 1, i)
                mask_node.node_tree.name = mask_node.name

            bpy.context.scene.matlayer_layer_stack.selected_layer_index = selected_layer_index + 1

        case 'DOWN':
            # Swap the layer index for all nodes in this layer with the layer below it (if one exists).
            layers = bpy.context.scene.matlayer_layers
            selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
            if not selected_layer_index - 1 >= 0:
                debug_logging.log_status("Can't move layer down. No layers exist below the selected layer.", self, type='INFO')
                return
            
            layer_node = get_material_layer_node('LAYER', selected_layer_index)
            layer_node.name += "~"
            layer_node.node_tree.name += "~"

            below_layer_node = get_material_layer_node('LAYER', selected_layer_index - 1)
            below_layer_node.name = str(selected_layer_index)
            material_name = parse_material_name(below_layer_node.node_tree.name)
            below_layer_node.node_tree.name = format_layer_group_node_name(material_name, selected_layer_index)

            layer_node.name = str(selected_layer_index - 1)
            material_name = parse_material_name(layer_node.node_tree.name)
            layer_node.node_tree.name = format_layer_group_node_name(material_name, selected_layer_index - 1)

            # Swap the layer index for all mask nodes in this layer with the layer below it.
            selected_layer_mask_count = layer_masks.count_masks(selected_layer_index)
            for i in range(0, selected_layer_mask_count):
                mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i)
                mask_node.name += "~"
                mask_node.node_tree.name = mask_node.name

            below_layer_mask_count = layer_masks.count_masks(selected_layer_index - 1)
            for i in range(0, below_layer_mask_count):
                mask_node = layer_masks.get_mask_node('MASK', selected_layer_index - 1, i)
                mask_node.name = layer_masks.format_mask_name(selected_layer_index, i)
                mask_node.node_tree.name = mask_node.name

            for i in range(0, selected_layer_mask_count):
                mask_node = layer_masks.get_mask_node('MASK', selected_layer_index, i, get_changed=True)
                mask_node.name = layer_masks.format_mask_name(selected_layer_index - 1, i)
                mask_node.node_tree.name = mask_node.name

            bpy.context.scene.matlayer_layer_stack.selected_layer_index = selected_layer_index - 1

        case _:
            debug_logging.log_status("Invalid direction provided for moving a material layer.", self, 'ERROR')
            return

    organize_layer_group_nodes()
    link_layer_group_nodes(self)
    layer_masks.organize_mask_nodes()
    layer_masks.refresh_mask_slots()
    debug_logging.log("Moved material layer.")

def count_layers(material=None):
    '''Counts the total layers in the specified material (active material if no material is specified) by reading the active material's node tree.'''
    layer_count = 0

    # Count the number of layers in the specified material.
    if material != None:
        while material.node_tree.nodes.get(str(layer_count)):
            layer_count += 1
        return layer_count
    
    # Count the number of layers in the active material.
    else:
        active_object_attribute = getattr(bpy.context, "active_object", None)
        if active_object_attribute == None:
            return 0
        if not bpy.context.active_object:
            return 0
        if not bpy.context.active_object.active_material:
            return 0

        active_material = bpy.context.active_object.active_material
        if active_material.use_nodes == False:
            return 0
        
        while active_material.node_tree.nodes.get(str(layer_count)):
            layer_count += 1
        
        return layer_count

def organize_layer_group_nodes():
    '''Organizes all layer group nodes in the active material to ensure the node tree is easy to read.'''
    active_material = bpy.context.active_object.active_material

    # Organize layer group nodes.
    layer_count = count_layers()
    position_x = -500
    for i in range(layer_count, 0, -1):
        layer_group_node = active_material.node_tree.nodes.get(str(i - 1))
        if layer_group_node:
            layer_group_node.width = 300
            layer_group_node.location = (position_x, 0)
            position_x -= 500

    # Organize blur noise.
    blur_noise = get_material_layer_node('BLUR_NOISE')
    if blur_noise:
        blur_node_y = 0
        layer_node = active_material.node_tree.nodes.get('0')
        if layer_node:
            blur_node_y = layer_node.height * -6
        blur_noise.location = (position_x, 0 + blur_node_y)

    debug_logging.log("Organized layer group nodes.")

def refresh_layer_stack(reason="", scene=None):
    '''Clears, and then reads the active material, to sync the number of layers in the user interface with the number of layers that exist within the material node tree.'''
    if scene:
        layers = scene.matlayer_layers
    else:
        layers = bpy.context.scene.matlayer_layers
    
    # Clear all layers.
    layers.clear()

    # Do not add material slots if there is no active object.
    if bpy.context.active_object != None:

        # Add a material slot for each material layer detected in the active material.
        layer_count = count_layers()
        for layer in range(0, layer_count):
            add_material_layer_slot()

        # Reset the layer index if it's out of range.
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        if selected_layer_index > len(layers) - 1 or selected_layer_index < 0:
            bpy.context.scene.matlayer_layer_stack.selected_layer_index = 0

    if reason != "":
        debug_logging.log("Refreshed layer stack due to: " + reason, sub_process=True)

def link_layer_group_nodes(self):
    '''Connects all layer group nodes to other existing group nodes, and the principled BSDF shader.'''

    if bau.verify_material_operation_context(self) == False:
        return

    shader_info = bpy.context.scene.matlayer_shader_info
    active_material = bpy.context.active_object.active_material
    node_tree = active_material.node_tree

    # Don't attempt to link layer group nodes if there are no layers.
    layer_count = count_layers()
    if layer_count <= 0:
        return

    # Disconnect all layer group nodes (don't disconnect masks).
    for i in range(0, layer_count):
        layer_node = get_material_layer_node('LAYER', i)
        if layer_node:
            for input in layer_node.inputs:
                if input.name != 'Layer Mask' and input.name != 'Blur Noise':
                    for link in input.links:
                        node_tree.links.remove(link)
            for output in layer_node.outputs:
                for link in output.links:
                    node_tree.links.remove(link)

    # Re-connect all (non-muted / active) layer group nodes.
    for i in range(0, layer_count):
        layer_node = get_material_layer_node('LAYER', i)
        if bau.get_node_active(layer_node):
            next_layer_index = i + 1
            next_layer_node = get_material_layer_node('LAYER', next_layer_index)
            if next_layer_node:
                while not bau.get_node_active(next_layer_node) and next_layer_index <= layer_count - 1:
                    next_layer_index += 1
                    next_layer_node = get_material_layer_node('LAYER', next_layer_index)

            if next_layer_node:
                if bau.get_node_active(next_layer_node):
                    for channel in shader_info.material_channels:
                        output_socket = layer_node.outputs.get(channel.name)
                        input_socket = next_layer_node.inputs.get(channel.name)
                        if output_socket and input_socket:
                            node_tree.links.new(output_socket, input_socket)

    # Connect the last (non-muted / active) layer node to the principled BSDF.
    shader_node = active_material.node_tree.nodes.get('SHADER_NODE')

    last_layer_node_index = layer_count - 1
    last_layer_node = get_material_layer_node('LAYER', last_layer_node_index)
    if last_layer_node:
        while not bau.get_node_active(last_layer_node) and last_layer_node_index >= 0:
            last_layer_node = get_material_layer_node('LAYER', last_layer_node_index)
            last_layer_node_index -= 1

    if last_layer_node:
        if bau.get_node_active(last_layer_node):
            
            for channel in shader_info.material_channels:

                # Only connect active material channels.
                if not tss.get_material_channel_active(channel.name):
                    continue

                output_socket = last_layer_node.outputs.get(channel.name)
                input_socket = shader_node.inputs.get(channel.name)
                if output_socket and input_socket:
                    node_tree.links.new(output_socket, input_socket)
    
    debug_logging.log("Linked layer group nodes.")

def link_material_channel_noise_blur(node_tree, layer_node):
    '''Links the blur noise texture to the layer input to allow it to apply blur filters to material channels.'''
    blur_noise_node = get_material_layer_node('BLUR_NOISE')
    if blur_noise_node:
        node_tree.links.new(blur_noise_node.outputs[1], layer_node.inputs.get("Blur Noise"))
    else:
        debug_logging.log("No blur noise texture node.", message_type='ERROR')

def reindex_layer_nodes(change_made, affected_layer_index):
    '''Reindexes layer group nodes to keep them properly indexed. This should be called after a change is made that effects the layer stack order such as adding, duplicating, deleting, or moving a material layer on the layer stack.'''
    match change_made:
        case 'ADDED_LAYER':
            # Increase the layer index for all layer group nodes, their node trees, and their masks that exist above the affected layer.
            layer_count = len(bpy.context.scene.matlayer_layers)
            for i in range(layer_count, affected_layer_index, -1):
                layer_node = get_material_layer_node('LAYER', i - 1)
                if layer_node:
                    layer_node.name = str(int(layer_node.name) + 1)
                    material_name = parse_material_name(layer_node.node_tree.name)
                    layer_index = parse_layer_index(layer_node.node_tree.name)
                    layer_node.node_tree.name = format_layer_group_node_name(material_name, layer_index + 1)
                    layer_mask_count = layer_masks.count_masks(i - 1)
                    for c in range(layer_mask_count, 0, -1):
                        mask_node = layer_masks.get_mask_node('MASK', i - 1, c - 1)
                        if mask_node:
                            mask_node.name = layer_masks.format_mask_name(i, c - 1)
                            mask_node.node_tree.name = mask_node.name

            new_layer_node = get_material_layer_node('LAYER', affected_layer_index, get_changed=True)
            if new_layer_node:
                new_layer_node.name = str(affected_layer_index)
                material_name = parse_material_name(new_layer_node.node_tree.name)
                new_layer_node.node_tree.name = format_layer_group_node_name(material_name, affected_layer_index)

        case 'DELETED_LAYER':
            # Reduce the layer index for all layer group nodes, their nodes trees, and their masks that exist above the affected layer.
            layer_count = len(bpy.context.scene.matlayer_layers)
            for i in range(affected_layer_index + 1, layer_count):
                layer_node = get_material_layer_node('LAYER', i)
                layer_node.name = str(int(layer_node.name) - 1)
                material_name = parse_material_name(layer_node.node_tree.name)
                layer_index = parse_layer_index(layer_node.node_tree.name)
                layer_node.node_tree.name = format_layer_group_node_name(material_name, layer_index - 1)
                layer_mask_count = layer_masks.count_masks(i)
                for c in range(0, layer_mask_count):
                    mask_node = layer_masks.get_mask_node('MASK', i, c)
                    if mask_node:
                        mask_node.name = layer_masks.format_mask_name(i - 1, c)
                        mask_node.node_tree.name = mask_node.name

    debug_logging.log("Re-indexed material layers.")

def apply_mesh_maps():
    '''Searches for all mesh map texture nodes in the node tree and applies mesh maps if they exist.'''
    # Apply baked mesh maps to all group nodes used as masks for all material layers.
    layers = bpy.context.scene.matlayer_layers
    for layer_index in range(0, len(layers)):
        mask_count = layer_masks.count_masks(layer_index)
        for mask_index in range(0, mask_count):
            for mesh_map_type in mesh_map_baking.MESH_MAP_TYPES:
                mask_node = layer_masks.get_mask_node('MASK', layer_index, mask_index)
                mesh_map_node = mask_node.node_tree.nodes.get(mesh_map_type)
                if mesh_map_node:
                    if mesh_map_node.bl_static_type == 'TEX_IMAGE':
                        mesh_map_node.image = mesh_map_baking.get_meshmap_image(bpy.context.active_object.name, mesh_map_type)

    debug_logging.log("Applied baked mesh maps.")

def relink_material_channel(relink_material_channel_name="", original_output_channel='', unlink_projection=False):
    '''Relinks projection nodes to material channels based on the current projection node tree being used.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node_tree = get_layer_node_tree(selected_layer_index)
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
    group_input_node = get_material_layer_node('GROUP_INPUT', selected_layer_index)
    
    # Unlink and relink projection for nodes if requested.
    if unlink_projection:
        bau.unlink_node(projection_node, layer_node_tree, unlink_inputs=False, unlink_outputs=True)

    # Relink projection for all material channels unless a specific material channel is specified.
    static_matchannel_name = bau.format_static_matchannel_name(relink_material_channel_name)
    shader_info = bpy.context.scene.matlayer_shader_info
    for channel in shader_info.material_channels:

        # If the material channel is using a blur filter, connect the projection and blur node.
        blur_node = get_material_layer_node('BLUR', selected_layer_index, channel.name)
        projection_output_node = projection_node
        if blur_node:
            projection_output_node = blur_node
            match projection_node.node_tree.name:
                case 'ML_TriplanarProjection':
                    layer_node_tree.links.new(projection_node.outputs.get('X'), blur_node.inputs.get('X'))
                    layer_node_tree.links.new(projection_node.outputs.get('Y'), blur_node.inputs.get('Y'))
                    layer_node_tree.links.new(projection_node.outputs.get('Z'), blur_node.inputs.get('Z'))
                case _:
                    layer_node_tree.links.new(projection_node.outputs[0], blur_node.inputs.get('Projection'))
            layer_node_tree.links.new(group_input_node.outputs.get('Blur Noise'), blur_node.inputs.get('Blur Noise'))

        if static_matchannel_name == "" or static_matchannel_name == bau.format_static_matchannel_name(channel.name):

            # Remember the original output channel of the material channel...
            # so it can be properly set after relinking projection.
            if original_output_channel == '':
                original_output_channel = get_material_channel_crgba_output(channel.name)

            # Relink the material channel projection node tree name...
            match projection_node.node_tree.name:
                case 'ML_TriplanarProjection':
                    value_node = get_material_layer_node('VALUE', selected_layer_index, channel.name, node_number=1)
                    triplanar_blend_node = get_material_layer_node('TRIPLANAR_BLEND', selected_layer_index, channel.name)

                    # If there is no triplanar blend node, this projection method can't be linked properly, abort.
                    if triplanar_blend_node:
                        bau.unlink_node(triplanar_blend_node, layer_node_tree, unlink_inputs=True, unlink_outputs=True)
                    else:
                        debug_logging.log("Triplanar blend node missing, can't relink triplanar hex grid projection.", message_type='ERROR')
                        return

                    # Link projection nodes when image textures are used as the material channel value.
                    if value_node.bl_static_type == 'TEX_IMAGE':
                        for i in range(0, 3):
                            value_node = get_material_layer_node('VALUE', selected_layer_index, channel.name, node_number=i + 1)
                            layer_node_tree.links.new(projection_output_node.outputs[i], value_node.inputs[0])

                            # Link triplanar blending nodes.
                            layer_node_tree.links.new(value_node.outputs.get('Color'), triplanar_blend_node.inputs[i])
                            layer_node_tree.links.new(value_node.outputs.get('Alpha'), triplanar_blend_node.inputs[i + 3])
                            layer_node_tree.links.new(projection_node.outputs.get('AxisMask'), triplanar_blend_node.inputs.get('AxisMask'))
                            if channel.name == 'NORMAL':
                                layer_node_tree.links.new(projection_node.outputs.get('Rotation'), triplanar_blend_node.inputs.get('Rotation'))
                                layer_node_tree.links.new(projection_node.outputs.get('SignedGeometryNormals'), triplanar_blend_node.inputs.get('SignedGeometryNormals'))

                    # Link the triplanar projection for custom group nodes with inputs that having matching names with projection node outputs.
                    else:
                        for input in TRIPLANAR_PROJECTION_INPUTS:
                            if value_node.inputs.get(input) and projection_node.outputs.get(input):
                                layer_node_tree.links.new(projection_node.outputs.get(input), value_node.inputs.get(input))

                case 'ML_TriplanarHexGridProjection':
                    value_node = get_material_layer_node('VALUE', selected_layer_index, channel.name, node_number=1)
                    triplanar_blend_node = get_material_layer_node('TRIPLANAR_BLEND', selected_layer_index, channel.name)

                    # If there is no triplanar blend node, this projection method can't be linked properly, abort.
                    if triplanar_blend_node:
                        bau.unlink_node(triplanar_blend_node, layer_node_tree, unlink_inputs=True, unlink_outputs=True)
                    else:
                        debug_logging.log("Triplanar blend node missing, can't relink triplanar hex grid projection.", message_type='ERROR')
                        return
                    
                    # Only image textures need to have projection linked.
                    # Link projection nodes when image textures are used as the material channel value.
                    if value_node.bl_static_type == 'TEX_IMAGE':

                        # Link X Hex Grid
                        for i in range(1, 4):
                            value_node = get_material_layer_node('VALUE', selected_layer_index, channel.name, node_number=i)
                            if value_node:
                                layer_node_tree.links.new(projection_output_node.outputs.get("X Grid {0}".format(i)), value_node.inputs[0])
                                layer_node_tree.links.new(projection_output_node.outputs.get("X Grid Mask {0}".format(i)), triplanar_blend_node.inputs.get("X Grid Mask {0}".format(i)))
                                layer_node_tree.links.new(value_node.outputs[0], triplanar_blend_node.inputs.get("X Grid Color {0}".format(i)))
                                layer_node_tree.links.new(value_node.outputs[1], triplanar_blend_node.inputs.get("X Grid Alpha {0}".format(i)))
                            else:
                                debug_logging.log(
                                    "Missing texture sample {0} for triplanar hex grid projection.".format(i),
                                    message_type='ERROR'
                                )
                        
                        # Link Y Hex Grid
                        for i in range(1, 4):
                            value_node = get_material_layer_node('VALUE', selected_layer_index, channel.name, node_number=i + 3)
                            if value_node:
                                layer_node_tree.links.new(projection_output_node.outputs.get("Y Grid {0}".format(i)), value_node.inputs[0])
                                layer_node_tree.links.new(projection_output_node.outputs.get("Y Grid Mask {0}".format(i)), triplanar_blend_node.inputs.get("Y Grid Mask {0}".format(i)))
                                layer_node_tree.links.new(value_node.outputs[0], triplanar_blend_node.inputs.get("Y Grid Color {0}".format(i)))
                                layer_node_tree.links.new(value_node.outputs[1], triplanar_blend_node.inputs.get("Y Grid Alpha {0}".format(i)))
                            else:
                                debug_logging.log(
                                    "Missing texture sample {0} for triplanar hex grid projection.".format(i),
                                    message_type='ERROR'
                                )
                        
                        # Link Z Hex Grid
                        for i in range(1, 4):
                            value_node = get_material_layer_node('VALUE', selected_layer_index, channel.name, node_number=i + 6)
                            if value_node:
                                layer_node_tree.links.new(projection_output_node.outputs.get("Z Grid {0}".format(i)), value_node.inputs[0])
                                layer_node_tree.links.new(projection_output_node.outputs.get("Z Grid Mask {0}".format(i)), triplanar_blend_node.inputs.get("Z Grid Mask {0}".format(i)))
                                layer_node_tree.links.new(value_node.outputs[0], triplanar_blend_node.inputs.get("Z Grid Color {0}".format(i)))
                                layer_node_tree.links.new(value_node.outputs[1], triplanar_blend_node.inputs.get("Z Grid Alpha {0}".format(i)))
                            else:
                                debug_logging.log(
                                    "Missing texture sample {0} for triplanar hex grid projection.".format(i),
                                    message_type='ERROR'
                                )
                        
                        # Link triplanar blending node.
                        layer_node_tree.links.new(projection_node.outputs.get('AxisMask'), triplanar_blend_node.inputs.get('AxisMask'))

                case _:
                    value_node = get_material_layer_node('VALUE', selected_layer_index, channel.name)
                    mix_image_alpha_node = get_material_layer_node('MIX_IMAGE_ALPHA', selected_layer_index, channel.name)
                    
                    match value_node.bl_static_type:
                        case 'TEX_IMAGE':
                            if value_node.bl_static_type == 'TEX_IMAGE':
                                layer_node_tree.links.new(projection_output_node.outputs[0], value_node.inputs[0])
                                layer_node_tree.links.new(value_node.outputs.get('Alpha'), mix_image_alpha_node.inputs[1])

                        case 'GROUP':
                            if value_node.bl_static_type == 'GROUP':
                                if not value_node.node_tree.name.startswith("ML_Default"):
                                    layer_node_tree.links.new(projection_node.outputs[0], value_node.inputs[0])

            set_material_channel_crgba_output(channel.name, original_output_channel, selected_layer_index)

def delete_value_nodes(material_channel_name, selected_layer_index, layer_node_tree):
    '''Deletes nodes used for triplanar texture sampling and blending for the specified material channel.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node_tree = get_layer_node_tree(selected_layer_index)

    # The max texture sample nodes that can exist is 9, for triplanar hex grid projection.
    # Remove all value / texture sample nodes.
    for i in range(0, 9):
        texture_sample_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, i + 1)
        if texture_sample_node:
            layer_node_tree.nodes.remove(texture_sample_node)

    # Delete triplanar blend node if one exists.
    triplanar_blend_node = get_material_layer_node('TRIPLANAR_BLEND', selected_layer_index, material_channel_name)
    if triplanar_blend_node:
        layer_node_tree.nodes.remove(triplanar_blend_node)

def set_matchannel_projection(material_channel_name, projection_method, set_texture_node=False):
    '''Changes the projection nodes for the specified material channel to match the specified projection method.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node_tree = get_layer_node_tree(selected_layer_index)
    value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, 1)
    static_channel_name = bau.format_static_matchannel_name(material_channel_name)
    frame = layer_node_tree.nodes.get(static_channel_name)

    # If a blur node exists for the material channel, update it to match the specified projection method.
    blur_node = get_material_layer_node('BLUR', selected_layer_index, material_channel_name)
    if blur_node:
        bau.unlink_node(blur_node, layer_node_tree, unlink_inputs=True, unlink_outputs=True)
        match projection_method:
            case 'TRIPLANAR':
                blur_node.node_tree = bau.append_group_node('ML_TriplanarBlur')
            case _:
                blur_node.node_tree = bau.append_group_node('ML_ProjectionBlur')

    # Texture nodes are the only nodes that require a specific projection node setup, ignore other node types.
    # If set_texture_node is true, the material channel value node will be replaced with a texture node, regardless of it's original node type.
    if value_node.bl_static_type == 'TEX_IMAGE' or set_texture_node:
        # Remember settings from the original texture sample nodes.
        value_node.parent = None
        original_node_location = value_node.location.copy()
        original_image = None
        original_interpolation = 'Linear'
        if value_node.bl_static_type == 'TEX_IMAGE':
            original_image = value_node.image
            original_interpolation = value_node.interpolation

        # Delete original value nodes.
        delete_value_nodes(material_channel_name, selected_layer_index, layer_node_tree)

        # Add new texture nodes based on the projection method.
        location_x = original_node_location[0]
        location_y = original_node_location[1]
        sample_count = PROJECTION_TEXTURE_SAMPLE_COUNTS[projection_method]
        for i in range(0, sample_count):
            texture_node = layer_node_tree.nodes.new('ShaderNodeTexImage')
            texture_node.name = format_material_channel_node_name(material_channel_name, 'VALUE', node_index=i + 1)
            texture_node.label = texture_node.name
            texture_node.hide = True
            texture_node.width = 300
            texture_node.location = (location_x, location_y)
            texture_node.parent = frame
            texture_node.image = original_image
            texture_node.interpolation = original_interpolation
            location_y -= 50

        # For decal projection, texture extension must be 'CLIP'.
        if projection_method == 'DECAL':
            texture_node.extension = 'CLIP'

        # Add texture sample blending modes if required.
        triplanar_blend_node = None
        match projection_method:
            case 'TRIPLANAR':
                triplanar_blend_node = layer_node_tree.nodes.new('ShaderNodeGroup')
                if static_channel_name == 'NORMAL':
                    triplanar_blend_node.node_tree = bau.append_group_node("ML_TriplanarNormalsBlend")
                else:
                    triplanar_blend_node.node_tree = bau.append_group_node("ML_TriplanarBlend")

            case 'TRIPLANAR_HEX_GRID':
                triplanar_blend_node = layer_node_tree.nodes.new('ShaderNodeGroup')
                if static_channel_name == 'NORMAL':
                    triplanar_blend_node.node_tree = bau.append_group_node("ML_TriplanarHexGridBlend")
                else:
                    triplanar_blend_node.node_tree = bau.append_group_node("ML_TriplanarHexGridBlend")

        if triplanar_blend_node:
            triplanar_blend_node.name = format_material_channel_node_name(static_channel_name, 'TRIPLANAR_BLEND')
            triplanar_blend_node.label = triplanar_blend_node.name
            triplanar_blend_node.width = 300
            triplanar_blend_node.hide = True
            triplanar_blend_node.location = (location_x, location_y)
            triplanar_blend_node.parent = frame
        
        # Connect texture sample and blending nodes for material channels.
        relink_material_channel(material_channel_name)

def replace_material_channel_node(material_channel_name, node_type):
    '''Replaces the existing material channel node with a new node of the given type.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node_tree = get_layer_node_tree(selected_layer_index)
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
    value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name)
    static_matchannel_name = bau.format_static_matchannel_name(material_channel_name)
    node_socket_name = shaders.get_shader_channel_socket_name(material_channel_name)

    match node_type:
        case 'GROUP':
            value_node.parent = None
            original_node_location = value_node.location.copy()

            # Remove the old nodes.
            delete_value_nodes(static_matchannel_name, selected_layer_index, layer_node_tree)

            # Replace the material channel value nodes with a group node.
            new_node = layer_node_tree.nodes.new('ShaderNodeGroup')
            new_node.name = format_material_channel_node_name(static_matchannel_name, "VALUE", node_index=1)
            new_node.label = new_node.name
            new_node.width = 300
            new_node.location = original_node_location

            # Frame the new node.
            frame = layer_node_tree.nodes.get(static_matchannel_name)
            new_node.parent = frame

            # TODO: IMPORTANT! If the default group node doesn't exist, create one!
            # Apply the default group node for the specified channel.
            default_node_tree_name = "ML_Default{0}".format(node_socket_name.replace(' ', ''))
            default_node_tree = bpy.data.node_groups.get(default_node_tree_name)
            new_node.node_tree = default_node_tree

            # Link the new group node.
            mix_node = get_material_layer_node('MIX', selected_layer_index, static_matchannel_name)
            if mix_node.bl_static_type == 'GROUP':
                layer_node_tree.links.new(new_node.outputs[0], mix_node.inputs[2])
            else:
                layer_node_tree.links.new(new_node.outputs[0], mix_node.inputs[7])

        # Apply projection to texture nodes based on the projection group node name.
        case 'TEXTURE':
            match projection_node.node_tree.name:
                case 'ML_UVProjection':
                    set_matchannel_projection(static_matchannel_name, 'UV', set_texture_node=True)

                case 'ML_TriplanarProjection':
                    set_matchannel_projection(static_matchannel_name, 'TRIPLANAR', set_texture_node=True)

                case 'ML_TriplanarHexGridProjection':
                    set_matchannel_projection(static_matchannel_name, 'TRIPLANAR_HEX_GRID', set_texture_node=True)

                case 'ML_DecalProjection':
                    set_matchannel_projection(static_matchannel_name, 'DECAL', set_texture_node=True)

def set_layer_projection(projection_mode, self):
    '''Changes the projection nodes for the selected layer.'''
    if bau.verify_material_operation_context(self) == False:
        return

    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)

    # If the projection node is somehow missing, throw an error and abort.
    if not projection_node:
        debug_logging.log("Missing layer projection node.", message_type='ERROR')
        return

    # Note that users can't change projection for decal layers, so it's not handled here.
    # Change projection nodes for the material channel.
    update_nodes = False
    match projection_mode:
        case 'UV':
            if projection_node.node_tree.name != "ML_UVProjection":
                projection_node.node_tree = bau.append_group_node("ML_UVProjection")
                update_nodes = True

        case 'TRIPLANAR':
            if projection_node.node_tree.name != "ML_TriplanarProjection":
                projection_node.node_tree = bau.append_group_node("ML_TriplanarProjection")
                update_nodes = True

        case 'TRIPLANAR_HEX_GRID':
            if projection_node.node_tree.name != "ML_TriplanarHexGridProjection":
                projection_node.node_tree = bau.append_group_node("ML_TriplanarHexGridProjection")
                update_nodes = True

    # Set the projection nodes for all channels if a node update is required.
    if update_nodes:
        layer_node = get_material_layer_node('LAYER', selected_layer_index)
        shader_info = bpy.context.scene.matlayer_shader_info
        for channel in shader_info.material_channels:
            channel_nodes_exist = check_channel_nodes_exist(channel.name, layer_node.node_tree)
            if channel_nodes_exist:
                set_matchannel_projection(channel.name, projection_mode)

    # Log the operation for debugging purposes.
    debug_logging.log("Changed layer projection to: {0}".format(projection_mode))

def get_material_channel_crgba_output(material_channel_name):
    '''Returns which Color / RGBA channel output is used for the specified material channel.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    filter_node = get_material_layer_node('FILTER', selected_layer_index, material_channel_name)

    output_channel = ''
    color_input_node = None

    # If the filter node is active, check the connected input in it for the current output channel.
    if bau.get_node_active(filter_node):
        color_input_node = filter_node
        if len(color_input_node.inputs[0].links) > 0:
            output_channel = color_input_node.inputs[0].links[0].from_socket.name.upper()

    # If the filter node isn't active, check the connected input for the mix node for the current output channel.
    else:
        color_input_node = get_material_layer_node('MIX', selected_layer_index, material_channel_name)

        if color_input_node.bl_static_type == 'MIX':
            if len(color_input_node.inputs[7].links) > 0:
                output_channel = color_input_node.inputs[7].links[0].from_socket.name.upper()

        if color_input_node.bl_static_type == 'GROUP':
            if len(color_input_node.inputs[2].links) > 0:
                output_channel = color_input_node.inputs[2].links[0].from_socket.name.upper()

    # If the set output channel is alpha, but the material value node isn't an image
    # which means it can't have an alpha channel, return color instead to avoid errors.
    # This can occur when custom group nodes are used.
    if output_channel == 'ALPHA':
        value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name)
        if value_node.bl_static_type != 'TEX_IMAGE':
            output_channel = 'COLOR'

    # If no output channel is determined, return 'COLOR' as the default output channel.
    if output_channel == '':
        return 'COLOR'
    else:
        return output_channel

def get_material_channel_output_node(material_channel_name, layer_index):
    '''Returns the node that outputs the material channel value.'''
    projection_node = get_material_layer_node('PROJECTION', layer_index)
    value_node = get_material_layer_node('VALUE', layer_index, material_channel_name)
    channel_output_node = None
    if projection_node.node_tree.name == 'ML_TriplanarProjection' or projection_node.node_tree.name == 'ML_TriplanarHexGridProjection':
        if value_node.bl_static_type == 'TEX_IMAGE':
            channel_output_node = get_material_layer_node('TRIPLANAR_BLEND', layer_index, material_channel_name)
        else:
            channel_output_node = value_node
    else:
        if material_channel_name == 'NORMAL':
            fix_normal_rotation_node = get_material_layer_node('FIX_NORMAL_ROTATION', layer_index, material_channel_name)
            if fix_normal_rotation_node:
                channel_output_node = fix_normal_rotation_node
            else:
                debug_logging.log("Fix normal rotation node missing.", message_type='ERROR')
        else:
            channel_output_node = get_material_layer_node('VALUE', layer_index, material_channel_name)
    return channel_output_node

def set_material_channel_crgba_output(material_channel_name, crgba_output, layer_index):
    '''Relinks material channel nodes to output the specified Color / RGBA channel.'''

    # TODO: Use get_material_channel_output_node here.
    # Determine the node that effectively outputs the material channel value.
    projection_node = get_material_layer_node('PROJECTION', layer_index)
    value_node = get_material_layer_node('VALUE', layer_index, material_channel_name)
    channel_output_node = None
    if projection_node.node_tree.name == 'ML_TriplanarProjection' or projection_node.node_tree.name == 'ML_TriplanarHexGridProjection':
        if value_node.bl_static_type == 'TEX_IMAGE':
            channel_output_node = get_material_layer_node('TRIPLANAR_BLEND', layer_index, material_channel_name)
        else:
            channel_output_node = value_node
    else:
        if material_channel_name == 'NORMAL':
            fix_normal_rotation_node = get_material_layer_node('FIX_NORMAL_ROTATION', layer_index, material_channel_name)
            if fix_normal_rotation_node:
                channel_output_node = fix_normal_rotation_node
            else:
                debug_logging.log("Fix normal rotation node missing.", message_type='ERROR')
        else:
            channel_output_node = get_material_layer_node('VALUE', layer_index, material_channel_name)

    # Determine if a separate RGB node is required.
    if crgba_output == 'RED' or crgba_output == 'BLUE' or crgba_output == 'GREEN':
        connect_separate_rgb = True
    else:
        connect_separate_rgb = False
    
    # Determine if connecting to a filter is required.
    connect_filters = False
    filter_count = material_filters.count_filter_nodes(material_channel_name)
    last_filter_node = material_filters.get_filter_node(material_channel_name, filter_count)
    if last_filter_node:
        connect_filters = True

    # Unlink nodes to avoid potential errors when re-linking.
    separate_rgb_node = get_material_layer_node('SEPARATE_RGB', layer_index, material_channel_name)
    layer_node_tree = get_layer_node_tree(layer_index)
    bau.unlink_node(channel_output_node, layer_node_tree, unlink_inputs=False, unlink_outputs=True)
    bau.unlink_node(separate_rgb_node, layer_node_tree, unlink_inputs=True, unlink_outputs=True)

    # Connect the nodes to the mix material channel ndoe based on the material channel and it's settings.
    mix_node = get_material_layer_node('MIX', layer_index, material_channel_name)
    if connect_separate_rgb:
        bau.safe_node_link(channel_output_node.outputs[0], separate_rgb_node.inputs[0], layer_node_tree)
    else:
        if connect_filters:
            first_filter_node = material_filters.get_filter_node(material_channel_name, 1)
            filter_type = material_filters.get_filter_type(first_filter_node)
            filter_input = material_filters.get_filter_info(filter_type, "main_input_socket")
            filter_output = material_filters.get_filter_info(filter_type, "main_output_socket")
            bau.safe_node_link(channel_output_node.outputs[0], first_filter_node.inputs[filter_input], layer_node_tree)
            if mix_node.bl_static_type == 'GROUP':
                bau.safe_node_link(last_filter_node.outputs[filter_output], mix_node.inputs[2], layer_node_tree)
            else:
                bau.safe_node_link(last_filter_node.outputs[filter_output], mix_node.inputs[7], layer_node_tree)
        else:
            if mix_node.bl_static_type == 'GROUP':
                bau.safe_node_link(channel_output_node.outputs[0], mix_node.inputs[2], layer_node_tree)
            else:
                bau.safe_node_link(channel_output_node.outputs[0], mix_node.inputs[7], layer_node_tree)

    # Always link alpha to opacity if the value node is using an image texture node.
    mix_image_alpha_node = get_material_layer_node('MIX_IMAGE_ALPHA', layer_index, material_channel_name)
    if value_node.bl_static_type == 'TEX_IMAGE':
        bau.safe_node_link(channel_output_node.outputs[1], mix_image_alpha_node.inputs[1], layer_node_tree)

def isolate_material_channel(material_channel_name):
    '''Isolates the specified material channel by linking the specified material channel output to an isolate (emission) node.'''
    active_node_tree = bpy.context.active_object.active_material.node_tree
    isolate_node = get_isolate_node()
    material_output = active_node_tree.nodes.get('MATERIAL_OUTPUT')

    output_socket_name = shaders.get_shader_channel_socket_name(material_channel_name)
    total_layers = count_layers(bpy.context.active_object.active_material)
    for i in range(total_layers, 0, -1):
        layer_node = get_material_layer_node('LAYER', i - 1)
        if bau.get_node_active(layer_node):
            bau.safe_node_link(layer_node.outputs.get(output_socket_name), isolate_node.inputs[0], active_node_tree)
            break
    
    active_node_tree.links.new(isolate_node.outputs[0], material_output.inputs[0])

def show_layer():
    '''Removes material channel or mask isolation if they are applied by re-linking the shader node to the material output node.'''
    active_object_attribute = getattr(bpy.context, "active_object", None)
    if not active_object_attribute:
        return
    
    if not bpy.context.active_object:
        return
    
    if not bpy.context.active_object.active_material:
        return

    active_node_tree = bpy.context.active_object.active_material.node_tree
    if not active_node_tree:
        return
    
    # Delete the isolate node if it exists.
    delete_isolate_node()

    # Re-link the shader node.
    material_output = active_node_tree.nodes.get('MATERIAL_OUTPUT')
    principled_bsdf = active_node_tree.nodes.get('SHADER_NODE')
    active_node_tree.links.new(principled_bsdf.outputs[0], material_output.inputs[0])

def toggle_image_alpha_blending(material_channel_name):
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    image_alpha_node = get_material_layer_node('MIX_IMAGE_ALPHA', selected_layer_index, material_channel_name)
    if image_alpha_node.mute:
        image_alpha_node.mute = False
    else:
        image_alpha_node.mute = True

def get_layer_blending_mode(layer_index, material_channel_name=''):
    '''Returns the current blending mode for the layer at the specified index.'''
    # If there is no specified material channel, use the current selected on from the layer stack.
    if material_channel_name == '':
        material_channel_name = bpy.context.scene.matlayer_layer_stack.selected_material_channel

    mix_node = get_material_layer_node('MIX', layer_index, material_channel_name)
    match mix_node.bl_static_type:
        case 'MIX':
            return mix_node.blend_type
        
        case 'GROUP':
            if mix_node.node_tree.name == 'ML_WhiteoutNormalMapMix':
                return 'NORMAL_MAP_COMBINE'
            
            if mix_node.node_tree.name == 'ML_ReorientedNormalMapMix':
                return 'NORMAL_MAP_DETAIL'
    return 'ERROR'

def set_layer_blending_mode(layer_index, blending_mode, material_channel_name='COLOR'):
    '''Sets the blending mode for the layer at the specified index.'''
    layer_node_tree = get_layer_node_tree(layer_index)
    original_mix_node = get_material_layer_node('MIX', layer_index, material_channel_name)
    static_node_channel_name = bau.format_static_matchannel_name(material_channel_name)
    original_output_channel = get_material_channel_crgba_output(material_channel_name)

    # Remember the layers original mix node and it's location.
    mix_node = original_mix_node
    original_node_location = copy.copy(mix_node.location)

    # For setting custom normal map layer blender modes unique to this add-on,
    # Set the layers mix node to a group node with the custom group node mix calculation.
    if blending_mode == 'NORMAL_MAP_COMBINE' or blending_mode == 'NORMAL_MAP_DETAIL':
        if original_mix_node.bl_static_type != 'GROUP':
            layer_node_tree.nodes.remove(original_mix_node)
            mix_node = layer_node_tree.nodes.new('ShaderNodeGroup')
        else:
            mix_node = original_mix_node
        if blending_mode == 'NORMAL_MAP_COMBINE':
            mix_node.node_tree = bau.append_group_node('ML_WhiteoutNormalMapMix')
        elif blending_mode == 'NORMAL_MAP_DETAIL':
            mix_node.node_tree = bau.append_group_node('ML_ReorientedNormalMapMix')

    # For setting layer blending modes already available through Blender's mix node,
    # Ensure the layers mix node is using Blender's mix RGB node then set the blending type.
    else:
        if original_mix_node.bl_static_type != 'MIX':
            layer_node_tree.nodes.remove(original_mix_node)
            mix_node = layer_node_tree.nodes.new('ShaderNodeMix')
            mix_node.data_type = 'RGBA'
        mix_node.blend_type = blending_mode
    
    # Reset the layers mix node name and label.
    mix_node.name = "{0}-MIX".format(static_node_channel_name)
    mix_node.label = mix_node.name

    # Reset the layers mix node back to it's original location and size.
    channel_frame = layer_node_tree.nodes.get(static_node_channel_name)
    if channel_frame:
        mix_node.parent = layer_node_tree.nodes.get(static_node_channel_name)
    mix_node.location = original_node_location
    mix_node.width = 300

    # Relink the mix node with layer opacity.
    opacity_node = get_material_layer_node('OPACITY', layer_index, material_channel_name)
    bau.safe_node_link(opacity_node.outputs[0], mix_node.inputs[0], layer_node_tree)

    # Relink the mix node with the channels value node.
    mix_reroute_node = get_material_layer_node('MIX_REROUTE', layer_index, material_channel_name)
    group_output = get_material_layer_node('GROUP_OUTPUT', layer_index)
    if mix_node.bl_static_type == 'GROUP':
        bau.safe_node_link(mix_node.outputs[0], group_output.inputs.get(material_channel_name), layer_node_tree)
        bau.safe_node_link(mix_reroute_node.outputs[0], mix_node.inputs[1], layer_node_tree)
    else:
        bau.safe_node_link(mix_node.outputs[2], group_output.inputs.get(material_channel_name), layer_node_tree)
        bau.safe_node_link(mix_reroute_node.outputs[0], mix_node.inputs[6], layer_node_tree)

    # Relink the material channel of this layer based on the original material output channel.
    set_material_channel_crgba_output(material_channel_name, original_output_channel, layer_index)

def add_bake_texture_nodes():
    '''Adds a bake texture node to all materials in all material slots on the active object.'''

    # Adding a placeholder image to the bake image nodes stops Blender from throwing annoying and incorrect 'no active image' warnings when baking'.
    placeholder_image = bau.create_data_image("ML_Placeholder", image_width=32, image_height=32)

    active_object = bpy.context.active_object
    for material_slot in active_object.material_slots:
        if material_slot.material:
            bake_texture_node = material_slot.material.node_tree.nodes.new('ShaderNodeTexImage')
            bake_texture_node.name = 'BAKE_IMAGE'
            bake_texture_node.label = bake_texture_node.name
            bake_texture_node.image = placeholder_image
            bake_texture_node.select = True
            material_slot.material.node_tree.nodes.active = bake_texture_node

            # Link the export UV map to the bake texture node.
            export_uv_map_node = get_material_layer_node('EXPORT_UV_MAP')
            if export_uv_map_node:
                material_slot.material.node_tree.links.new(export_uv_map_node.outputs[0], bake_texture_node.inputs[0])

                # Select the export UV map, otherwise Blender will still bake to the original UV map.
                export_uv_map_name = export_uv_map_node.uv_map
                export_uv_map_data = active_object.data.uv_layers.get(export_uv_map_name)
                if export_uv_map_data:
                    export_uv_map_data.active = True

def remove_bake_texture_nodes():
    '''Removes image texture nodes for baking from all materials in all material slots on the active object.'''
    placeholder_image = bpy.data.images.get('ML_Placeholder')
    if placeholder_image:
        bpy.data.images.remove(placeholder_image)

    active_object = bpy.context.active_object
    for material_slot in active_object.material_slots:
        if material_slot.material:
            bake_texture_node = material_slot.material.node_tree.nodes.get('BAKE_IMAGE')
            if bake_texture_node:
                material_slot.material.node_tree.nodes.remove(bake_texture_node)

def add_channel_output_sockets(layer_group_node):
    '''Creates color and alpha output sockets for the provided group node if they don't already exist.'''
    if "Channel Color" not in layer_group_node.outputs:
        output_color_socket = layer_group_node.node_tree.interface.new_socket(
            name="Channel Color",
            description="Color output for a material channel",
            in_out='OUTPUT',
            socket_type='NodeSocketColor'
        )
        output_color_socket.default_value = [0.0, 0.0, 0.0, 1.0]

    if "Channel Alpha" not in layer_group_node.outputs:
        output_alpha_socket = layer_group_node.node_tree.interface.new_socket(
            name="Channel Alpha",
            description="Output for material channel alpha",
            in_out='OUTPUT',
            socket_type='NodeSocketFloat'
        )
        output_alpha_socket.subtype = 'FACTOR'
        output_alpha_socket.default_value = 1.0
        output_alpha_socket.min_value = 0.0
        output_alpha_socket.max_value = 1.0

def ensure_image_saved(layer_index, material_channel_name):
    '''Ensures that the image texture in the specified material channel and layer index is either saved to disk, or packed into the saved blend file.'''
    value_node = get_material_layer_node('VALUE', layer_index, material_channel_name)
    if value_node.bl_static_type == 'TEX_IMAGE':
        debug_logging.log("Ensuring layer {0}'s, {1} is saved or packed.".format(layer_index, material_channel_name))

        image = value_node.image
        if image == None:
            debug_logging.log("There's no image for layer {0}'s, {1}.".format(layer_index, material_channel_name))
            return
        
        # If the image is not dirty (an unsaved change has been made), no saving / packing is required.
        if not image.is_dirty:
            debug_logging.log("Image isn't dirty, no saving / packing required.")
            return
        
        # If the image has no data, no saving / packing is required.
        if not image.has_data:
            debug_logging.log("Image has no data, no saving / packing required.")
            return
        
        # If the image has a defined filepath, save it to that filepath.
        if image.filepath != '':
            debug_logging.log("Image has a defined filepath, saving...")
            image.save()
            debug_logging.log("Image saved.")

        # If there is no defined filepath, pack the image in the blend files data.
        else:
            debug_logging.log("Image has no defined filepath, return")
            image.pack()

def get_merge_bake_node():
    '''Returns a node used for merge baking layers. If a merge bake node doesn't exist in the active node tree, one will be created.'''
    active_material = bpy.context.active_object.active_material
    merge_bake_node = active_material.node_tree.nodes.get('MERGE_BAKE_NODE')
    if not merge_bake_node:
        merge_bake_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
        merge_bake_node.name = 'MERGE_BAKE_NODE'
        merge_bake_node.label = merge_bake_node.name
        merge_bake_node.node_tree = bau.append_group_node("ML_MergeBake", never_auto_delete=True)
        merge_bake_node.location = [0.0, 200.0]
        merge_bake_node.width = 250.0
    return merge_bake_node

def delete_merge_bake_node():
    '''Deletes the merge bake node from the active material's node tree, and the merge bake node group from blend data.'''

    # Delete the merge bake node from the active material's node tree.
    active_material = bpy.context.active_object.active_material
    merge_bake_node = active_material.node_tree.nodes.get('MERGE_BAKE_NODE')
    if merge_bake_node:
        active_material.node_tree.nodes.remove(merge_bake_node)

    # Deletes the merge bake node from blend data.
    merge_bake_node_tree = bpy.data.node_groups.get("ML_MergeBake")
    if merge_bake_node_tree:
        bpy.data.node_groups.remove(merge_bake_node_tree, do_unlink=True, do_id_user=True, do_ui_user=True)

def merge_bake_material_channel(material_channel_name):
    '''Triggers a bake for the specified material channel to convert it pixel data.'''
    
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    active_material = bpy.context.active_object.active_material
    selected_layer_node = get_material_layer_node('LAYER', selected_layer_index)
    below_layer_node = get_material_layer_node('LAYER', selected_layer_index - 1)

    # Assign a color for the bake image background based on the material channel being baked.
    static_channel_name = bau.format_static_matchannel_name(material_channel_name)
    if static_channel_name == 'NORMAL':
        background_color = (0.735337, 0.735337, 1.0, 1.0)
        use_alpha = False
    else:
        background_color = (0.0, 0.0, 0.0, 0.0)
        use_alpha = True

    # Create a new image to bake the material channel to.
    bake_image_name = selected_layer_node.label
    bake_image = bau.create_image(
        new_image_name=bake_image_name + "_Merged",
        image_width=tss.get_texture_width(),
        image_height=tss.get_texture_height(),
        base_color=background_color,
        generate_type='BLANK',
        alpha_channel=use_alpha,
        thirty_two_bit=True,
        add_unique_id=False,
        delete_existing=True
    )

    # Add the baking image to the bake texture node.
    material_nodes = bpy.context.active_object.active_material.node_tree.nodes
    image_node = material_nodes.get('BAKE_IMAGE')
    image_node.image = bake_image
    image_node.select = True
    material_nodes.active = image_node
    bau.set_texture_paint_image(bake_image)

    # Create output sockets for the material channel color and it's alpha values
    add_channel_output_sockets(selected_layer_node)
    add_channel_output_sockets(below_layer_node)

    # Link the material channel color and alpha values to their respective group outputs.
    channel_output_node = get_material_channel_output_node(material_channel_name, selected_layer_index)
    opacity_node = get_material_layer_node('OPACITY', selected_layer_index, material_channel_name)
    group_output_node = get_material_layer_node('GROUP_OUTPUT', selected_layer_index)
    selected_layer_node.node_tree.links.new(channel_output_node.outputs[0], group_output_node.inputs.get("Channel Color"))
    selected_layer_node.node_tree.links.new(opacity_node.outputs[0], group_output_node.inputs.get("Channel Alpha"))

    channel_output_node = get_material_channel_output_node(material_channel_name, selected_layer_index - 1)
    opacity_node = get_material_layer_node('OPACITY', selected_layer_index - 1, material_channel_name)
    group_output_node = get_material_layer_node('GROUP_OUTPUT', selected_layer_index - 1)
    below_layer_node.node_tree.links.new(channel_output_node.outputs[0], group_output_node.inputs.get("Channel Color"))
    below_layer_node.node_tree.links.new(opacity_node.outputs[0], group_output_node.inputs.get("Channel Alpha"))

    # Link the material channel color and alpha outputs to the bake node.
    merge_bake_node = get_merge_bake_node()
    active_material.node_tree.links.new(selected_layer_node.outputs.get("Channel Color"), merge_bake_node.inputs.get("Color 2"))
    active_material.node_tree.links.new(selected_layer_node.outputs.get("Channel Alpha"), merge_bake_node.inputs.get("Alpha 2"))
    active_material.node_tree.links.new(below_layer_node.outputs.get("Channel Color"), merge_bake_node.inputs.get("Color 1"))
    active_material.node_tree.links.new(below_layer_node.outputs.get("Channel Alpha"), merge_bake_node.inputs.get("Alpha 1"))

    # Connect the bake node to the material output node.
    material_output_node = get_material_layer_node('MATERIAL_OUTPUT')
    bau.unlink_node(material_output_node, active_material.node_tree, unlink_inputs=True, unlink_outputs=False)
    active_material.node_tree.links.new(merge_bake_node.outputs[0], material_output_node.inputs[0])

    # IMPORTANT: If either material channel being merged is using an image texture,
    # it must be saved, or packed otherwise triggering a bake will erase it's data!
    ensure_image_saved(selected_layer_index, material_channel_name)
    ensure_image_saved(selected_layer_index - 1, material_channel_name)

    # TODO: Account for normal map baking here.
    # Adjust settings, then trigger a baking operation based on the material channel being baked.
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.ops.object.bake('INVOKE_DEFAULT', type='DIFFUSE')

    return bake_image.name

def relink_shader_node():
    '''Relinks the shader node to the material output node.'''
    active_material = bpy.context.active_object.active_material
    material_output_node = get_material_layer_node('MATERIAL_OUTPUT')
    shader_node = active_material.node_tree.nodes.get('SHADER_NODE')
    bau.unlink_node(material_output_node, active_material.node_tree, unlink_inputs=True, unlink_outputs=False)
    active_material.node_tree.links.new(shader_node.outputs[0], material_output_node.inputs[0])


#----------------------------- OPERATORS -----------------------------#


class MATLAYER_layer_stack(PropertyGroup):
    '''Properties for the layer stack.'''
    selected_layer_index: IntProperty(default=-1, description="Selected material layer", update=update_layer_index)
    selected_material_channel: StringProperty(name="Material Channel", description="The currently selected material channel", default='NONE')

class MATLAYER_layers(PropertyGroup):
    # Storing properties in the layer slot data can potentially cause many errors and often more code -
    # - Properties stored in the layer slots must be read from the material node tree when a new active material is selected.
    # - Properties stored in the layer slots must be updated first in the interface, then trigger callback functions to update their associated properties in material nodes.
    # To help avoid the errors above, all properties are stored in the material node tree of created materials (in one way or another) and referenced directly when displayed in the user interface.
    # A placeholder property is kept here so the UI still has a property group to reference to draw the UIList.
    placeholder_property: IntProperty()

class MATLAYER_OT_add_material_channel_nodes(Operator):
    bl_idname = "matlayer.add_material_channel_nodes"
    bl_label = "Add Material Channel Nodes"
    bl_description = "Adds framed material channel nodes for the specified material channel"
    bl_options = {'REGISTER', 'UNDO'}

    material_channel_name: StringProperty(default="ERROR")

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        layer_node = get_material_layer_node('LAYER', selected_layer_index)
        layer_type = get_layer_type()
        add_material_channel_nodes(self.material_channel_name, layer_node.node_tree, layer_type, self)
        organize_material_channel_frames(layer_node.node_tree)
        return {'FINISHED'}

class MATLAYER_OT_delete_material_channel_nodes(Operator):
    bl_idname = "matlayer.delete_material_channel_nodes"
    bl_label = "Delete Material Channel Nodes"
    bl_description = "Deletes all nodes for the specified material channel"
    bl_options = {'REGISTER', 'UNDO'}

    material_channel_name: StringProperty(default="ERROR")
    
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        delete_material_channel_nodes(self.material_channel_name)
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        layer_node = get_material_layer_node('LAYER', selected_layer_index)
        organize_material_channel_frames(layer_node.node_tree)
        return {'FINISHED'}

class MATLAYER_OT_add_material_layer(Operator):
    bl_idname = "matlayer.add_material_layer"
    bl_label = "Add Material Layer"
    bl_description = "Adds a material layer to the active material"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_material_layer('NORMAL', self)
        return {'FINISHED'}

class MATLAYER_OT_add_decal_material_layer(Operator):
    bl_idname = "matlayer.add_decal_material_layer"
    bl_label = "Add Decal Layer"
    bl_description = "Adds a non-destructive layer designed specifically for placing decals (stickers / text). Control the position and scale of the decal using the layers associated decal (empty) object"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_material_layer('DECAL', self)
        return {'FINISHED'}

class MATLAYER_OT_add_image_layer(Operator):
    bl_idname = "matlayer.add_image_layer"
    bl_label = "Add Image Layer"
    bl_description = "Adds a new layer setup that uses only the base color channel. A new image is automatically added to the base color channel. The shader must have a base color channel to add image layers"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_material_layer('IMAGE', self)
        return {'FINISHED'}

class MATLAYER_OT_duplicate_layer(Operator):
    bl_idname = "matlayer.duplicate_layer"
    bl_label = "Duplicate Layer"
    bl_description = "Duplicates the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bau.verify_addon_active_material(context)

    def execute(self, context):
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        duplicate_layer(selected_layer_index, self)
        return {'FINISHED'}

class MATLAYER_OT_delete_layer(Operator):
    bl_idname = "matlayer.delete_layer"
    bl_label = "Delete Layer"
    bl_description = "Deletes the selected material layer from the active material"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bau.verify_addon_active_material(context)

    def execute(self, context):
        delete_layer(self)
        return {'FINISHED'}

class MATLAYER_OT_move_material_layer_up(Operator):
    bl_idname = "matlayer.move_material_layer_up"
    bl_label = "Move Layer Up"
    bl_description = "Moves the material layer up on the layer stack"
    bl_options = {'REGISTER', 'UNDO'}

    direction: StringProperty(default='UP')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bau.verify_addon_active_material(context)

    def execute(self, context):
        move_layer('UP', self)
        return {'FINISHED'}

class MATLAYER_OT_move_material_layer_down(Operator):
    bl_idname = "matlayer.move_material_layer_down"
    bl_label = "Move Layer Down"
    bl_description = "Moves the material layer down on the layer stack"
    bl_options = {'REGISTER', 'UNDO'}

    direction: StringProperty(default='UP')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bau.verify_addon_active_material(context)

    def execute(self, context):
        move_layer('DOWN', self)
        return {'FINISHED'}

class MATLAYER_OT_toggle_material_channel_preview(Operator):
    bl_idname = "matlayer.toggle_material_channel_preview"
    bl_label = "Toggle Material Channel Preview"
    bl_description = "Toggle on / off a preview for the selected material channel"
    bl_options = {'REGISTER', 'UNDO'}

    direction: StringProperty(default='UP')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}

class MATLAYER_OT_toggle_hide_layer(Operator):
    bl_idname = "matlayer.toggle_hide_layer"
    bl_label = "Toggle Hide Layer"
    bl_description = "Hides / Unhides the layer by muting / unmuting the layer group node and triggering a relink of group nodes"
    bl_options = {'REGISTER', 'UNDO'}

    layer_index: IntProperty(default=-1)

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        layer_node = get_material_layer_node('LAYER', self.layer_index)

        if bau.get_node_active(layer_node):
            bau.set_node_active(layer_node, False)
        else:
            bau.set_node_active(layer_node, True)

        link_layer_group_nodes(self)
        return {'FINISHED'}

class MATLAYER_OT_set_layer_projection(Operator):
    bl_idname = "matlayer.set_layer_projection"
    bl_label = "Set Layer Projection"
    bl_description = "Sets the projection mode for the layer to UV projection, which uses the UV layout of the object to project textures used on this material layer"
    bl_options = {'REGISTER', 'UNDO'}

    projection_method: StringProperty(default='UV')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        set_layer_projection(self.projection_method, self)
        return {'FINISHED'}

class MATLAYER_OT_change_material_channel_value_node(Operator):
    bl_idname = "matlayer.change_material_channel_value_node"
    bl_label = "Change Material Channel Node"
    bl_description = "Changes value node representing the provided layer material channel"
    bl_options = {'REGISTER', 'UNDO'}

    material_channel_name: StringProperty(default='COLOR')
    node_type: StringProperty(default='GROUP')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        replace_material_channel_node(self.material_channel_name, node_type=self.node_type)
        return {'FINISHED'}

class MATLAYER_OT_isolate_material_channel(Operator):
    bl_idname = "matlayer.isolate_material_channel"
    bl_label = "Isolate Material Channel"
    bl_description = "Isolates the selected material channel. Select a material layer to de-isolate"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object, or layers.
    @ classmethod
    def poll(cls, context):
        if len(context.scene.matlayer_layers) < 1:
            return False
        else:
            return bau.verify_addon_active_material(context)

    def execute(self, context):
        selected_material_channel = bpy.context.scene.matlayer_layer_stack.selected_material_channel
        isolate_material_channel(selected_material_channel)
        return {'FINISHED'}

class MATLAYER_OT_show_compiled_material(Operator):
    bl_idname = "matlayer.show_compiled_material"
    bl_label = "Show Compiled Material"
    bl_description = "Shows the full compiled material"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object, or layers.
    @ classmethod
    def poll(cls, context):
        if len(context.scene.matlayer_layers) < 1:
            return False
        else:
            return bau.verify_addon_active_material(context)

    def execute(self, context):
        show_layer()
        return {'FINISHED'}    

class MATLAYER_OT_toggle_image_alpha_blending(Operator):
    bl_idname = "matlayer.toggle_image_alpha_blending"
    bl_label = "Toggle Image Alpha Blending"
    bl_description = "Toggles blending the alpha channel of the image node into the layers opacity. Off by default for better shader compilation and viewport performance"
    bl_options = {'REGISTER', 'UNDO'}

    material_channel_name: StringProperty(default='COLOR')

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        toggle_image_alpha_blending(self.material_channel_name)
        return {'FINISHED'}

class MATLAYER_OT_set_material_channel(Operator):
    bl_idname = "matlayer.set_material_channel"
    bl_label = "Set Material Channel"
    bl_description = "Sets the material channel being edited in the layer stack"

    material_channel_name: StringProperty(default="NONE")

    def execute(self, context):
        bpy.context.scene.matlayer_layer_stack.selected_material_channel = self.material_channel_name
        debug_logging.log("Selected material channel set to: {0}".format(self.material_channel_name))
        return {'FINISHED'}

class MATLAYER_OT_set_matchannel_crgba_output(Operator):
    bl_idname = "matlayer.set_material_channel_crgba_output"
    bl_label = "Set Material Channel Output Channel"
    bl_description = "Sets the material channel to use the specified output channel"
    bl_options = {'REGISTER', 'UNDO'}

    output_channel_name: StringProperty(default='COLOR')
    material_channel_name: StringProperty(default='COLOR')

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        set_material_channel_crgba_output(self.material_channel_name, self.output_channel_name, selected_layer_index)
        return {'FINISHED'}

class MATLAYER_OT_set_layer_blending_mode(Operator):
    bl_idname = "matlayer.set_layer_blending_mode"
    bl_label = "Set Layer Blending Mode"
    bl_description = "Sets the blending mode for the layer at the specified index"
    bl_options = {'REGISTER', 'UNDO'}

    layer_index: IntProperty(default=-1)
    blending_mode: StringProperty(default='MIX')

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        material_channel = bpy.context.scene.matlayer_layer_stack.selected_material_channel
        set_layer_blending_mode(self.layer_index, self.blending_mode, material_channel)
        link_layer_group_nodes(self)
        return {'FINISHED'}

class MATLAYER_OT_merge_with_layer_below(Operator):
    bl_idname = "matlayer.merge_with_layer_below"
    bl_label = "Merge With Layer Below"
    bl_description = "Merges the selected layer with the layer below it by converting all material channels to images through a baking operation"
    bl_options = {'REGISTER', 'UNDO'}

    _timer = None
    _bake_texture_index = -1
    _active_material_channels = []
    _original_render_engine_name = ""
    _start_bake_time = 0
    _bake_image_name = ""

    # Users must have an object selected to call this operator.
    @ classmethod
    def poll(cls, context):
        return bau.verify_addon_active_material(context)
    
    def modal(self, context, event):
        if event.type in {'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}
        
        if event.type == 'TIMER':

            # If baking still isn't finished, abort until the next timer event.
            if bpy.app.is_job_running('OBJECT_BAKE'):
                return {'RUNNING_MODAL'}
            
            # If an image was baked, pack it in the blend files data.
            bake_image = bpy.data.images.get(self._bake_image_name)
            if bake_image != None:
                if not bake_image.packed_file:
                    bake_image.pack()
                    debug_logging.log("Baking complete for: {0}".format(self._bake_image_name))

            # Start baking the next material channel.
            if self._bake_texture_index < len(self._active_material_channels) - 1:
                self._bake_texture_index += 1
                self._bake_image_name = ""
                next_material_channel_to_bake = self._active_material_channels[self._bake_texture_index]
                self._bake_image_name = merge_bake_material_channel(next_material_channel_to_bake)
                debug_logging.log("Starting baking to merge {0}.".format(next_material_channel_to_bake))
            
            # Finish if there are no more material channels to bake.
            else:
                self.finish(context)
                return {'FINISHED'}
                
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # If there is no layer below the selected one to merge with, abort.
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        if selected_layer_index - 1 < 0:
            debug_logging.log_status("No layer below to merge with.", self, type='INFO')
            return {'FINISHED'}
        
        # To avoid errors don't start baking if there is somehow already a bake job running.
        if bpy.app.is_job_running('OBJECT_BAKE') == True:
            debug_logging.log_status("Bake job already in process, cancel or wait until the bake is finished before starting another.", self)
            return {'FINISHED'}
        
        # Record the starting time before baking.
        self._start_bake_time = time.time()

        # Pause auto updating for add-on properties, they will cause errors while baking.
        bpy.context.scene.pause_auto_updates = True
        
        # Set the viewport shading mode to 'Material' so users can monitor the baking process.
        bpy.context.space_data.shading.type = 'MATERIAL'

        # Create a list of active material channels that need to be baked.
        shader_info = bpy.context.scene.matlayer_shader_info
        self._active_material_channels = []
        for material_channel in shader_info.material_channels:
            layer_node_tree = get_layer_node_tree(selected_layer_index)
            nodes_exist = check_channel_nodes_exist(material_channel.name, layer_node_tree)
            if nodes_exist and material_channel.name not in self._active_material_channels:
                self._active_material_channels.append(material_channel.name)

        for material_channel in shader_info.material_channels:
            layer_node_tree = get_layer_node_tree(selected_layer_index - 1)
            nodes_exist = check_channel_nodes_exist(material_channel.name, layer_node_tree)
            if nodes_exist and material_channel.name not in self._active_material_channels:
                self._active_material_channels.append(material_channel.name)

        debug_logging.log("Merging active material channels: {0}".format(self._active_material_channels))

        # If there are no material channels to bake, abort.
        if len(self._active_material_channels) <= 0:
            debug_logging.log_status("No active material channels to bake, can't merge layers.", self, type='INFO')
            return {'FINISHED'}
        
        # Add a temporary texture node to the material setup to bake to.
        add_bake_texture_nodes()

        # Remember the original render engine so we can reset it after baking.
        bpy.context.scene.render.engine = 'CYCLES'
        self._original_render_engine_name = bpy.context.scene.render.engine

        # Apply baking settings.
        bpy.context.scene.render.bake.margin = 14
        bpy.context.scene.render.bake.use_selected_to_active = False
        bpy.context.scene.cycles.samples = 32

        # Force save all textures (unsaved textures will be cleared and not bake properly).
        bau.force_save_all_textures()

        # Add a timer to provide periodic timer events.
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)

        # Baking will start automatically when the timer hits the first event.
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        # Remove the modal operator timer.
        if self._timer:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)

        # Remove unnecessary nodes.
        remove_bake_texture_nodes()
        delete_merge_bake_node()

        # Refresh the layer stack.
        refresh_layer_stack()

        # Relink the shader node.
        relink_shader_node()

        # Reset settings.
        bpy.context.scene.render.engine = self._original_render_engine_name
        bpy.context.scene.pause_auto_updates = False

        # Log the user has manually cancelled merging layers.
        debug_logging.log_status("Merging layers was cancelled by the user.", self, type='INFO')

    def finish(self, context):
        # Remove the modal operator timer.
        if self._timer:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)

        # Store the selected layer name.
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        selected_layer_node = get_material_layer_node('LAYER', selected_layer_index)
        layer_name = selected_layer_node.label

        # Delete both layer group nodes.
        delete_layer(self)
        delete_layer(self)

        # Make a new layer and set the selected layers name.
        add_material_layer('NORMAL', self)
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        selected_layer_node = get_material_layer_node('LAYER', selected_layer_index)
        selected_layer_node.label = layer_name

        # Add material channel nodes for each active (merged) material channels.
        for material_channel_name in self._active_material_channels:
            add_material_channel_nodes(
                material_channel_name, 
                selected_layer_node.node_tree, 
                'NORMAL', 
                self, 
                log_in_info_window=True
            )

            # Replace the standard value nodes with image textures,
            # then add the images with the merged pixel data to them.
            replace_material_channel_node(material_channel_name, node_type='TEXTURE')
            merged_image = bpy.data.images.get(layer_name + "_Merged")
            if merged_image:
                value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, node_number=1)
                value_node.image = merged_image

            # Image alpha blending needs to be on to see merged alpha channels.
            toggle_image_alpha_blending(material_channel_name)


        # Relink all layer nodes together.
        link_layer_group_nodes(self)
        show_layer()

        # Select the image in the selected material channel for painting.
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        selected_material_channel = bpy.context.scene.matlayer_layer_stack.selected_material_channel
        value_node = get_material_layer_node('VALUE', selected_layer_index, selected_material_channel)
        if value_node:
            if value_node.bl_static_type == 'TEX_IMAGE':
                bau.set_texture_paint_image(value_node.image)

        # Relink the shader node.
        relink_shader_node()

        # Remove unnecessary nodes.
        remove_bake_texture_nodes()
        delete_merge_bake_node()

        # Reset settings.
        bpy.context.scene.render.engine = self._original_render_engine_name
        bpy.context.scene.pause_auto_updates = False

        # Log the completion of merging layers.
        end_bake_time = time.time()
        total_bake_time = end_bake_time - self._start_bake_time
        debug_logging.log_status("Merging layers completed, total time: {0} seconds.".format(round(total_bake_time), 1), self, 'INFO')