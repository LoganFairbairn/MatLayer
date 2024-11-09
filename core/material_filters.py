# This file contains operators for adding, editing and removing filters for material channels.

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, StringProperty
from ..core import material_layers
from ..core import debug_logging
from ..core import blender_addon_utils as bau

FILTER_DEFAULT_LOCATION_X = 150
FILTER_DEFAULT_LOCATION_Y = -220
FILTER_SPACING = 50
FILTER_NODE_WIDTH = 200

# Info lookup table for filter node info.
FILTER_INFO = {
    "HUE_SAT": {
        "bpy_node_name": "ShaderNodeHueSaturation",
        "node_label": "Hue Saturation Value",
        "main_input_socket": 4,
        "main_output_socket": 0,
        "custom_node_group": ""
    },
    "INVERT": {
        "bpy_node_name": "ShaderNodeInvert", 
        "node_label": "Invert",
        "main_input_socket": 1,
        "main_output_socket": 0,
        "custom_node_group": ""
    },
    "BRIGHTCONTRAST": {
        "bpy_node_name": "ShaderNodeBrightContrast",
        "node_label": "Brightness / Contrast",
        "main_input_socket": 0,
        "main_output_socket": 0,
        "custom_node_group": ""
    },
    "GAMMA": {
        "bpy_node_name": "ShaderNodeGamma",
        "node_label": "Gamma",
        "main_input_socket": 0,
        "main_output_socket": 0,
        "custom_node_group": ""
    },
    "CURVE_RGB": {
        "bpy_node_name": "ShaderNodeRGBCurve",
        "node_label": "RGB Curves",
        "main_input_socket": 1,
        "main_output_socket": 0,
        "custom_node_group": ""
    },
    "RGBTOBW": {
        "bpy_node_name": "ShaderNodeRGBToBW",
        "node_label": "RGB to BW",
        "main_input_socket": 0,
        "main_output_socket": 0,
        "custom_node_group": ""
    },
    "VALTORGB": {
        "bpy_node_name": "ShaderNodeValToRGB",
        "node_label": "Color Ramp",
        "main_input_socket": 0,
        "main_output_socket": 0,
        "custom_node_group": ""
    },
    "CHEAP_CONTRAST": {
        "bpy_node_name": "ShaderNodeGroup",
        "node_label": "Cheap Contrast",
        "main_input_socket": 0,
        "main_output_socket": 0,
        "custom_node_group": "ML_CheapContrast"
    },
    "NORMAL_INTENSITY": {
        "bpy_node_name": "ShaderNodeGroup",
        "node_label": "Normal Intensity",
        "main_input_socket": 0,
        "main_output_socket": 0,
        "custom_node_group": "ML_AdjustNormalIntensity"
    }
}

def format_filter_name(material_channel_name, filter_index):
    '''Correctly formats the name of material filter nodes.'''
    static_channel_name = bau.format_static_channel_name(material_channel_name)
    return "{0}_FILTER_{1}".format(static_channel_name, str(filter_index))

def count_filter_nodes(material_channel_name):
    '''Returns the total count of the number of filter nodes for the specified material channel.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node = material_layers.get_material_layer_node('LAYER', selected_layer_index)
    filter_count = 0
    filter_exists = True
    while filter_exists:
        filter_node_name = format_filter_name(material_channel_name, filter_count + 1)
        filter_node = layer_node.node_tree.nodes.get(filter_node_name)
        if filter_node:
            filter_count += 1
        else:
            filter_exists = False
    return filter_count

def get_filter_info(filter_type, filter_info):
    '''Returns the main socket index for the specified filter node.'''
    if filter_type in FILTER_INFO:
        info = FILTER_INFO[filter_type]
        if info:
            return info[filter_info]
    debug_logging.log("No filter info for: {0}".format(filter_type), message_type='ERROR')
    return 0

def get_filter_type(filter_node):
    '''Returns the static type name for the provided filter node.'''
    if filter_node.bl_static_type == 'GROUP':
        match filter_node.node_tree.name:
            case 'ML_CheapContrast':
                return 'CHEAP_CONTRAST'
            case 'ML_AdjustNormalIntensity':
                return 'NORMAL_INTENSITY'
            case _:
                debug_logging.log("Can't determing filter node type for filter node.")
                return 'INVALID_FILTER_TYPE'
    else:
        return filter_node.bl_static_type   

def relink_filter_nodes(material_channel_name):
    '''Relinks filter nodes to other existing filter nodes.'''
    # We don't need to link filters to other filters if there's only one.
    filter_count = count_filter_nodes(material_channel_name)
    if filter_count <= 1:
        return

    # Cycle through all existing filters and link all of them to each other.
    else:
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        layer_node_tree = material_layers.get_layer_node_tree(selected_layer_index)
        for i in range(1, filter_count):
            filter_one = get_filter_node(material_channel_name, i)
            filter_two = get_filter_node(material_channel_name, i + 1)
            if filter_one and filter_two:
                filter_type = get_filter_type(filter_two)
                output_socket = get_filter_info(filter_type, "main_output_socket")
                input_socket = get_filter_info(filter_type, "main_input_socket")
                bau.safe_node_link(filter_one.outputs[output_socket], filter_two.inputs[input_socket], layer_node_tree)

def add_material_channel_blur(self, layer_index, layer_node, material_channel_name):
    '''Adds a blur to the specified material channel by adding a blur node and triggering a relink for material channel projection.'''

    # Only one blur filter is required for material channels.
    # If a blur node exists, don't add another one.
    blur_node_name = material_layers.format_material_channel_node_name(material_channel_name, 'BLUR')
    blur_node = layer_node.node_tree.nodes.get(blur_node_name)
    if blur_node:
        debug_logging.log_status('Blur is already applied for this material channel.', self, type='INFO')
        return

    # If no blur node exists, append one based on the layer projection.
    projection_node = material_layers.get_material_layer_node('PROJECTION', layer_index)
    match projection_node.node_tree.name:
        case 'ML_TriplanarProjection':
            blur_node_tree = bau.append_group_node('ML_TriplanarBlur')
        case _:
            blur_node_tree = bau.append_group_node('ML_ProjectionBlur')

    new_blur_node = layer_node.node_tree.nodes.new('ShaderNodeGroup')
    new_blur_node.name = blur_node_name
    new_blur_node.label = new_blur_node.name
    new_blur_node.node_tree = blur_node_tree
    new_blur_node.hide = True

    # Parent the blur node to the material channels frame, 
    frame = material_layers.get_material_layer_node('FRAME', layer_index, material_channel_name)
    if frame:
        new_blur_node.parent = frame

    # Move the blur node above the value node.
    value_node = material_layers.get_material_layer_node('VALUE', layer_index, material_channel_name)
    if value_node:
        new_blur_node.location = [value_node.location[0], value_node.location[1] + 100]
        new_blur_node.width = value_node.width

    # Re-link layer projection for the material channel.
    material_layers.relink_material_channel(material_channel_name)

def remove_material_channel_blur(layer_index, layer_node, material_channel_name):
    '''Removes the blur applied to the material channel by deleting the blur node and triggering a relink for material channel projection.'''
    blur_node = material_layers.get_material_layer_node('BLUR', layer_index, material_channel_name)
    if blur_node:
        layer_node.node_tree.nodes.remove(blur_node)
    
    # Re-link layer projection for the material channel.
    material_layers.relink_material_channel(material_channel_name)

def add_material_filter(self, material_channel_name, filter_type):
    '''Adds a filter of the specified type to the specified material channel'''

    # Verify standard context is correct.
    if bau.verify_material_operation_context(self, check_active_material=False) == False:
        return
    
    # Add the filter node of the specified type to the node tree.
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node = material_layers.get_material_layer_node('LAYER', selected_layer_index)

    # For blur filters, perform special setup steps.
    if filter_type == 'BLUR':
        add_material_channel_blur(self, selected_layer_index, layer_node, material_channel_name)
        return

    node_type = get_filter_info(filter_type, "bpy_node_name")
    new_filter_node = layer_node.node_tree.nodes.new(node_type)
    
    # Name the filter node with an index to determine it's connection order.
    static_channel_name = bau.format_static_channel_name(material_channel_name)
    filter_index = 1
    filter_node_name = format_filter_name(material_channel_name, filter_index)
    filter_node = layer_node.node_tree.nodes.get(filter_node_name)
    while filter_node:
        filter_index += 1
        filter_node_name = format_filter_name(material_channel_name, filter_index)
        filter_node = layer_node.node_tree.nodes.get(filter_node_name)
    new_filter_node.name = filter_node_name
    new_filter_node.label = get_filter_info(filter_type, "node_label")

    # Parent the new filter node to the respective channel frame.
    frame = layer_node.node_tree.nodes.get(static_channel_name)
    new_filter_node.parent = frame

    # Append and insert filter node groups if necessary.
    filter_node_tree = None
    match filter_type:
        case 'CHEAP_CONTRAST':
            filter_node_tree = bau.append_group_node('ML_CheapContrast')
        case 'NORMAL_INTENSITY':
            filter_node_tree = bau.append_group_node('ML_AdjustNormalIntensity')
    if filter_node_tree != None:
        new_filter_node.node_tree = filter_node_tree

    # Relink the nodes for the material channel to link the new filters.
    relink_filter_nodes(material_channel_name)
    original_crgba_output = material_layers.get_material_channel_crgba_output(material_channel_name)
    material_layers.relink_material_channel(material_channel_name, original_crgba_output, unlink_projection=False)

    # Organize filter nodes.
    organize_filter_nodes(material_channel_name)

    # Log action.
    debug_logging.log("Added {0} filter to {1}.".format(filter_type, material_channel_name))

def delete_material_filter(material_channel_name, filter_index, filter_type):
    '''Deletes the material filter node with the specified index.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node = material_layers.get_material_layer_node('LAYER', selected_layer_index)

    # Perform special steps to delete blur filters.
    if filter_type == 'BLUR':
        remove_material_channel_blur(selected_layer_index, layer_node, material_channel_name)
        return

    # Remember the original CRGBA output for the material channel so it can be reset properly after deleting nodes.
    original_crgba_output = material_layers.get_material_channel_crgba_output(material_channel_name)

    # Delete the specified filter.
    filter_node_name = format_filter_name(material_channel_name, filter_index)
    filter_node = layer_node.node_tree.nodes.get(filter_node_name)
    if filter_node:
        layer_node.node_tree.nodes.remove(filter_node)

    # Rename all filter nodes above the deleted one.
    filter_index += 1
    filter_node_name = format_filter_name(material_channel_name, filter_index)
    filter_node = layer_node.node_tree.nodes.get(filter_node_name)
    while filter_node:
        filter_node.name = format_filter_name(material_channel_name, filter_index - 1)
        filter_index += 1
        filter_node_name = format_filter_name(material_channel_name, filter_index)
        filter_node = layer_node.node_tree.nodes.get(filter_node_name)
    
    # Trigger a relink of material channel nodes so filters will be linked properly.
    relink_filter_nodes(material_channel_name)
    material_layers.relink_material_channel(material_channel_name, original_crgba_output, unlink_projection=False)

    # Organize filter nodes.
    organize_filter_nodes(material_channel_name)

    # Log action.
    debug_logging.log("Deleted filter at index {0}".format(filter_index))

def get_filter_node(material_channel_name, filter_index):
    '''Returns the filter with the specified index.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node = material_layers.get_material_layer_node('LAYER', selected_layer_index)
    filter_node_name = format_filter_name(material_channel_name, filter_index)
    return layer_node.node_tree.nodes.get(filter_node_name)

def organize_filter_nodes(material_channel_name):
    '''Organizes all filter nodes within the material channel frame.'''

    # Cycle through all filter nodes and set the location, width and collapse / hide them.
    filter_index = 1
    filter_x = FILTER_DEFAULT_LOCATION_X
    filter_y = FILTER_DEFAULT_LOCATION_Y
    filter_node = get_filter_node(material_channel_name, filter_index)
    while filter_node:
        filter_node.location[0] = filter_x
        filter_node.location[1] = filter_y
        filter_node.width = FILTER_NODE_WIDTH
        filter_node.hide = True

        # Add spacing between nodes.
        filter_y -= FILTER_SPACING

        # Increment the index to organize the next filter node.
        filter_index += 1
        filter_node = get_filter_node(material_channel_name, filter_index)

class MATLAYER_OT_add_material_filter(Operator):
    bl_label = "Add Material Filter"
    bl_idname = "matlayer.add_material_filter"
    bl_description = "Adds a filter of the specified type to the specified material channel"
    bl_options = {'REGISTER', 'UNDO'}

    filter_type: StringProperty()
    material_channel: StringProperty()

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_material_filter(self, self.material_channel, self.filter_type)
        return {'FINISHED'}
  
class MATLAYER_OT_delete_material_filter(Operator):
    bl_label = "Delete Material Filter"
    bl_idname = "matlayer.delete_material_filter"
    bl_description = "Deletes the specified material filter"
    bl_options = {'REGISTER', 'UNDO'}

    filter_index: IntProperty()
    material_channel: StringProperty()
    filter_type: StringProperty(default='NORMAL')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        delete_material_filter(self.material_channel, self.filter_index, self.filter_type)
        return {'FINISHED'}