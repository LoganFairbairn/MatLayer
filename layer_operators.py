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

import os
import sys
import random
from . import layer_functions

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

class COATER_OT_add_image_layer(Operator):
    '''Adds a new blank image layer to the layer stack'''
    bl_idname = "coater.add_image_layer"
    bl_label = "Add Blank Image Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds an image layer with a new blank image assigned to it"

    def execute(self, context):
        layer_functions.add_layer_slot(self, context)
        layer_functions.ready_coater_material(self, context)
        layer_functions.create_channel_group_node(self, context)
        layer_functions.create_layer_nodes(self, context, 'IMAGE_LAYER')
        layer_functions.organize_nodes(self, context)
        layer_functions.link_layers(self, context)
        
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index
        layers[layer_index].layer_type = 'IMAGE_LAYER'
        
        # TODO: Make the image name match.
        # Assign the image an available name.
        layer_name = layers[layer_index].layer_name + "_" + str(random.randint(0, 99999))
        while bpy.data.images.get(layer_name) != None:
            layer_name = layers[layer_index].layer_name + "_" + str(random.randint(0, 99999))

        # Create a new image, assign it to the node.
        bpy.ops.image.new(name=layer_name,
                          width=1024,
                          height=1024,
                          color=(0.0, 0.0, 0.0, 0.0),
                          alpha=True,
                          generated_type='BLANK',
                          float=False,
                          use_stereo_3d=False,
                          tiled=False)

        # TODO: Auto-save the image to the image folder (defined in addon preferences).
        #bpy.data.images[layer_name].filepath = "G:/Projects/Coater/" + layer_name + ".png"
        #bpy.data.images[layer_name].file_format = 'PNG'
        #bpy.data.images[layer_name].save()

        # Put the image in the image node.
        node_group = layer_functions.get_channel_node_group(self, context)
        color_node = node_group.nodes.get(layers[layer_index].color_node_name)
        color_node.image = bpy.data.images[layer_name]

        # Store the active image in the layer.
        layers[layer_index].color_image = bpy.data.images[layer_name]

        # Update the active paint slot to the new image.
        if layer_index != -1:
            if layers[layer_index].color_image != None:
                context.scene.tool_settings.image_paint.canvas = layers[layer_index].color_image

        # Set the material shading mode, so the user can see the changes.
        layer_functions.set_material_shading(context)

        return {'FINISHED'}

class COATER_OT_add_empty_image_layer(Operator):
    '''Adds a new layer to the layer stack'''
    bl_idname = "coater.add_empty_image_layer"
    bl_label = "Add Empty Image Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds an image layer with no image assigned to it"

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        layer_functions.add_layer_slot(self, context)
        layer_functions.ready_coater_material(self, context)
        layer_functions.create_channel_group_node(self, context)
        layer_functions.create_layer_nodes(self, context, 'IMAGE_LAYER')
        layer_functions.organize_nodes(self, context)
        layer_functions.link_layers(self, context)

        # Update the layer's type.
        layers[layer_index].layer_type = 'IMAGE_LAYER'

        layer_functions.set_material_shading(context)

        return {'FINISHED'}

class COATER_OT_add_color_layer(Operator):
    '''Adds a new layer to the layer stack'''
    bl_idname = "coater.add_color_layer"
    bl_label = "Add Color Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds a new color layer"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.active_object

    # Runs the function.
    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        layer_functions.add_layer_slot(self, context)
        layer_functions.ready_coater_material(self, context)
        layer_functions.create_channel_group_node(self, context)
        layer_functions.create_layer_nodes(self, context, 'COLOR_LAYER')
        layer_functions.organize_nodes(self, context)
        layer_functions.link_layers(self, context)

        # Update the layer's type.
        layers[layer_index].layer_type = 'COLOR_LAYER'

        layer_functions.set_material_shading(context)

        return {'FINISHED'}

class COATER_OT_add_image_mask(Operator):
    bl_idname = "coater.add_image_mask"
    bl_label = "Add Image Mask"
    bl_description = "Adds an image mask to the selected layer."

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        # Create mask nodes.
        channel_node = layer_functions.get_channel_node(self, context)

        if channel_node != None:
            mask_node = channel_node.node_tree.nodes.new('ShaderNodeTexImage')
            mask_mix_node = channel_node.node_tree.nodes.new('ShaderNodeMixRGB')
            mask_coord_node = channel_node.node_tree.nodes.new(type='ShaderNodeTexCoord')
            mask_mapping_node = channel_node.node_tree.nodes.new(type='ShaderNodeMapping')
            mask_levels_node = channel_node.node_tree.nodes.new(type='ShaderNodeValToRGB')

            # Store mask nodes.
            layers[layer_index].mask_node_name = mask_node.name
            layers[layer_index].mask_mix_node_name = mask_mix_node.name
            layers[layer_index].mask_coord_node_name = mask_coord_node.name
            layers[layer_index].mask_mapping_name = mask_mapping_node.name
            layers[layer_index].mask_levels_node = mask_levels_node.name

        layer_functions.update_node_labels(self, context)
        layer_functions.organize_nodes(self, context)
        layer_functions.link_layers(self, context)

        # Add the nodes to the frame.
        frame = channel_node.node_tree.nodes.get(layers[layer_index].frame_name)
        if frame != None:
            mask_node.parent = frame
            mask_mix_node.parent = frame
            mask_coord_node.parent = frame
            mask_mapping_node.parent = frame
            mask_levels_node.parent = frame

        return{'FINISHED'}

class COATER_OT_delete_layer(Operator):
    '''Deletes the selected layer from the layer stack.'''
    bl_idname = "coater.delete_layer"
    bl_label = ""
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

        channel_node = layer_functions.get_channel_node(self, context)

        # If there is an image assigned to the layer, delete the image too.
        if layers[layer_index].color_image != None:
            bpy.data.images.remove(layers[layer_index].color_image)

        # Remove all nodes for this layer if they exist.
        node_list = layer_functions.get_layer_nodes(self, context, layer_index)
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
        layer_functions.link_layers(self, context)

        # Re-organize all nodes.
        layer_functions.organize_nodes(self, context)

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

        layer_functions.update_node_labels(self, context)   # Update the node lables.
        layer_functions.organize_nodes(self, context)       # Organize nodes

        return {'FINISHED'}

class COATER_OT_move_layer_up(Operator):
    """Moves the selected layer up on the layer stack."""
    bl_idname = "coater.move_layer_up"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the currently selected layer"

    # Poll tests if the operator can be called or not.
    @ classmethod
    def poll(cls, context):
        return context.scene.coater_layers

    def execute(self, context):
        layer_functions.move_layer(self, context, "Up")
        return{'FINISHED'}

class COATER_OT_move_layer_down(Operator):
    """Moves the selected layer down the layer stack."""
    bl_idname = "coater.move_layer_down"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the currently selected layer"
    
    # Poll tests if the operator can be called or not.
    @ classmethod
    def poll(cls, context):
        return context.scene.coater_layers

    def execute(self, context):
        layer_functions.move_layer(self, context, "Down")
        return{'FINISHED'}

class COATER_OT_merge_layer(Operator):
    """Merges the selected layer with the layer below."""
    bl_idname = "coater.merge_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Merges the selected layer with the layer below."

    @ classmethod
    def poll(cls, context):
        #return context.scene.coater_layers
        return False

    def execute(self, context):
        return{'FINISHED'}

class COATER_OT_duplicate_layer(Operator):
    """Duplicates the selected layer."""
    bl_idname = "coater.duplicate_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Duplicates the selected layer."

    @ classmethod
    def poll(cls, context):
        #return context.scene.coater_layers
        return False

    def execute(self, context):
        return{'FINISHED'}

class COATER_OT_toggle_channel_preview(Operator):
    bl_idname = "coater.toggle_channel_preview"
    bl_label = "Toggle Channel Preview"
    bl_description = "Toggles the preview for the current material channel"

    def execute(self, context):
        layer_stack = context.scene.coater_layer_stack
        material_nodes = context.active_object.active_material.node_tree.nodes
        active_material = context.active_object.active_material
        node_links = context.active_object.active_material.node_tree.links

        # Toggle preview off.
        if layer_stack.channel_preview == True:
            layer_stack.channel_preview = False

            principled_bsdf_node = material_nodes.get('Principled BSDF')
            material_output_node = material_nodes.get('Material Output')

            # Remove all links.
            channel_nodes = layer_functions.get_channel_nodes(self, context)
            for node in channel_nodes:
                node_links.clear()

            base_color_group = material_nodes.get(active_material.name + "_" + "BASE_COLOR")
            metallic_group = material_nodes.get(active_material.name + "_" + "METALLIC")
            roughness_group = material_nodes.get(active_material.name + "_" + "ROUGHNESS")
            height_group = material_nodes.get(active_material.name + "_" + "HEIGHT")

            if base_color_group != None:
                node_links.new(base_color_group.outputs[0], principled_bsdf_node.inputs[0])
                
            if metallic_group != None:
                node_links.new(metallic_group.outputs[0], principled_bsdf_node.inputs[4])

            if roughness_group != None:
                node_links.new(roughness_group.outputs[0], principled_bsdf_node.inputs[7])

            if height_group != None:
                node_links.new(height_group.outputs[0], principled_bsdf_node.inputs[20])

            node_links.new(principled_bsdf_node.outputs[0], material_output_node.inputs[0])

        # Toggle preview on.
        elif layer_stack.channel_preview == False:
            layer_stack.channel_preview = True

            # De-attach all channels from Principled BSDF shader.
            channel_nodes = layer_functions.get_channel_nodes(self, context)
            for node in channel_nodes:
                node_links.clear()

            # Attach the selected channel to the emission shader.
            emission_node = material_nodes.get('Emission')
            material_output_node = material_nodes.get('Material Output')
            group_node_name = active_material.name + "_" + str(layer_stack.channel)
            group_node = material_nodes.get(group_node_name)

            node_links.new(group_node.outputs[0], emission_node.inputs[0])
            node_links.new(emission_node.outputs[0], material_output_node.inputs[0])

        return {'FINISHED'}

class COATER_OT_import_color_image(Operator, ImportHelper):
    bl_idname = "coater.import_color_image"
    bl_label = ""
    bl_description = "Opens a menu that allows the user to import a color image."

    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp',
        options={'HIDDEN'}
    )

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        head_tail = os.path.split(self.filepath)
        image_name = head_tail[1]

        bpy.ops.image.open(filepath=self.filepath)

        layers[layer_index].color_image_name = self.filepath

        # Update the image node's value.
        group_node = layer_functions.get_channel_node_group(self, context)
        color_node_name = layers[layer_index].color_node_name
        color_node = group_node.nodes.get(color_node_name)

        if (color_node != None):
            color_node.image = bpy.data.images[image_name]

        layer_functions.organize_nodes(self, context)
        
        return {'FINISHED'}

class COATER_OT_refresh_layers(Operator):
    bl_idname = "coater.refresh_layers"
    bl_label = "Refresh Layers"
    bl_description = "Reads the layers in the active material and updates the layer stack based on that."

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_stack = context.scene.coater_layer_stack
        material_nodes = context.active_object.active_material.node_tree.nodes

        # Clear all layers.
        layers.clear()
        layer_stack.layer_index = -1

        # Make sure this is a coater material before rebuilding the layer stack.
        principled_bsdf = material_nodes.get('Principled BSDF')

        if principled_bsdf.label == "Coater PBR":
            # Check to see if there's nodes in the selected layer channel group node.
            node_group = layer_functions.get_channel_node_group(self, context)
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
                    layer_functions.add_layer_slot(self, context)

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
                        if frame_name_split[1] == str(i):
                            layers[i].layer_name = frame_name_split[0]
                            layers[i].frame_name = f.name
                            break

                    # Get nodes using their names and store the nodes in the layer.
                    color_node = node_group.nodes.get("Color_" + str(i))
                    opacity_node = node_group.nodes.get("Opacity_" + str(i))
                    mix_layer_node = node_group.nodes.get("MixLayer_" + str(i))
                    coord_node_name = node_group.nodes.get("Coord_" + str(i))
                    mapping_node = node_group.nodes.get("Mapping_" + str(i))

                    if color_node != None:
                        if color_node.bl_static_type == 'TEX_IMAGE':
                            layers[i].color_node_name = color_node.name
                            layers[i].color_image = color_node.image
                            layers[i].layer_type = 'IMAGE_LAYER'

                        if color_node.bl_static_type == 'RGB':
                            layers[i].color_node_name = color_node.name
                            color = color_node.outputs[0].default_value
                            layers[i].color = (color[0], color[1], color[2])
                            layers[i].layer_type = 'COLOR_LAYER'

                    if opacity_node != None:
                        layers[i].opacity_node_name = opacity_node.name
                        layers[i].layer_opacity = opacity_node.inputs[1].default_value

                    if mix_layer_node != None:
                        layers[i].mix_layer_node_name = mix_layer_node.name
                        layers[i].blend_mode = mix_layer_node.blend_type

                    if coord_node_name != None:
                        layers[i].coord_node_name = coord_node_name.name

                    if mapping_node != None:
                        layers[i].mapping_node_name = mapping_node.name

                    # Organize the nodes for good measure.
                    layer_functions.organize_nodes(self, context)

        return {'FINISHED'}
