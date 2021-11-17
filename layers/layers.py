# Copyright (c) 2021 Logan Fairbairn
# logan-fairbairn@outlook.com
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.types import PropertyGroup
import random
from .import coater_node_info
from .import link_layers

# When a property in the Coater UI is changed, these functions are triggered and their respective properties are updated.
def update_layer_name(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node = coater_node_info.get_channel_node(context)

    if layer_index != -1:

        # Rename the layer's frame node.
        frame = channel_node.node_tree.nodes.get(layers[layer_index].frame_name)
        if frame != None:
            frame.name = layers[layer_index].layer_name + "_" + str(layer_index)
            frame.label = frame.name
            layers[layer_index].frame_name = frame.name

        # If the layer has an image, rename the image to the layer's name.
        if coater_node_info.get_layer_image(context, layer_index) != None:
            image_name = layers[layer_index].layer_name + "_" + str(random.randint(0, 99999))

            while bpy.data.images.get(image_name) != None:
                image_name = layers[layer_index].layer_name + "_" + str(random.randint(0, 99999))

        # Rename layers with duplicate names.
        if len(layers) > 1:
            # If another layer has the new name already, rename that layer.
            duplicate_index = -1
            for i in range(len(layers)):

                # Do not check the renamed layer index.
                if i != layer_index:
                    if layers[layer_index].layer_name == layers[i].layer_name:
                        layers[i].layer_name = layers[i].layer_name + " copy"
                        duplicate_index = i

                        # Rename the frame node.
                        frame = channel_node.nodes.get(layers[i].frame_name)
                        if frame != None:
                            frame.name = layers[i].layer_name + " copy" + "_" + str(i)
                            frame.label = frame.name
                            layers[layer_index].frame_name = frame.name
                        break
            
            # Make sure the renamed layer doesn't have another layer name already.
            if duplicate_index != -1:
                duplicate_layer_name = layers[duplicate_index].layer_name
                layer_number = 0
                name_exists = True
                number_of_layers = len(layers)
                i = 0

                while(name_exists):
                    for i in range(number_of_layers):

                        # Do not check the duplicate layer index.
                        if i != duplicate_index:
                            if layers[i].layer_name == duplicate_layer_name:
                                layer_number += 1
                                duplicate_layer_name = duplicate_layer_name + str(layer_number)
                                break
                        
                        if i == number_of_layers - 1:
                            name_exists = False
                            layers[duplicate_index].layer_name = duplicate_layer_name

                            # TODO: Rename layer's frame node.
                            frame = channel_node.nodes.get(layers[duplicate_index].frame_name)
                            if frame != None:
                                frame.name = duplicate_layer_name + "_" + str(duplicate_index)
                                frame.label = frame.name
                                layers[duplicate_index].frame_name = frame.name

def update_layer_coord(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node_group = coater_node_info.get_channel_node_group(context)
    color_node = channel_node_group.nodes.get(layers[layer_index].color_node_name)
    coord_node = channel_node_group.nodes.get(layers[layer_index].coord_node_name)
    mapping_node = channel_node_group.nodes.get(layers[layer_index].mapping_node_name)

    # Delink coordinate node.
    outputs = coord_node.outputs
    for o in outputs:
        for l in o.links:
            if l != 0:
                channel_node_group.links.remove(l)

    # Connect nodes based on projection type.
    if layers[layer_index].layer_projection == 'FLAT':
        channel_node_group.links.new(coord_node.outputs[2], mapping_node.inputs[0])
        color_node.projection = 'FLAT'

    if layers[layer_index].layer_projection == 'BOX':
        channel_node_group.links.new(coord_node.outputs[0], mapping_node.inputs[0])
        color_node.projection = 'BOX'

    if layers[layer_index].layer_projection == 'SPHERE':
        channel_node_group.links.new(coord_node.outputs[0], mapping_node.inputs[0])
        color_node.projection = 'SPHERE'

    if layers[layer_index].layer_projection == 'TUBE':
        channel_node_group.links.new(coord_node.outputs[0], mapping_node.inputs[0])
        color_node.projection = 'TUBE'

def update_mapping_coord(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node_group = coater_node_info.get_channel_node_group(context)
    mask_node = channel_node_group.nodes.get(layers[layer_index].mask_node_name)
    mask_coord_node = channel_node_group.nodes.get(layers[layer_index].mask_coord_node_name)
    mask_mapping_node = channel_node_group.nodes.get(layers[layer_index].mask_mapping_node_name)

    # Delink coordinate node.
    outputs = mask_coord_node.outputs
    for o in outputs:
        for l in o.links:
            if l != 0:
                channel_node_group.links.remove(l)

    # Connect nodes based on projection type.
    if layers[layer_index].mask_projection == 'FLAT':
        channel_node_group.links.new(mask_coord_node.outputs[2], mask_mapping_node.inputs[0])
        mask_node.projection = 'FLAT'

    if layers[layer_index].mask_projection == 'BOX':
        channel_node_group.links.new(mask_coord_node.outputs[0], mask_mapping_node.inputs[0])
        mask_node.projection = 'BOX'

    if layers[layer_index].mask_projection == 'SPHERE':
        channel_node_group.links.new(mask_coord_node.outputs[0], mask_mapping_node.inputs[0])
        mask_node.projection = 'SPHERE'

    if layers[layer_index].mask_projection == 'TUBE':
        channel_node_group.links.new(mask_coord_node.outputs[0], mask_mapping_node.inputs[0])
        mask_node.projection = 'TUBE'

def update_layer_opacity(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    opacity_node = coater_node_info.get_node(context, 'OPACITY', layer_index)

    if opacity_node != None:
        opacity_node.inputs[1].default_value = layers[layer_index].layer_opacity

def update_hidden(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    layer_nodes = coater_node_info.get_layer_nodes(context, layer_index)

    if layers[layer_index].hidden == True:
        for n in layer_nodes:
            n.mute = True

    else:
        for n in layer_nodes:
            n.mute = False

    link_layers.link_layers(context)

class COATER_layers(PropertyGroup):
    '''Layer stack item.'''
    layer_name: bpy.props.StringProperty(
        name="",
        description="The name of the layer",
        default="Layer naming error",
        update=update_layer_name)

    layer_type: bpy.props.EnumProperty(
        items=[('IMAGE_LAYER', "Image Layer", ""),
               ('COLOR_LAYER', "Color Layer", "")],
        name="",
        description="Type of the layer",
        default='IMAGE_LAYER',
        options={'HIDDEN'},
    )

    layer_projection: bpy.props.EnumProperty(
        items=[('FLAT', "Flat", ""),
               ('BOX', "Box", ""),
               ('SPHERE', "Sphere", ""),
               ('TUBE', "Tube", "")],
        name="Projection",
        description="Projection type of the image attached to the selected layer",
        default='FLAT',
        update=update_layer_coord
    )

    mask_projection: bpy.props.EnumProperty(
        items=[('FLAT', "Flat", ""),
               ('BOX', "Box", ""),
               ('SPHERE', "Sphere", ""),
               ('TUBE', "Tube", "")],
        name="Projection",
        description="Projection type of the mask attached to the selected layer",
        default='FLAT',
        update=update_mapping_coord
    )

    layer_opacity: bpy.props.FloatProperty(name="Opacity",
                                           description="Opacity of the currently selected layer.",
                                           default=1.0,
                                           min=0.0,
                                           max=1.0,
                                           subtype='FACTOR',
                                           update=update_layer_opacity)

    hidden: bpy.props.BoolProperty(name="", update=update_hidden)
    masked: bpy.props.BoolProperty(name="", default=True)

    # Store nodes.
    frame_name: bpy.props.StringProperty(default="")
    coord_node_name: bpy.props.StringProperty(default="")
    mapping_node_name: bpy.props.StringProperty(default="")
    color_node_name: bpy.props.StringProperty(default="")
    opacity_node_name: bpy.props.StringProperty(default="")
    mix_layer_node_name: bpy.props.StringProperty(default="")

    # Store mask nodes.
    mask_node_name: bpy.props.StringProperty(default="")
    mask_mix_node_name: bpy.props.StringProperty(default="")
    mask_coord_node_name: bpy.props.StringProperty(default="")
    mask_mapping_node_name: bpy.props.StringProperty(default="")
    mask_levels_node_name: bpy.props.StringProperty(default="")