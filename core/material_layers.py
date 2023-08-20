# This file contains layer properties and functions for updating layer properties.

import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import BoolProperty, FloatProperty, EnumProperty, StringProperty
import math

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
    ("FLAT", "UV / Flat", "Projects the texture using the model's UV map."),
    ("TRIPLANAR", "Triplanar", "Projects the textures onto the object from each axis. This projection method can be used to quickly remove seams from objects."),
    #("SPHERE", "Sphere", ""),
    #("TUBE", "Tube", "")
]

TEXTURE_EXTENSION_MODES = [
    ("REPEAT", "Repeat", ""), 
    ("EXTEND", "Extend", ""),
    ("CLIP", "Clip", "")
]

TEXTURE_INTERPOLATION_MODES = [
    ("Linear", "Linear", ""),
    ("Cubic", "Cubic", ""),
    ("Closest", "Closest", ""),
    ("Smart", "Smart", "")
]

MATERIAL_CHANNELS = [
    ("COLOR", "Color", ""), 
    ("SUBSURFACE", "Subsurface", ""),
    ("SUBSURFACE_COLOR", "Subsurface Color", ""),
    ("METALLIC", "Metallic", ""),
    ("SPECULAR", "Specular", ""),
    ("ROUGHNESS", "Roughness", ""),
    ("EMISSION", "Emission", ""),
    ("NORMAL", "Normal", ""),
    ("HEIGHT", "Height", "")
]

MATERIAL_LAYER_TYPES = [
    ("FILL", "Fill", "A layer that fills the entier object with a material."), 
    ("DECAL", "Decal", "A material projected onto the model using a decal object (empty) which allows users to dynamically position textures.")
]

class MATLAYER_layer_stack(PropertyGroup):
    '''Properties for the layer stack.'''
    selected_layer_index: bpy.props.IntProperty(default=-1)
    material_channel_preview: bpy.props.BoolProperty(name="Material Channel Preview", description="If true, only the rgb output values for the selected material channel will be used on the object.", default=False)
    node_default_width: bpy.props.IntProperty(default=250)
    node_spacing: bpy.props.IntProperty(default=80)
    selected_material_channel: bpy.props.EnumProperty(items=MATERIAL_CHANNELS, name="Material Channel", description="The currently selected material channel", default='COLOR')
    auto_update_layer_properties: bpy.props.BoolProperty(name="Auto Update Layer Properties", description="When true, select layer properties are automatically updated when changed. This toggle is used for rare cases when you want to perform an operation where layer properties are edited without them automatically updating (i.e refreshing / reading the layer stack)", default=True)

    # Note: These tabs exist to help keep the user interface elements on screen limited, thus simplifying the editing process, and helps avoid the need to scroll down on the user interface to see settings.
    # Tabs for material / mask layer properties.
    layer_property_tab: bpy.props.EnumProperty(
        items=[('MATERIAL', "MATERIAL", "Material settings for the selected layer."),
               ('MASK', "MASK", "Mask settings for the selected layer.")],
        name="Layer Properties Tab",
        description="Tabs for layer properties.",
        default='MATERIAL',
        options={'HIDDEN'},
    )

    material_property_tab: bpy.props.EnumProperty(
        items=[('MATERIAL', "MATERIAL", "Material properties for the selected material layer."),
               ('PROJECTION', "PROJECTION", "Projection settings for the selected material layer."),
               ('FILTERS', "FILTERS", "Layer filters and their properties for the selected material layer.")],
        name="Material Property Tabs",
        description="Tabs for material layer properties",
        default='MATERIAL',
        options={'HIDDEN'},       
    )

    mask_property_tab: bpy.props.EnumProperty(
        items=[('FILTERS', "FILTERS", "Masks, their properties and filters for masks."),
               ('PROJECTION', "PROJECTION", "Projection settings for the selected mask.")],
        name="Mask Property Tabs",
        description="Tabs for layer mask properties.",
        default='FILTERS',
        options={'HIDDEN'},
    )

class MATLAYER_layers(PropertyGroup):
    name: StringProperty(name="", description="The name of the layer", default="Layer Naming Error")
    opacity: FloatProperty(name="Opacity", description="Layers Opacity", default=1.0, min=0.0, soft_max=1.0, subtype='FACTOR')
    hidden: BoolProperty(name="Hidden", description="Show if the layer is hidden")

class MATLAYER_OT_add_layer(Operator):
    bl_idname = "matlayer.add_layer"
    bl_label = "Add Layer"
    bl_description = ""

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):

        # TODO: Append / add the layer group node.

        # TODO: Connect to other existing layers.

        # TODO: Organize layer group nodes.

        return {'FINISHED'}
    
class MATLAYER_OT_delete_layer(Operator):
    bl_idname = "matlayer.delete_layer"
    bl_label = "Delete Layer"
    bl_description = ""

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):

        return {'FINISHED'}
    
class MATLAYER_OT_duplicate_layer(Operator):
    bl_idname = "matlayer.duplicate_layer"
    bl_label = "Duplicate Layer"
    bl_description = ""

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):

        return {'FINISHED'}
    
class MATLAYER_OT_move_layer(Operator):
    bl_idname = "matlayer.move_layer"
    bl_label = "Move Layer"
    bl_description = ""

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):

        return {'FINISHED'}