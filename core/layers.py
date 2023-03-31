# This file contains layer properties and functions for updating layer properties.

import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, FloatProperty, PointerProperty, FloatVectorProperty, EnumProperty
from ..core import layer_nodes
from . import material_channels
from ..utilities.info_messages import popup_message_box

# List of node types that can be used in the texture slot.
TEXTURE_NODE_TYPES = [
    ("COLOR", "Color", "A RGB color value is used to represent the material channel."), 
    ("VALUE", "Uniform Value", "RGB material channel values are represented uniformly by a single value. This mode is useful for locking the texture rgb representation to colourless values."),
    ("TEXTURE", "Texture", "An image texture is used to represent the material channel."),
    ("GROUP_NODE", "Group Node", "A custom group node is used to represent the material channel. You can create a custom group node and add it to the layer stack using this mode, with the only requirement being the first node output must be the main value used to represent the material channel."),
    ("NOISE", "Noise", "Procedurally generated noise is used to represent the material channel."),
    ("VORONOI", "Voronoi", "A procedurally generated voronoi pattern is used to represent the material channel."),
    ("MUSGRAVE", "Musgrave", "A procedurally generated musgrave pattern is used to represent the material channel.")
    ]

PROJECTION_MODES = [
    ("FLAT", "Flat", "Projects the texture using the model's UV map."),
    ("BOX", "Tri-Planar Projection", "Also known as 'cube, or box' projection, this projection method projects onto the 3D model from all axises."),
    ("SPHERE", "Sphere", ""),
    ("TUBE", "Tube", "")
    ]

TEXTURE_EXTENSION_MODES = [
    ("REPEAT", "Repeat", ""), 
    ("EXTEND", "Extend", ""),
    ("CLIP", "Clip", "")
    ]

TEXTURE_INTERPOLATION_MODES = [
    ("LINEAR", "Linear", ""),
    ("CUBIC", "Cubic", ""),
    ("CLOSEST", "Closest", ""),
    ("SMART", "Smart", "")
    ]

#----------------------------- UPDATE FUNCTIONS FOR GENERAL LAYER SETTNGS -----------------------------#

def update_layer_name(self, context):
    '''Updates the layers name in all layer frames when the layer name is changed.'''

    # Layer names can't contain underscores since they are used as delimiters to parse information from layer frames correctly.
    # If the layer name contains an underscore, throw the user an error message notifying them they can't use underscores in layer names.
    if '_' in self.name:
        popup_message_box("Layer names can't contain underscores.", "Error", 'ERROR')
        self.name = self.name.replace('_', "")
    
    else:
        # Update the frame name for all material channels on the layer that was changed.
        # Since the layer's name is already updated in the UI directly after a name change, a cached frame name (previous name) is used to get the layer frame nodes and update their names.
        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            material_channel = material_channels.get_material_channel_node(context, material_channel_name)
            cached_frame_name = self.cached_frame_name
            frame = material_channel.node_tree.nodes.get(cached_frame_name)
            if frame:
                new_name = self.name + "_" + str(self.id) + "_" + str(self.layer_stack_array_index)
                frame.name = new_name
                frame.label = frame.name

        # Update the cached frame name.
        self.cached_frame_name = self.name + "_" + str(self.id) + "_" + str(self.layer_stack_array_index)

def update_layer_opacity(self, context):
    '''Updates the layer opacity node values when the opacity is changed.'''
    selected_material_channel = context.scene.matlay_layer_stack.selected_material_channel
    opacity_node = layer_nodes.get_layer_node("OPACITY", selected_material_channel, self.layer_stack_array_index, context)
    if opacity_node:
        opacity_node.inputs[1].default_value = self.opacity

def update_hidden(self, context):
    '''Hide or unhide layers.'''
    material_channel_list = material_channels.get_material_channel_list()
    
    # Hide selected layer by muting all nodes within the layer.
    if self.hidden:
        for material_channel in material_channel_list:
            layer_nodes.mute_layer_material_channel(True, self.layer_stack_array_index, material_channel, context)

    # Unhide the selected layer by unmuting all active layers.
    else:
        for material_channel_name in material_channel_list:
            material_channel_active = getattr(self.material_channel_toggles, material_channel_name.lower() + "_channel_toggle")
            if material_channel_active:
                layer_nodes.mute_layer_material_channel(False, self.layer_stack_array_index, material_channel_name, context)

#----------------------------- UPDATE PROJECTION SETTINGS -----------------------------#

def update_layer_projection(self, context):
    '''Changes the layer projection by reconnecting nodes.'''
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    selected_material_channel = context.scene.matlay_layer_stack.selected_material_channel

    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)

        # Get nodes.
        texture_node = layer_nodes.get_layer_node("TEXTURE", material_channel_name, selected_layer_index, context)
        coord_node = layer_nodes.get_layer_node("COORD", material_channel_name, selected_layer_index, context)
        mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)

        # Delink coordinate node.
        if coord_node:
            outputs = coord_node.outputs
            for o in outputs:
                for l in o.links:
                    if l != 0:
                        material_channel_node.node_tree.links.remove(l)

            if selected_layer_index > -1:
                # Connect nodes based on projection type.
                if layers[selected_layer_index].projection.projection_mode == 'FLAT':
                    material_channel_node.node_tree.links.new(coord_node.outputs[2], mapping_node.inputs[0])
                    texture_node.projection = 'FLAT'

                if layers[selected_layer_index].projection.projection_mode == 'BOX':
                    material_channel_node.node_tree.links.new(coord_node.outputs[0], mapping_node.inputs[0])
                    texture_node = layer_nodes.get_layer_node("TEXTURE", selected_material_channel, selected_layer_index, context)
                    if texture_node and texture_node.type == 'TEX_IMAGE':
                        texture_node.projection_blend = self.projection_blend
                    texture_node.projection = 'BOX'

                if layers[selected_layer_index].projection.projection_mode == 'SPHERE':
                    material_channel_node.node_tree.links.new(coord_node.outputs[0], mapping_node.inputs[0])
                    texture_node.projection = 'SPHERE'

                if layers[selected_layer_index].projection.projection_mode == 'TUBE':
                    material_channel_node.node_tree.links.new(coord_node.outputs[0], mapping_node.inputs[0])
                    texture_node.projection = 'TUBE'

def update_projection_blend(self, context):
    '''Updates the projection blend node values when the cube projection blend value is changed.'''
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index

    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        texture_node = layer_nodes.get_layer_node("TEXTURE", material_channel_name, selected_layer_index, context)
    
        if texture_node:
            texture_node.projection_blend = layers[selected_layer_index].projection_blend

def update_projection_offset_x(self, context):
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index

    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)

        if mapping_node:
            mapping_node.inputs[1].default_value[0] = layers[selected_layer_index].projection.projection_offset_x

def update_projection_offset_y(self, context):
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index

    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)

        if mapping_node:
            mapping_node.inputs[1].default_value[1] = layers[selected_layer_index].projection.projection_offset_y

def update_projection_rotation(self, context):
    '''Updates the layer projections rotation for all layers.'''
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index

    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)
        if mapping_node:
            mapping_node.inputs[2].default_value[2] = layers[selected_layer_index].projection.projection_rotation

def update_projection_scale_x(self, context):
    '''Updates the layer projections x scale for all mapping nodes in the selected layer.'''
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index

    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)

        if mapping_node:
            mapping_node.inputs[3].default_value[0] = layers[selected_layer_index].projection.projection_scale_x

        if self.match_layer_scale:
            layers[selected_layer_index].projection.projection_scale_y = layers[selected_layer_index].projection.projection_scale_x

def update_projection_scale_y(self, context):
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index

    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)
        
        if mapping_node:
            mapping_node.inputs[3].default_value[1] = layers[selected_layer_index].projection.projection_scale_y

def update_match_layer_scale(self, context):
    '''Updates matching of the projected layer scales.'''
    if self.match_layer_scale:
        layers = context.scene.matlay_layers
        layer_index = context.scene.matlay_layer_stack.layer_index
        layers[layer_index].projection.projection_scale_y = layers[layer_index].projection.projection_scale_x

#----------------------------- UPDATE MATERIAL CHANNEL TOGGLES (mute / unmute material channels for individual layers) -----------------------------#

def update_color_channel_toggle(self, context):
    if self.color_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, context.scene.matlay_layer_stack.layer_index, "COLOR", context)

    else:
        layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "COLOR", context)

def update_subsurface_channel_toggle(self, context):
    if self.subsurface_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, context.scene.matlay_layer_stack.layer_index, "SUBSURFACE", context)

    else:
        layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "SUBSURFACE", context)

def update_subsurface_color_channel_toggle(self, context):
    if self.subsurface_color_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, context.scene.matlay_layer_stack.layer_index, "SUBSURFACE_COLOR", context)

    else:
        layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "SUBSURFACE_COLOR", context)

def update_metallic_channel_toggle(self, context):
    if self.metallic_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, context.scene.matlay_layer_stack.layer_index, "METALLIC", context)

    else:
        layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "METALLIC", context)

def update_specular_channel_toggle(self, context):
    if self.specular_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, context.scene.matlay_layer_stack.layer_index, "SPECULAR", context)

    else:
        layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "SPECULAR", context)

def update_roughness_channel_toggle(self, context):
    if self.roughness_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, context.scene.matlay_layer_stack.layer_index, "ROUGHNESS", context)

    else:
        layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "ROUGHNESS", context)

def update_normal_channel_toggle(self, context):
    if self.normal_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, context.scene.matlay_layer_stack.layer_index, "NORMAL", context)

    else:
        layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "NORMAL", context)

def update_height_channel_toggle(self, context):
    if self.height_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, context.scene.matlay_layer_stack.layer_index, "HEIGHT", context)

    else:
        layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "HEIGHT", context)

def update_emission_channel_toggle(self, context):
    if self.emission_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, context.scene.matlay_layer_stack.layer_index, "EMISSION", context)

    else:
        layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "EMISSION", context)


#----------------------------- UPDATE LAYER PREVIEW COLORS -----------------------------#
# To show values as uniform colors, color preview values are stored per layer as displaying them as a property through the ui required them to be stored somewhere.
# When these values which are displayed in the ui are updated, they automatically update their respective color / value nodes in the node tree through these functions.

def update_color_channel_color(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "COLOR", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.color_channel_color.r, self.color_channel_color.g, self.color_channel_color.b, 1)

def update_subsurface_channel_color(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "SUBSURFACE", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.subsurface_channel_color.r, self.subsurface_channel_color.g, self.subsurface_channel_color.b, 1)

def update_subsurface_color_channel_color(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "SUBSURFACE_COLOR", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.subsurface_color_channel_color.r, self.subsurface_color_channel_color.g, self.subsurface_color_channel_color.b, 1)

def update_metallic_channel_color(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "METALLIC", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.metallic_channel_color.r, self.metallic_channel_color.g, self.metallic_channel_color.b, 1)

def update_specular_channel_color(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "SPECULAR", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.specular_channel_color.r, self.specular_channel_color.g, self.specular_channel_color.b, 1)

def update_roughness_channel_color(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "ROUGHNESS", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.roughness_channel_color.r, self.roughness_channel_color.g, self.roughness_channel_color.b, 1)

def update_normal_channel_color(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "NORMAL", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.normal_channel_color.r, self.normal_channel_color.g, self.normal_channel_color.b, 1)

def update_height_channel_color(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "HEIGHT", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.height_channel_color.r, self.height_channel_color.g, self.height_channel_color.b, 1)

def update_emission_channel_color(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "EMISSION", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.emission_channel_color.r, self.emission_channel_color.g, self.emission_channel_color.b, 1)

#----------------------------- UPDATE UNIFORM LAYER VALUES -----------------------------#
# To have correct min / max values for sliders when the user is using uniform value nodes in the user interface
# When these values which are displayed in the ui are updated, they automatically update their respective value nodes in the node tree through these functions.

def update_uniform_color_value(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "COLOR", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_color_value
        self.color_channel_color = (self.uniform_color_value, self.uniform_color_value, self.uniform_color_value)

def update_uniform_subsurface_value(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "SUBSURFACE", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_subsurface_value
        self.subsurface_channel_color = (self.uniform_subsurface_value,self.uniform_subsurface_value,self.uniform_subsurface_value)

def update_uniform_subsurface_color_value(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "SUBSURFACE_COLOR", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_subsurface_color_value
        self.subsurface_color_channel_color = (self.uniform_subsurface_color_value,self.uniform_subsurface_color_value,self.uniform_subsurface_color_value)

def update_uniform_metallic_value(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "METALLIC", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_metallic_value
        self.metallic_channel_color = (self.uniform_metallic_value,self.uniform_metallic_value,self.uniform_metallic_value)

def update_uniform_specular_value(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "SPECULAR", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_specular_value
        self.specular_channel_color = (self.uniform_specular_value,self.uniform_specular_value,self.uniform_specular_value)

def update_uniform_roughness_value(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "ROUGHNESS", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_roughness_value
        self.roughness_channel_color = (self.uniform_roughness_value,self.uniform_roughness_value,self.uniform_roughness_value)

def update_uniform_normal_value(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "NORMAL", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_normal_value
        self.normal_channel_color = (self.uniform_normal_value,self.uniform_normal_value,self.uniform_normal_value)

def update_uniform_height_value(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "HEIGHT", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_height_value
        self.height_channel_color = (self.uniform_height_value,self.uniform_height_value,self.uniform_height_value)

def update_uniform_emission_value(self, context):
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "EMISSION", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_emission_value
        self.emission_channel_color = (self.uniform_emission_value,self.uniform_emission_value,self.uniform_emission_value)


#----------------------------- UPDATE TEXTURE NODE TYPES -----------------------------#
# When nodes that represent the texture value for a material are swapped, they trigger automatic updates for their respective nodes in the node tree through these functions.

def replace_texture_node(texture_node_type, material_channel_name, self, context):
    '''Replaced the texture node with a new texture node based on the given node type.'''

    selected_layer_stack_index = context.scene.matlay_layer_stack.layer_index
    material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
    
    # Delete the old layer node.
    old_texture_node = layer_nodes.get_layer_node("TEXTURE", material_channel_name, selected_layer_stack_index, context)
    if old_texture_node:
        material_channel_node.node_tree.nodes.remove(old_texture_node)

    # Add the new node based on the provided type.
    texture_node = None
    match texture_node_type:
        case "COLOR":
            texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')

        case "VALUE":
            texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeValue')

        case "TEXTURE":
            texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeTexImage')

        case "GROUP_NODE":
            texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeGroup')
            empty_group_node = bpy.data.node_groups['MATLAY_EMPTY']
            if not empty_group_node:
                material_channels.create_empty_group_node(context)
            texture_node.node_tree = bpy.data.node_groups['MATLAY_EMPTY']

        case "NOISE":
            texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeTexNoise')

        case "VORONOI":
            texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeTexVoronoi')

        case "MUSGRAVE":
            texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeTexMusgrave')

    # Match the texture node name and label.
    texture_node.name = "TEXTURE_" + str(selected_layer_stack_index)
    texture_node.label = texture_node.name
    self.texture_node_name = texture_node.name

    # Link the new texture node to the mix layer node.
    link = material_channel_node.node_tree.links.new
    mix_layer_node = layer_nodes.get_layer_node("MIXLAYER", material_channel_name, selected_layer_stack_index, context)
    link(texture_node.outputs[0], mix_layer_node.inputs[2])

    # For some texture types, connect texture node outputs to the mapping or opacity nodes.
    if texture_node_type == "TEXTURE":
        opacity_node = layer_nodes.get_layer_node("OPACITY", material_channel_name, selected_layer_stack_index, context)
        link(texture_node.outputs[1], opacity_node.inputs[0])

        mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_stack_index, context)
        link(mapping_node.outputs[0], texture_node.inputs[0])

    # TODO: For some texture types, connect the mapping node to the texture vector input.

    # Parent the new node to the layer's frame.
    layer_frame = layer_nodes.get_layer_frame(material_channel_name, selected_layer_stack_index, context)
    texture_node.parent = layer_frame

    # Update the layer nodes because they were changed.
    layer_nodes.update_layer_nodes(context)

def update_color_channel_node_type(self, context):
    replace_texture_node(self.color_node_type, "COLOR", self, context)

def update_subsurface_channel_node_type(self, context):
    replace_texture_node(self.subsurface_node_type, "SUBSURFACE", self, context)

def update_subsurface_color_channel_node_type(self, context):
    replace_texture_node(self.subsurface_color_node_type, "SUBSURFACE_COLOR", self, context)

def update_specular_channel_node_type(self, context):
    replace_texture_node(self.specular_node_type, "SPECULAR", self, context)

def update_metallic_channel_node_type(self, context):
    replace_texture_node(self.metallic_node_type, "METALLIC", self, context)

def update_roughness_channel_node_type(self, context):
    replace_texture_node(self.roughness_node_type, "ROUGHNESS", self, context)

def update_normal_channel_node_type(self, context):
    replace_texture_node(self.normal_node_type, "NORMAL", self, context)

def update_height_channel_node_type(self, context):
    replace_texture_node(self.height_node_type, "HEIGHT", self, context)

def update_emission_channel_node_type(self, context):
    replace_texture_node(self.emission_node_type, "EMISSION", self, context)


#----------------------------- LAYER PROPERTIES -----------------------------#

class MaterialChannelToggles(PropertyGroup):
    '''Boolean toggles for each material channel.'''
    color_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the color material channel for this layer", update=update_color_channel_toggle)
    subsurface_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the subsurface material channel for this layer", update=update_subsurface_channel_toggle)
    subsurface_color_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the subsurface color material channel for this layer.", update=update_subsurface_color_channel_toggle)
    metallic_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the metallic material channel for this layer", update=update_metallic_channel_toggle)
    specular_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the specular material channel for this layer.", update=update_specular_channel_toggle)
    roughness_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the roughness material channel for this layer", update=update_roughness_channel_toggle)
    emission_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the emission material channel for this layer", update=update_emission_channel_toggle)
    normal_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the normal material channel for this layer", update=update_normal_channel_toggle)
    height_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the height material channel for this layer", update=update_height_channel_toggle)

class MaterialChannelNodeType(PropertyGroup):
    '''An enum node type for the material node used to represent the material channel texture in every material channel.'''
    color_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Color Channel Node Type", description="The node type for the color channel", default='COLOR', update=update_color_channel_node_type)
    subsurface_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Subsurface Scattering Channel Node Type", description="The node type for the subsurface scattering channel", default='VALUE', update=update_subsurface_channel_node_type)
    subsurface_color_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Subsurface Scattering Color Channel Node Type", description="The node type for the subsurface scattering color channel", default='COLOR', update=update_subsurface_color_channel_node_type)
    metallic_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Metallic Channel Node Type", description="The node type for the metallic channel", default='VALUE', update=update_metallic_channel_node_type)
    specular_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Specular Channel Node Type", description="The node type for the specular channel", default='VALUE', update=update_specular_channel_node_type)
    roughness_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Roughness Channel Node Type", description="The node type for roughness channel", default='VALUE', update=update_roughness_channel_node_type)
    normal_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Normal Channel Node Type", description="The node type for the normal channel", default='COLOR', update=update_normal_channel_node_type)
    height_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Height Channel Node Type", description="The node type for the height channel", default='VALUE', update=update_height_channel_node_type)
    emission_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Emission Channel Node Type", description="The node type for the emission channel", default='COLOR', update=update_emission_channel_node_type)
 
class ProjectionSettings(PropertyGroup):
    '''Projection settings for this add-on.'''
    projection_mode: EnumProperty(items=PROJECTION_MODES, name="Projection", description="Projection type of the image attached to the selected layer", default='FLAT', update=update_layer_projection)
    texture_extension: EnumProperty(items=TEXTURE_EXTENSION_MODES, name="Extension", description="", default='REPEAT')
    texture_interpolation: EnumProperty(items=TEXTURE_INTERPOLATION_MODES, name="Interpolation", description="", default='LINEAR')
    projection_blend: FloatProperty(name="Projection Blend", description="The projection blend amount", default=0.5, min=0.0, max=1.0, subtype='FACTOR', update=update_projection_blend)
    projection_offset_x: FloatProperty(name="Offset X", description="Projected x offset of the selected layer", default=0.0, min=-1.0, max=1.0, subtype='FACTOR', update=update_projection_offset_x)
    projection_offset_y: FloatProperty(name="Offset Y", description="Projected y offset of the selected layer", default=0.0, min=-1.0, max=1.0, subtype='FACTOR', update=update_projection_offset_y)
    projection_rotation: FloatProperty(name="Rotation", description="Projected rotation of the selected layer", default=0.0, min=-6.283185, max=6.283185, subtype='ANGLE', update=update_projection_rotation)
    projection_scale_x: FloatProperty(name="Scale X", description="Projected x scale of the selected layer", default=1.0, step=1, soft_min=-4.0, soft_max=4.0, subtype='FACTOR', update=update_projection_scale_x)
    projection_scale_y: FloatProperty(name="Scale Y", description="Projected y scale of the selected layer", default=1.0, step=1, soft_min=-4.0, soft_max=4.0, subtype='FACTOR', update=update_projection_scale_y)
    match_layer_scale: bpy.props.BoolProperty(name="Match Layer Scale", default=True,update=update_match_layer_scale)
    match_layer_mask_scale: bpy.props.BoolProperty(name="Match Layer Mask Scale", default=True)

class MaterialChannelColors(PropertyGroup):
    '''Color values for each material channel. These are used for layer previews when the layer can be accurately displayed using rgb values (rgb node / value node).'''
    color_channel_color: FloatVectorProperty(name="Layer preview color for the color material channel.", description="", default=(0.25, 0.25, 0.25), min=0, max=1, subtype='COLOR', update=update_color_channel_color)
    subsurface_channel_color: FloatVectorProperty(name="Layer preview color for the subsurface scattering material channel.", description="", default=(0.0, 0.0, 0.0), min=0, max=1, subtype='COLOR', update=update_subsurface_channel_color)
    subsurface_color_channel_color: FloatVectorProperty(name="Layer preview color for the subsurface color material channel.", description="", default=(0.0, 0.0, 0.0), min=0, max=1, subtype='COLOR', update=update_subsurface_color_channel_color)
    metallic_channel_color: FloatVectorProperty(name="Layer preview color for the metallic material channel.", description="", default=(0.25, 0.25, 0.25), min=0, max=1, subtype='COLOR', update=update_metallic_channel_color)
    specular_channel_color: FloatVectorProperty(name="Layer preview color for the specular material channel.", description="", default=(0.5, 0.5, 0.5), min=0, max=1, subtype='COLOR', update=update_specular_channel_color)
    roughness_channel_color: FloatVectorProperty(name="Layer preview color for the roughness material channel.", description="", default=(0.5, 0.5, 0.5), min=0, max=1, subtype='COLOR', update=update_roughness_channel_color)
    normal_channel_color: FloatVectorProperty(name="Layer preview color for the normal material channel.", description="", default=(0.5, 0.5, 1.0), min=0, max=1, subtype='COLOR', update=update_normal_channel_color)
    height_channel_color: FloatVectorProperty(name="Layer preview color for the height material channel.", description="", default=(0.0, 0.0, 0.0), min=0, max=1, subtype='COLOR', update=update_height_channel_color)
    emission_channel_color: FloatVectorProperty(name="Layer preview color for the emission material channel.", description="", default=(0.0, 0.0, 0.0), min=0, max=1, subtype='COLOR', update=update_emission_channel_color)

class MaterialChannelUniformValues(PropertyGroup):
    '''Uniform float values used for each material channel. These are used to represent correct min / max value ranges within the user interface.'''
    uniform_color_value: FloatProperty(name="Uniform Color Value", description="Uniform color value for this layer", default=0.0, min=0, max=1, update=update_uniform_color_value)
    uniform_subsurface_value: FloatProperty(name="Uniform Subsurface Scattering Value", description="Uniform subsurface scattering value for this layer", default=0.0, min=0, max=1, update=update_uniform_subsurface_value)
    uniform_subsurface_color_value: FloatProperty(name="Uniform Subsurface Color Value", description="Uniform subsurface color value for this layer", default=0.0, min=0, max=1, update=update_uniform_subsurface_color_value)
    uniform_metallic_value: FloatProperty(name="Uniform Metallic Value", description="Uniform metallic value for this layer", default=0.0, min=0, max=1, update=update_uniform_metallic_value)
    uniform_specular_value: FloatProperty(name="Uniform Specular Value", description="Uniform specular value for this layer", default=0.5, min=0, max=1, update=update_uniform_specular_value)
    uniform_roughness_value: FloatProperty(name="Uniform Roughness Value", description="Uniform roughness value for this layer", default=0.5, min=0, max=1, update=update_uniform_roughness_value)
    uniform_emission_value: FloatProperty(name="Uniform Emission Value", description="Uniform emission value for this layer", default=0.0, min=0, max=1, update=update_uniform_emission_value)
    uniform_normal_value: FloatProperty(name="Uniform Normal Value", description="Uniform normal value for this layer", default=0.0, min=0, max=1, update=update_uniform_normal_value)
    uniform_height_value: FloatProperty(name="Uniform Height Value", description="Uniform height value for this layer", default=0.0, min=0, max=1, update=update_uniform_height_value)

class MATLAY_layers(PropertyGroup):
    layer_stack_array_index: bpy.props.IntProperty(name="Layer Stack Array Index", description="The array index of this layer within the layer stack, stored to make it easy to access the array index of a specific layer.", default=-9)
    id: bpy.props.IntProperty(name="ID", description="Unique numeric ID for the selected layer.", default=0)
    name: bpy.props.StringProperty(name="", description="The name of the layer", default="Layer Naming Error", update=update_layer_name)
    cached_frame_name: bpy.props.StringProperty(name="", description="A cached version of the layer name. This allows layer nodes using the layers previous layer name to be accessed until they are renamed.", default="Layer Naming Error")
    opacity: FloatProperty(name="Opacity", description="Layers Opacity", default=1.0, min=0.0, soft_max=1.0, subtype='FACTOR', update=update_layer_opacity)
    hidden: BoolProperty(name="Hidden", description="Show if the layer is hidden.", update=update_hidden)
    masked: BoolProperty(name="Masked", description="This layer has a mask.", default=True)
    material_channel_toggles: bpy.props.PointerProperty(type=MaterialChannelToggles, name="Material Channel Toggles")
    channel_node_types: PointerProperty(type=MaterialChannelNodeType, name="Channel Node Types")
    projection: PointerProperty(type=ProjectionSettings, name="Projection Settings")
    color_channel_values: PointerProperty(type=MaterialChannelColors, name="Color Channel Values")
    uniform_channel_values: PointerProperty(type=MaterialChannelUniformValues, name="Uniform Channel Values")