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

def update_node_labels(context):
    '''Update the labels for all layer nodes.'''
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    group_node_name = context.active_object.active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)

    # Rename all layer nodes with their appropriate index.
    for x in range(2):
        for i in range(len(layers), 0, -1):
                index = i - 1
                layers = context.scene.coater_layers
                layer_stack = context.scene.coater_layer_stack
                group_node_name = context.active_object.active_material.name + "_" + str(layer_stack.channel)
                node_group = bpy.data.node_groups.get(group_node_name)

                # Update every nodes name and label only if they exist.
                frame = node_group.nodes.get(layers[index].frame_name)
                if frame != None:
                    frame.name = layers[index].layer_name  + "_" + str(index)
                    frame.label = frame.name
                    layers[index].frame_name = frame.name

                # Color Nodes
                color_node = node_group.nodes.get(layers[index].color_node_name)
                if color_node != None:
                    color_node.name = "Color_" + str(index)
                    color_node.label = color_node.name
                    layers[index].color_node_name = color_node.name

                coord_node_name = node_group.nodes.get(layers[index].coord_node_name)
                if coord_node_name != None:
                    coord_node_name.name = "Coord_" + str(index)
                    coord_node_name.label = coord_node_name.name
                    layers[index].coord_node_name = coord_node_name.name

                mapping_node = node_group.nodes.get(layers[index].mapping_node_name)
                if mapping_node != None:
                    mapping_node.name = "Mapping_" + str(index)
                    mapping_node.label = mapping_node.name
                    layers[index].mapping_node_name = mapping_node.name

                opacity_node = node_group.nodes.get(layers[index].opacity_node_name)
                if opacity_node != None:
                    opacity_node.name = "Opacity_" + str(index)
                    opacity_node.label = opacity_node.name
                    layers[index].opacity_node_name = opacity_node.name

                mix_layer_node = node_group.nodes.get(layers[index].mix_layer_node_name)
                if mix_layer_node != None:
                    mix_layer_node.name = "MixLayer_" + str(index)
                    mix_layer_node.label = mix_layer_node.name
                    layers[index].mix_layer_node_name = mix_layer_node.name

                # Mask Nodes
                mask_node = node_group.nodes.get(layers[index].mask_node_name)
                if mask_node != None:
                    mask_node.name = "Mask_" + str(index)
                    mask_node.label = mask_node.name
                    layers[index].mask_node_name = mask_node.name

                mask_mix_node = node_group.nodes.get(layers[index].mask_mix_node_name)
                if mask_mix_node != None:
                    mask_mix_node.name = "MaskMix_" + str(index)
                    mask_mix_node.label = mask_mix_node.name
                    layers[index].mask_mix_node_name = mask_mix_node.name

                mask_coord_node = node_group.nodes.get(layers[index].mask_coord_node_name)
                if mask_coord_node != None:
                    mask_coord_node.name = "MaskCoords_" + str(index)
                    mask_coord_node.label = mask_coord_node.name
                    layers[index].mask_coord_node_name = mask_coord_node.name

                mask_mapping_node = node_group.nodes.get(layers[index].mask_mapping_node_name)
                if mask_mapping_node != None:
                    mask_mapping_node.name = "MaskMapping_" + str(index)
                    mask_mapping_node.label = mask_mapping_node.name
                    layers[index].mask_mapping_node_name = mask_mapping_node.name

                mask_levels_node = node_group.nodes.get(layers[index].mask_levels_node_name)
                if mask_levels_node != None:
                    mask_levels_node.name = "MaskLevels_" + str(index)
                    mask_levels_node.label = mask_levels_node.name
                    layers[index].mask_levels_node_name = mask_levels_node.name