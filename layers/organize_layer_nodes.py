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
from . import coater_node_info

def organize_layer_nodes(context):
    '''Organizes all coater nodes in the material node editor.'''
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    node_spacing = layer_stack.node_spacing

    # Organize channel nodes.
    channel_nodes = coater_node_info.get_channel_nodes(context)
    header_position = [0.0, 0.0]
    for node in channel_nodes:
        if node != None:
            node.location = (-node.width + -node_spacing, header_position[1])
            header_position[1] -= (node.height + (layer_stack.node_spacing * 0.5))

    # Organize all layer nodes.
    channel_node = coater_node_info.get_channel_node(context)
    header_position = [0.0, 0.0]
    for i in range(0, len(layers)):
        header_position[0] -= layer_stack.node_default_width + node_spacing
        header_position[1] = 0.0

        node_list = coater_node_info.get_layer_nodes(context, i)
        for node in node_list:
            node.width = layer_stack.node_default_width
            node.location = (header_position[0], header_position[1])
            header_position[1] -= (node.dimensions.y) + node_spacing

    # Organize group input node.
    if channel_node != None:
        header_position[0] -= layer_stack.node_default_width + node_spacing
        group_input_node = channel_node.node_tree.nodes.get('Group Input')
        group_input_node.location = (header_position[0], 0.0)
    
    # Organize group output node.
    if channel_node != None:
        group_output_node = channel_node.node_tree.nodes.get('Group Output')
        group_output_node.location = (0.0, 0.0)

    # If the current channel is a height channel, organize the bump node too.
    if layer_stack.channel == 'HEIGHT':
        if channel_node != None:
            bump_node = channel_node.node_tree.nodes.get('Bump')

            if bump_node != None:
                bump_node.location = (0.0, -group_input_node.dimensions.y - node_spacing)