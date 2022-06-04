# This file contains layer properties and functions for updating layer properties.

import bpy
from bpy.types import PropertyGroup
from ..nodes import layer_nodes
from ..nodes import material_channel_nodes
from ..nodes import update_layer_nodes

# TODO: Support other texture node types.
TEXTURE_NODE_TYPES = [
    ("COLOR", "Color", ""), 
    ("VALUE", "Value", ""),
    ("TEXTURE", "Texture", ""),
    ("NOISE", "Noise", ""),
    ("VORONOI", "Voronoi", ""),
    ("MUSGRAVE", "Musgrave", "")
    ]

PROJECTION_MODES = [
    ("FLAT", "Flat", ""),
    ("BOX", "Box", ""),
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

def layer_image_path_error(self, context):
    self.layout.label(text="Layer image path does not exist, so the image can't be renamed! Manually save the image to the layer folder to resolve the error.")

def update_layer_name(self, context):
    '''Updates layer nodes, frames when the layer name is changed.'''
    selected_layer_stack_index = context.scene.coater_layer_stack.layer_index

    # Rename layer frame when the layer is renamed.
    layer_nodes.rename_layer_frame(self.name, selected_layer_stack_index, context)

        
def update_layer_projection(self, context):
    '''Changes the layer projection by reconnecting nodes.'''
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node_group = layer_nodes.get_channel_node_group(context)
    color_node = channel_node_group.nodes.get(layers[layer_index].color_node_name)
    coord_node = channel_node_group.nodes.get(layers[layer_index].coord_node_name)
    mapping_node = channel_node_group.nodes.get(layers[layer_index].mapping_node_name)

    # Delink coordinate node.
    if coord_node != None:
        outputs = coord_node.outputs
        for o in outputs:
            for l in o.links:
                if l != 0:
                    channel_node_group.links.remove(l)

        if layer_index > -1:
            # Connect nodes based on projection type.
            if layers[layer_index].projection == 'FLAT':
                channel_node_group.links.new(coord_node.outputs[2], mapping_node.inputs[0])
                color_node.projection = 'FLAT'

            if layers[layer_index].projection == 'BOX':
                channel_node_group.links.new(coord_node.outputs[0], mapping_node.inputs[0])
                color_node.projection = 'BOX'

            if layers[layer_index].projection == 'SPHERE':
                channel_node_group.links.new(coord_node.outputs[0], mapping_node.inputs[0])
                color_node.projection = 'SPHERE'

            if layers[layer_index].projection == 'TUBE':
                channel_node_group.links.new(coord_node.outputs[0], mapping_node.inputs[0])
                color_node.projection = 'TUBE'

def update_projection_blend(self, context):
    '''Updates the projection blend node values when the cube projection blend value is changed.'''
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node_group = layer_nodes.get_channel_node_group(context)
    color_node = channel_node_group.nodes.get(layers[layer_index].color_node_name)
    
    if color_node != None:
        color_node.projection_blend = layers[layer_index].projection_blend

def update_mask_projection_blend(self, context):
    '''Updates the mask projection blend node values when the cube projection blend value is changed.'''
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node_group = layer_nodes.get_channel_node_group(context)
    mask_node = channel_node_group.nodes.get(layers[layer_index].mask_node_name)

    if mask_node != None:
        mask_node.projection_blend = layers[layer_index].mask_projection_blend

def update_mask_projection(self, context):
    '''Changes the mask projection by reconnecting nodes.'''
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node_group = layer_nodes.get_channel_node_group(context)
    mask_node = channel_node_group.nodes.get(layers[layer_index].mask_node_name)
    mask_coord_node = channel_node_group.nodes.get(layers[layer_index].mask_coord_node_name)
    mask_mapping_node = channel_node_group.nodes.get(layers[layer_index].mask_mapping_node_name)

    # Delink coordinate node.
    if mask_coord_node != None:
        outputs = mask_coord_node.outputs
        for o in outputs:
            for l in o.links:
                if l != 0:
                    channel_node_group.links.remove(l)

        # Connect nodes based on projection type.
        if layer_index > -1:
            if layers[layer_index].mask_projection == 'FLAT':
                channel_node_group.links.new(mask_coord_node.outputs[2], mask_mapping_node.inputs[0])
                mask_node.projection = 'FLAT'

            if layers[layer_index].mask_projection == 'BOX':
                channel_node_group.links.new(mask_coord_node.outputs[0], mask_mapping_node.inputs[0])
                mask_node.projection = 'BOX'

            if layers[layer_index].mask_projection == 'SPHERE':
                channel_node_group.links.new(mask_coord_node.outputs[0], mask_mapping_node.inputs[0])
                mask_node.projection = 'SPHERE'

            if layers[layer_index].mask_projection == 'TUBE':
                channel_node_group.links.new(mask_coord_node.outputs[0], mask_mapping_node.inputs[0])
                mask_node.projection = 'TUBE'

def update_layer_opacity(self, context):
    '''Updates the layer opacity node values when the opacity is changed.'''

    selected_material_channel = context.scene.coater_layer_stack.channel    # error here, wrong material channel.
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    opacity_node = layer_nodes.get_layer_node_from_name(self.opacity_node_name, "COLOR", context)

    if opacity_node != None:
        opacity_node.inputs[1].default_value = self.opacity

# TODO: Fix this.
def update_hidden(self, context):
    '''Updates node values when the layer hidden property is changed.'''

    if self.hidden == True:
        nodes = layer_nodes.get_self_layer_nodes(self, context)
        for n in nodes:
            n.mute = True
    else:
        nodes = layer_nodes.get_self_layer_nodes(self, context)
        for n in nodes:
            n.mute = False

def update_projected_offset_x(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mapping_node = layer_nodes.get_node(context, 'MAPPING', layer_index)

    # Set the mapping node value.
    if mapping_node != None:
        mapping_node.inputs[1].default_value[0] = layers[layer_index].projected_offset_x

def update_projected_offset_y(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mapping_node = layer_nodes.get_node(context, 'MAPPING', layer_index)

    # Set the mapping node value.
    if mapping_node != None:
        mapping_node.inputs[1].default_value[1] = layers[layer_index].projected_offset_y

def update_projected_rotation(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mapping_node = layer_nodes.get_node(context, 'MAPPING', layer_index)

    # Set the mapping node value.
    if mapping_node != None:
        mapping_node.inputs[2].default_value[2] = layers[layer_index].projected_rotation

def update_projected_scale_x(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mapping_node = layer_nodes.get_node(context, 'MAPPING', layer_index)

    # Set the mapping node value.
    if mapping_node != None:
        mapping_node.inputs[3].default_value[0] = layers[layer_index].projected_scale_x

    layer_settings = context.scene.coater_layer_settings
    if layer_settings.match_layer_scale:
        layers[layer_index].projected_scale_y = layers[layer_index].projected_scale_x

def update_projected_scale_y(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mapping_node = layer_nodes.get_node(context, 'MAPPING', layer_index)

    # Set the mapping node value.
    if mapping_node != None:
        mapping_node.inputs[3].default_value[1] = layers[layer_index].projected_scale_y

def update_projected_mask_offset_x(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mask_mapping_node = layer_nodes.get_node(context, 'MASK_MAPPING', layer_index)

    # Set the mapping node value.
    if mask_mapping_node != None:
        mask_mapping_node.inputs[1].default_value[0] = layers[layer_index].projected_mask_offset_x

def update_projected_mask_offset_y(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mask_mapping_node = layer_nodes.get_node(context, 'MASK_MAPPING', layer_index)

    # Set the mapping node value.
    if mask_mapping_node != None:
        mask_mapping_node.inputs[1].default_value[1] = layers[layer_index].projected_mask_offset_y

def update_projected_mask_rotation(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mask_mapping_node = layer_nodes.get_node(context, 'MASK_MAPPING', layer_index)

    # Set the mapping node value.
    if mask_mapping_node != None:
        mask_mapping_node.inputs[2].default_value[2] = layers[layer_index].projected_mask_rotation

def update_projected_mask_scale_x(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mask_mapping_node = layer_nodes.get_node(context, 'MASK_MAPPING', layer_index)

    # Set the mapping node value.
    if mask_mapping_node != None:
        mask_mapping_node.inputs[3].default_value[0] = layers[layer_index].projected_mask_scale_x

    layer_settings = context.scene.coater_layer_settings
    if layer_settings.match_layer_mask_scale:
        layers[layer_index].projected_mask_scale_y = layers[layer_index].projected_mask_scale_x

def update_projected_mask_scale_y(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mask_mapping_node = layer_nodes.get_node(context, 'MASK_MAPPING', layer_index)

    # Set the mapping node value.
    if mask_mapping_node != None:
        mask_mapping_node.inputs[3].default_value[1] = layers[layer_index].projected_mask_scale_y



# MUTE / UNMUTE MATERIAL CHANNELS #
def update_color_channel_toggle(self, context):
    print("Updated color channel.")
    # TODO: Mute or un-mute all color channel nodes.

def update_metallic_channel_toggle(self, context):
    print("Updated metallic channel.")

def update_roughness_channel_toggle(self, context):
    print("Updated roughness channel.")

def update_normal_channel_toggle(self, context):
    print("Updated normal channel.")

def update_height_channel_toggle(self, context):
    print("Updated height channel.")

def update_scattering_channel_toggle(self, context):
    print("Updated subsurface scattering channel.")

def update_emission_channel_toggle(self, context):
    print("Updated emission channel.")



# UPDATE TEXTURE NODE TYPES (for each material channel) #
def update_color_texture_node_type(self, context):
    replace_texture_node(self.color_texture_node_type, "COLOR", self, context)


def replace_texture_node(texture_node_type, material_channel, self, context):
    '''Replaced the texture node with a new texture node based on the given node type.'''

    selected_layer_stack_index = context.scene.coater_layer_stack.layer_index
    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)
    
    # Delete the old layer node.
    old_texture_node = layer_nodes.get_layer_node("TEXTURE", "COLOR", selected_layer_stack_index, context)
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
    mix_layer_node = layer_nodes.get_layer_node("MIXLAYER", material_channel, selected_layer_stack_index, context)
    link(texture_node.outputs[0], mix_layer_node.inputs[1])

    # Parent the new node to the layer's frame.
    layers = context.scene.coater_layers
    layer_frame = layer_nodes.get_layer_frame(material_channel_node, layers, selected_layer_stack_index)
    texture_node.parent = layer_frame

    # Update the layer nodes because they were changed.
    update_layer_nodes.update_layer_nodes(context)



class COATER_layers(PropertyGroup):
    # Index within the layer stack (stored here for convenience).
    layer_stack_index: bpy.props.IntProperty(name="Layer Stack Index", description="Layer stack index.", default=-1)

    # Layer ID used as a unique identifier.
    id: bpy.props.IntProperty(name="ID", description="Numeric ID for the selected layer.", default=0)

    # Layer name for organization purposes.
    name: bpy.props.StringProperty(name="", description="The name of the layer", default="Layer naming error", update=update_layer_name)

    # General layer settings (all layers have these).
    opacity: bpy.props.FloatProperty(name="Opacity", description="Layers Opacity", default=1.0, min=0.0, soft_max=1.0, subtype='FACTOR', update=update_layer_opacity)
    hidden: bpy.props.BoolProperty(name="", update=update_hidden)
    masked: bpy.props.BoolProperty(name="", default=True)

    # Material Channels Toggles (for quickly linking or unlinking material channels)
    color_channel_toggle: bpy.props.BoolProperty(default=True, update=update_color_channel_toggle)
    metallic_channel_toggle: bpy.props.BoolProperty(default=True, update=update_metallic_channel_toggle)
    roughness_channel_toggle: bpy.props.BoolProperty(default=True, update=update_roughness_channel_toggle)
    normal_channel_toggle: bpy.props.BoolProperty(default=True, update=update_normal_channel_toggle)
    height_channel_toggle: bpy.props.BoolProperty(default=True, update=update_height_channel_toggle)
    scattering_channel_toggle: bpy.props.BoolProperty(default=True, update=update_scattering_channel_toggle)
    emission_channel_toggle: bpy.props.BoolProperty(default=True, update=update_emission_channel_toggle)

    # Layer Node Names (used to quickly access nodes for a layer)
    frame_name: bpy.props.StringProperty(name="Frame Node Name", default="")
    texture_node_name: bpy.props.StringProperty(name="Texture Node Name", default="")
    opacity_node_name: bpy.props.StringProperty(name="Opacity Node Name", default="")
    mix_layer_node_name: bpy.props.StringProperty(name="Mix Layer Node Name", default="")
    coord_node_name: bpy.props.StringProperty(name="Coord Node Name", default="")
    mapping_node_name: bpy.props.StringProperty(name="Mapping Node Name", default="")

    # Projection Settings
    projection_mode: bpy.props.EnumProperty(items=PROJECTION_MODES, name="Projection", description="Projection type of the image attached to the selected layer", default='FLAT', update=update_layer_projection)
    texture_extension: bpy.props.EnumProperty(items=TEXTURE_EXTENSION_MODES, name="Extension", description="", default='REPEAT')
    texture_interpolation: bpy.props.EnumProperty(items=TEXTURE_INTERPOLATION_MODES, name="Interpolation", description="", default='LINEAR')
    projection_blend: bpy.props.FloatProperty(name="Projection Blend", description="The projection blend amount", default=0.5, min=0.0, max=1.0, subtype='FACTOR', update=update_projection_blend)
    projection_offset_x: bpy.props.FloatProperty(name="Offset X", description="Projected x offset of the selected layer", default=0.0, min=-1.0, max=1.0, subtype='FACTOR', update=update_projected_offset_x)
    projection_offset_y: bpy.props.FloatProperty(name="Offset Y", description="Projected y offset of the selected layer", default=0.0, min=-1.0, max=1.0, subtype='FACTOR', update=update_projected_offset_y)
    projection_rotation: bpy.props.FloatProperty(name="Rotation", description="Projected rotation of the selected layer", default=0.0, min=-6.283185, max=6.283185, subtype='ANGLE', update=update_projected_rotation)
    projection_scale_x: bpy.props.FloatProperty(name="Scale X", description="Projected x scale of the selected layer", default=1.0, step=1, soft_min=-4.0, soft_max=4.0, subtype='FACTOR', update=update_projected_scale_x)
    projection_scale_y: bpy.props.FloatProperty(name="Scale Y", description="Projected y scale of the selected layer", default=1.0, step=1, soft_min=-4.0, soft_max=4.0, subtype='FACTOR', update=update_projected_scale_y)

    # Mask Nodes
    mask_node_name: bpy.props.StringProperty(name="Mask Node Name", default="")
    mask_mix_node_name: bpy.props.StringProperty(name="Mix Mask Node Name", default="")
    mask_coord_node_name: bpy.props.StringProperty(name="Mask Coord Node Name", default="")
    mask_mapping_node_name = bpy.props.StringProperty(name="Mask Mapping Node Name", default="")
    mask_levels_node_name = bpy.props.StringProperty(name="Mask Levels Node Name", default="")

    # Mask Projection Settings
    mask_projection_mode: bpy.props.EnumProperty(items=[('FLAT', "Flat", ""), ('BOX', "Box (Tri-Planar)", ""), ('SPHERE', "Sphere", ""),('TUBE', "Tube", "")],
                                            name="Projection", description="Projection type of the mask attached to the selected layer", default='FLAT', update=update_mask_projection)
    mask_projection_blend: bpy.props.FloatProperty(name="Mask Projection Blend", description="The mask projection blend amount", default=0.5, min=0.0, max=1.0, subtype='FACTOR', update=update_mask_projection_blend)
    projection_mask_offset_x: bpy.props.FloatProperty(name="Offset X", description="Projected x offset of the selected mask", default=0.0, min=-1.0, max=1.0, subtype='FACTOR', update=update_projected_mask_offset_x)
    projection_mask_offset_y: bpy.props.FloatProperty(name="Offset Y", description="Projected y offset of the selected mask", default=0.0, min=-1.0, max=1.0, subtype='FACTOR', update=update_projected_mask_offset_y)
    projection_mask_rotation: bpy.props.FloatProperty(name="Rotation", description="Projected rotation of the selected mask", default=0.0, min=-6.283185, max=6.283185, subtype='ANGLE', update=update_projected_mask_rotation)
    projection_mask_scale_x: bpy.props.FloatProperty(name="Scale X", description="Projected x scale of the selected mask", default=1.0, soft_min=-4.0, soft_max=4.0, subtype='FACTOR', update=update_projected_mask_scale_x)
    projection_mask_scale_y: bpy.props.FloatProperty(name="Scale Y", description="Projected y scale of the selected mask", default=1.0, soft_min=-4.0, soft_max=4.0, subtype='FACTOR', update=update_projected_mask_scale_y)

    # Node Types (used for properly drawing user interface for node properties)
    color_texture_node_type: bpy.props.EnumProperty(items=TEXTURE_NODE_TYPES, name = "Color Texture Node Type", description="The node type for the color channel texture", default='COLOR', update=update_color_texture_node_type)
    metallic_texture_node_type: bpy.props.EnumProperty(items=TEXTURE_NODE_TYPES, name = "Metallic Texture Node Type", description="The node type for the roughness channel texture", default='COLOR')
    roughness_texture_node_type: bpy.props.EnumProperty(items=TEXTURE_NODE_TYPES, name = "Roughness Texture Node Type", description="The node type for roughness channel texture", default='COLOR')
    normal_texture_node_type: bpy.props.EnumProperty(items=TEXTURE_NODE_TYPES, name = "Normal Texture Node Type", description="The node type for the texture", default='COLOR')
    height_texture_node_type: bpy.props.EnumProperty(items=TEXTURE_NODE_TYPES, name = "Height Texture Node Type", description="The node type for the texture", default='COLOR')
    scattering_texture_node_type: bpy.props.EnumProperty(items=TEXTURE_NODE_TYPES, name = "Scattering Texture Node Type", description="The node type for the texture", default='COLOR')
    emission_texture_node_type: bpy.props.EnumProperty(items=TEXTURE_NODE_TYPES, name = "Emission Texture Node Type", description="The node type for the texture", default='COLOR')
