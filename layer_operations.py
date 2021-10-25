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

# Adds a image layer with a blank image.
class COATER_OT_add_image_layer(bpy.types.Operator):
    '''Adds a new blank image layer to the layer stack'''
    bl_idname = "coater.add_image_layer"
    bl_label = "Add Blank Image Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds an image layer with a new blank image assigned to it"

    def execute(self, context):
        bpy.ops.coater.add_layer_slot()
        ready_coater_material(self, context)
        create_channel_group_node(self, context)
        create_layer_nodes(self, context, 'IMAGE_LAYER')
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

        # Auto-save the image to the image folder (defined in addon preferences).
        #bpy.data.images[layer_name].filepath = "G:/Projects/Coater/" + layer_name + ".png"
        #bpy.data.images[layer_name].file_format = 'PNG'
        #bpy.data.images[layer_name].save()

        # Put the image in the image node.
        group_node = get_channel_node_group(self, context)
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

# Adds an empty image layer.
class COATER_OT_add_empty_image_layer(bpy.types.Operator):
    '''Adds a new layer to the layer stack'''
    bl_idname = "coater.add_empty_image_layer"
    bl_label = "Add Empty Image Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds an image layer with no image assigned to it"

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index
        layer_stack = context.scene.coater_layer_stack

        bpy.ops.coater.add_layer_slot()
        ready_coater_material(self, context)
        create_channel_group_node(self, context)
        create_layer_nodes(self, context, 'IMAGE_LAYER')
        organize_nodes(self, context)
        link_layers(self, context)

        # Update the layer's type.
        layers[layer_index].layer_type = 'IMAGE_LAYER'

        set_material_shading(context)

        return {'FINISHED'}

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
        create_channel_group_node(self, context)
        create_layer_nodes(self, context, 'COLOR_LAYER')
        organize_nodes(self, context)
        link_layers(self, context)

        # Update the layer's type.
        layers[layer_index].layer_type = 'COLOR_LAYER'

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

        node_group = get_channel_node_group(self, context)

        # If there is an image assigned to the layer, delete the image too.
        if layers[layer_index].color_image != None:
            bpy.data.images.remove(layers[layer_index].color_image)

        # Remove all nodes for this layer if they exist.
        node_list = get_layer_nodes(self, context, layer_index)
        for node in node_list:
            node_group.nodes.remove(node)

        # Remove the layer from the list.
        layers.remove(layer_stack.layer_index)
        layer_stack.layer_index = min(max(0, layer_stack.layer_index - 1), len(layers) - 1)

        # Re-link layers.
        link_layers(self, context)

        # Re-organize all nodes.
        organize_nodes(self, context)

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
        move_layer(self, context, "Up")
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
        move_layer(self, context, "Down")
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
            channel_nodes = get_channel_nodes(self, context)
            for node in channel_nodes:
                node_links.clear()

            base_color_group = material_nodes.get(active_material.name + "_" + "BASE_COLOR")
            metallic_group = material_nodes.get(active_material.name + "_" + "METALLIC")
            roughness_group = material_nodes.get(active_material.name + "_" + "ROUGHNESS")
            height_group = material_nodes.get(active_material.name + "_" + "HEIGHT")

            if base_color_group != None:
                node_links.new(base_color_group.outputs[0], principled_bsdf_node.inputs[0])
                
            if metallic_group != None:
                node_links.new(metallic_group.outputs[0], principled_bsdf_node.inputs[7])

            if roughness_group != None:
                node_links.new(roughness_group.outputs[0], principled_bsdf_node.inputs[4])

            if height_group != None:
                node_links.new(height_group.outputs[0], principled_bsdf_node.inputs[20])

            node_links.new(principled_bsdf_node.outputs[0], material_output_node.inputs[0])
                    

        # Toggle preview on.
        elif layer_stack.channel_preview == False:
            layer_stack.channel_preview = True

            # De-attach all channels from Principled BSDF shader.
            channel_nodes = get_channel_nodes(self, context)
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
        group_node = get_channel_node_group(self, context)
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
        layer_index = context.scene.coater_layer_stack.layer_index

        # Clear all layers.
        layers.clear()

        # Check to see if there's nodes in the selected layer channel group node.
        node_group = get_channel_node_group(self, context)
        if node_group != None:

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
                uv_map_node = node_group.nodes.get("UVMap_" + str(i))
                mapping_node = node_group.nodes.get("Mapping_" + str(i))

                # If the node exists, store the node and it's values.
                if color_node != None:
                    # Store values based on node type.
                    if color_node.bl_static_type == 'TEX_IMAGE':
                        layers[layer_index].color_node_name = color_node.name
                        layers[layer_index].color_image = color_node.image

                    if color_node.bl_static_type == 'RGB':
                        layers[layer_index].color_node_name = color_node.name
                        color = color_node.outputs[0].default_value
                        layers[layer_index].color = (color[0], color[1], color[2])

                if opacity_node != None:
                    layers[layer_index].opacity_node_name = opacity_node.name
                    opacity = opacity_node.inputs[1].default_value
                    layers[layer_index].layer_opacity = opacity

                if mix_layer_node != None:
                    layers[layer_index].mix_layer_node_name = mix_layer_node.name
                    blend_mode = mix_layer_node.blend_type
                    layers[layer_index].blend_mode = blend_mode

                if uv_map_node != None:
                    layers[layer_index].uv_map_node_name = uv_map_node.name

                if mapping_node != None:
                    layers[layer_index].mapping_node_name = mapping_node.name

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

        # Add a new layer slot.
        layers.add()

        # TODO: Assign the layer a unique name.
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
    channel_node = get_channel_node(self, context)
    group_output_node = channel_node.node_tree.nodes.get('Group Output')
    group_output_node.location = (0.0, 0.0)

    # TODO: Organize all layer nodes.
    header_position = [0.0, 0.0]
    for i in range(0, len(layers)):
        header_position[0] -= layer_stack.node_default_width + node_spacing
        header_position[1] = 0.0

        # Organize all nodes in the layer.
        node_list = get_layer_nodes(self, context, i)
        for node in node_list:
            node.width = layer_stack.node_default_width
            node.location = (header_position[0], header_position[1])
            header_position[1] -= (node.dimensions.y) + node_spacing

# Links all layers together by connecting their mix RGB nodes.
def link_layers(self, context):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    active_material = context.active_object.active_material
    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)

    group_output_node = node_group.nodes.get('Group Output')
    
    for x in range(len(layers), 0, -1):
        mix_layer_node = node_group.nodes.get(layers[x - 1].mix_layer_node_name)
        next_mix_layer_node = node_group.nodes.get(layers[x - 2].mix_layer_node_name)

        # Connect to the next mix layer node if one exists.
        if x - 2 >= 0:
            node_group.links.new(mix_layer_node.outputs[0], next_mix_layer_node.inputs[1])

        # Connect to the color output if there are no more mix layer nodes.
        else:
            output = mix_layer_node.outputs[0]
            
            for l in output.links:
                if l != 0:
                    node_group.links.remove(l)
            node_group.links.new(mix_layer_node.outputs[0], group_output_node.inputs[0])

    # TODO: Link to alpha to calculate alpha nodes if required.

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

    update_node_labels(self, context)   # Re-name nodes.
    organize_nodes(self, context)       # Re-organize nodes.
    link_layers(self, context)          # Re-connect layers.

# Sets up a coater material.
def ready_coater_material(self, context):
    active_object = context.active_object
    active_material = context.active_object.active_material

    # Add a new Coater material if there is none.
    if active_object != None:

        # There is no active material, make one.
        if active_material == None:
            remove_all_material_slots()
            create_coater_material(self, context, active_object)

        # There is a material, make sure it's a Coater material.
        else:
            # If the material is a coater material, it's good to go!
            if active_material.node_tree.nodes.get('Principled BSDF').label == "Coater PBR":
                return {'FINISHED'}

            # If the material isn't a coater material, make a new material.
            else:
                remove_all_material_slots()
                create_coater_material(self, context, active_object)
            
    else:
        self.report({'WARNING'}, "There is no active object, select an object.")
        return {'FINISHED'}

# Removes all existing material slots from the active object.
def remove_all_material_slots():
    for x in bpy.context.object.material_slots:
        bpy.context.object.active_material_index = 0
        bpy.ops.object.material_slot_remove()

# Creates a new Coater specific material.
def create_coater_material(self, context, active_object):
    new_material = bpy.data.materials.new(name=active_object.name)
    active_object.data.materials.append(new_material)
    layer_stack = context.scene.coater_layer_stack
    
    # The active material MUST use nodes.
    new_material.use_nodes = True

    # Use alpha clip blend mode to make the material transparent.
    new_material.blend_method = 'CLIP'

    # Make a new emission node (used for channel previews).
    material_nodes = new_material.node_tree.nodes
    emission_node = material_nodes.new(type='ShaderNodeEmission')
    emission_node.width = layer_stack.node_default_width

    # Get the principled BSDF & material output node.
    principled_bsdf_node = material_nodes.get('Principled BSDF')
    principled_bsdf_node.width = layer_stack.node_default_width
    material_output_node = material_nodes.get('Material Output')

    # Set the label of the Principled BSDF node (allows this material to be identified as a Coater material).
    principled_bsdf_node.label = "Coater PBR"

    # Adjust nodes locations.
    node_spacing = context.scene.coater_layer_stack.node_spacing
    principled_bsdf_node.location = (0.0, 0.0)
    material_output_node.location = (principled_bsdf_node.width + node_spacing, 0.0)
    emission_node.location = (0.0, emission_node.height + node_spacing)

# Creates a channel group node (if one does not exist).
def create_channel_group_node(self, context):
    active_material = context.active_object.active_material
    material_nodes = context.active_object.active_material.node_tree.nodes
    layer_stack = context.scene.coater_layer_stack

    # Create a node group for the selected channel if one does not exist.
    group_node_name = active_material.name + "_" + str(layer_stack.channel)

    if bpy.data.node_groups.get(group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(group_node_name, 'ShaderNodeTree')

        group_output_node = new_node_group.nodes.new('NodeGroupOutput')
        new_node_group.outputs.new('NodeSocketColor', 'Base Color')
        new_node_group.outputs.new('NodeSocketFloat', 'Alpha')

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
    if layer_type == 'IMAGE_LAYER':
        color_node = node_group.nodes.new(type='ShaderNodeTexImage')
        uv_map_node = node_group.nodes.new(type='ShaderNodeUVMap')
        mapping_node = node_group.nodes.new(type='ShaderNodeMapping')

    if layer_type == 'COLOR_LAYER':
        color_node = node_group.nodes.new(type='ShaderNodeRGB')
    opacity_node = node_group.nodes.new(type='ShaderNodeMath')
    mix_layer_node = node_group.nodes.new(type='ShaderNodeMixRGB')

    # Store new nodes in the selected layer.
    layers[layer_index].color_node_name = color_node.name
    layers[layer_index].opacity_node_name = opacity_node.name
    layers[layer_index].mix_layer_node_name = mix_layer_node.name

    if layer_type == 'IMAGE_LAYER':
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
    mix_layer_node.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0)

    # Link nodes for this layer (based on layer type).
    link = node_group.links.new
    link(color_node.outputs[0], mix_layer_node.inputs[2])
    link(opacity_node.outputs[0], mix_layer_node.inputs[0])

    if layer_type == 'IMAGE_LAYER':
        link(color_node.outputs[1], opacity_node.inputs[0])
        link(uv_map_node.outputs[0], mapping_node.inputs[0])
        link(mapping_node.outputs[0], color_node.inputs[0])

    # TODO: Frame nodes.
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

    # If there is another layer already, add a group node to help calculate alpha blending.
    #if len(layers) > 1:
    #    create_calculate_alpha_node(self, context)

# Creates a group node for calculating alpha blending between layers (if one does not already exist).
def create_calculate_alpha_node(self, context):
    active_material = context.active_object.active_material
    material_nodes = context.active_object.active_material.node_tree.nodes
    layer_stack = context.scene.coater_layer_stack
    channel_node = get_channel_node(self, context)

    group_node_name = "Coater Calculate Alpha"
    if bpy.data.node_groups.get(group_node_name) == None:
        new_node_group = bpy.data.node_groups.new(group_node_name, 'ShaderNodeTree')

        # Create Nodes
        input_node = new_node_group.nodes.new('NodeGroupInput')
        output_node = new_node_group.nodes.new('NodeGroupOutput')
        subtract_node = new_node_group.nodes.new(type='ShaderNodeMath')
        multiply_node = new_node_group.nodes.new(type='ShaderNodeMath')
        add_node = new_node_group.nodes.new(type='ShaderNodeMath')

        # Add Sockets
        new_node_group.inputs.new('NodeSocketFloat', 'Alpha 1')
        new_node_group.inputs.new('NodeSocketFloat', 'Alpha 2')
        new_node_group.outputs.new('NodeSocketFloat', 'Alpha')

        # Set node values.
        subtract_node.operation = 'SUBTRACT'
        multiply_node.operation = 'MULTIPLY'
        add_node.operation = 'ADD'
        subtract_node.inputs[0].default_value = 1

        # Link nodes.
        link = new_node_group.links.new
        link(input_node.outputs[0], subtract_node.inputs[1])
        link(subtract_node.outputs[0], multiply_node.inputs[0])
        link(input_node.outputs[0], multiply_node.inputs[1])
        link(multiply_node.outputs[0], add_node.inputs[1])
        link(input_node.outputs[1], add_node.inputs[0])
        link(add_node.outputs[0], output_node.inputs[0])

        calculate_alpha_node = channel_node.node_tree.nodes.new('ShaderNodeGroup')
        calculate_alpha_node.node_tree = bpy.data.node_groups[group_node_name]
        calculate_alpha_node.name = group_node_name
        calculate_alpha_node.label = group_node_name
        calculate_alpha_node.width = layer_stack.node_default_width

        # Organize nodes.
        nodes = []
        nodes.append(input_node)
        nodes.append(subtract_node)
        nodes.append(multiply_node)
        nodes.append(add_node)
        nodes.append(output_node)

        header_position = [0.0, 0.0]
        for n in nodes:
            n.width = layer_stack.node_default_width
            n.location = (header_position[0], header_position[1])
            header_position[0] -= (layer_stack.node_default_width + layer_stack.node_spacing)

# Sets the material shading mode to 'Material'.
def set_material_shading(context):
    context.space_data.shading.type = 'MATERIAL'

# Returns the current channel node or None if one doesn't exist.
def get_channel_node(self, context):
    active_material = context.active_object.active_material
    material_nodes = context.active_object.active_material.node_tree.nodes
    layer_stack = context.scene.coater_layer_stack

    return material_nodes.get(active_material.name + "_" + str(layer_stack.channel))

# Returns the currently selected channel node group or None if one doesn't exist.
def get_channel_node_group(self, context):
    layer_stack = context.scene.coater_layer_stack
    active_material = context.active_object.active_material

    if active_material != None:
        group_node_name = active_material.name + "_" + str(layer_stack.channel)
        node_group = bpy.data.node_groups.get(group_node_name)
        return node_group
    
    else:
        return None

# Returns a list of all existing channel group nodes.
def get_channel_nodes(self, context):
    # Returns a list of all channel group nodes.
    active_material = context.active_object.active_material
    material_nodes = context.active_object.active_material.node_tree.nodes

    base_color_group = material_nodes.get(active_material.name + "_" + "BASE_COLOR")
    metallic_group = material_nodes.get(active_material.name + "_" + "METALLIC")
    roughness_group = material_nodes.get(active_material.name + "_" + "ROUGHNESS")
    height_group = material_nodes.get(active_material.name + "_" + "HEIGHT")

    group_nodes = []
    if base_color_group != None:
        group_nodes.append(base_color_group)
        
    if metallic_group != None:
        group_nodes.append(metallic_group)

    if roughness_group != None:
        group_nodes.append(roughness_group)

    if height_group != None:
        group_nodes.append(height_group)

    return group_nodes

# Returns a list of all existing nodes in the given layer.
def get_layer_nodes(self, context, layer_index):
    node_group = get_channel_node_group(self, context)
    
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