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
                bau.safe_node_link(filter_one.outputs[0], filter_two.inputs[0], layer_node_tree)

def add_material_filter(self, material_channel_name, filter_type):
    '''Adds a filter of the specified type to the specified material channel'''

    # Verify standard context is correct.
    if bau.verify_material_operation_context(self, check_active_material=False) == False:
        return
    
    # Based on the filter type, determine the Blender node name, and the node label.
    node_type = ""
    filter_node_label = "Error"
    match filter_type:
        case 'HSV':
            node_type = 'ShaderNodeHueSaturation'
            filter_node_label = "Hue Saturation Value"
        case 'INVERT':
            node_type = 'ShaderNodeInvert'
            filter_node_label = "Invert"
        case 'BRIGHTNESS_CONTRAST':
            node_type = 'ShaderNodeBrightContrast'
            filter_node_label = "Brightness Contrast"
        case 'GAMMA':
            node_type = 'ShaderNodeGamma'
            filter_node_label = "Gamma"
        case 'RGB_CURVES':
            node_type = 'ShaderNodeRGBCurves'
            filter_node_label = "Shader Node Curves"
        case 'RGB_TO_BW':
            node_type = 'ShaderNodeRGBToBW'
            filter_node_label = "RGB to BW"
        case 'COLOR_RAMP':
            node_type = 'ShaderNodeValToRGB'
            filter_node_label = "Color Ramp"
        case 'CHEAP_CONTRAST':
            node_type = 'ShaderNodeGroup'
            filter_node_label = "Cheap Contrast"
        case 'NORMAL_INTENSITY':
            node_type = 'ShaderNodeGroup'
            filter_node_label = "Normal Intensity"
        case _:
            debug_logging.log("Can't add material filter, invalid type: {0}".format(filter_type))
    
    # Add the filter node of the specified type to the node tree.
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node = material_layers.get_material_layer_node('LAYER', selected_layer_index)
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
    new_filter_node.label = filter_node_label

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

def delete_material_filter(material_channel_name, filter_index):
    '''Deletes the material filter node with the specified index.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_node = material_layers.get_material_layer_node('LAYER', selected_layer_index)

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

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        delete_material_filter(self.material_channel, self.filter_index)
        return {'FINISHED'}