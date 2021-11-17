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

from os import link
import bpy
from bpy.types import Operator
from .import coater_node_info
from .import link_layers
from .import organize_layer_nodes
from .import update_node_labels

class COATER_OT_delete_layer(Operator):
    '''Deletes the selected layer from the layer stack.'''
    bl_idname = "coater.delete_layer"
    bl_label = "Delete Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the currently selected layer"

    @ classmethod
    def poll(cls, context):
        return context.scene.coater_layers

    def execute(self, context):
        # Delete the nodes stored in this layer.
        layers = context.scene.coater_layers
        layer_stack = context.scene.coater_layer_stack
        layer_index = context.scene.coater_layer_stack.layer_index

        channel_node = coater_node_info.get_channel_node(context)

        # If there is an image assigned to the layer, delete the image too.
        layer_image = coater_node_info.get_layer_image(context, layer_index)
        delete_unused_image(context, layer_image)

        # Remove all nodes for this layer if they exist.
        node_list = coater_node_info.get_layer_nodes(context, layer_index)
        for node in node_list:
            channel_node.node_tree.nodes.remove(node)

        # Remove node frame if it exists.
        frame = channel_node.node_tree.nodes.get(layers[layer_index].frame_name)
        if frame != None:
            channel_node.node_tree.nodes.remove(frame)

        # Remove the layer from the list.
        layers.remove(layer_stack.layer_index)
        layer_stack.layer_index = min(max(0, layer_stack.layer_index - 1), len(layers) - 1)

        # Re-link layers.
        link_layers.link_layers(context)

        # Re-organize all nodes.
        organize_layer_nodes.organize_layer_nodes(context)

        # If there are no layers left, delete the channel's node group from the blend file.
        active_material = context.active_object.active_material
        material_nodes = active_material.node_tree.nodes
        if layer_stack.layer_index == -1:
            group_node_name = active_material.name + "_" + str(layer_stack.channel)
            node_group = bpy.data.node_groups.get(group_node_name)
            group_node = material_nodes.get(group_node_name)

            if group_node != None:
                material_nodes.remove(group_node)

            if node_group != None:
                bpy.data.node_groups.remove(node_group)

        update_node_labels.update_node_labels(context)          # Update the node lables.
        organize_layer_nodes.organize_layer_nodes(context)      # Organize nodes

        return {'FINISHED'}

# Deletes the layer image if exists, and it's not being used in another layer.
def delete_unused_image(context, image):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Only attempt to delete the image if it exists.
    if image != None:
        layer_exist = False

        # Check all layers and all masks to see if this image is in use.
        for l in range(len(layers)):
            if l != layer_index:
                if coater_node_info.get_layer_image(context, l):
                    layer_exist = True
                    break

                if coater_node_info.get_layer_mask_image(context, l):
                    layer_exist = True
                    break

        if layer_exist == False:
            bpy.data.images.remove(image)

            # TODO: Delete the image from the folder too!