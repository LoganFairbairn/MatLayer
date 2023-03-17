# This file contains layer properties and functions for updating layer properties.

import bpy
from bpy.types import PropertyGroup
from . import layer_nodes
from . import material_channel_nodes

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
    layers = context.scene.coater_layer_stack

    # Rename all layer frames with the new name. To access the layer frames, use the previous layers name as it's been updated already.
    layers = context.scene.coater_layers

    material_channel_list = material_channel_nodes.get_material_channel_list()
    for material_channel_name in material_channel_list:
        material_channel = material_channel_nodes.get_material_channel_node(context, material_channel_name)

        cached_frame_name = self.cached_frame_name
        frame = material_channel.node_tree.nodes.get(cached_frame_name)
        if frame:
            new_name = self.name + "_" + str(self.id) + "_" + str(self.layer_stack_array_index)
            frame.name = new_name
            frame.label = frame.name

def update_layer_opacity(self, context):
    '''Updates the layer opacity node values when the opacity is changed.'''
    selected_material_channel = context.scene.coater_layer_stack.selected_material_channel
    opacity_node = layer_nodes.get_layer_node("OPACITY", selected_material_channel, self.layer_stack_array_index, context)
    if opacity_node:
        opacity_node.inputs[1].default_value = self.opacity

def update_hidden(self, context):
    '''Hide or unhide layers.'''
    selected_material_channel = context.scene.coater_layer_stack.selected_material_channel
    material_channel_names = material_channel_nodes.get_material_channel_list()

    # Hide selected layer by muting all nodes within the layer.
    if self.hidden:
        for material_channel in material_channel_names:
            layer_nodes.mute_layer_material_channel(True, self.layer_stack_array_index, material_channel, context)

    # Unhide the selected layer by unmuting all active layers.
    else:
        for material_channel in material_channel_names:
            if material_channel == "COLOR" and self.color_channel_toggle:
                layer_nodes.mute_layer_material_channel(False, self.layer_stack_array_index, "COLOR", context)

            if material_channel == "METALLIC" and self.metallic_channel_toggle:
                layer_nodes.mute_layer_material_channel(False, self.layer_stack_array_index, "METALLIC", context)

            if material_channel == "ROUGHNESS" and self.roughness_channel_toggle:
                layer_nodes.mute_layer_material_channel(False, self.layer_stack_array_index, "ROUGHNESS", context)

            if material_channel == "NORMAL" and self.normal_channel_toggle:
                layer_nodes.mute_layer_material_channel(False, self.layer_stack_array_index, "NORMAL", context)

            if material_channel == "HEIGHT" and self.height_channel_toggle:
                layer_nodes.mute_layer_material_channel(False, self.layer_stack_array_index, "HEIGHT", context)

            if material_channel == "SCATTERING" and self.scattering_channel_toggle:
                layer_nodes.mute_layer_material_channel(False, self.layer_stack_array_index, "SCATTERING", context)

            if material_channel == "EMISSION" and self.emission_channel_toggle:
                layer_nodes.mute_layer_material_channel(True, self.layer_stack_array_index, "EMISSION", context)

#----------------------------- UPDATE PROJECTION SETTINGS -----------------------------#

def update_layer_projection(self, context):
    '''Changes the layer projection by reconnecting nodes.'''
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    selected_material_channel = context.scene.coater_layer_stack.selected_material_channel

    material_channel_list = material_channel_nodes.get_material_channel_list()
    for material_channel_name in material_channel_list:
        material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)

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
                if layers[selected_layer_index].projection_mode == 'FLAT':
                    material_channel_node.node_tree.links.new(coord_node.outputs[2], mapping_node.inputs[0])
                    texture_node.projection = 'FLAT'

                if layers[selected_layer_index].projection_mode == 'BOX':
                    material_channel_node.node_tree.links.new(coord_node.outputs[0], mapping_node.inputs[0])
                    texture_node = layer_nodes.get_layer_node("TEXTURE", selected_material_channel, selected_layer_index, context)
                    if texture_node and texture_node.type == 'TEX_IMAGE':
                        texture_node.projection_blend = self.projection_blend
                    texture_node.projection = 'BOX'

                if layers[selected_layer_index].projection_mode == 'SPHERE':
                    material_channel_node.node_tree.links.new(coord_node.outputs[0], mapping_node.inputs[0])
                    texture_node.projection = 'SPHERE'

                if layers[selected_layer_index].projection_mode == 'TUBE':
                    material_channel_node.node_tree.links.new(coord_node.outputs[0], mapping_node.inputs[0])
                    texture_node.projection = 'TUBE'

def update_projection_blend(self, context):
    '''Updates the projection blend node values when the cube projection blend value is changed.'''
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    material_channel_list = material_channel_nodes.get_material_channel_list()
    for material_channel_name in material_channel_list:
        texture_node = layer_nodes.get_layer_node("TEXTURE", material_channel_name, selected_layer_index, context)
    
        if texture_node:
            texture_node.projection_blend = layers[selected_layer_index].projection_blend

def update_projection_offset_x(self, context):
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    material_channel_list = material_channel_nodes.get_material_channel_list()
    for material_channel_name in material_channel_list:
        mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)

        if mapping_node:
            mapping_node.inputs[1].default_value[0] = layers[selected_layer_index].projection_offset_x

def update_projection_offset_y(self, context):
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    material_channel_list = material_channel_nodes.get_material_channel_list()
    for material_channel_name in material_channel_list:
        mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)

        if mapping_node:
            mapping_node.inputs[1].default_value[1] = layers[selected_layer_index].projection_offset_y

def update_projection_rotation(self, context):
    '''Updates the layer projections rotation for all layers.'''
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    material_channel_list = material_channel_nodes.get_material_channel_list()
    for material_channel_name in material_channel_list:
        mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)
        if mapping_node:
            mapping_node.inputs[2].default_value[2] = layers[selected_layer_index].projection_rotation

def update_projection_scale_x(self, context):
    '''Updates the layer projections x scale for all mapping nodes in the selected layer.'''
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    material_channel_list = material_channel_nodes.get_material_channel_list()
    for material_channel_name in material_channel_list:
        mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)

        if mapping_node:
            mapping_node.inputs[3].default_value[0] = layers[selected_layer_index].projection_scale_x

        layer_settings = context.scene.coater_layer_settings
        if layer_settings.match_layer_scale:
            layers[selected_layer_index].projection_scale_y = layers[selected_layer_index].projection_scale_x

def update_projection_scale_y(self, context):
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    material_channel_list = material_channel_nodes.get_material_channel_list()
    for material_channel_name in material_channel_list:
        mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)
        
        if mapping_node:
            mapping_node.inputs[3].default_value[1] = layers[selected_layer_index].projection_scale_y

#----------------------------- MUTE / UNMUTE MATERIAL CHANNELS -----------------------------#
def update_color_channel_toggle(self, context):
    if self.color_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, self.layer_stack_array_index, "COLOR", context)

    else:
        layer_nodes.mute_layer_material_channel(True, self.layer_stack_array_index, "COLOR", context)

def update_metallic_channel_toggle(self, context):
    if self.metallic_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, self.layer_stack_array_index, "METALLIC", context)

    else:
        layer_nodes.mute_layer_material_channel(True, self.layer_stack_array_index, "METALLIC", context)

def update_roughness_channel_toggle(self, context):
    if self.roughness_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, self.layer_stack_array_index, "ROUGHNESS", context)

    else:
        layer_nodes.mute_layer_material_channel(True, self.layer_stack_array_index, "ROUGHNESS", context)

def update_normal_channel_toggle(self, context):
    if self.normal_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, self.layer_stack_array_index, "NORMAL", context)

    else:
        layer_nodes.mute_layer_material_channel(True, self.layer_stack_array_index, "NORMAL", context)

def update_height_channel_toggle(self, context):
    if self.height_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, self.layer_stack_array_index, "HEIGHT", context)

    else:
        layer_nodes.mute_layer_material_channel(True, self.layer_stack_array_index, "HEIGHT", context)

def update_scattering_channel_toggle(self, context):
    if self.scattering_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, self.layer_stack_array_index, "SCATTERING", context)

    else:
        layer_nodes.mute_layer_material_channel(True, self.layer_stack_array_index, "SCATTERING", context)

def update_emission_channel_toggle(self, context):
    if self.emission_channel_toggle:
        layer_nodes.mute_layer_material_channel(False, self.layer_stack_array_index, "EMISSION", context)

    else:
        layer_nodes.mute_layer_material_channel(True, self.layer_stack_array_index, "EMISSION", context)


#----------------------------- UPDATE LAYER PREVIEW COLORS -----------------------------#
# To show values as uniform colors, color preview values are stored per layer as displaying them as a property through the ui required them to be stored somewhere.
# When these values which are displayed in the ui are updated, they automatically update their respective color / value nodes in the node tree through these functions.

def update_color_prieview_color(self, context):
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "COLOR", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.color_layer_color_preview.r, self.color_layer_color_preview.g, self.color_layer_color_preview.b, 1)

def update_metallic_prieview_color(self, context):
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "METALLIC", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.metallic_layer_color_preview.r, self.metallic_layer_color_preview.g, self.metallic_layer_color_preview.b, 1)

def update_roughness_prieview_color(self, context):
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "ROUGHNESS", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.roughness_layer_color_preview.r, self.roughness_layer_color_preview.g, self.roughness_layer_color_preview.b, 1)

def update_normal_prieview_color(self, context):
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "NORMAL", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.normal_layer_color_preview.r, self.normal_layer_color_preview.g, self.normal_layer_color_preview.b, 1)

def update_height_prieview_color(self, context):
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "HEIGHT", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.height_layer_color_preview.r, self.height_layer_color_preview.g, self.height_layer_color_preview.b, 1)

def update_scattering_prieview_color(self, context):
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "SCATTERING", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.scattering_layer_color_preview.r, self.scattering_layer_color_preview.g, self.scattering_layer_color_preview.b, 1)

def update_emission_prieview_color(self, context):
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "EMISSION", selected_layer_index, context)
    if node and node.type == 'RGB':
        node.outputs[0].default_value = (self.emission_layer_color_preview.r, self.emission_layer_color_preview.g, self.emission_layer_color_preview.b, 1)

#----------------------------- UPDATE UNIFORM LAYER VALUES -----------------------------#
# To show correct min / max values for sliders when the user is using uniform value nodes in the user interface
# When these values which are displayed in the ui are updated, they automatically update their respective value nodes in the node tree through these functions.

def update_uniform_color_value(self, context):
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "COLOR", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_color_value
        self.color_layer_color_preview = (self.uniform_color_value,self.uniform_color_value,self.uniform_color_value)

def update_uniform_metallic_value(self, context):
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "METALLIC", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_metallic_value
        self.metallic_layer_color_preview = (self.uniform_metallic_value,self.uniform_metallic_value,self.uniform_metallic_value)

def update_uniform_roughness_value(self, context):
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "ROUGHNESS", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_roughness_value
        self.roughness_layer_color_preview = (self.uniform_roughness_value,self.uniform_roughness_value,self.uniform_roughness_value)

def update_uniform_normal_value(self, context):
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "NORMAL", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_normal_value
        self.normal_layer_color_preview = (self.uniform_normal_value,self.uniform_normal_value,self.uniform_normal_value)

def update_uniform_height_value(self, context):
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "HEIGHT", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_height_value
        self.height_layer_color_preview = (self.uniform_height_value,self.uniform_height_value,self.uniform_height_value)

def update_uniform_emission_value(self, context):
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "EMISSION", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_emission_value
        self.emission_layer_color_preview = (self.emission_layer_color_preview,self.emission_layer_color_preview,self.emission_layer_color_preview)

def update_uniform_scattering_value(self, context):
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    node = layer_nodes.get_layer_node("TEXTURE", "SCATTERING", selected_layer_index, context)
    if node and node.type == 'VALUE':
        node.outputs[0].default_value = self.uniform_scattering_value
        self.scattering_layer_color_preview = (self.uniform_scattering_value,self.uniform_scattering_value,self.uniform_scattering_value)

def update_uniform_values(self, context):
    update_uniform_color_value(self, context)
    update_uniform_metallic_value(self, context)
    update_uniform_roughness_value(self, context)
    update_uniform_normal_value(self, context)
    update_uniform_height_value(self, context)
    update_uniform_emission_value(self, context)
    update_uniform_scattering_value(self, context)

#----------------------------- UPDATE TEXTURE NODE TYPES -----------------------------#
# When nodes that represent the texture value for a material are swapped, they trigger automatic updates for their respective nodes here.

def replace_texture_node(texture_node_type, material_channel_name, self, context):
    '''Replaced the texture node with a new texture node based on the given node type.'''

    selected_layer_stack_index = context.scene.coater_layer_stack.layer_index
    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)
    
    # Delete the old layer node.
    old_texture_node = layer_nodes.get_layer_node("TEXTURE", material_channel_name, selected_layer_stack_index, context)
    if old_texture_node:
        material_channel_node.node_tree.nodes.remove(old_texture_node)

    # Add the new node.
    texture_node = None
    if texture_node_type == "COLOR":
        texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')

    if texture_node_type == "VALUE":
        texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeValue')

    if texture_node_type == "TEXTURE":
        texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeTexImage')

    if texture_node_type == "NOISE":
        texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeTexNoise')

    if texture_node_type == "VORONOI":
        texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeTexVoronoi')

    if texture_node_type == "MUSGRAVE":
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

    # Update the uniform node values when the nodes are updated.
    update_uniform_values(self, context)

def update_color_texture_node_type(self, context):
    replace_texture_node(self.color_texture_node_type, "COLOR", self, context)

def update_metallic_texture_node_type(self, context):
    replace_texture_node(self.metallic_texture_node_type, "METALLIC", self, context)

def update_roughness_texture_node_type(self, context):
    replace_texture_node(self.roughness_texture_node_type, "ROUGHNESS", self, context)

def update_normal_texture_node_type(self, context):
    replace_texture_node(self.normal_texture_node_type, "NORMAL", self, context)

def update_height_texture_node_type(self, context):
    replace_texture_node(self.height_texture_node_type, "HEIGHT", self, context)

def update_scattering_texture_node_type(self, context):
    replace_texture_node(self.scattering_texture_node_type, "SCATTERING", self, context)

def update_emission_texture_node_type(self, context):
    replace_texture_node(self.emission_texture_node_type, "EMISSION", self, context)


#----------------------------- LAYER PROPERTIES -----------------------------#

class COATER_layers(PropertyGroup):
    # The layer stack index for each layer is stored here for convenience. This should be automatically updated everytime update_layer_nodes is called.
    layer_stack_array_index: bpy.props.IntProperty(name="Layer Stack Array Index", description="Layer Stack Array Index", default=-9)

    # Layer ID used as a unique identifier.
    id: bpy.props.IntProperty(name="ID", description="Numeric ID for the selected layer.", default=0)

    # Layer name for organization purposes.
    name: bpy.props.StringProperty(name="", description="The name of the layer", default="Layer Naming Error", update=update_layer_name)
    cached_frame_name: bpy.props.StringProperty(name="", description="A cached version of the layer name. This allows layer nodes using the layers previous layer name to be accessed until they are renamed.", default="Layer Naming Error")

    # General layer settings (all layers have these).
    opacity: bpy.props.FloatProperty(name="Opacity", description="Layers Opacity", default=1.0, min=0.0, soft_max=1.0, subtype='FACTOR', update=update_layer_opacity)
    hidden: bpy.props.BoolProperty(name="Hidden", description="Show if the layer is hidden.", update=update_hidden)
    masked: bpy.props.BoolProperty(name="Masked", description="This layer has a mask.", default=True)

    # Material Channels Toggles (for quickly linking or unlinking material channels)
    color_channel_toggle: bpy.props.BoolProperty(default=True, update=update_color_channel_toggle, description="Click to toggle on / off the color material channel for this layer")
    metallic_channel_toggle: bpy.props.BoolProperty(default=True, update=update_metallic_channel_toggle, description="Click to toggle on / off the metallic material channel for this layer")
    roughness_channel_toggle: bpy.props.BoolProperty(default=True, update=update_roughness_channel_toggle, description="Click to toggle on / off the roughness material channel for this layer")
    normal_channel_toggle: bpy.props.BoolProperty(default=True, update=update_normal_channel_toggle, description="Click to toggle on / off the normal material channel for this layer")
    height_channel_toggle: bpy.props.BoolProperty(default=True, update=update_height_channel_toggle, description="Click to toggle on / off the height material channel for this layer")
    scattering_channel_toggle: bpy.props.BoolProperty(default=True, update=update_scattering_channel_toggle, description="Click to toggle on / off the scattering material channel for this layer")
    emission_channel_toggle: bpy.props.BoolProperty(default=True, update=update_emission_channel_toggle, description="Click to toggle on / off the emission material channel for this layer")

    # Projection Settings
    projection_mode: bpy.props.EnumProperty(items=PROJECTION_MODES, name="Projection", description="Projection type of the image attached to the selected layer", default='FLAT', update=update_layer_projection)
    texture_extension: bpy.props.EnumProperty(items=TEXTURE_EXTENSION_MODES, name="Extension", description="", default='REPEAT')
    texture_interpolation: bpy.props.EnumProperty(items=TEXTURE_INTERPOLATION_MODES, name="Interpolation", description="", default='LINEAR')
    projection_blend: bpy.props.FloatProperty(name="Projection Blend", description="The projection blend amount", default=0.5, min=0.0, max=1.0, subtype='FACTOR', update=update_projection_blend)
    projection_offset_x: bpy.props.FloatProperty(name="Offset X", description="Projected x offset of the selected layer", default=0.0, min=-1.0, max=1.0, subtype='FACTOR', update=update_projection_offset_x)
    projection_offset_y: bpy.props.FloatProperty(name="Offset Y", description="Projected y offset of the selected layer", default=0.0, min=-1.0, max=1.0, subtype='FACTOR', update=update_projection_offset_y)
    projection_rotation: bpy.props.FloatProperty(name="Rotation", description="Projected rotation of the selected layer", default=0.0, min=-6.283185, max=6.283185, subtype='ANGLE', update=update_projection_rotation)
    projection_scale_x: bpy.props.FloatProperty(name="Scale X", description="Projected x scale of the selected layer", default=1.0, step=1, soft_min=-4.0, soft_max=4.0, subtype='FACTOR', update=update_projection_scale_x)
    projection_scale_y: bpy.props.FloatProperty(name="Scale Y", description="Projected y scale of the selected layer", default=1.0, step=1, soft_min=-4.0, soft_max=4.0, subtype='FACTOR', update=update_projection_scale_y)

    # Node Types (used for properly drawing user interface for node properties)
    color_texture_node_type: bpy.props.EnumProperty(items=TEXTURE_NODE_TYPES, name="Color Texture Node Type", description="The node type for the color channel", default='COLOR', update=update_color_texture_node_type)
    metallic_texture_node_type: bpy.props.EnumProperty(items=TEXTURE_NODE_TYPES, name="Metallic Texture Node Type", description="The node type for the roughness channel", default='VALUE', update=update_metallic_texture_node_type)
    roughness_texture_node_type: bpy.props.EnumProperty(items=TEXTURE_NODE_TYPES, name="Roughness Texture Node Type", description="The node type for roughness channel", default='VALUE', update=update_roughness_texture_node_type)
    normal_texture_node_type: bpy.props.EnumProperty(items=TEXTURE_NODE_TYPES, name="Normal Texture Node Type", description="The node type for the normal channel", default='COLOR', update=update_normal_texture_node_type)
    height_texture_node_type: bpy.props.EnumProperty(items=TEXTURE_NODE_TYPES, name="Height Texture Node Type", description="The node type for the height channel", default='VALUE', update=update_height_texture_node_type)
    scattering_texture_node_type: bpy.props.EnumProperty(items=TEXTURE_NODE_TYPES, name="Scattering Texture Node Type", description="The node type for the scattering channel", default='COLOR', update=update_scattering_texture_node_type)
    emission_texture_node_type: bpy.props.EnumProperty(items=TEXTURE_NODE_TYPES, name="Emission Texture Node Type", description="The node type for the emission channel", default='COLOR', update=update_emission_texture_node_type)

    # Color layer previews for layers.
    # To display value nodes as uniform rgb colors within the layer stack ui, color previews are stored here, and updated when users update the colors through the interface.
    color_layer_color_preview: bpy.props.FloatVectorProperty(name="Layer preview color for the color material channel.", description="", default=(1.0, 0.0, 1.0), min=0, max=1, subtype='COLOR', update=update_color_prieview_color)
    metallic_layer_color_preview: bpy.props.FloatVectorProperty(name="Layer preview color for the metallic material channel.", description="", default=(0.25, 0.25, 0.25), min=0, max=1, subtype='COLOR', update=update_metallic_prieview_color)
    roughness_layer_color_preview: bpy.props.FloatVectorProperty(name="Layer preview color for the roughness material channel.", description="", default=(0.5, 0.5, 0.5), min=0, max=1, subtype='COLOR', update=update_roughness_prieview_color)
    normal_layer_color_preview: bpy.props.FloatVectorProperty(name="Layer preview color for the normal material channel.", description="", default=(0.5, 0.5, 1.0), min=0, max=1, subtype='COLOR', update=update_normal_prieview_color)
    height_layer_color_preview: bpy.props.FloatVectorProperty(name="Layer preview color for the height material channel.", description="", default=(0.0, 0.0, 0.0), min=0, max=1, subtype='COLOR', update=update_height_prieview_color)
    scattering_layer_color_preview: bpy.props.FloatVectorProperty(name="Layer preview color for the color material channel.", description="", default=(0.0, 0.0, 0.0), min=0, max=1, subtype='COLOR', update=update_scattering_prieview_color)
    emission_layer_color_preview: bpy.props.FloatVectorProperty(name="Layer preview color for the emission material channel.", description="", default=(0.0, 0.0, 0.0), min=0, max=1, subtype='COLOR', update=update_emission_prieview_color)

    # To provide accurate min / max slider ranges in the user interface, float values are stored in each layer to use as the values (even for material channels that wouldn't typically be represented by a uniform rgb values).
    uniform_color_value: bpy.props.FloatProperty(name="Uniform Color Value", description="Uniform color value for this layer", default=0.0, min=0, max=1, update=update_uniform_color_value)
    uniform_scattering_value: bpy.props.FloatProperty(name="Uniform Scattering Value", description="Uniform scattering value for this layer", default=0.0, min=0, max=1, update=update_uniform_scattering_value)
    uniform_metallic_value: bpy.props.FloatProperty(name="Uniform Metallic Value", description="Uniform metallic value for this layer", default=0.0, min=0, max=1, update=update_uniform_metallic_value)
    uniform_roughness_value: bpy.props.FloatProperty(name="Uniform Roughness Value", description="Uniform roughness value for this layer", default=0.5, min=0, max=1, update=update_uniform_roughness_value)
    uniform_emission_value: bpy.props.FloatProperty(name="Uniform Emission Value", description="Uniform emission value for this layer", default=0.0, min=0, max=1, update=update_uniform_emission_value)
    uniform_normal_value: bpy.props.FloatProperty(name="Uniform Normal Value", description="Uniform normal value for this layer", default=0.0, min=0, max=1, update=update_uniform_normal_value)
    uniform_height_value: bpy.props.FloatProperty(name="Uniform Height Value", description="Uniform height value for this layer", default=0.0, min=0, max=1, update=update_uniform_height_value)