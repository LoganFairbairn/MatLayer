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
import random
import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

# Adds a color layer.
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

        bpy.ops.coater.add_layer_slot()
        ready_coater_material(self, context)
        ready_channel_group_node(self, context)
        create_layer_nodes(self, context, 1)
        organize_nodes(self, context)
        link_layers(self, context)

        # Update the layer's type.
        layers[layer_index].layer_type = 'COLOR_LAYER'

        set_material_shading(context)

        return {'FINISHED'}

# Adds an image layer.
class COATER_OT_add_image_layer(bpy.types.Operator):
    '''Adds a new layer to the layer stack'''
    bl_idname = "coater.add_image_layer"
    bl_label = "Add Image Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds a new color layer"

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        bpy.ops.coater.add_layer_slot()
        ready_coater_material(self, context)
        ready_channel_group_node(self, context)
        create_layer_nodes(self, context, 0)
        organize_nodes(self, context)
        link_layers(self, context)

        # Update the layer's type.
        layers[layer_index].layer_type = 'IMAGE_LAYER'

        set_material_shading(context)

        return {'FINISHED'}

# Adds a image layer with a blank image.
class COATER_OT_add_blank_image_layer(bpy.types.Operator):
    '''Adds a new blank image layer to the layer stack'''
    bl_idname = "coater.add_blank_image_layer"
    bl_label = "Add Blank Image Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds a blank image layer to the layer stack"

    def execute(self, context):
        bpy.ops.coater.add_layer_slot()
        ready_coater_material(self, context)
        ready_channel_group_node(self, context)
        create_layer_nodes(self, context, 0)
        organize_nodes(self, context)
        link_layers(self, context)

        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index
        layers[layer_index].layer_type = 'IMAGE_LAYER'
        active_material = context.object.active_material
        
        # TODO: Make the image name match.
        # Assign the image an available name.
        layer_name = "Layer " + str(random.randint(0, 99999))
        while bpy.data.images.get(layer_name) != None:
            layer_name = "Layer " + str(random.randint(0, 99999))

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
        bpy.data.images[layer_name].filepath = "G:/Projects/Coater/" + layer_name + ".png"
        bpy.data.images[layer_name].file_format = 'PNG'
        bpy.data.images[layer_name].save()

        # Put the image in the image node.
        group_node = get_current_channel_group_node(self, context)
        color_node = group_node.nodes.get(layers[layer_index].color_node_name)
        color_node.image = bpy.data.images[layer_name]

        # Store the active image in the layer.
        layers[layer_index].color_image = bpy.data.images[layer_name]

        # Update the active paint slot to the new image.
        bpy.context.scene.tool_settings.image_paint.mode = 'MATERIAL'
        active_material.paint_active_slot = len(active_material.texture_paint_slots) - 1

        # Set the material shading mode, so the user can see the changes.
        set_material_shading(context)

        return {'FINISHED'}

# Adds an image mask nodes to the selected layer.
class COATER_OT_add_image_mask(bpy.types.Operator):
    bl_idname = "coater.add_image_mask"
    bl_label = "Add Mask"
    bl_description = "Adds an image mask to the selected layer."

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
        return{'FINISHED'}

# Deletes the selected layer.
class COATER_OT_delete_layer(bpy.types.Operator):
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

        node_group = get_current_channel_group_node(self, context)

        # If there is an image assigned to the layer, delete the image too.
        if layers[layer_index].color_image != None:
            bpy.data.images.remove(layers[layer_index].color_image)
            print("Removed image assigned to layer.")

        # Remove all nodes for this layer if they exist.
        node_list = get_layer_nodes(self, context, layer_index)
        for node in node_list:
            node_group.nodes.remove(node)

        # Remove the layer from the list.
        layers.remove(layer_stack.layer_index)
        layer_stack.layer_index = min(max(0, layer_stack.layer_index - 1), len(layers) - 1)

        # Organize all nodes.
        organize_nodes(self, context)

        # Connect layers.
        link_layers(self, context)

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

        # Update the node lables.
        update_node_labels(self, context)

        return {'FINISHED'}

# Moves the layer up on the layer stack.
class COATER_OT_move_layer_up(bpy.types.Operator):
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
        move_layer(self,context, "Up")
        return{'FINISHED'}

# Moves the selected layer down on the layer stack.
class COATER_OT_move_layer_down(bpy.types.Operator):
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
        move_layer(self,context, "Down")
        return{'FINISHED'}

# Merges the selected layer with the layer below.
class COATER_OT_merge_layer(bpy.types.Operator):
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

# Duplicates the selected layer.
class COATER_OT_duplicate_layer(bpy.types.Operator):
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

# Toggles the channel preview on and off.
class COATER_OT_toggle_channel_preview(bpy.types.Operator):
    bl_idname = "coater.toggle_channel_preview"
    bl_label = ""
    bl_description = "Toggles the preview for the current material channel"

    def execute(self, context):
        # TODO: Disconnect all channels (group nodes) and connect only the selected channel.
        layer_stack = context.scene.coater_layer_stack
        material_nodes = context.active_object.active_material.node_tree.nodes
        node_links = context.active_object.active_material.node_tree.links

        if layer_stack.channel_preview == True:
            layer_stack.channel_preview = False
            # If an emission shader exists, delete it.
            emission_node = material_nodes.get('Emission')
            if emission_node != None:
                material_nodes.remove(emission_node)

            # Detach all channels from Principled BSDF shader.
            channel_nodes = get_channel_nodes(self, context)
            for node in channel_nodes:
                node_links.clear()

        elif layer_stack.channel_preview == False:
            layer_stack.channel_preview = True
            # If there is no emission node, make one.
            emission_node = material_nodes.new('ShaderNodeEmission')

            # Position the emission node over the Material Output node.
            material_output_node = material_nodes.get('Material Output')

            emission_node.width = material_output_node.width

            node_spacing = layer_stack.node_spacing
            emission_node.location = (material_output_node.location[0], material_output_node.location[1] + node_spacing)

            # TODO: De-attach all channels from Principled BSDF shader.

        return {'FINISHED'}

# Opens a file browser where a user can select an image to import.
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
        group_node = get_current_channel_group_node(self, context)
        color_node_name = layers[layer_index].color_node_name
        color_node = group_node.nodes.get(color_node_name)

        if (color_node != None):
            color_node.image = bpy.data.images[image_name]

        organize_nodes(self, context)
        
        return {'FINISHED'}

# Reads node label's in the active material.
class COATER_OT_refresh_layers(Operator):
    bl_idname = "coater.refresh_layers"
    bl_label = "Refresh Layers"
    bl_description = "Reads the layers in the active material and updates the layer stack based on that."

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_stack = context.scene.coater_layer_stack
        layer_index = context.scene.coater_layer_stack.layer_index

        # Clear all layers.
        layers.clear()

        # Check to see if there's nodes in the selected layer channel group node.
        node_group = get_current_channel_group_node(self, context)
        if node_group != None:

            # Rebuild the layer stack by reading the layer nodes.

            # Get the total number of layers.
            total_layers = 0
            for x in range(0, 100):
                node = node_group.nodes.get("MixLayer_" + str(x)) # ERROR Incorrect name.
                if(node != None):
                    total_layers += 1
                else:
                    break

            # Rebuild each layer in the layer stack.
            for i in range(0, int(total_layers)):
                # Add a layer slot.
                bpy.ops.coater.add_layer_slot()

                # Get nodes using their names and store the nodes in the layer.
                color_node = node_group.nodes.get("Color_" + str(i))
                opacity_node = node_group.nodes.get("Opacity_" + str(i))
                mix_layer_node = node_group.nodes.get("MixLayer_" + str(i))

                # Set the layer stack values equal to the node values.
                if color_node != None:
                    color = color_node.outputs[0].default_value
                    layers[layer_index].color = (color[0], color[1], color[2])

                if opacity_node != None:
                    opacity = opacity_node.inputs[1].default_value
                    layers[layer_index].layer_opacity = opacity

                if mix_layer_node != None:
                    blend_mode = mix_layer_node.blend_type
                    layers[layer_index].blend_mode = blend_mode

                # Store the node names in the layer.
                layers[layer_index].color_node_name = color_node.name
                layers[layer_index].opacity_node_name = opacity_node.name
                layers[layer_index].mix_layer_node_name = mix_layer_node.name

                # Organize the nodes for good measure.
                organize_nodes(self, context)
        return {'FINISHED'}

# Adds an empty layer slot to the layer stack.
class COATER_OT_add_layer_slot(Operator):
    bl_idname = "coater.add_layer_slot"
    bl_label = "Add Layer Slot"
    bl_description = "Adds an empty layer slot to the layer stack."

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_stack = context.scene.coater_layer_stack
        layer_index = context.scene.coater_layer_stack.layer_index

        # TODO: New name must be UNIQUE
        # Add a new layer slot.
        layers.add()
        layers[len(layers) - 1].layer_name = "Layer"

        # Moves the new layer above the currently selected layer and selects it.
        if(layer_index != -1):
            move_index = len(layers) - 1
            move_to_index = max(0, min(layer_index, len(layers) - 1))
            layers.move(move_index, move_to_index)
            layer_index = move_to_index

        else:
            move_index = len(layers) - 1
            move_to_index = 0
            layers.move(move_index, move_to_index)
            layer_stack.layer_index = move_to_index 

        return {'FINISHED'}

# Organizes all nodes.
def organize_nodes(self, context):
    '''Organizes all nodes in the material node editor.'''
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    layer_stack = context.scene.coater_layer_stack
    active_material = context.active_object.active_material
    node_spacing = layer_stack.node_spacing

    # Organize channel nodes.
    group_nodes = get_channel_nodes(self, context)

    header_position = [0.0, 0.0]
    for node in group_nodes:
        if node != None:
            node.location = (-node.width + -node_spacing, header_position[1])
            header_position[1] -= node.height

    # Organize group output node.
    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)
    group_output_node = node_group.nodes.get('Group Output')
    group_output_node.location = (0.0, 0.0)

    # Organize all layer nodes.
    header_position = [0.0, 0.0]
    for i in range(0, len(layers)):
        header_position[0] -= layer_stack.node_default_width + node_spacing
        header_position[1] = 0.0

        # Organize all nodes in the layer.
        node_list = get_layer_nodes(self, context, layer_index)
        for node in node_list:
            node.width = layer_stack.node_default_width
            node.location = (header_position[0], header_position[1])
            header_position[1] -= ((node.height * 2) + node_spacing)

# Links all layers together by connecting their mix RGB nodes.
def link_layers(self, context):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    active_material = context.active_object.active_material
    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)

    # Organize all coater layer nodes.
    link = node_group.links.new
    group_output_node = node_group.nodes.get('Group Output')
    
    for x in range(len(layers), 0, -1):
        mix_layer_node = node_group.nodes.get(layers[x - 1].mix_layer_node_name)
        next_mix_layer_node = node_group.nodes.get(layers[x - 2].mix_layer_node_name)

        # Connect to the next layer if one exists.
        if x - 2 >= 0:
            node_group.links.new(mix_layer_node.outputs[0], next_mix_layer_node.inputs[2])

        # Connect to the Principled BSDF if there are no more layers.
        else:
            output = mix_layer_node.outputs[0]
            
            for l in output.links:
                if l != 0:
                    node_group.links.remove(l)
            node_group.links.new(mix_layer_node.outputs[0], group_output_node.inputs[0])

            # TODO: Disconnect mix layer node.

# Updates all node labels (allows nodes to be read later).
def update_node_labels(self, context):
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

                # Get the nodes stored in the layer.
                color_node = node_group.nodes.get(layers[index].color_node_name)
                uv_map_node = node_group.nodes.get(layers[index].uv_map_node_name)
                mapping_node = node_group.nodes.get(layers[index].mapping_node_name)
                opacity_node = node_group.nodes.get(layers[index].opacity_node_name)
                mix_layer_node = node_group.nodes.get(layers[index].mix_layer_node_name)

                # Update every nodes name and label only if they exist.
                if color_node != None:
                    color_node.name = "Color_" + str(index)
                    color_node.label = color_node.name
                    layers[index].color_node_name = color_node.name

                if uv_map_node != None:
                    uv_map_node.name = "UVMap_" + str(index)
                    uv_map_node.label = uv_map_node.name
                    layers[index].uv_map_node_name = uv_map_node.name

                if mapping_node != None:
                    mapping_node.name = "Mapping_" + str(index)
                    mapping_node.label = mapping_node.name
                    layers[index].mapping_node_name = mapping_node.name

                if opacity_node != None:
                    opacity_node.name = "Opacity_" + str(index)
                    opacity_node.label = opacity_node.name
                    layers[index].opacity_node_name = opacity_node.name

                if mix_layer_node != None:
                    mix_layer_node.name = "MixLayer_" + str(index)
                    mix_layer_node.label = mix_layer_node.name
                    layers[index].mix_layer_node_name = mix_layer_node.name

# Moves the selected layer up or down the layer stack.
def move_layer(self, context, direction):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    layer_index = context.scene.coater_layer_stack.layer_index

    index_to_move_to = max(0, min(layer_index + (-1 if direction == "Up" else 1), len(layers) - 1))
    layers.move(layer_index, index_to_move_to)
    layer_stack.layer_index = index_to_move_to

    organize_nodes(self, context)       # Re-organize nodes.
    update_node_labels(self, context)   # Re-name nodes.
    link_layers(self, context)          # Re-connect layers.

# Sets up a coater material.
def ready_coater_material(self, context):
    active_object = context.active_object
    active_material = context.active_object.active_material

    # Add a new Coater material if there is none.
    if active_object != None:
        if active_material == None:
            new_material = bpy.data.materials.new(name=active_object.name)
            active_object.data.materials.append(new_material)
            material_nodes = context.active_object.active_material.node_tree.nodes

            # The active material MUST use nodes.
            new_material.use_nodes = True

            # Material must be transparent.
            new_material.blend_method = 'CLIP'

            # Make a new emission node (used for channel previews).
            emission_node = material_nodes.new(type='ShaderNodeEmission')

            # Get the principled BSDF & material output node.
            principled_bsdf_node = material_nodes.get('Principled BSDF')
            material_output_node = material_nodes.get('Material Output')

            # Set the label of the Principled BSDF node (allows this material to be identified as a Coater material).
            principled_bsdf_node.label = "Coater PBR"

            # Adjust nodes locations.
            node_spacing = context.scene.coater_layer_stack.node_spacing
            principled_bsdf_node.location = (0.0, 0.0)
            material_output_node.location = (principled_bsdf_node.width + node_spacing, 0.0)
            emission_node.location = (0.0, emission_node.height + node_spacing)
            
    else:
        self.report({'WARNING'}, "Select an object.")
        return {'FINISHED'}

# Sets up a channel group node.
def ready_channel_group_node(self, context):
    active_material = context.active_object.active_material
    material_nodes = context.active_object.active_material.node_tree.nodes
    layer_stack = context.scene.coater_layer_stack
    node_spacing = context.scene.coater_layer_stack.node_spacing

    # Create a node group for the selected channel if one does not exist.
    group_node_name = active_material.name + "_" + str(layer_stack.channel)

    if(bpy.data.node_groups.get(group_node_name) == None):
        new_node_group = bpy.data.node_groups.new(group_node_name, 'ShaderNodeTree')

        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        new_node_group.outputs.new('NodeSocketColor', 'Base Color')

        group_output_node.width = layer_stack.node_default_width

    # Add the group node to the active material if there is there isn't a group node already.
    if material_nodes.get(group_node_name) == None:
        group_node = material_nodes.new('ShaderNodeGroup')
        group_node.node_tree = bpy.data.node_groups[group_node_name]
        group_node.name = group_node_name
        group_node.label = group_node_name
        group_node.width = layer_stack.node_default_width * 1.2

        # Link the group node with the Principled BSDF node.
        principled_bsdf_node = material_nodes.get('Principled BSDF')

        if principled_bsdf_node != None:
            node_links = active_material.node_tree.links

            # Link the group node to the correct channel.
            if layer_stack.channel == "BASE_COLOR":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[0])

            if layer_stack.channel == "ROUGHNESS":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[7])

            if layer_stack.channel == "METALLIC":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[4])

            if layer_stack.channel == "HEIGHT":
                node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[20])

# Creates layer nodes based on the given layer type.
def create_layer_nodes(self, context, layer_type):
    active_material = context.active_object.active_material
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the node group.
    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)

    # Create new nodes based on the layer type.
    if layer_type == 0:
        color_node = node_group.nodes.new(type='ShaderNodeTexImage')
        uv_map_node = node_group.nodes.new(type='ShaderNodeUVMap')
        mapping_node = node_group.nodes.new(type='ShaderNodeMapping')

    if layer_type == 1:
        color_node = node_group.nodes.new(type='ShaderNodeRGB')
    opacity_node = node_group.nodes.new(type='ShaderNodeMath')
    mix_layer_node = node_group.nodes.new(type='ShaderNodeMixRGB')

    # Store new nodes in the selected layer.
    layers[layer_index].color_node_name = color_node.name
    layers[layer_index].opacity_node_name = opacity_node.name
    layers[layer_index].mix_layer_node_name = mix_layer_node.name

    if layer_type == 0:
        layers[layer_index].uv_map_node_name = uv_map_node.name
        layers[layer_index].mapping_node_name = mapping_node.name

    # Update node labels.
    update_node_labels(self, context)

    # Set node default values.
    default_color = layers[layer_index].color
    color_node.outputs[0].default_value = (default_color[0], default_color[1], default_color[2], 1.0)
    opacity_node.operation = 'MULTIPLY'
    opacity_node.use_clamp = True
    opacity_node.inputs[0].default_value = 1
    opacity_node.inputs[1].default_value = 1
    mix_layer_node.inputs[0].default_value = 1
    mix_layer_node.use_clamp = True

    # Link nodes for this layer.
    link = node_group.links.new
    link(color_node.outputs[0], mix_layer_node.inputs[1])
    link(opacity_node.outputs[0], mix_layer_node.inputs[0])

    if layer_type == 0:
        link(uv_map_node.outputs[0], mapping_node.inputs[0])
        link(mapping_node.outputs[0], color_node.inputs[0])

    # TODO: Frame given nodes.
    #material_nodes = context.active_object.active_material.node_tree.nodes
    #group_node_name = active_material.name + "_" + str(layer_stack.channel)

    #group_node = material_nodes.get(group_node_name)
    #if group_node != None:
    #    material_nodes.active = group_node

    #bpy.context.area.type = 'NODE_EDITOR'
    #color_node.select = True
    #opacity_node.select = True
    #mix_layer_node.select = True
    #bpy.ops.node.join()
    #bpy.context.area.ui_type = 'VIEW_3D'

# Sets the material shading mode to 'Material'.
def set_material_shading(context):
    context.space_data.shading.type = 'MATERIAL'

# Returns the currently selected channel group node.
def get_current_channel_group_node(self, context):
    layer_stack = context.scene.coater_layer_stack
    active_material = context.active_object.active_material

    # TODO: Check for active material.
    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)
    return node_group

# Returns a list of all channel group nodes.
def get_channel_nodes(self, context):
    # Returns a list of all channel group nodes.
    active_material = context.active_object.active_material
    material_nodes = context.active_object.active_material.node_tree.nodes
        
    # Get references to all group nodes for all channels by their name.
    group_nodes = []
    group_nodes.append(material_nodes.get(active_material.name + "_" + "BASE_COLOR"))
    group_nodes.append(material_nodes.get(active_material.name + "_" + "METALLIC"))
    group_nodes.append(material_nodes.get(active_material.name + "_" + "ROUGHNESS"))
    group_nodes.append(material_nodes.get(active_material.name + "_" + "HEIGHT"))

    return group_nodes

# Returns a list of all nodes in the given layer.
def get_layer_nodes(self, context, layer_index):
    node_group = get_current_channel_group_node(self, context)
    
    color_node = node_group.nodes.get("Color_" + str(layer_index))
    uv_map_node = node_group.nodes.get("UVMap_" + str(layer_index))
    mapping_node = node_group.nodes.get("Mapping_" + str(layer_index))
    opacity_node = node_group.nodes.get("Opacity_" + str(layer_index))
    mix_node = node_group.nodes.get("MixLayer_" + str(layer_index))

    nodes = []
    
    if color_node != None:
        nodes.append(color_node)

    if uv_map_node != None:
        nodes.append(uv_map_node)

    if mapping_node != None:
        nodes.append(mapping_node)

    if opacity_node != None:
        nodes.append(opacity_node)

    if mix_node != None:
        nodes.append(mix_node)

    return nodes