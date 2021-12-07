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
from bpy.types import Operator, PropertyGroup
from .import coater_node_info
from .import add_layer_slot
from .import organize_layer_nodes
from .import coater_material_functions

class COATER_OT_refresh_layers(Operator):
    bl_idname = "coater.refresh_layers"
    bl_label = "Refresh Layers"
    bl_description = "Reads the layers in the active material and updates the layer stack based on that"

    def execute(self, context):
        # Make sure the active material is a Coater material before attempting to refresh the layer stack.
        if coater_material_functions.check_coater_material(context) == False:
            return {'FINISHED'}

        layers = context.scene.coater_layers
        layer_stack = context.scene.coater_layer_stack
        material_nodes = context.active_object.active_material.node_tree.nodes

        # Clear all layers.
        layers.clear()
        layer_stack.layer_index = -1

        # Check to see if there's nodes in the selected layer channel group node.
        node_group = coater_node_info.get_channel_node_group(context)
        if node_group != None:

            # Get the total number of layers using mix nodes.
            total_layers = 0
            for x in range(0, 100):
                node = node_group.nodes.get("MixLayer_" + str(x))
                if(node != None):
                    total_layers += 1
                else:
                    break

            # Add a layer slot for each layer.
            for i in range(total_layers):
                add_layer_slot.add_layer_slot(context)

            # Get all of the frame nodes.
            frame_nodes = []
            for n in node_group.nodes:
                if n.bl_static_type == 'FRAME':
                    frame_nodes.append(n)

            # Read and store node values.
            for i in range(0, total_layers):

                # Get the layer name from the frame node.
                for f in frame_nodes:
                    frame_name_split = f.name.split('_')
                    if frame_name_split[2] == str(i):
                        id = int(frame_name_split[1])
                        layers[i].id = id
                        layers[i].name = frame_name_split[0]
                        layers[i].frame_name = f.name
                        break

                # Get nodes using their names and store the nodes in the layer.
                color_node = node_group.nodes.get("Color_" + str(i))
                if color_node != None:
                    if color_node.bl_static_type == 'TEX_IMAGE':
                        layers[i].color_node_name = color_node.name
                        layers[i].color_image = color_node.image
                        layers[i].type = 'IMAGE_LAYER'
                        layers[i].projection = color_node.projection

                    if color_node.bl_static_type == 'RGB':
                        layers[i].color_node_name = color_node.name
                        color = color_node.outputs[0].default_value
                        layers[i].color = (color[0], color[1], color[2])
                        layers[i].type = 'COLOR_LAYER'

                # Read hidden layers.
                if color_node.mute:
                    layers[i].hidden = True

                opacity_node = node_group.nodes.get("Opacity_" + str(i))
                if opacity_node != None:
                    layers[i].opacity_node_name = opacity_node.name
                    layers[i].layer_opacity = opacity_node.inputs[1].default_value

                mix_layer_node = node_group.nodes.get("MixLayer_" + str(i))
                if mix_layer_node != None:
                    layers[i].mix_layer_node_name = mix_layer_node.name
                    layers[i].blend_mode = mix_layer_node.blend_type

                coord_node_name = node_group.nodes.get("Coord_" + str(i))
                if coord_node_name != None:
                    layers[i].coord_node_name = coord_node_name.name

                mapping_node = node_group.nodes.get("Mapping_" + str(i))
                if mapping_node != None:
                    layers[i].mapping_node_name = mapping_node.name

                mask_node = node_group.nodes.get("Mask_" + str(i))
                if mask_node != None:
                    layers[i].mask_node_name = mask_node.name
                    layers[i].masked = True

                    if mask_node.bl_static_type == 'TEX_IMAGE':
                        layers[i].mask_projection = mask_node.projection

                mask_mix_node = node_group.nodes.get("MaskMix_" + str(i))
                if mask_mix_node != None:
                    layers[i].mask_mix_node_name = mask_mix_node.name

                mask_coord_node = node_group.nodes.get("MaskCoords_" + str(i))
                if mask_coord_node != None:
                    layers[i].mask_coord_node_name = mask_coord_node.name

                mask_mapping_node = node_group.nodes.get("MaskMapping_" + str(i))
                if mask_mapping_node != None:
                    layers[i].mask_mapping_node_name = mask_mapping_node.name

                mask_levels_node = node_group.nodes.get("MaskLevels_" + str(i))
                if mask_levels_node != None:
                    layers[i].mask_levels_node_name = mask_levels_node.name

                # Organize the nodes for good measure.
                organize_layer_nodes.organize_layer_nodes(context)

            # If the top layer is a layer image, select the image as the active paint image.
            image = coater_node_info.get_layer_image(context, 0)
            if image != None:
                context.scene.tool_settings.image_paint.canvas = image

        return {'FINISHED'}
