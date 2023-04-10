# Masking module containing properties and functions for masking material layers.

import bpy
from bpy.types import Operator, PropertyGroup, UIList
from bpy.props import BoolProperty, IntProperty, FloatProperty, StringProperty, EnumProperty, PointerProperty
from ..core.layers import PROJECTION_MODES, TEXTURE_EXTENSION_MODES, TEXTURE_INTERPOLATION_MODES
from . import layer_nodes
from . import material_channels

MASK_NODE_TYPES = [
    ("TEXTURE", "Texture", "An image texture is used to represent the material channel."),
    ("GROUP_NODE", "Group Node", "A custom group node is used to represent the material channel. You can create a custom group node and add it to the layer stack using this mode, with the only requirement being the first node output must be the main value used to represent the material channel."),
    ("NOISE", "Noise", "Procedurally generated noise is used to represent the material channel."),
    ("VORONOI", "Voronoi", "A procedurally generated voronoi pattern is used to represent the material channel."),
    ("MUSGRAVE", "Musgrave", "A procedurally generated musgrave pattern is used to represent the material channel.")
    ]

#----------------------------- MASK AUTO UPDATING FUNCTIONS -----------------------------#


def update_layer_projection(self, context):
    '''Changes the layer projection by reconnecting nodes.'''
    if not context.scene.matlay_layer_stack.auto_update_layer_properties:
        return 
    
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

        if texture_node.type == 'TEX_IMAGE':
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

def update_projection_interpolation(self, context):
    '''Updates the image texture interpolation mode when it's changed.'''
    if not context.scene.matlay_layer_stack.auto_update_layer_properties:
        return 
    
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        texture_node = layer_nodes.get_layer_node("TEXTURE", material_channel_name, selected_layer_index, context)
        if texture_node and texture_node.type == 'TEX_IMAGE':
            texture_node.interpolation = layers[selected_layer_index].projection.texture_interpolation

def update_projection_extension(self, context):
    '''Updates the image texture extension projection mode when it's changed.'''
    if not context.scene.matlay_layer_stack.auto_update_layer_properties:
        return 
    
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        texture_node = layer_nodes.get_layer_node("TEXTURE", material_channel_name, selected_layer_index, context)
        if texture_node and texture_node.type == 'TEX_IMAGE':
            texture_node.extension = layers[selected_layer_index].projection.texture_extension

def update_projection_blend(self, context):
    '''Updates the projection blend node values when the cube projection blend value is changed.'''
    if not context.scene.matlay_layer_stack.auto_update_layer_properties:
        return

    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        texture_node = layer_nodes.get_layer_node("TEXTURE", material_channel_name, selected_layer_index, context)
        if texture_node and texture_node.type == 'TEX_IMAGE':
            texture_node.projection_blend = layers[selected_layer_index].projection.texture_extension

def update_projection_offset_x(self, context):
    if context.scene.matlay_layer_stack.auto_update_layer_properties:
        layers = context.scene.matlay_layers
        selected_layer_index = context.scene.matlay_layer_stack.layer_index

        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)

            if mapping_node:
                mapping_node.inputs[1].default_value[0] = layers[selected_layer_index].projection.projection_offset_x

def update_projection_offset_y(self, context):
    if context.scene.matlay_layer_stack.auto_update_layer_properties:
        layers = context.scene.matlay_layers
        selected_layer_index = context.scene.matlay_layer_stack.layer_index

        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)

            if mapping_node:
                mapping_node.inputs[1].default_value[1] = layers[selected_layer_index].projection.projection_offset_y

def update_projection_rotation(self, context):
    '''Updates the layer projections rotation for all layers.'''
    if context.scene.matlay_layer_stack.auto_update_layer_properties:
        layers = context.scene.matlay_layers
        selected_layer_index = context.scene.matlay_layer_stack.layer_index

        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)
            if mapping_node:
                mapping_node.inputs[2].default_value[2] = layers[selected_layer_index].projection.projection_rotation

def update_projection_scale_x(self, context):
    '''Updates the layer projections x scale for all mapping nodes in the selected layer.'''
    if context.scene.matlay_layer_stack.auto_update_layer_properties:
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
    if context.scene.matlay_layer_stack.auto_update_layer_properties:
        layers = context.scene.matlay_layers
        selected_layer_index = context.scene.matlay_layer_stack.layer_index

        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            mapping_node = layer_nodes.get_layer_node("MAPPING", material_channel_name, selected_layer_index, context)
            
            if mapping_node:
                mapping_node.inputs[3].default_value[1] = layers[selected_layer_index].projection.projection_scale_y

def update_match_layer_scale(self, context):
    '''Updates matching of the projected layer scales.'''
    if self.match_layer_scale and context.scene.matlay_layer_stack.auto_update_layer_properties:
        layers = context.scene.matlay_layers
        layer_index = context.scene.matlay_layer_stack.layer_index
        layers[layer_index].projection.projection_scale_y = layers[layer_index].projection.projection_scale_x


#----------------------------- CORE MASK FUNCTIONS -----------------------------#

def format_mask_node_name(mask_node_type, material_layer_index, filter_index):
    '''All node names including mask node names must be formatted properly so they can be re-read from the layer stack. This function should be used to properly format the name of a mask node.'''
    return  "{0}_{1}_{2}".format(mask_node_type, str(material_layer_index), str(filter_index))

#def get_all_layer_mask_nodes(material_channel_name, material_layer_index, context):
#   '''Returns an array of all mask nodes that exist within the given material channel for the provided layer index'''

#def update_layer_mask_node_indicies(context):
#    '''Renames all mask nodes with correct indicies by checking the node tree for newly added, edited #(signified by a tilda at the end of their name), or deleted filter nodes'''


def add_default_mask_nodes(context):
    '''Adds default mask nodes to all material channels.'''
    selected_layer_index = context.scene.matlay_layer_stack.layer_index

    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
        if material_channel_node:
                
            # Create default mask nodes.
            mask_node = material_channel_node.node_tree.nodes.new('ShaderNodeTexImage')
            mask_node.name = "MASK_TEXTURE_" + str(selected_layer_index) + "~"
            mask_node.label = mask_node.name
                
            mask_coord_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeTexCoord')
            mask_coord_node.name = "MASK_COORD_" + str(selected_layer_index) + "~"
            mask_coord_node.label = mask_coord_node.name

            mask_mapping_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeMapping')
            mask_mapping_node.name = "MASK_MAPPING_" + str(selected_layer_index) + "~"
            mask_mapping_node.label = mask_mapping_node.name

            mask_mix_node = material_channel_node.node_tree.nodes.new('ShaderNodeMixRGB')
            mask_mix_node.name = "MASK_MIX_LAYER_" + str(selected_layer_index) + "~"
            mask_mix_node.label = mask_mix_node.name
                
            # Link new nodes.
            material_channel_node.node_tree.links.new(mask_coord_node.outputs[2], mask_mapping_node.inputs[0])
            material_channel_node.node_tree.links.new(mask_mapping_node.outputs[0], mask_node.inputs[0])

            # Link mix layer node to the mix mask node.
            mix_layer_node = layer_nodes.get_layer_node("MIXLAYER", material_channel_name, selected_layer_index, context)
            material_channel_node.node_tree.links.new(mix_layer_node.outputs[0], mask_mix_node.inputs[1])

            # Add the nodes to the layer frame.
            frame = layer_nodes.get_layer_frame(material_channel_name, selected_layer_index, context)
            if frame:
                mask_node.parent = frame
                mask_mix_node.parent = frame
                mask_coord_node.parent = frame
                mask_mapping_node.parent = frame
                
            # Update the layer nodes.
            layer_nodes.update_layer_nodes(context)

def add_mask(mask_type, context):
    '''Adds a mask of the specified type to the selected material layer.'''
    match mask_type:
        case 'BLACK_TEXTURE':
            masks = context.scene.matlay_masks
            masks.add()
            

            add_default_mask_nodes(context)

            # TODO: Update the mask node indicies.

            # TODO: Re-link nodes.

            # TODO: Organize nodes.


#----------------------------- MASK PROPERTIES & OPERATORS -----------------------------#

class MaskProjectionSettings(PropertyGroup):
    '''Projection settings for this add-on.'''
    projection_mode: EnumProperty(items=PROJECTION_MODES, name="Projection", description="Projection type of the image attached to the selected layer", default='FLAT')
    texture_extension: EnumProperty(items=TEXTURE_EXTENSION_MODES, name="Extension", description="", default='REPEAT')
    texture_interpolation: EnumProperty(items=TEXTURE_INTERPOLATION_MODES, name="Interpolation", description="", default='Linear')
    projection_blend: FloatProperty(name="Projection Blend", description="The projection blend amount", default=0.5, min=0.0, max=1.0, subtype='FACTOR')
    projection_offset_x: FloatProperty(name="Offset X", description="Projected x offset of the selected layer", default=0.0, min=-1.0, max=1.0, subtype='FACTOR')
    projection_offset_y: FloatProperty(name="Offset Y", description="Projected y offset of the selected layer", default=0.0, min=-1.0, max=1.0, subtype='FACTOR')
    projection_rotation: FloatProperty(name="Rotation", description="Projected rotation of the selected layer", default=0.0, min=-6.283185, max=6.283185, subtype='ANGLE')
    projection_scale_x: FloatProperty(name="Scale X", description="Projected x scale of the selected layer", default=1.0, step=1, soft_min=-4.0, soft_max=4.0, subtype='FACTOR')
    projection_scale_y: FloatProperty(name="Scale Y", description="Projected y scale of the selected layer", default=1.0, step=1, soft_min=-4.0, soft_max=4.0, subtype='FACTOR')
    match_layer_scale: BoolProperty(name="Match Layer Scale", default=True,update=update_match_layer_scale)
    match_layer_mask_scale: BoolProperty(name="Match Layer Mask Scale", default=True)

class MATLAY_mask_stack(PropertyGroup):
    '''Properties for the mask stack.'''
    selected_mask_index: IntProperty(default=-1)
    mask_property_tab: EnumProperty(
        items=[('MASK', "MASK", "Properties for the selected mask."),
               ('PROJECTION', "PROJECTION", "Projection settings for the selected mask."),
               ('FILTERS', "FILTERS", "Filters for the selcted mask.")],
        name="Mask Properties Tab",
        description="Tabs for mask properties.",
        default='MASK',
        options={'HIDDEN'},
    )

class MATLAY_masks(PropertyGroup):
    '''Properties for layer masks.'''
    name: StringProperty(name="Mask Name", default="Mask Naming Error")
    projection: PointerProperty(type=MaskProjectionSettings)
    texture_type: EnumProperty(items=MASK_NODE_TYPES, name="Mask Texture Type", description="The node type for the texture used as a mask", default='TEXTURE')

class MATLAY_UL_mask_stack(bpy.types.UIList):
    '''Draws the mask stack for the selected layer.'''
    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=self.name)

class MATLAY_OT_add_black_layer_mask(Operator):
    '''Creates a new completely black texture and adds it to a new mask. Use this for when only a portion of the object is planned to be masked'''
    bl_idname = "matlay.add_black_layer_mask"
    bl_label = "Add Black Mask"
    bl_description = "Creates a new completely black texture and adds it to a new mask. Use this for when only a portion of the object is planned to be masked"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        add_mask('BLACK_MASK', context)
        return{'FINISHED'}

class MATLAY_OT_add_white_layer_mask(Operator):
    '''Creates a new completely white texture and adds it to a new mask. Use this for when the majority of the object is masked.'''
    bl_idname = "matlay.add_white_layer_mask"
    bl_label = "Add White Mask"
    bl_description = "Adds a mask to the selected layer"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        add_mask('WHITE_MASK', context)
        return{'FINISHED'}
    
class MATLAY_OT_add_empty_layer_mask(Operator):
    '''Adds a layer mask to the selected layer with no texture assigned to it's texture slot. Use this operator to add a mask for when you will load a custom texture into the newly added mask, or you plan to change to a procedural node type after adding the mask (noise, voronoi, musgrave).'''
    bl_idname = "matlay.add_empty_layer_mask"
    bl_label = "Add Empty Mask"
    bl_description = "Adds a layer mask to the selected layer with no texture assigned to it's texture slot"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        add_mask('EMPTY', context)
        return{'FINISHED'}

class MATLAY_OT_open_layer_mask_menu(Operator):
    '''Opens a menu of masks that can be added to the selected material layer.'''
    bl_idname = "matlay.open_layer_mask_menu"
    bl_label = "Open Layer Mask Menu"
    bl_description = "Opens a menu of masks that can be added to the selected material layer"

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

    # Opens the menu when the button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=150)

    # Draws the properties in the popup.
    def draw(self, context):
        layout = self.layout
        split = layout.split()
        col = split.column(align=True)
        col.scale_y = 1.4
        col.operator("matlay.add_black_layer_mask", text="Black Mask")
        col.operator("matlay.add_white_layer_mask", text="White Mask")
        col.operator("matlay.add_empty_layer_mask", text="Empty Mask")

class MATLAY_OT_delete_layer_mask(Operator):
    bl_idname = "matlay.delete_layer_mask"
    bl_label = "Delete Layer Mask"
    bl_description = "Deletes the mask for the selected layer if one exists"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
        masks = context.scene.matlay_masks

        masks.remove(selected_mask_index)

        return{'FINISHED'}

class MATLAY_OT_move_layer_mask_up(Operator):
    '''Moves the selected layer up on the layer stack'''
    bl_idname = "matlay.move_layer_mask_up"
    bl_label = "Move Layer Mask Up"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the selected layer up on the layer stack"

    def execute(self, context):
        return {'FINISHED'}

class MATLAY_OT_move_layer_mask_down(Operator):
    '''Moves the selected layer down on the layer stack'''
    bl_idname = "matlay.move_layer_mask_down"
    bl_label = "Move Layer Mask Down"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the selected layer down on the layer stack"

    def execute(self, context):
        return {'FINISHED'}


#----------------------------- MASK FILTERS -----------------------------#

class MATLAY_mask_filter_stack(PropertyGroup):
    '''Properties for the mask stack.'''
    selected_mask_index: IntProperty(default=-1)

class MATLAY_mask_filters(PropertyGroup):
    name: StringProperty(name="Mask Name", description="The name of the layer mask.", default="Invalid Name")
    stack_index: IntProperty(name="Stack Index", description = "The (array) stack index for this filter used to define the order in which filters should be applied to the material", default=-999)

class MATLAY_UL_mask_filter_stack(UIList):
    '''Draws the mask stack for the selected layer.'''
    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text="SOMETHING HERE")

class MATLAY_OT_add_mask_filter_invert(Operator):
    '''Adds an invert adjustment to the masks applied to the selected layer'''
    bl_idname = "matlay.add_mask_filter_invert"
    bl_label = "Add Invert Mask Filter"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds an invert adjustment to the masks applied to the selected layer"

    def execute(self, context):
        return {'FINISHED'}

class MATLAY_OT_add_mask_filter_levels(Operator):
    '''Adds a level adjustment to the masks applied to the selected layer'''
    bl_idname = "matlay.add_mask_filter_levels"
    bl_label = "Add Levels Mask Filter"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds a level adjustment to the masks applied to the selected layer"

    def execute(self, context):
        return {'FINISHED'}

class MATLAY_OT_add_layer_mask_filter_menu(Operator):
    '''Opens a menu of filters that can be added to the selected mask.'''
    bl_label = ""
    bl_idname = "matlay.add_layer_mask_filter_menu"
    bl_description = "Opens a menu of layer filters that can be added to the selected mask stack"

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

    # Opens the popup when the add layer button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=150)

    # Draws the properties in the popup.
    def draw(self, context):
        layout = self.layout
        split = layout.split()
        col = split.column(align=True)
        col.scale_y = 1.4
        col.operator("matlay.add_mask_filter_invert")
        col.operator("matlay.add_mask_filter_levels")

class MATLAY_OT_delete_mask_filter(Operator):
    bl_idname = "matlay.delete_mask_filter"
    bl_label = "Delete Mask Filter"
    bl_description = "Deletes the mask filter"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        # TODO: Delete the selected mask filter.
        return{'FINISHED'}
    
class MATLAY_OT_move_layer_mask_filter(Operator):
    '''Moves the selected layer mask filter on the layer stack'''
    bl_idname = "matlay.move_layer_mask_filter"
    bl_label = "Move Mask Filter"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the selected layer mask filter on the layer stack"

    direction: StringProperty(default="True")

    def execute(self, context):
        # TODO: Implement moving layer mask filters up or down on the layer mask filter stack.
        if self.direction == 'UP':
            print("Moved layer mask filter up.")
        else:
            print("Moved layer mask filter down.")
        return {'FINISHED'}