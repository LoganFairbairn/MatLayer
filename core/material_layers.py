# This file contains layer properties and functions for updating layer properties.

import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import IntProperty, EnumProperty, StringProperty
from ..core import layer_masks
from ..core import mesh_map_baking
from ..core import blender_addon_utils
from ..core import debug_logging
from ..core import texture_set_settings as tss
from .. import preferences
import random

MATERIAL_CHANNEL = [
    ("COLOR", "Color", ""), 
    ("SUBSURFACE", "Subsurface", ""),
    ("SUBSURFACE_RADIUS", "Subsurface Radius", ""),
    ("METALLIC", "Metallic", ""),
    ("SPECULAR", "Specular", ""),
    ("SPECULAR-TINT", "Specular Tint", ""),
    ("ROUGHNESS", "Roughness", ""),
    ("EMISSION", "Emission", ""),
    ("NORMAL", "Normal", ""),
    ("HEIGHT", "Height", ""),
    ("AMBIENT-OCCLUSION", "Ambient Occlusion", ""),
    ("ALPHA", "Alpha", ""),
    ("COAT", "Coat", ""),
    ("COAT-ROUGHNESS", "Coat Roughness", ""),
    ("COAT-TINT", "Coat Tint", ""),
    ("COAT-NORMAL", "Coat Normal", ""),
    ("SHEEN", "Sheen", ""),
    ("SHEEN-ROUGHNESS", "Sheen Roughness", ""),
    ("SHEEN-TINT", "Sheen Tint", ""),
    ("DISPLACEMENT", "Displacement", "Displacement")
]

MATERIAL_CHANNEL_LIST = [
    'COLOR',
    'SUBSURFACE',
    'SUBSURFACE-RADIUS',
    'METALLIC',
    'SPECULAR',
    'SPECULAR-TINT',
    'ROUGHNESS',
    'EMISSION',
    'NORMAL',
    'HEIGHT',
    'AMBIENT-OCCLUSION',
    'ALPHA',
    'COAT',
    'COAT-ROUGHNESS',
    'COAT-TINT',
    'COAT-NORMAL',
    'SHEEN',
    'SHEEN-ROUGHNESS',
    'SHEEN-TINT',
    'DISPLACEMENT'
]

TRIPLANAR_PROJECTION_INPUTS = [
    'LeftRight',
    'FrontBack',
    'TopBottom',
    'UnflippedLeftRight',
    'UnflippedFrontBack',
    'UnflippedTopBottom',
    'AxisMask',
    'Rotation',
    'SignedGeometryNormals'
]


#----------------------------- UPDATING PROPERTIES -----------------------------#


def update_layer_index(self, context):
    '''Updates properties and user interface when a new layer is selected.'''

    # Check that the active object attribute exists within the current Blender context.
    active_object_attribute = getattr(bpy.context, "active_object", None)
    if active_object_attribute == None:
        return
    
    show_layer()
    layer_masks.refresh_mask_slots()

    # Select the image for texture painting.
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    selected_material_channel = bpy.context.scene.matlayer_layer_stack.selected_material_channel
    value_node = get_material_layer_node('VALUE', selected_layer_index, selected_material_channel)
    if value_node:
        if value_node.bl_static_type == 'TEX_IMAGE':
            if value_node.image != None:
                blender_addon_utils.set_texture_paint_image(value_node.image)
    
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

def sync_triplanar_settings():
    '''Syncs triplanar texture settings to match the first texture sample (only if triplanar layer projection is being used).'''
    if blender_addon_utils.verify_material_operation_context(display_message=False) == False:
        return

    # Sync triplanar texture samples for all material channels.
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
    if projection_node:
        if projection_node.node_tree.name == 'ML_TriplanarProjection':
            for material_channel_name in MATERIAL_CHANNEL_LIST:
                value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, node_number=1)
                if value_node:
                    if value_node.bl_static_type == 'TEX_IMAGE':
                        texture_sample_2 = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, node_number=2)
                        texture_sample_3 = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, node_number=3)
                        
                        # Running these additional if checks to avoid accidentally triggering shader re-compiling by changing an image to the same image.
                        if texture_sample_2:
                            if texture_sample_2.image != value_node.image:
                                texture_sample_2.image = value_node.image

                            if texture_sample_2.interpolation != value_node.interpolation:
                                texture_sample_2.interpolation = value_node.interpolation

                        if texture_sample_3:
                            if texture_sample_3.image != value_node.image:
                                texture_sample_3.image = value_node.image

                            if texture_sample_3.interpolation != value_node.interpolation:
                                texture_sample_3.interpolation = value_node.interpolation

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

def get_shorthand_material_channel_name(material_channel_name):
    '''Returns the short-hand version of the provided material channel name.'''
    match material_channel_name:
        case 'COLOR':
            return 'COLOR'
        case 'BASE-COLOR':
            return 'COLOR'
        case 'SUBSURFACE':
            return 'SUBSURF'
        case 'SUBSURFACE-RADIUS':
            return 'SS-RADIUS'
        case 'METALLIC':
            return 'METAL'
        case 'SPECULAR':
            return 'SPEC'
        case 'SPECULAR-TINT':
            return 'SPEC-TINT'
        case 'ROUGHNESS':
            return 'ROUGH'
        case 'EMISSION':
            return 'EMIT'
        case 'NORMAL':
            return 'NORMAL'
        case 'HEIGHT':
            return 'HEIGHT'
        case 'AMBIENT-OCCLUSION':
            return 'AO'
        case 'ALPHA':
            return 'ALPHA'
        case 'COAT':
            return 'COAT'
        case 'COAT-ROUGHNESS':
            return 'COAT-ROUGH'
        case 'COAT-TINT':
            return 'COAT-TINT'
        case 'COAT-NORMAL':
            return 'COAT-NORM'
        case 'SHEEN':
            return 'SHEEN'
        case 'SHEEN-ROUGHNESS':
            return 'SHEEN-ROUGH'
        case 'SHEEN-TINT':
            return 'SHEEN-TINT'
        case 'DISPLACEMENT':
            return 'DISPLACE'
        case _:
            return material_channel_name

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

def format_layer_group_node_name(material_name, layer_index):
    '''Properly formats the layer group node names for this add-on.'''
    return "{0}_{1}".format(material_name, layer_index)

def get_layer_node_tree(layer_index):
    '''Returns the node group for the specified layer (from Blender data) if it exists'''
    
    if not bpy.context.active_object:
        return None
    
    if not bpy.context.active_object.active_material:
        return None
    
    layer_group_name = format_layer_group_node_name(bpy.context.active_object.active_material.name, layer_index)

    return bpy.data.node_groups.get(layer_group_name)

def get_material_layer_node(layer_node_name, layer_index=0, material_channel_name='COLOR', node_number=1, get_changed=False):
    '''Returns the desired material node if it exists. Supply the material channel name to get nodes specific to material channels.'''

    # This function exists to allow easy access to premade nodes from a node tree appended from an asset blend file.
    # Using specified names for nodes allows consistent access to specific nodes accross languages in Blender (as Blender's auto translate feature will translate default node names).
    # This function also has the benefit of being able to return nodes in sub-node groups, if required.

    if not getattr(bpy.context, 'active_object'):
        debug_logging.log("Context has no attribute 'active_object'.")
        return

    if bpy.context.active_object == None:
        return
    
    active_material = bpy.context.active_object.active_material
    if active_material == None:
        return
    
    layer_group_node_name = format_layer_group_node_name(active_material.name, layer_index)

    match layer_node_name:
        case 'LAYER':
            if get_changed:
                return active_material.node_tree.nodes.get(str(layer_index) + "~")
            else:
                return active_material.node_tree.nodes.get(str(layer_index))
            
        case 'NORMAL_HEIGHT_MIX':
            return active_material.node_tree.nodes.get('NORMAL_HEIGHT_MIX')
        
        case 'BASE_NORMALS':
            return active_material.node_tree.nodes.get('BASE_NORMALS')

        case 'BASE_NORMALS_MIX':
            return active_material.node_tree.nodes.get('BASE_NORMALS_MIX')
        
        case 'DISPLACEMENT':
            return active_material.node_tree.nodes.get('DISPLACEMENT')
        
        case 'MATERIAL_OUTPUT':
            return active_material.node_tree.nodes.get('MATERIAL_OUTPUT')
        
        case 'GLOBAL':
            global_channel_toggle_node_name = "GLOBAL_{0}_TOGGLE".format(material_channel_name)
            return active_material.node_tree.nodes.get(global_channel_toggle_node_name)
        
        case 'EXPORT_UV_MAP':
            return active_material.node_tree.nodes.get('EXPORT_UV_MAP')

        case 'PROJECTION':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("PROJECTION")
            return None
        
        case 'TRIPLANAR_BLEND':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("TRIPLANAR_BLEND_{0}".format(material_channel_name))
            return None

        case 'FIX_NORMAL_ROTATION':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("FIX_NORMAL_ROTATION")
            return None      

        case 'MIX_IMAGE_ALPHA':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("MIX_{0}_IMAGE_ALPHA".format(material_channel_name))
            return None  

        case 'BLUR':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("BLUR")
            return None

        case 'MIX':
            mix_node_name = "{0}_MIX".format(material_channel_name)
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get(mix_node_name)
            return None
        
        case 'OPACITY':
            opacity_node_name = "{0}_OPACITY".format(material_channel_name)
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get(opacity_node_name)
            return None
        
        case 'VALUE':
            value_node_name = "{0}_VALUE_{1}".format(material_channel_name, node_number)
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get(value_node_name)
            return None
        
        case 'FILTER':
            filter_node_name = "{0}_FILTER".format(material_channel_name)
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get(filter_node_name)
            return None
        
        case 'COORDINATES':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                decal_projection_node = node_tree.nodes.get('PROJECTION')
                if decal_projection_node:
                    return decal_projection_node.node_tree.nodes.get('COORDINATES')
            return None

        case 'DECAL_COORDINATES':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get('DECAL_COORDINATES')
            return None

        case 'SEPARATE':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("SEPARATE_{0}".format(material_channel_name))
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
        
        case _:
            debug_logging.log("Invalid material node name passed to get_material_layer_node.")
            return None

def add_material_layer_slot():
    '''Adds a new slot to the material layer stack, and returns the index of the new layer slot.'''
    layers = bpy.context.scene.matlayer_layers
    layer_stack = bpy.context.scene.matlayer_layer_stack

    layer_slot = layers.add()

    # Assign a random, unique number to the layer slot. This allows the layer slot array index to be found using the name of the layer slot as a key.
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

def apply_base_normals():
    '''Applies the base normal map for the active object if one exists, applies a default base normal map if one doesn't.'''
    base_normals_node = get_material_layer_node('BASE_NORMALS')
    if base_normals_node:
        base_normals_image = mesh_map_baking.get_meshmap_image(bpy.context.active_object.name, 'NORMALS')
        if base_normals_image:
            base_normals_node.image = base_normals_image
        else:
            default_normal_image = blender_addon_utils.append_image('DefaultNormal')
            base_normals_node.image = default_normal_image

def create_default_material_setup():
    '''Creates a default material setup for the applied shader.'''

    # Append a blank material setup from the add-on assets blend file.
    blank_material = blender_addon_utils.append_material('BlankMaterialSetup')
    if blank_material:
        blank_node_tree = blank_material.node_tree
        if blank_node_tree:
            shader_info = bpy.context.scene.matlayer_shader_info
            shader_node = blank_node_tree.nodes.get('MATLAYER_SHADER')
            shader_group_node_name = shader_info.group_node_name
            shader_group_node = blender_addon_utils.append_group_node(shader_group_node_name)
            
            # Replace the shader node in the blank material setup.
            if shader_group_node:
                old_node_location = shader_node.location
                old_node_width = shader_node.width
                blank_node_tree.nodes.remove(shader_node)
                new_shader_node = blank_node_tree.nodes.new('ShaderNodeGroup')
                new_shader_node.name = 'MATLAYER_SHADER'
                new_shader_node.label = new_shader_node.name
                new_shader_node.location = old_node_location
                new_shader_node.width = old_node_width
                new_shader_node.node_tree = shader_group_node

                # Re-link the main shader node.
                material_output_node = blank_node_tree.nodes.get('MATERIAL_OUTPUT')
                if material_output_node:
                    blank_node_tree.links.new(new_shader_node.outputs[0], material_output_node.inputs[0])

                normal_height_mix_node = get_material_layer_node('NORMAL_HEIGHT_MIX')
                if normal_height_mix_node:
                    blank_node_tree.links.new(normal_height_mix_node.outputs[0], new_shader_node.inputs.get('Normal'))

            else:
                debug_logging.log("Shader group node {0} doesn't exist.".format(shader_group_node_name))
                return

            # Add global channel toggle nodes for all material channels defined in the shader.
            node_width = 400
            node_x = 300
            node_y = -150
            node_spacing = 40
            for channel in shader_info.material_channels:
                new_channel_toggle_node = blank_node_tree.nodes.new('ShaderNodeValue')
                new_channel_toggle_node.hide = True
                new_channel_toggle_node.name = "GLOBAL_{0}_TOGGLE".format(channel.name)
                new_channel_toggle_node.label = new_channel_toggle_node.name
                new_channel_toggle_node.width = node_width
                new_channel_toggle_node.location[0] = node_x
                new_channel_toggle_node.location[1] = node_y
                node_y -= node_spacing

                if channel.default_active == False:
                    new_channel_toggle_node.mute = True
    
    else:
        debug_logging.log("Missing blank material setup.", message_type='ERROR', sub_process=False)

    return blank_material

def create_default_layer_node(layer_type):
    '''Creates a default setup for a layer node based on shader material channels.'''

    # Create a default node group for the layer, if one exists already, delete it.
    default_node_group_name = "ML_DefaultNodeGroup"
    default_node_group = bpy.data.node_groups.get(default_node_group_name)
    if default_node_group:
        bpy.data.node_groups.remove(default_node_group)
    default_node_group = bpy.data.node_groups.new(default_node_group_name, type='ShaderNodeTree')

    # Add inputs and outputs to the group node for all shader channels.
    shader_info = bpy.context.scene.matlayer_shader_info
    for channel in shader_info.material_channels:
        input_socket = default_node_group.interface.new_socket(
            name=channel.name, 
            description=channel.name, 
            in_out='INPUT', 
            socket_type=channel.socket_type
        )

        output_socket = default_node_group.interface.new_socket(
            name=channel.name,
            description=channel.name,
            in_out='OUTPUT',
            socket_type=channel.socket_type
        )

        match channel.socket_type:
            case 'NodeSocketFloat':
                input_socket.default_value = channel.socket_float_default
                output_socket.default_value = channel.socket_float_default
            case 'NodeSocketColor':
                input_socket.default_value = (channel.socket_color_default[0], channel.socket_color_default[1], channel.socket_color_default[2], 1)
                output_socket.default_value = (channel.socket_color_default[0], channel.socket_color_default[1], channel.socket_color_default[2], 1)
            case 'NodeSocketVector':
                input_socket.default_value = channel.socket_vector_default
                output_socket.default_value = channel.socket_vector_default
    
    # Add a layer mask input.
    default_node_group.interface.new_socket(
        name="LayerMask",
        description="Mask input for the layer",
        in_out='INPUT',
        socket_type='NodeSocketFloat'
    )

    # Add input and output nodes.
    input_node = default_node_group.nodes.new('NodeGroupInput')
    input_node.name = 'GROUP_INPUT'
    input_node.label = input_node.name
    input_node.location[0] = -3000
    input_node.location[1] = 0
    input_node.width = 300

    output_node = default_node_group.nodes.new('NodeGroupOutput')
    output_node.name = 'GROUP_OUTPUT'
    output_node.label = output_node.name
    output_node.location[0] = 0
    output_node.location[1] = 0
    output_node.width = 300

    # Add projection nodes.
    projection_node = default_node_group.nodes.new('ShaderNodeGroup')
    projection_node.name = 'PROJECTION'
    projection_node.label = projection_node.name
    projection_node.location[0] = -3000
    projection_node.location[1] = -200
    projection_node.node_tree = blender_addon_utils.append_group_node('ML_UVProjection')
    projection_node.width = 300

    # TODO: Add nodes for blurring material channels.
    blur_node = default_node_group.nodes.new('ShaderNodeGroup')
    blur_node.name = 'BLUR'
    blur_node.label = blur_node.name
    blur_node.location[0] = -3000
    blur_node.location[1] = -500
    blur_node.width = 300

    # Add framed material channel nodes for values, filtering and mixing.
    frame_x = -1000
    frame_y = 0
    for channel in shader_info.material_channels:
        channel_frame_node = default_node_group.nodes.new('NodeFrame')
        channel_frame_node.name = channel.name
        channel_frame_node.label = channel.name

        # TODO: Create default value group nodes for all shader channels.
        default_value_group_node_name = "ML_Default{0}".format(channel.name)
        default_value_group_node = bpy.data.node_groups.get(default_value_group_node_name)
        if default_value_group_node:
            bpy.data.node_groups.remove(default_value_group_node)
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

        value_node = default_node_group.nodes.new('ShaderNodeGroup')
        value_node.name = "{0}_VALUE_1".format(channel.name)
        value_node.label = value_node.name
        value_node.location[0] = -1000
        value_node.location[1] = -400
        value_node.parent = channel_frame_node
        value_node.width = 300
        value_node.node_tree = default_value_group_node

        image_alpha_node = default_node_group.nodes.new('ShaderNodeMath')
        image_alpha_node.name = "MIX_{0}_IMAGE_ALPHA".format(channel.name)
        image_alpha_node.label = image_alpha_node.name
        image_alpha_node.location[0] = -500
        image_alpha_node.location[1] = 0
        image_alpha_node.parent = channel_frame_node
        image_alpha_node.operation = 'MULTIPLY'
        image_alpha_node.mute = True
        image_alpha_node.hide = True
        image_alpha_node.use_clamp = True

        image_alpha_node_reroute = default_node_group.nodes.new('NodeReroute')
        image_alpha_node_reroute.name = "MIX_{0}_IMAGE_ALPHA_REROUTE".format(channel.name)
        image_alpha_node_reroute.label = image_alpha_node_reroute.name
        image_alpha_node_reroute.location[0] = -1000
        image_alpha_node_reroute.location[1] = 0
        image_alpha_node_reroute.parent = channel_frame_node

        opacity_node = default_node_group.nodes.new('ShaderNodeMath')
        opacity_node.name = "{0}_OPACITY".format(channel.name)
        opacity_node.label = opacity_node.name
        opacity_node.location[0] = -300
        opacity_node.location[1] = 0
        opacity_node.parent = channel_frame_node
        opacity_node.width = 250
        opacity_node.operation = 'MULTIPLY'

        separate_node = default_node_group.nodes.new('ShaderNodeSeparateRGB')
        separate_node.name = "SEPARATE_{0}".format(channel.name)
        separate_node.label = separate_node.label
        separate_node.location[0] = -200
        separate_node.location[1] = -500
        separate_node.parent = channel_frame_node
        

        # Assign a default group node filter based on the socket type.
        match channel.socket_type:
            case 'NodeSocketFloat':
                default_group_filter = blender_addon_utils.append_group_node('ML_DefaultFloatFilter')
            case 'NodeSocketColor':
                default_group_filter = blender_addon_utils.append_group_node('ML_DefaultColorFilter')
            case 'NodeSocketVector':
                default_group_filter = blender_addon_utils.append_group_node('ML_DefaultVectorFilter')
            case 'NodeSocketNormal':
                default_group_filter = blender_addon_utils.append_group_node('ML_DefaultNormalFilter')

        filter_node = default_node_group.nodes.new('ShaderNodeGroup')
        filter_node.name = "{0}_FILTER".format(channel.name)
        filter_node.label = filter_node.name
        filter_node.location[0] = 0
        filter_node.location[1] = -500
        filter_node.parent = channel_frame_node
        filter_node.width = 300
        filter_node.node_tree = default_group_filter
        blender_addon_utils.set_node_active(filter_node, active=False)

        mix_node_reroute = default_node_group.nodes.new('NodeReroute')
        mix_node_reroute.name = "{0}_MIX_REROUTE".format(channel.name)
        mix_node_reroute.label = mix_node_reroute.name
        mix_node_reroute.location[0] = -1000
        mix_node_reroute.location[1] = -177
        mix_node_reroute.parent = channel_frame_node

        # Change the mix node and it's linking based on the default blend mode.
        if channel.default_blend_mode == 'NORMAL_MAP_COMBINE' or channel.default_blend_mode == 'NORMAL_MAP_DETAIL':
            normal_rotation_fix_node = default_node_group.nodes.new('ShaderNodeGroup')
            normal_rotation_fix_node.name = 'FIX_NORMAL_ROTATION'
            normal_rotation_fix_node.label = normal_rotation_fix_node.name
            normal_rotation_fix_node.location[0] = -600
            normal_rotation_fix_node.location[1] = -500
            normal_rotation_fix_node.parent = channel_frame_node
            normal_rotation_fix_node.width = 300
            normal_rotation_fix_node.node_tree = blender_addon_utils.append_group_node('ML_FixNormalRotation')

            mix_node = default_node_group.nodes.new('ShaderNodeGroup')
            mix_node.node_tree = blender_addon_utils.append_group_node('ML_ReorientedNormalMapMix')
            default_node_group.links.new(mix_node_reroute.outputs[0], mix_node.inputs[1])
            default_node_group.links.new(value_node.outputs[0], mix_node.inputs[2])
            default_node_group.links.new(mix_node.outputs[0], output_node.inputs.get(channel.name))

        else:
            mix_node = default_node_group.nodes.new('ShaderNodeMix')
            mix_node.data_type = 'RGBA'
            mix_node.clamp_factor = True
            mix_node.clamp_result = True
            mix_node.blend_type = channel.default_blend_mode
            default_node_group.links.new(mix_node_reroute.outputs[0], mix_node.inputs[6])
            default_node_group.links.new(value_node.outputs[0], mix_node.inputs[7])
            default_node_group.links.new(mix_node.outputs[2], output_node.inputs.get(channel.name))

        mix_node.name = "{0}_MIX".format(channel.name)
        mix_node.label = mix_node.name
        mix_node.location[0] = 500
        mix_node.location[1] = 0
        mix_node.parent = channel_frame_node

        # Organize the location of the material channel frame.
        channel_frame_node.location[0] = frame_x
        channel_frame_node.location[1] = frame_y
        frame_y -= 1000

        # Link all default nodes together.
        default_node_group.links.new(input_node.outputs.get('LayerMask'), image_alpha_node_reroute.inputs[0])
        default_node_group.links.new(image_alpha_node_reroute.outputs[0], image_alpha_node.inputs[0])
        default_node_group.links.new(image_alpha_node.outputs[0], opacity_node.inputs[1])
        default_node_group.links.new(opacity_node.outputs[0], mix_node.inputs[0])
        
        default_node_group.links.new(input_node.outputs.get(channel.name), mix_node_reroute.inputs[0])
        

    return default_node_group

def add_material_layer(layer_type, self):
    '''Adds a material layer to the active materials layer stack.'''

    # Append group nodes to help avoid node group duplication from appending.
    blender_addon_utils.append_default_node_groups()        

    # Verify standard context is correct.
    if blender_addon_utils.verify_material_operation_context(self, check_active_material=False) == False:
        return

    # If there are no material slots, or no material in the active material slot, make a new MatLayer material by appending the default material setup.
    active_object = bpy.context.active_object
    if len(active_object.material_slots) == 0:
        new_material = create_default_material_setup()
        new_material_name = blender_addon_utils.get_unique_material_name(active_object.name.replace('_', ''))
        new_material.name = new_material_name
        active_object.data.materials.append(new_material)
        active_object.active_material_index = 0
        apply_base_normals()

    # If material slots exist on the object, but the active material slot is empty, add a new material.
    elif active_object.material_slots[active_object.active_material_index].material == None:
        new_material = create_default_material_setup()
        new_material_name = blender_addon_utils.get_unique_material_name(active_object.name.replace('_', ''))
        new_material.name = new_material_name
        active_object.material_slots[active_object.active_material_index].material = new_material
        apply_base_normals()

    # If material slots exist on the object, but the active material isn't properly formatted to work with this add-on, display an error.
    else:
        active_material = bpy.context.active_object.active_material
        if blender_addon_utils.verify_addon_material(active_material) == False:
            debug_logging.log_status("Can't add layer, active material format is invalid.", self, type='ERROR')
            return
    
    new_layer_slot_index = add_material_layer_slot()

    # Create a material layer group node based on the specified layer type.
    match layer_type:
        case 'DECAL':
            default_layer_node_group = create_default_layer_node(layer_type='DECAL')
            debug_logging.log("Added decal layer.")

        case _:
            default_layer_node_group = create_default_layer_node(layer_type='MATERIAL')
            debug_logging.log("Added material layer.")

    active_material = bpy.context.active_object.active_material
    default_layer_node_group.name = format_layer_group_node_name(active_material.name, str(new_layer_slot_index)) + "~"
    new_layer_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
    new_layer_group_node.node_tree = default_layer_node_group
    new_layer_group_node.name = str(new_layer_slot_index) + "~"
    new_layer_group_node.label = "Layer " + str(new_layer_slot_index + 1)
    
    reindex_layer_nodes(change_made='ADDED_LAYER', affected_layer_index=new_layer_slot_index)
    organize_layer_group_nodes()
    link_layer_group_nodes(self)
    layer_masks.organize_mask_nodes()
    layer_masks.refresh_mask_slots()

    # TODO: For specific layer types, perform additional setup steps.
    '''
    match layer_type:
        case 'PAINT':
            replace_material_channel_node('COLOR', 'TEXTURE')
            addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
            high_bit_depth = addon_preferences.thirty_two_bit
            new_image = blender_addon_utils.create_image("Paint", base_color=(0.0, 0.0, 0.0, 0.0), alpha_channel=True, add_unique_id=True, thirty_two_bit=high_bit_depth)
            texture_node = get_material_layer_node('VALUE', new_layer_slot_index, 'COLOR')
            if texture_node:
                texture_node.image = new_image
            blender_addon_utils.set_texture_paint_image(new_image)
            blender_addon_utils.save_image(new_image)

            for material_channel_name in MATERIAL_CHANNEL_LIST:
                if material_channel_name != 'COLOR':
                    mix_layer_node = get_material_layer_node('MIX', new_layer_slot_index, material_channel_name)
                    if mix_layer_node:
                        mix_layer_node.mute = True

            # Use image alpha blending by default.
            toggle_image_alpha_blending('COLOR')

        case 'DECAL':

            # Create a new empty to use as a decal object.
            unique_decal_name = blender_addon_utils.get_unique_object_name("Decal", start_id_number=1)
            decal_object = bpy.data.objects.new(unique_decal_name, None)
            decal_object.empty_display_type = 'CUBE'
            decal_object.scale[2] = 0.1
            blender_addon_utils.add_object_to_collection("Decals", decal_object, color_tag='COLOR_03', unlink_from_other_collections=True)

            # Add the new decal object to the decal coordinate node.
            decal_coordinate_node = get_material_layer_node('DECAL_COORDINATES', new_layer_slot_index)
            if decal_coordinate_node:
                decal_coordinate_node.object = decal_object

            # Add a default decal to the color material channel.
            default_decal_image = blender_addon_utils.append_image('DefaultDecal')
            replace_material_channel_node('COLOR', 'TEXTURE')
            texture_node = get_material_layer_node('VALUE', new_layer_slot_index, 'COLOR')
            if texture_node:
                if texture_node.bl_static_type == 'TEX_IMAGE':
                    texture_node.image = default_decal_image
                    blender_addon_utils.set_texture_paint_image(default_decal_image)
                    blender_addon_utils.save_image(default_decal_image)

            # Add an image mask to the decal layer by default.
            layer_masks.add_layer_mask('DECAL', self)
            mask_texture_node = layer_masks.get_mask_node('TEXTURE', new_layer_slot_index, 0)
            if mask_texture_node:
                mask_texture_node.image = default_decal_image
            layer_masks.set_mask_output_channel('ALPHA')
            
            blender_addon_utils.set_snapping('DECAL', snap_on=True)
    '''

def duplicate_layer(original_layer_index, self):
    '''Duplicates the material layer at the provided layer index.'''

    if blender_addon_utils.verify_material_operation_context(self) == False:
        return
    
    duplicated_decal_object = None

    # Duplicate the node tree and add it to the layer stack.
    layer_node_tree = get_layer_node_tree(original_layer_index)
    if layer_node_tree:
        duplicated_node_tree = blender_addon_utils.duplicate_node_group(layer_node_tree.name)
        if duplicated_node_tree:
            active_material = bpy.context.active_object.active_material

            new_layer_slot_index = add_material_layer_slot()

            duplicated_node_tree.name = "{0}_{1}".format(active_material.name, str(new_layer_slot_index))
            new_layer_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
            new_layer_group_node.node_tree = duplicated_node_tree
            new_layer_group_node.name = str(new_layer_slot_index) + "~"
            new_layer_group_node.label = "Layer " + str(new_layer_slot_index + 1)
            
            reindex_layer_nodes(change_made='ADDED_LAYER', affected_layer_index=new_layer_slot_index)
            organize_layer_group_nodes()
            link_layer_group_nodes(self)
            layer_masks.organize_mask_nodes()

            # Duplicate decal objects if the original layer was a decal layer.
            decal_coordinate_node = get_material_layer_node('DECAL_COORDINATES', original_layer_index)
            if decal_coordinate_node:
                decal_object = decal_coordinate_node.object
                if decal_object:
                    duplicated_decal_object = blender_addon_utils.duplicate_object(decal_object)
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
                duplicated_node_tree = blender_addon_utils.duplicate_node_group(original_mask_node.node_tree.name)
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

        debug_logging.log("Duplicated material layer.")

def delete_layer(self):
    '''Deletes the selected layer'''
    if blender_addon_utils.verify_material_operation_context(self) == False:
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
    if blender_addon_utils.verify_material_operation_context(self) == False:
        return
    
    match direction:
        case 'UP':
            # Swap the layer index for all layer nodes in this layer with the layer above it (if one exists).
            layers = bpy.context.scene.matlayer_layers
            layer_count = len(layers)
            selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
            if selected_layer_index < layer_count:
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

            else:
                debug_logging.log("Can't move layer up, no layers exist above the selected layer.")

        case 'DOWN':
            # Swap the layer index for all nodes in this layer with the layer below it (if one exists).
            layers = bpy.context.scene.matlayer_layers
            selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
            if selected_layer_index - 1 >= 0:
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

            else:
                debug_logging.log("Can't move layer down, no layers exist below the selected layer.")

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
    # Count the number of layers in the specified material.
    if material != None:
        layer_count = 0
        while material.node_tree.nodes.get(str(layer_count)):
            layer_count += 1
        return layer_count
    
    # Count the active material, since no material was specified to have it's layers counted.
    else:
        active_object_attribute = getattr(bpy.context, "active_object", None)
        if active_object_attribute == None:
            return 0
        if not bpy.context.active_object:
            return 0
        if not bpy.context.active_object.active_material:
            return 0
        
        active_material = bpy.context.active_object.active_material
        layer_count = 0
        while active_material.node_tree.nodes.get(str(layer_count)):
            layer_count += 1
        return layer_count

def organize_layer_group_nodes():
    '''Organizes all layer group nodes in the active material to ensure the node tree is easy to read.'''
    active_material = bpy.context.active_object.active_material
    layer_count = count_layers()

    position_x = -500
    for i in range(layer_count, 0, -1):
        layer_group_node = active_material.node_tree.nodes.get(str(i - 1))
        if layer_group_node:
            layer_group_node.width = 300
            layer_group_node.location = (position_x, 0)
            position_x -= 500
    debug_logging.log("Organized layer group nodes.")

def refresh_layer_stack(reason="", scene=None):
    '''Clears, and then reads the active material, to sync the number of layers in the user interface with the number of layers that exist within the material node tree.'''
    if scene:
        layers = scene.matlayer_layers
    else:
        layers = bpy.context.scene.matlayer_layers
        
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

    if blender_addon_utils.verify_material_operation_context(self) == False:
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
                if input.name != 'LayerMask':
                    for link in input.links:
                        node_tree.links.remove(link)
            for output in layer_node.outputs:
                for link in output.links:
                    node_tree.links.remove(link)

    # Re-connect all (non-muted / active) layer group nodes.
    for i in range(0, layer_count):
        layer_node = get_material_layer_node('LAYER', i)
        if blender_addon_utils.get_node_active(layer_node):
            next_layer_index = i + 1
            next_layer_node = get_material_layer_node('LAYER', next_layer_index)
            if next_layer_node:
                while not blender_addon_utils.get_node_active(next_layer_node) and next_layer_index <= layer_count - 1:
                    next_layer_index += 1
                    next_layer_node = get_material_layer_node('LAYER', next_layer_index)

            if next_layer_node:
                if blender_addon_utils.get_node_active(next_layer_node):
                    for channel in shader_info.material_channels:

                        # If the next layers material channel is blending using the 'mix' blending method,
                        # and the next layer has no mask applied, this layers material channel values will have no
                        # effect on the material output. We can skip linking these channels so shaders will compile much faster.
                        mask_node = layer_masks.get_mask_node('MASK', next_layer_index, 0)
                        if not mask_node:
                            next_layer_mix_node = get_material_layer_node('MIX', next_layer_index, channel.name)
                            if next_layer_mix_node.bl_static_type == 'MIX':
                                if next_layer_mix_node.blend_type == 'MIX':
                                    next_layer_opacity_node = get_material_layer_node('OPACITY', next_layer_index, channel.name)
                                    if next_layer_opacity_node:
                                        if next_layer_opacity_node.inputs[0].default_value == 1:
                                            continue

                        output_socket_name = channel.name
                        input_socket_name = "{0} Mix".format(channel.name)
                        node_tree.links.new(layer_node.outputs.get(output_socket_name), next_layer_node.inputs.get(input_socket_name))

    # TODO: Connect the last (non-muted / active) layer node to the principled BSDF.
    base_normals_mix_node = active_material.node_tree.nodes.get('BASE_NORMALS_MIX')
    normal_and_height_mix_node = active_material.node_tree.nodes.get('NORMAL_HEIGHT_MIX')
    shader_node = active_material.node_tree.nodes.get('MATLAYER_SHADER')

    last_layer_node_index = layer_count - 1
    last_layer_node = get_material_layer_node('LAYER', last_layer_node_index)
    if last_layer_node:
        while not blender_addon_utils.get_node_active(last_layer_node) and last_layer_node_index >= 0:
            last_layer_node = get_material_layer_node('LAYER', last_layer_node_index)
            last_layer_node_index -= 1

    if last_layer_node:
        if blender_addon_utils.get_node_active(last_layer_node):
            
            for channel in shader_info.material_channels:

                # Only connect active material channels.
                if not tss.get_material_channel_active(channel.name):
                    continue
                
                # Connect normal and height channels differently.
                match channel.name:
                    case 'NORMAL':
                        output_socket = last_layer_node.outputs.get(channel.name)
                        input_socket = base_normals_mix_node.inputs.get('Normal Map 1')
                        if output_socket and input_socket:
                            node_tree.links.new(output_socket, input_socket)
                
                    case 'HEIGHT':
                        output_socket = last_layer_node.outputs.get(channel.name)
                        input_socket = normal_and_height_mix_node.inputs.get(channel.name)
                        if output_socket and input_socket:
                            node_tree.links.new(output_socket, input_socket)

                    case _:
                        output_socket = last_layer_node.outputs.get(channel.name)
                        input_socket = shader_node.inputs.get(channel.name)
                        if output_socket and input_socket:
                            node_tree.links.new(output_socket, input_socket)
    debug_logging.log("Linked layer group nodes.")

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

    # Apply base normals.
    apply_base_normals()

    debug_logging.log("Applied baked mesh maps.")

def relink_material_channel(relink_material_channel_name="", original_output_channel='', unlink_projection=False):
    '''Relinks the projection / blurring nodes and then links them to material channels based on the current projection node tree being used. If no material channel is specified to be relinked, all will be relinked.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node_tree = get_layer_node_tree(selected_layer_index)
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
    blur_node = get_material_layer_node('BLUR', selected_layer_index)
    
    # Unlink and relink projection for blur nodes if requested.
    if unlink_projection:
        blender_addon_utils.unlink_node(projection_node, layer_node_tree, unlink_inputs=False, unlink_outputs=True)
        blender_addon_utils.unlink_node(blur_node, layer_node_tree, unlink_inputs=True, unlink_outputs=True)
        match projection_node.node_tree.name:
            case 'ML_UVProjection':
                layer_node_tree.links.new(projection_node.outputs[0], blur_node.inputs[0])

            case "ML_TriplanarProjection":
                layer_node_tree.links.new(projection_node.outputs[0], blur_node.inputs[0])
                layer_node_tree.links.new(projection_node.outputs[1], blur_node.inputs[1])
                layer_node_tree.links.new(projection_node.outputs[2], blur_node.inputs[2])

            case 'ML_DecalProjection':
                layer_node_tree.links.new(projection_node.outputs[0], blur_node.inputs[0])
                layer_node_tree.links.new(projection_node.outputs[0], blur_node.inputs[0])

    # Relink projection for all material channels unless a specific material channel is specified.
    for material_channel_name in MATERIAL_CHANNEL_LIST:
        if relink_material_channel_name == "" or relink_material_channel_name == material_channel_name:

            # Remember the original output channel of the material channel so it can be properly set after relinking projection.
            if original_output_channel == '':
                original_output_channel = get_material_channel_output_channel(material_channel_name)

            match projection_node.node_tree.name:

                # Relink a material channel with a triplanar projection setup.
                case 'ML_TriplanarProjection':
                    value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, node_number=1)
                    triplanar_blend_node = get_material_layer_node('TRIPLANAR_BLEND', selected_layer_index, material_channel_name)

                    # Link projection / blur nodes when image textures are used as the material channel value.
                    if value_node.bl_static_type == 'TEX_IMAGE':
                        for i in range(0, 3):
                            value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, node_number=i + 1)

                            if blender_addon_utils.get_node_active(blur_node):
                                channel_name = material_channel_name.replace('-', ' ')
                                channel_name = blender_addon_utils.capitalize_by_space(channel_name)
                                blur_output_property_name = "{0} {1}".format(channel_name, str(i + 1))
                                layer_node_tree.links.new(blur_node.outputs.get(blur_output_property_name), value_node.inputs[0])
                            else:
                                layer_node_tree.links.new(projection_node.outputs[i], value_node.inputs[0])

                            # Link triplanar blending nodes.
                            if triplanar_blend_node:
                                layer_node_tree.links.new(value_node.outputs.get('Color'), triplanar_blend_node.inputs[i])
                                layer_node_tree.links.new(value_node.outputs.get('Alpha'), triplanar_blend_node.inputs[i + 3])
                                layer_node_tree.links.new(projection_node.outputs.get('AxisMask'), triplanar_blend_node.inputs.get('AxisMask'))
                                if material_channel_name == 'NORMAL':
                                    layer_node_tree.links.new(projection_node.outputs.get('Rotation'), triplanar_blend_node.inputs.get('Rotation'))
                                    layer_node_tree.links.new(projection_node.outputs.get('SignedGeometryNormals'), triplanar_blend_node.inputs.get('SignedGeometryNormals'))

                    # Link the triplanar projection for custom group nodes with inputs that having matching names with projection node outputs.
                    else:
                        for input in TRIPLANAR_PROJECTION_INPUTS:
                            if value_node.inputs.get(input) and projection_node.outputs.get(input):
                                layer_node_tree.links.new(projection_node.outputs.get(input), value_node.inputs.get(input))

                # Relink the material channel projection for all other projection setups.
                case _:
                    value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name)
                    mix_image_alpha_node = get_material_layer_node('MIX_IMAGE_ALPHA', selected_layer_index, material_channel_name)
                    
                    # Relink for image texture nodes.
                    if value_node.bl_static_type == 'TEX_IMAGE':
                        if blender_addon_utils.get_node_active(blur_node):
                            layer_node_tree.links.new(blur_node.outputs.get(material_channel_name.capitalize()), value_node.inputs[0])
                        else:
                            layer_node_tree.links.new(projection_node.outputs[0], value_node.inputs[0])
                            layer_node_tree.links.new(value_node.outputs.get('Alpha'), mix_image_alpha_node.inputs[1])

                    # Relink for custom user group nodes.
                    if value_node.bl_static_type == 'GROUP':
                        if not value_node.node_tree.name.startswith("ML_Default"):
                            if blender_addon_utils.get_node_active(blur_node):
                                layer_node_tree.links.new(blur_node.outputs.get(material_channel_name.capitalize()), value_node.inputs[0])
                            else:
                                layer_node_tree.links.new(projection_node.outputs[0], value_node.inputs[0])

            set_material_channel_output_channel(material_channel_name, original_output_channel)

def set_layer_projection_nodes(projection_method):
    '''Changes the layer projection nodes to use the specified layer projection method.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
    layer_node_tree = get_layer_node_tree(selected_layer_index)
    blur_node = get_material_layer_node('BLUR', selected_layer_index)
    
    match projection_method:
        case 'UV':
            projection_node.node_tree = blender_addon_utils.append_group_node("ML_UVProjection")
            blur_node.node_tree = blender_addon_utils.append_group_node("ML_LayerBlur")

            if blender_addon_utils.get_node_active(blur_node):
                layer_node_tree.links.new(projection_node.outputs[0], blur_node.inputs[0])

        case 'TRIPLANAR':
            projection_node.node_tree = blender_addon_utils.append_group_node("ML_TriplanarProjection")
            blur_node.node_tree = blender_addon_utils.append_group_node("ML_TriplanarLayerBlur")

            if blender_addon_utils.get_node_active(blur_node):
                layer_node_tree.links.new(projection_node.outputs.get('X'), blur_node.inputs.get('X'))
                layer_node_tree.links.new(projection_node.outputs.get('Y'), blur_node.inputs.get('Y'))
                layer_node_tree.links.new(projection_node.outputs.get('Z'), blur_node.inputs.get('Z'))

def delete_triplanar_blending_nodes(material_channel_name):
    '''Deletes nodes used for triplanar texture sampling and blending for the specified material channel.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node_tree = get_layer_node_tree(selected_layer_index)

    for i in range(0, 3):
        texture_sample_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, i + 1)
        if texture_sample_node:
            layer_node_tree.nodes.remove(texture_sample_node)

    triplanar_blend_node = get_material_layer_node('TRIPLANAR_BLEND', selected_layer_index, material_channel_name)
    if triplanar_blend_node:
        layer_node_tree.nodes.remove(triplanar_blend_node)

def setup_material_channel_projection_nodes(material_channel_name, projection_method, set_texture_node=False):
    '''Replaces the projection node setup for the specified material channel based on the projection method.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node_tree = get_layer_node_tree(selected_layer_index)
    value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name, 1)
    
    # Texture nodes are the only nodes that require a specific projection node setup, ignore other node types.
    # If set_texture_node is true, the material channel value node will be replaces with a texture node, regardless of it's original node type.
    if value_node.bl_static_type == 'TEX_IMAGE' or set_texture_node:

        # Remember the original nodes location and type.
        original_value_node_type = value_node.bl_static_type
        value_node.parent = None
        original_node_location = value_node.location.copy()

        # Update the nodes based on the layer projection method.
        match projection_method:
            case 'UV':
                # Remember original location and image of the texture node.
                if original_value_node_type == 'TEX_IMAGE':
                    original_image = value_node.image
                    original_interpolation = value_node.interpolation

                # Delete triplanar texture nodes if they exist.
                delete_triplanar_blending_nodes(material_channel_name)

                # Replace the material channel value nodes with a texture node.
                texture_sample_node = layer_node_tree.nodes.new('ShaderNodeTexImage')
                texture_sample_node.name = "{0}_VALUE_{1}".format(material_channel_name, 1)
                texture_sample_node.label = texture_sample_node.name
                texture_sample_node.hide = True
                texture_sample_node.width = 300
                texture_sample_node.location = original_node_location

                if original_value_node_type == 'TEX_IMAGE':
                    texture_sample_node.image = original_image
                    texture_sample_node.interpolation = original_interpolation

                # Frame the new nodes.
                frame_name = material_channel_name.replace('-', ' ')
                frame = layer_node_tree.nodes.get(frame_name)
                texture_sample_node.parent = frame

                # Link the texture to projection / blur and mix layer nodes.
                relink_material_channel(material_channel_name)

            case 'DECAL':
                # Remember original location and image of the texture node.
                if original_value_node_type == 'TEX_IMAGE':
                    original_image = value_node.image
                    original_interpolation = value_node.interpolation

                # Delete triplanar texture nodes if they exist.
                delete_triplanar_blending_nodes(material_channel_name)

                # Replace with a single texture node.
                texture_node = layer_node_tree.nodes.new('ShaderNodeTexImage')
                texture_node.name = "{0}_VALUE_{1}".format(material_channel_name, 1)
                texture_node.label = texture_node.name
                texture_node.hide = True
                texture_node.width = 300
                texture_node.location = original_node_location
                texture_node.extension = 'CLIP'
                if original_value_node_type == 'TEX_IMAGE':
                    texture_node.image = original_image
                    texture_node.interpolation = original_interpolation

                # Frame the new nodes.
                frame_name = material_channel_name.replace('-', ' ')
                frame = layer_node_tree.nodes.get(frame_name)
                texture_node.parent = frame

                # Link the texture to projection / blur and mix layer nodes.
                relink_material_channel(material_channel_name)

            case 'TRIPLANAR':
                # Remember the old image and location.
                original_value_node_type = value_node.bl_static_type
                if original_value_node_type == 'TEX_IMAGE':
                    original_image = value_node.image
                    original_interpolation = value_node.interpolation

                # Remove the old value node.
                layer_node_tree.nodes.remove(value_node)

                # Add 3 required texture samples for triplanar projection and frame them.
                texture_sample_nodes = []
                location_x = original_node_location[0]
                location_y = original_node_location[1]
                frame_name = material_channel_name.replace('-', ' ')
                frame = layer_node_tree.nodes.get(frame_name)
                for i in range(0, 3):
                    texture_sample_node = layer_node_tree.nodes.new('ShaderNodeTexImage')
                    texture_sample_node.name = "{0}_VALUE_{1}".format(material_channel_name, i + 1)
                    texture_sample_node.label = texture_sample_node.name
                    texture_sample_node.hide = True
                    texture_sample_node.width = 300
                    texture_sample_node.location = (location_x, location_y)
                    texture_sample_nodes.append(texture_sample_node)
                    location_y -= 50
                    if original_value_node_type == 'TEX_IMAGE':
                        texture_sample_node.image = original_image
                        texture_sample_node.interpolation = original_interpolation
                    texture_sample_node.parent = frame

                # Add a node for blending texture samples.
                triplanar_blend_node = layer_node_tree.nodes.new('ShaderNodeGroup')
                if material_channel_name == 'NORMAL':
                    triplanar_blend_node.node_tree = blender_addon_utils.append_group_node("ML_TriplanarNormalsBlend")
                else:
                    triplanar_blend_node.node_tree = blender_addon_utils.append_group_node("ML_TriplanarBlend")
                triplanar_blend_node.name = "TRIPLANAR_BLEND_{0}".format(material_channel_name)
                triplanar_blend_node.label = triplanar_blend_node.name
                triplanar_blend_node.width = 300
                triplanar_blend_node.hide = True
                triplanar_blend_node.location = (location_x, location_y)
                triplanar_blend_node.parent = frame

                # Connect texture sample and blending nodes for material channels.
                relink_material_channel(material_channel_name)

def replace_material_channel_node(material_channel_name, node_type):
    '''Replaces the existing material channel node with a new node of the given type. Valid node types include: 'GROUP', 'TEXTURE'.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_group_node = get_layer_node_tree(selected_layer_index)
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
    value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name)

    match node_type:
        case 'GROUP':
            value_node.parent = None
            original_node_location = value_node.location.copy()

            # Remove the old nodes.
            match projection_node.node_tree.name:
                case 'ML_TriplanarProjection':
                    delete_triplanar_blending_nodes(material_channel_name)
                case _:
                    layer_group_node.nodes.remove(value_node)

            # Replace the material channel value nodes with a group node.
            new_node = layer_group_node.nodes.new('ShaderNodeGroup')
            new_node.name = "{0}_VALUE_1".format(material_channel_name)
            new_node.label = new_node.name
            new_node.width = 300
            new_node.location = original_node_location

            # Frame the new node.
            frame_name = material_channel_name.replace('-', ' ')
            frame = layer_group_node.nodes.get(frame_name)
            new_node.parent = frame

            # Apply the default group node for the specified channel.
            default_node_tree_name = material_channel_name.replace('-', ' ')
            default_node_tree_name = blender_addon_utils.capitalize_by_space(default_node_tree_name)
            default_node_tree_name = "ML_Default{0}".format(default_node_tree_name. replace(' ', ''))
            default_node_tree = bpy.data.node_groups.get(default_node_tree_name)
            new_node.node_tree = default_node_tree

            # Link the new group node.
            mix_node = get_material_layer_node('MIX', selected_layer_index, material_channel_name)
            if mix_node.bl_static_type == 'GROUP':
                layer_group_node.links.new(new_node.outputs[0], mix_node.inputs[2])
            else:
                layer_group_node.links.new(new_node.outputs[0], mix_node.inputs[7])

        case 'TEXTURE':
            # Apply projection to texture nodes based on the projection node tree name.
            match projection_node.node_tree.name:
                case 'ML_UVProjection':
                    setup_material_channel_projection_nodes(material_channel_name, 'UV', set_texture_node=True)

                case 'ML_TriplanarProjection':
                    setup_material_channel_projection_nodes(material_channel_name, 'TRIPLANAR', set_texture_node=True)

                case 'ML_DecalProjection':
                    setup_material_channel_projection_nodes(material_channel_name, 'DECAL', set_texture_node=True)

def set_layer_projection(projection_mode, self):
    '''Changes projection nodes for the layer to use the specified projection mode. Valid options include: 'UV', 'TRIPLANAR'.'''
    if blender_addon_utils.verify_material_operation_context(self) == False:
        return

    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
    if not projection_node:
        debug_logging.log_status("Error, missing layer projection node. The material node format is corrupt, or the active material is not made with this add-on.")
        return

    match projection_mode:
        case 'UV':
            if projection_node.node_tree.name != "ML_UVProjection":
                set_layer_projection_nodes('UV')

                for material_channel_name in MATERIAL_CHANNEL_LIST:
                    setup_material_channel_projection_nodes(material_channel_name, 'UV')

                debug_logging.log("Changed layer projection to 'UV'.")

        case 'TRIPLANAR':
            if projection_node.node_tree.name != "ML_TriplanarProjection":
                set_layer_projection_nodes('TRIPLANAR')

                for material_channel_name in MATERIAL_CHANNEL_LIST:
                    setup_material_channel_projection_nodes(material_channel_name, 'TRIPLANAR')

                debug_logging.log("Changed layer projection to 'TRIPLANAR'.")

def get_material_channel_output_channel(material_channel_name):
    '''Returns the output channel for the specified material channel.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    filter_node = get_material_layer_node('FILTER', selected_layer_index, material_channel_name)

    output_channel = ''
    color_input_node = None

    # If the filter node is active, check the connected input in it for the current output channel.
    if blender_addon_utils.get_node_active(filter_node):
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

    # If the set output channel is alpha, but the material value node isn't an image (and thus can't have an alpha channel), return color instead to avoid errors.
    if output_channel == 'ALPHA':
        value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name)
        if value_node.bl_static_type != 'TEX_IMAGE':
            output_channel = 'COLOR'

    return output_channel

def set_material_channel_output_channel(material_channel_name, output_channel_name, layer_index=-1):
    '''Links the specified output channel for the specified material channel.'''
    if layer_index == -1:
        layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index

    layer_node_tree = get_layer_node_tree(layer_index)
    separate_color_node = get_material_layer_node('SEPARATE', layer_index, material_channel_name)
    projection_node = get_material_layer_node('PROJECTION', layer_index)
    filter_node = get_material_layer_node('FILTER', layer_index, material_channel_name)
    value_node = get_material_layer_node('VALUE', layer_index, material_channel_name)
    mix_image_alpha_node = get_material_layer_node('MIX_IMAGE_ALPHA', layer_index, material_channel_name)
    mix_node = get_material_layer_node('MIX', layer_index, material_channel_name)
    fix_normal_rotation_node = get_material_layer_node('FIX_NORMAL_ROTATION', layer_index, material_channel_name)

    # Determine the node the main material channel output value is coming from.
    output_node = None
    match projection_node.node_tree.name:
        case 'ML_TriplanarProjection':
            if value_node.bl_static_type == 'TEX_IMAGE':
                output_node = get_material_layer_node('TRIPLANAR_BLEND', layer_index, material_channel_name)
            else:
                output_node = value_node
        case _:
            output_node = get_material_layer_node('VALUE', layer_index, material_channel_name)

    # Determine the input node for the main material channel value.
    input_node = None
    input_socket = -1
    connect_filter_node = False
    if blender_addon_utils.get_node_active(filter_node):
        input_node = filter_node
        input_socket = 0
        connect_filter_node = True

    else:
        input_node = mix_node
        if mix_node.bl_static_type == 'GROUP':
            input_socket = 2
        else:
            input_socket = 7

    # Unlink nodes to ensure only the correct nodes will be linked after this function is complete.
    blender_addon_utils.unlink_node(output_node, layer_node_tree, unlink_inputs=False, unlink_outputs=True)
    blender_addon_utils.unlink_node(separate_color_node, layer_node_tree, unlink_inputs=True, unlink_outputs=True)

    # Determine the output socket that should be used, and if a channel separator is required.
    connect_channel_separator = False
    output_socket = 0
    match output_channel_name:
        case 'ALPHA':
            if output_node.bl_static_type == 'TEX_IMAGE':
                output_socket = 1
            else:
                output_socket = 0

        case 'RED':
            output_socket = 0
            connect_channel_separator = True

        case 'GREEN':
            output_socket = 1
            connect_channel_separator = True

        case 'BLUE':
            output_socket = 2
            connect_channel_separator = True

        case _:
            debug_logging.log("Invalid material output channel provided to set_material_channel_output_channel.", message_type='ERROR', sub_process=False)
            output_socket = 0

    # Always link the output node alpha to the mix image alpha node.
    if value_node.bl_static_type == 'TEX_IMAGE':
        layer_node_tree.links.new(output_node.outputs[1], mix_image_alpha_node.inputs[1])

    # Link to a normal rotation fix node for layers using UV projection.
    if material_channel_name == 'NORMAL' and projection_node.node_tree.name == 'ML_UVProjection':
        layer_node_tree.links.new(projection_node.outputs.get('Rotation'), fix_normal_rotation_node.inputs.get('Rotation'))

        if connect_channel_separator:
            layer_node_tree.links.new(output_node.outputs[0], fix_normal_rotation_node.inputs[0])
            layer_node_tree.links.new(fix_normal_rotation_node.outputs[0], separate_color_node.inputs[0])
            layer_node_tree.links.new(separate_color_node.outputs[output_socket], input_node.inputs[input_socket])

        else:
            layer_node_tree.links.new(output_node.outputs[output_socket], fix_normal_rotation_node.inputs[0])
            layer_node_tree.links.new(fix_normal_rotation_node.outputs[0], input_node.inputs[input_socket])

    else:
        # Link the the channel separator node for red, green or blue channels.
        if connect_channel_separator:
            layer_node_tree.links.new(output_node.outputs[0], separate_color_node.inputs[0])
            layer_node_tree.links.new(separate_color_node.outputs[output_socket], input_node.inputs[input_socket])
        else:
            layer_node_tree.links.new(output_node.outputs[output_socket], input_node.inputs[input_socket])

    # Link the filter node if it's enabled in this material channel.
    if connect_filter_node:
        if mix_node.bl_static_type == 'GROUP':
            layer_node_tree.links.new(input_node.outputs[0], mix_node.inputs[2])
        else:
            layer_node_tree.links.new(input_node.outputs[0], mix_node.inputs[7])

def isolate_material_channel(material_channel_name):
    '''Isolates the specified material channel by linking only the specified material channel output to the material channel output / emission node.'''
    active_node_tree = bpy.context.active_object.active_material.node_tree
    emission_node = active_node_tree.nodes.get('EMISSION')
    material_output = active_node_tree.nodes.get('MATERIAL_OUTPUT')

    # Unlink the emission node (ensures nothing else is connected to it).
    blender_addon_utils.unlink_node(emission_node, active_node_tree, unlink_inputs=True, unlink_outputs=True)

    # For the normal material channel, connect the normal and height mix to the emission node.
    if material_channel_name == 'NORMAL':
        base_normals_mix_node = get_material_layer_node('BASE_NORMALS_MIX')
        active_node_tree.links.new(base_normals_mix_node.outputs[0], emission_node.inputs[0])

    # For all other material channels connect the specified material channel for the last active material channel.
    total_layers = count_layers(bpy.context.active_object.active_material)
    for i in range(total_layers, 0, -1):
        layer_node = get_material_layer_node('LAYER', i - 1)
        if blender_addon_utils.get_node_active(layer_node):
            channel_name = material_channel_name.replace('-', ' ')
            channel_name = blender_addon_utils.capitalize_by_space(channel_name)
            active_node_tree.links.new(layer_node.outputs.get(channel_name), emission_node.inputs[0])
            break
    
    active_node_tree.links.new(emission_node.outputs[0], material_output.inputs[0])

def show_layer():
    '''Removes material channel or mask isolation if they are applied.'''
    active_object_attribute = getattr(bpy.context, "active_object", None)
    if not active_object_attribute:
        return
    
    if bpy.context.active_object:
        if bpy.context.active_object.active_material:
            active_node_tree = bpy.context.active_object.active_material.node_tree
            emission_node = active_node_tree.nodes.get('EMISSION')
            if emission_node:
                if len(emission_node.outputs[0].links) != 0:
                    blender_addon_utils.unlink_node(emission_node, active_node_tree, unlink_inputs=True, unlink_outputs=True)
                    material_output = active_node_tree.nodes.get('MATERIAL_OUTPUT')
                    principled_bsdf = active_node_tree.nodes.get('MATLAYER_SHADER')
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
    original_output_channel = get_material_channel_output_channel(material_channel_name)

    # Ensure the mix not is a group node and apply the layer blending modes.
    mix_node = original_mix_node
    if blending_mode == 'NORMAL_MAP_COMBINE' or blending_mode == 'NORMAL_MAP_DETAIL':
        if original_mix_node.bl_static_type != 'GROUP':
            original_location = original_mix_node.location
            layer_node_tree.nodes.remove(original_mix_node)
            mix_node = layer_node_tree.nodes.new('ShaderNodeGroup')
            mix_node.location = (original_location[0], original_location[1])
            mix_node.name = "{0}_MIX".format(material_channel_name)
            mix_node.label = mix_node.name
            mix_node.width = 300
        else:
            mix_node = original_mix_node

        if blending_mode == 'NORMAL_MAP_COMBINE':
            mix_node.node_tree = blender_addon_utils.append_group_node('ML_WhiteoutNormalMapMix')
        elif blending_mode == 'NORMAL_MAP_DETAIL':
            mix_node.node_tree = blender_addon_utils.append_group_node('ML_ReorientedNormalMapMix')

    # Ensure the mix node type isn't a group node and then apply the layer blending value.
    else:
        if original_mix_node.bl_static_type != 'MIX':
            original_location = original_mix_node.location
            layer_node_tree.nodes.remove(original_mix_node)

            mix_node = layer_node_tree.nodes.new('ShaderNodeMix')
            mix_node.location = (original_location[0], original_location[1])
            mix_node.name = "{0}_MIX".format(material_channel_name)
            mix_node.label = mix_node.name
            mix_node.data_type = 'RGBA'
            mix_node.width = 300
        
        mix_node.blend_type = blending_mode

    # Relink the layer mix node with the layer opacity and previous layer values.
    opacity_node = get_material_layer_node('OPACITY', layer_index, material_channel_name)
    layer_node_tree.links.new(opacity_node.outputs[0], mix_node.inputs[0])

    group_input = get_material_layer_node('GROUP_INPUT', layer_index)
    channel_name = material_channel_name.replace('-', ' ')
    channel_name = blender_addon_utils.capitalize_by_space(channel_name)
    channel_input_name = channel_name + " Mix"
    group_output = get_material_layer_node('GROUP_OUTPUT', layer_index)
    if mix_node.bl_static_type == 'GROUP':
        layer_node_tree.links.new(mix_node.outputs[0], group_output.inputs.get(channel_name))
        layer_node_tree.links.new(group_input.outputs.get(channel_input_name), mix_node.inputs[1])
    else:
        layer_node_tree.links.new(mix_node.outputs[2], group_output.inputs.get(channel_name))
        layer_node_tree.links.new(group_input.outputs.get(channel_input_name), mix_node.inputs[6])

    # Relink the material channel of this layer based on the original material output channel.
    set_material_channel_output_channel(material_channel_name, original_output_channel, layer_index)


#----------------------------- OPERATORS -----------------------------#


class MATLAYER_layer_stack(PropertyGroup):
    '''Properties for the layer stack.'''
    selected_layer_index: IntProperty(default=-1, description="Selected material layer", update=update_layer_index)
    selected_material_channel: EnumProperty(items=MATERIAL_CHANNEL, name="Material Channel", description="The currently selected material channel", default='COLOR')

class MATLAYER_layers(PropertyGroup):
    # Storing properties in the layer slot data can potentially cause many errors and often more code -
    # - Properties stored in the layer slots must be read from the material node tree when a new active material is selected.
    # - Properties stored in the layer slots must be updated first in the interface, then trigger callback functions to update their associated properties in material nodes.
    # To help avoid the errors above, all properties are stored in the material node tree of created materials (in one way or another) and referenced directly when displayed in the user interface.
    # A placeholder property is kept here so the UI still has a property group to reference to draw the UIList.
    placeholder_property: IntProperty()

class MATLAYER_OT_add_material_layer(Operator):
    bl_idname = "matlayer.add_material_layer"
    bl_label = "Add Material Layer"
    bl_description = "Adds a material layer to the active material (if the material is created with this add-on)"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_material_layer('DEFAULT', self)
        return {'FINISHED'}

class MATLAYER_OT_add_paint_material_layer(Operator):
    bl_idname = "matlayer.add_paint_material_layer"
    bl_label = "Add Paint Material Layer"
    bl_description = "Creates a material layer and an image texture that's placed in the materials color channel"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_material_layer('PAINT', self)
        return {'FINISHED'}

class MATLAYER_OT_add_decal_material_layer(Operator):
    bl_idname = "matlayer.add_decal_material_layer"
    bl_label = "Add Decal Material Layer"
    bl_description = "Adds a non-destructive layer designed specifically for placing decals (stickers / text). Control the position of the decal using the layers associated decal (empty) object"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_material_layer('DECAL', self)
        return {'FINISHED'}

class MATLAYER_OT_duplicate_layer(Operator):
    bl_idname = "matlayer.duplicate_layer"
    bl_label = "Duplicate Layer"
    bl_description = "Duplicates the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

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
        return context.active_object

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
        return context.active_object

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
        return context.active_object

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

class MATLAYER_OT_toggle_layer_blur(Operator):
    bl_idname = "matlayer.toggle_layer_blur"
    bl_label = "Toggle Layer Blur"
    bl_description = "Toggle on / off blurring for the selected layer. Toggle blurring off when not in use to improve shader compilation time and viewport performance"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        selected_layer_index = context.scene.matlayer_layer_stack.selected_layer_index
        blur_node = get_material_layer_node('BLUR', selected_layer_index)
        if blur_node:
            # Connect the projection node to all material channels.
            if blender_addon_utils.get_node_active(blur_node):
                blender_addon_utils.set_node_active(blur_node, False)
            
            # Connect the blur node to all material channels.
            else:
                blender_addon_utils.set_node_active(blur_node, True)
        relink_material_channel(unlink_projection=True)
        return {'FINISHED'}

class MATLAYER_OT_toggle_material_channel_blur(Operator):
    bl_idname = "matlayer.toggle_material_channel_blur"
    bl_label = "Toggle Material Channel Blur"
    bl_description = "Toggle on / off a blur filter for the specified material channel"
    bl_options = {'REGISTER', 'UNDO'}

    material_channel_name: StringProperty(default="COLOR")

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        selected_layer_index = context.scene.matlayer_layer_stack.selected_layer_index

        BLUR_node = get_material_layer_node('BLUR', selected_layer_index)
        channel_name = self.material_channel_name.replace('-', ' ')
        channel_name = blender_addon_utils.capitalize_by_space(channel_name)
        blur_toggle_property_name = "{0} Blur Toggle".format(channel_name)
        if BLUR_node.inputs.get(blur_toggle_property_name).default_value == 1:
            BLUR_node.inputs.get(blur_toggle_property_name).default_value = 0
        else:
            BLUR_node.inputs.get(blur_toggle_property_name).default_value = 1

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

        if blender_addon_utils.get_node_active(layer_node):
            blender_addon_utils.set_node_active(layer_node, False)
        else:
            blender_addon_utils.set_node_active(layer_node, True)

        link_layer_group_nodes(self)
        return {'FINISHED'}

class MATLAYER_OT_set_layer_projection_uv(Operator):
    bl_idname = "matlayer.set_layer_projection_uv"
    bl_label = "Set Layer Projection UV"
    bl_description = "Sets the projection mode for the layer to UV projection, which uses the UV layout of the object to project textures used on this material layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        set_layer_projection('UV', self)
        return {'FINISHED'}

class MATLAYER_OT_set_layer_projection_triplanar(Operator):
    bl_idname = "matlayer.set_layer_projection_triplanar"
    bl_label = "Set Layer Projection Triplanar"
    bl_description = "Sets the projection mode for the layer to triplanar projection which projects the textures onto the object from each axis. This projection method can be used to apply materials to objects without needing to manually blend seams"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        set_layer_projection('TRIPLANAR', self)
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

class MATLAYER_OT_toggle_triplanar_flip_correction(Operator):
    bl_idname = "matlayer.toggle_triplanar_flip_correction"
    bl_label = "Toggle Triplanar Flip Correction"
    bl_description = "Toggles extra shader math that correctly flips the axis projection. This allows textures with text or directional pixel information to be properly projected using triplanar projection. Most texture's don't require this, which is why it's off by default"
    bl_options = {'REGISTER', 'UNDO'}

    material_channel_name: StringProperty(default='COLOR')
    node_type: StringProperty(default='GROUP')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        # Mute / unmute nodes that correct triplanar projection axis flipping.
        selected_layer_index = context.scene.matlayer_layer_stack.selected_layer_index
        projection_node = get_material_layer_node('PROJECTION', selected_layer_index)
        if projection_node:
            if projection_node.node_tree.name == 'ML_TriplanarProjection':
                for i in range(0, 3):
                    correct_axis_flip_node = projection_node.node_tree.nodes.get("CORRECT_AXIS_FLIP_{0}".format(i + 1))
                    if correct_axis_flip_node:
                        if correct_axis_flip_node.mute:
                            correct_axis_flip_node.mute = False
                        else:
                            correct_axis_flip_node.mute = True
        return {'FINISHED'}

class MATLAYER_OT_isolate_material_channel(Operator):
    bl_idname = "matlayer.isolate_material_channel"
    bl_label = "Isolate Material Channel"
    bl_description = "Isolates the selected material channel. Select a material layer to de-isolate"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        selected_material_channel = bpy.context.scene.matlayer_layer_stack.selected_material_channel
        isolate_material_channel(selected_material_channel)
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

class MATLAYER_OT_toggle_material_channel_filter(Operator):
    bl_idname = "matlayer.toggle_material_channel_filter"
    bl_label = "Toggle Material Channel Filter"
    bl_description = "Toggles the filter node for the material channel on / off"
    bl_options = {'REGISTER', 'UNDO'}

    material_channel_name: StringProperty(default='COLOR')

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        filter_node = get_material_layer_node('FILTER', selected_layer_index, self.material_channel_name)

        output_channel = get_material_channel_output_channel(self.material_channel_name)

        # Toggle the active state for the filter node.
        if blender_addon_utils.get_node_active(filter_node) == True:
            blender_addon_utils.set_node_active(filter_node, False)

        else:
            blender_addon_utils.set_node_active(filter_node, True)

        # Trigger a relink of the material layer.
        relink_material_channel(relink_material_channel_name=self.material_channel_name, original_output_channel=output_channel)

        return {'FINISHED'}

class MATLAYER_OT_set_material_channel_output_channel(Operator):
    bl_idname = "matlayer.set_material_channel_output_channel"
    bl_label = "Set Material Channel Output Channel"
    bl_description = "Sets the material channel to use the specified output channel"
    bl_options = {'REGISTER', 'UNDO'}

    output_channel_name: StringProperty(default='COLOR')
    material_channel_name: StringProperty(default='COLOR')

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        set_material_channel_output_channel(self.material_channel_name, self.output_channel_name)
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
