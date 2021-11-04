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
import random   # For random layer numbers.

# When a property in the Coater UI is changed, these functions are triggered and their respective properties are updated.
def update_layer_color(self, context):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    layer_index = context.scene.coater_layer_stack.layer_index
    active_material = context.active_object.active_material

    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)

    color = layers[layer_index].color

    color_node = node_group.nodes.get(layers[layer_index].color_node_name)
    if color_node != None:
        color_node.outputs[0].default_value = (color[0], color[1], color[2], 1.0)

def update_layer_opactity(self, context):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    layer_index = context.scene.coater_layer_stack.layer_index
    active_material = context.active_object.active_material

    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)

    opacity = layers[layer_index].layer_opacity

    opacity_node = node_group.nodes.get(layers[layer_index].opacity_node_name)
    if opacity_node != None:
        opacity_node.inputs[1].default_value = opacity

def update_blending_mode(self, context):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    layer_index = context.scene.coater_layer_stack.layer_index
    active_material = context.active_object.active_material
    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)

    blend_mode = layers[layer_index].blend_mode

    mix_layer_node = node_group.nodes.get(layers[layer_index].mix_layer_node_name)
    if mix_layer_node != None:
        mix_layer_node.blend_type = blend_mode

def update_layer_image(self, context):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    layer_index = context.scene.coater_layer_stack.layer_index
    active_material = context.active_object.active_material
    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)

    color_node = node_group.nodes.get(layers[layer_index].color_node_name)
    if color_node != None and color_node.bl_static_type == 'TEX_IMAGE':
        color_node.image = layers[layer_index].color_image

def update_layer_name(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node = get_channel_node(self, context)

    if layer_index != -1:

        # Rename the layer's frame node.
        frame = channel_node.node_tree.nodes.get(layers[layer_index].frame_name)
        if frame != None:
            frame.name = layers[layer_index].layer_name + "_" + str(layer_index)
            frame.label = frame.name
            layers[layer_index].frame_name = frame.name

        # If the layer has an image, rename the image to the layer's name.
        if layers[layer_index].color_image != None:
            image_name = layers[layer_index].layer_name + "_" + str(random.randint(0, 99999))

            while bpy.data.images.get(image_name) != None:
                image_name = layers[layer_index].layer_name + "_" + str(random.randint(0, 99999))

            layers[layer_index].color_image.name = image_name

            # TODO: Remame the saved image too!

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

class COATER_layers(bpy.types.PropertyGroup):
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

    blend_mode: bpy.props.EnumProperty(
        items=[('MIX', "Normal", "Set this layer's blending mode to normal (mix)"),
               ('DARKEN', "Darken","Set this layer's blending mode to darken"),
               ('MULTIPLY', "Multiply", "Set this layer's blending mode to multiply"),
               ('BURN', "Color Burn", "Set this layer's blending mode to color burn"),
               ('LIGHTEN', "Lighten", "Set this layer's blending mode to lighten"),
               ('SCREEN', "Screen", "Set this layer's blending mode to screen"),
               ('DODGE', "Color Dodge", "Set this layer's blending mode to Color Dodge"),
               ('ADD', "Add", "Set this layer's blending mode to add"),
               ('OVERLAY', "Overlay", "Set this layer's blending mode to overlay"),
               ('SOFT_LIGHT', "Soft Light", "Set this layer's blending mode to softlight"),
               ('LINEAR_LIGHT', "Linear Light", "Set this layer's blending mode to linear light"),
               ('DIFFERENCE', "Difference", "Set this layer's blending mode to difference"),
               ('SUBTRACT', "Subtract", "Set this layer's blending mode to subtract"),
               ('DIVIDE', "Divide", "Set this layer's blending mode to divide"),
               ('HUE', "Hue", "Set this layer's blending mode to hue"),
               ('SATURATION', "Saturation", "Set this layers blending mode to saturation"),
               ('COLOR', "Color", "Set this layer's blending mode to color"),
               ('VALUE', "Value", "Set this layer's blending mode to value")],
        name="",
        description="Blending mode of the layer.",
        default=None,
        options={'HIDDEN'},
        update=update_blending_mode
    )

    layer_hidden: bpy.props.BoolProperty(name="")
    masked: bpy.props.BoolProperty(name="", default=True)

    layer_opacity: bpy.props.FloatProperty(name="Opacity",
                                           description="Opacity of the currently selected layer.",
                                           default=1.0,
                                           min=0.0,
                                           max=1.0,
                                           subtype='FACTOR',
                                           update=update_layer_opactity)

    # Store nodes.
    frame_name: bpy.props.StringProperty(default="")
    coord_node_name: bpy.props.StringProperty(default="")
    mapping_node_name: bpy.props.StringProperty(default="")
    color_node_name: bpy.props.StringProperty(default="")
    opacity_node_name: bpy.props.StringProperty(default="")
    mix_layer_node_name: bpy.props.StringProperty(default="")

    mask_node_name: bpy.props.StringProperty(default="")
    mask_mix_node_name: bpy.props.StringProperty(default="")
    mask_coord_node_name: bpy.props.StringProperty(default="")
    mask_mapping_node_name: bpy.props.StringProperty(default="")
    mask_levels_node_name: bpy.props.StringProperty(default="")

    # TODO: These might be possible to access directly instead of storing them!
    # Store layer properties.
    color: bpy.props.FloatVectorProperty(name="", subtype='COLOR_GAMMA', min=0.0, max=1.0, update=update_layer_color)
    color_image: bpy.props.PointerProperty(name="Image", type=bpy.types.Image, update=update_layer_image)

def get_current_group_node(self, context):
    layer_stack = context.scene.coater_layer_stack
    active_material = context.active_object.active_material

    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)
    return node_group

def get_channel_node(self, context):
    active_material = context.active_object.active_material
    material_nodes = context.active_object.active_material.node_tree.nodes
    layer_stack = context.scene.coater_layer_stack

    return material_nodes.get(active_material.name + "_" + str(layer_stack.channel))