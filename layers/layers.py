import os
import bpy
from bpy.types import PropertyGroup
from .import coater_node_info
from .import link_layers

def layer_image_path_error(self, context):
    self.layout.label(text="Layer image path does not exist, so the image can't be renamed! Manually save the image to the layer folder to resolve the error.")

def update_layer_name(self, context):
    '''Updates layer nodes, frames when the layer name is changed.'''
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node = coater_node_info.get_channel_node(context)

    if layer_index != -1:
        # Rename the layer's frame node. The frame name must be unique, so the layer's ID is added.
        frame = channel_node.node_tree.nodes.get(layers[layer_index].frame_name)
        if frame != None:
            frame.name = layers[layer_index].name + "_" + str(layers[layer_index].id) + "_" + str(layer_index)
            frame.label = frame.name
            layers[layer_index].frame_name = frame.name

        # If the image assigned to this layer is an image layer, rename the image too.
        image = coater_node_info.get_layer_image(context, layer_index)
        if image != None:
            image_name_split = image.name.split('_')

            if image_name_split[0] == 'l':
                image.name = "l_" + layers[layer_index].name + "_" + str(layers[layer_index].id)
        
def update_layer_projection(self, context):
    '''Changes the layer projection by reconnecting nodes.'''
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node_group = coater_node_info.get_channel_node_group(context)
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
    channel_node_group = coater_node_info.get_channel_node_group(context)
    color_node = channel_node_group.nodes.get(layers[layer_index].color_node_name)
    
    if color_node != None:
        color_node.projection_blend = layers[layer_index].projection_blend

def update_mask_projection_blend(self, context):
    '''Updates the mask projection blend node values when the cube projection blend value is changed.'''
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node_group = coater_node_info.get_channel_node_group(context)
    mask_node = channel_node_group.nodes.get(layers[layer_index].mask_node_name)

    if mask_node != None:
        mask_node.projection_blend = layers[layer_index].mask_projection_blend

def update_mask_projection(self, context):
    '''Changes the mask projection by reconnecting nodes.'''
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index
    channel_node_group = coater_node_info.get_channel_node_group(context)
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
    opacity_node = coater_node_info.get_self_node(self, context, 'OPACITY')

    if opacity_node != None:
        opacity_node.inputs[1].default_value = self.opacity

def update_hidden(self, context):
    '''Updates node values when the layer hidden property is changed.'''

    if self.hidden == True:
        nodes = coater_node_info.get_self_layer_nodes(self, context)
        for n in nodes:
            n.mute = True
    else:
        nodes = coater_node_info.get_self_layer_nodes(self, context)
        for n in nodes:
            n.mute = False


    link_layers.link_layers(context)

def update_projected_offset_x(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mapping_node = coater_node_info.get_node(context, 'MAPPING', layer_index)

    # Set the mapping node value.
    if mapping_node != None:
        mapping_node.inputs[1].default_value[0] = layers[layer_index].projected_offset_x

def update_projected_offset_y(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mapping_node = coater_node_info.get_node(context, 'MAPPING', layer_index)

    # Set the mapping node value.
    if mapping_node != None:
        mapping_node.inputs[1].default_value[1] = layers[layer_index].projected_offset_y

def update_projected_rotation(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mapping_node = coater_node_info.get_node(context, 'MAPPING', layer_index)

    # Set the mapping node value.
    if mapping_node != None:
        mapping_node.inputs[2].default_value[2] = layers[layer_index].projected_rotation

def update_projected_scale_x(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mapping_node = coater_node_info.get_node(context, 'MAPPING', layer_index)

    # Set the mapping node value.
    if mapping_node != None:
        mapping_node.inputs[3].default_value[0] = layers[layer_index].projected_scale_x

def update_projected_scale_y(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mapping_node = coater_node_info.get_node(context, 'MAPPING', layer_index)

    # Set the mapping node value.
    if mapping_node != None:
        mapping_node.inputs[3].default_value[1] = layers[layer_index].projected_scale_y

def update_projected_mask_offset_x(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mask_mapping_node = coater_node_info.get_node(context, 'MASK_MAPPING', layer_index)

    # Set the mapping node value.
    if mask_mapping_node != None:
        mask_mapping_node.inputs[1].default_value[0] = layers[layer_index].projected_mask_offset_x

def update_projected_mask_offset_y(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mask_mapping_node = coater_node_info.get_node(context, 'MASK_MAPPING', layer_index)

    # Set the mapping node value.
    if mask_mapping_node != None:
        mask_mapping_node.inputs[1].default_value[1] = layers[layer_index].projected_mask_offset_y

def update_projected_mask_rotation(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mask_mapping_node = coater_node_info.get_node(context, 'MASK_MAPPING', layer_index)

    # Set the mapping node value.
    if mask_mapping_node != None:
        mask_mapping_node.inputs[2].default_value[2] = layers[layer_index].projected_mask_rotation

def update_projected_mask_scale_x(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mask_mapping_node = coater_node_info.get_node(context, 'MASK_MAPPING', layer_index)

    # Set the mapping node value.
    if mask_mapping_node != None:
        mask_mapping_node.inputs[3].default_value[0] = layers[layer_index].projected_mask_scale_x

def update_projected_mask_scale_y(self, context):
    layers = context.scene.coater_layers
    layer_index = context.scene.coater_layer_stack.layer_index

    # Get the mapping node.
    mask_mapping_node = coater_node_info.get_node(context, 'MASK_MAPPING', layer_index)

    # Set the mapping node value.
    if mask_mapping_node != None:
        mask_mapping_node.inputs[3].default_value[1] = layers[layer_index].projected_mask_scale_y

class COATER_layers(PropertyGroup):
    id: bpy.props.IntProperty(name="ID", description="Numeric ID for the selected layer.", default=0)

    name: bpy.props.StringProperty(
        name="",
        description="The name of the layer",
        default="Layer naming error",
        update=update_layer_name)

    type: bpy.props.EnumProperty(
        items=[('IMAGE_LAYER', "Image Layer", ""),
               ('COLOR_LAYER', "Color Layer", "")],
        name="",
        description="Type of the layer",
        default='IMAGE_LAYER',
        options={'HIDDEN'},
    )

    # Projection Settings
    projection: bpy.props.EnumProperty(
        items=[('FLAT', "Flat", ""),
               ('BOX', "Box (Tri-Planar)", ""),
               ('SPHERE', "Sphere", ""),
               ('TUBE', "Tube", "")],
        name="Projection",
        description="Projection type of the image attached to the selected layer",
        default='FLAT',
        update=update_layer_projection
    )

    projection_blend: bpy.props.FloatProperty(name="Projection Blend", description="The projection blend amount.", default=0.5, min=0.0, max=1.0, subtype='FACTOR', update=update_projection_blend)

    projected_offset_x: bpy.props.FloatProperty(name="Offset X", description="Projected x offset of the selected layer.", default=0.0, min=-1.0, max=1.0, subtype='FACTOR', update=update_projected_offset_x)
    projected_offset_y: bpy.props.FloatProperty(name="Offset Y", description="Projected y offset of the selected layer.", default=0.0, min=-1.0, max=1.0, subtype='FACTOR', update=update_projected_offset_y)
    projected_rotation: bpy.props.FloatProperty(name="Rotation", description="Projected rotation of the selected layer.", default=0.0, min=-6.283185, max=6.283185, subtype='ANGLE', update=update_projected_rotation)
    projected_scale_x: bpy.props.FloatProperty(name="Scale X", description="Projected x scale of the selected layer.", default=1.0, step=1, soft_min=-4.0, soft_max=4.0, subtype='FACTOR', update=update_projected_scale_x)
    projected_scale_y: bpy.props.FloatProperty(name="Scale Y", description="Projected y scale of the selected layer.", default=1.0, step=1, soft_min=-4.0, soft_max=4.0, subtype='FACTOR', update=update_projected_scale_y)

    # Mask Projection Settings
    mask_projection: bpy.props.EnumProperty(
        items=[('FLAT', "Flat", ""),
               ('BOX', "Box (Tri-Planar)", ""),
               ('SPHERE', "Sphere", ""),
               ('TUBE', "Tube", "")],
        name="Projection",
        description="Projection type of the mask attached to the selected layer",
        default='FLAT',
        update=update_mask_projection
    )

    mask_projection_blend: bpy.props.FloatProperty(name="Mask Projection Blend", description="The mask projection blend amount.", default=0.5, min=0.0, max=1.0, subtype='FACTOR', update=update_mask_projection_blend)

    projected_mask_offset_x: bpy.props.FloatProperty(name="Offset X", description="Projected x offset of the selected mask.", default=0.0, min=-1.0, max=1.0, subtype='FACTOR', update=update_projected_mask_offset_x)
    projected_mask_offset_y: bpy.props.FloatProperty(name="Offset Y", description="Projected y offset of the selected mask.", default=0.0, min=-1.0, max=1.0, subtype='FACTOR', update=update_projected_mask_offset_y)
    projected_mask_rotation: bpy.props.FloatProperty(name="Rotation", description="Projected rotation of the selected mask.", default=0.0, min=-6.283185, max=6.283185, subtype='ANGLE', update=update_projected_mask_rotation)
    projected_mask_scale_x: bpy.props.FloatProperty(name="Scale X", description="Projected x scale of the selected mask.", default=1.0, soft_min=-4.0, soft_max=4.0, subtype='FACTOR', update=update_projected_mask_scale_x)
    projected_mask_scale_y: bpy.props.FloatProperty(name="Scale Y", description="Projected y scale of the selected mask.", default=1.0, soft_min=-4.0, soft_max=4.0, subtype='FACTOR', update=update_projected_mask_scale_y)

    opacity: bpy.props.FloatProperty(name="Opacity",
                                     description="Opacity of the currently selected layer.",
                                     default=1.0,
                                     min=0.0,
                                     soft_max=1.0,
                                     subtype='FACTOR',
                                     update=update_layer_opacity)

    hidden: bpy.props.BoolProperty(name="", update=update_hidden)
    masked: bpy.props.BoolProperty(name="", default=True)

    # Store nodes.
    frame_name: bpy.props.StringProperty(default="")
    coord_node_name: bpy.props.StringProperty(default="")
    mapping_node_name: bpy.props.StringProperty(default="")
    color_node_name: bpy.props.StringProperty(default="")
    opacity_node_name: bpy.props.StringProperty(default="")
    mix_layer_node_name: bpy.props.StringProperty(default="")

    # Store mask nodes.
    mask_node_name: bpy.props.StringProperty(default="")
    mask_mix_node_name: bpy.props.StringProperty(default="")
    mask_coord_node_name: bpy.props.StringProperty(default="")
    mask_mapping_node_name: bpy.props.StringProperty(default="")
    mask_levels_node_name: bpy.props.StringProperty(default="")