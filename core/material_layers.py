# This file contains layer properties and functions for updating layer properties.

import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import BoolProperty, IntProperty, EnumProperty, StringProperty, PointerProperty
from . import blender_addon_utils
import random

# List of node types that can be used in the texture slot.

PROJECTION_MODES = [
    ("FLAT", "UV / Flat", "Projects the texture using the model's UV map."),
    ("TRIPLANAR", "Triplanar", "Projects the textures onto the object from each axis. This projection method can be used to quickly remove seams from objects."),
    #("SPHERE", "Sphere", ""),
    #("TUBE", "Tube", "")
]

TEXTURE_NODE_TYPES = [
    ("GROUP", "GROUP", ""),
    ("TEXTURE", "TEXTURE", ""),
]

TEXTURE_INTERPOLATION_MODES = [
    ("Linear", "Linear", ""),
    ("Cubic", "Cubic", ""),
    ("Closest", "Closest", ""),
    ("Smart", "Smart", "")
]

MATERIAL_CHANNEL = [
    ("COLOR", "Color", ""), 
    ("SUBSURFACE", "Subsurface", ""),
    ("METALLIC", "Metallic", ""),
    ("SPECULAR", "Specular", ""),
    ("ROUGHNESS", "Roughness", ""),
    ("EMISSION", "Emission", ""),
    ("NORMAL", "Normal", ""),
    ("HEIGHT", "Height", ""),
    ("ALPHA", "Alpha", "")
]

MATERIAL_CHANNEL_LIST = (
    'COLOR',
    'SUBSURFACE',
    'METALLIC',
    'SPECULAR',
    'ROUGHNESS',
    'EMISSION',
    'NORMAL',
    'HEIGHT',
    'ALPHA'
)

MATERIAL_LAYER_TYPES = [
    ("FILL", "Fill", "A layer that fills the entier object with a material."), 
    ("DECAL", "Decal", "A material projected onto the model using a decal object (empty) which allows users to dynamically position textures.")
]

class MATLAYER_layer_stack(PropertyGroup):
    '''Properties for the layer stack.'''
    selected_layer_index: IntProperty(default=-1, description="Selected material layer")
    material_channel_preview: BoolProperty(name="Material Channel Preview", description="If true, only the rgb output values for the selected material channel will be used on the object.", default=False)
    selected_material_channel: EnumProperty(items=MATERIAL_CHANNEL, name="Material Channel", description="The currently selected material channel", default='COLOR')

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

def replace_material_channel_node(material_channel_name, node_type):
    '''Replaces the existing material channel node with a new node of the given type.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    layer_group_node = get_layer_node_tree(selected_layer_index)
    value_node = get_material_layer_node('VALUE', selected_layer_index, material_channel_name)
    old_node_location = value_node.location

    layer_group_node.nodes.remove(value_node)

    match node_type:
        case 'GROUP':
            new_node = layer_group_node.nodes.new('ShaderNodeGroup')
            channel_name = material_channel_name.lower()
            default_node_tree = bpy.data.node_groups.get("ML_Default{0}".format(channel_name.capitalize()))
            new_node.node_tree = default_node_tree
        case 'TEXTURE':
            new_node = layer_group_node.nodes.new('ShaderNodeTexImage')
            projection_node = get_material_layer_node('PROJECTION', selected_layer_index, material_channel_name)
            layer_group_node.links.new(projection_node.outputs[0], new_node.inputs[0])

    new_node.name = "{0}_VALUE".format(material_channel_name)
    new_node.label = new_node.name
    new_node.location = old_node_location
    new_node.width = 200

    mix_node = get_material_layer_node('MIX', selected_layer_index, material_channel_name)
    layer_group_node.links.new(new_node.outputs[0], mix_node.inputs[7])

def update_color_channel_node_type(self, context):
    replace_material_channel_node('COLOR', self.color_node_type)

def update_subsurface_channel_node_type(self, context):
    replace_material_channel_node('SUBSURFACE', self.subsurface_node_type)

def update_metallic_channel_node_type(self, context):
    replace_material_channel_node('METALLIC', self.metallic_node_type)

def update_specular_channel_node_type(self, context):
    replace_material_channel_node('SPECULAR', self.specular_node_type)

def update_roughness_channel_node_type(self, context):
    replace_material_channel_node('ROUGHNESS', self.roughness_node_type)

def update_emission_channel_node_type(self, context):
    replace_material_channel_node('EMISSION', self.emission_node_type)

def update_normal_channel_node_type(self, context):
    replace_material_channel_node('NORMAL', self.normal_node_type)

def update_height_channel_node_type(self, context):
    replace_material_channel_node('HEIGHT', self.height_node_type)

def update_alpha_channel_node_type(self, context):
    replace_material_channel_node('ALPHA', self.alpha_node_type)

class MaterialChannelNodeType(PropertyGroup):
    '''An enum node type for the material node used to represent the material channel texture in every material channel.'''
    color_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Color Channel Node Type", description="The node type for the color channel", default='GROUP', update=update_color_channel_node_type)
    subsurface_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Subsurface Scattering Channel Node Type", description="The node type for the subsurface scattering channel", default='GROUP', update=update_subsurface_channel_node_type)
    metallic_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Metallic Channel Node Type", description="The node type for the metallic channel", default='GROUP', update=update_metallic_channel_node_type)
    specular_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Specular Channel Node Type", description="The node type for the specular channel", default='GROUP', update=update_specular_channel_node_type)
    roughness_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Roughness Channel Node Type", description="The node type for roughness channel", default='GROUP', update=update_roughness_channel_node_type)
    emission_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Emission Channel Node Type", description="The node type for the emission channel", default='GROUP', update=update_emission_channel_node_type)
    normal_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Normal Channel Node Type", description="The node type for the normal channel", default='GROUP', update=update_normal_channel_node_type)
    height_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Height Channel Node Type", description="The node type for the height channel", default='GROUP', update=update_height_channel_node_type)
    alpha_node_type: EnumProperty(items=TEXTURE_NODE_TYPES, name="Alpha Channel Node Type", description="The node type for the alpha channel", default='GROUP', update=update_emission_channel_node_type)

class MATLAYER_layers(PropertyGroup):
    hidden: BoolProperty(name="Hidden", description="Show if the layer is hidden")
    material_channel_node_types: PointerProperty(type=MaterialChannelNodeType)

class MATLAYER_OT_add_material_layer(Operator):
    bl_idname = "matlayer.add_material_layer"
    bl_label = "Add Material Layer"
    bl_description = ""

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        active_object = bpy.context.active_object

        # Append default node groups to avoid them being duplicated if they are imported as a sub node group.
        blender_addon_utils.append_default_node_groups()

        # Run checks the make sure this operator can be ran without errors, display info messages to users if it can't be ran.
        if active_object.type != 'MESH':
            blender_addon_utils.log_status("Selected object must be a mesh to add materials", self, 'ERROR')
            return {'FINISHED'}

        # If there are no material slots, or no material in the active material slot, make a new MatLayer material by appending the default material setup.
        if len(active_object.material_slots) == 0:
            new_material = blender_addon_utils.append_material("DefaultMatLayerMaterial")
            new_material.name = active_object.name
            active_object.data.materials.append(new_material)
            active_object.active_material_index = 0

        elif active_object.material_slots[active_object.active_material_index].material == None:
            new_material = blender_addon_utils.append_material("DefaultMatLayerMaterial")
            new_material.name = active_object.name
            active_object.material_slots[active_object.active_material_index].material = new_material

        new_layer_slot_index = add_material_layer_slot()

        # Add a material layer by appending a layer group node.
        active_material = bpy.context.active_object.active_material
        default_layer_node_group = blender_addon_utils.append_node_group("ML_DefaultLayer", never_auto_delete=True)
        default_layer_node_group.name = "{0}_{1}".format(active_material.name, str(new_layer_slot_index))
        new_layer_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
        new_layer_group_node.node_tree = default_layer_node_group
        new_layer_group_node.name = str(new_layer_slot_index)               # Layer index within the material layer stack.
        new_layer_group_node.label = "Layer " + str(new_layer_slot_index)   # Layer display name.
        
        organize_layer_group_nodes()
        connect_layer_group_nodes()

        return {'FINISHED'}

class MATLAYER_OT_add_paint_material_layer(Operator):
    bl_idname = "matlayer.add_paint_material_layer"
    bl_label = "Add Paint Material Layer"
    bl_description = "Creates a material layer and an image texture that's placed in the materials color channel"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}

class MATLAYER_OT_add_decal_material_layer(Operator):
    bl_idname = "matlayer.add_decal_material_layer"
    bl_label = "Add Decal Material Layer"
    bl_description = ""

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
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
        layers = context.scene.matlayer_layers
        selected_layer_index = context.scene.matlayer_layer_stack.selected_layer_index
        layers.remove(selected_layer_index)
        context.scene.matlayer_layer_stack.layer_index = max(min(selected_layer_index - 1, len(layers) - 1), 0)
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
    
class MATLAYER_OT_move_material_layer(Operator):
    bl_idname = "matlayer.move_material_layer"
    bl_label = "Move Layer"
    bl_description = "Moves the material layer up or down on the layer stack"

    direction: StringProperty(default='UP')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):

        return {'FINISHED'}


#----------------------------- MATERIAL CHANNEL IMAGES / TEXTURES -----------------------------#

class MATLAYER_OT_add_material_channel_image(Operator):
    bl_idname = "matlayer.add_material_channel_image"
    bl_label = "Add Material Channel Image"
    bl_description = "Creates a new image and assigns it to the specified material channel"


    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}

#----------------------------- HELPER FUNCTIONS -----------------------------#

def format_layer_group_node_name(active_material_name, layer_index):
    '''Properly formats the layer group node names for this add-on.'''
    return "{0}_{1}".format(active_material_name, layer_index)

def get_layer_node_tree(layer_index):
    '''Returns the node group for the specified layer (from Blender data) if it exists'''
    layer_group_name = format_layer_group_node_name(bpy.context.active_object.active_material.name, layer_index)
    return bpy.data.node_groups.get(layer_group_name)

def get_material_layer_node(layer_node_name, layer_index, material_channel_name='COLOR'):
    '''Returns the desired material node if it exists. Supply the material channel name to get nodes specific to material channels.'''
    active_material = bpy.context.active_object.active_material
    if active_material:
        layer_group_node_name = format_layer_group_node_name(active_material.name, layer_index)

        match layer_node_name:
            case 'LAYER':
                return active_material.node_tree.nodes.get(str(layer_index))
            case 'PROJECTION':
                return bpy.data.node_groups.get(layer_group_node_name).nodes.get("PROJECTION")
            case 'MIX':
                mix_node_name = "{0}_MIX".format(material_channel_name)
                return bpy.data.node_groups.get(layer_group_node_name).nodes.get(mix_node_name)
            case 'OPACITY':
                opacity_node_name = "{0}_OPACITY".format(material_channel_name)
                return bpy.data.node_groups.get(layer_group_node_name).nodes.get(opacity_node_name)
            case 'VALUE':
                value_node_name = "{0}_VALUE".format(material_channel_name)
                return bpy.data.node_groups.get(layer_group_node_name).nodes.get(value_node_name)
            case 'OUTPUT':
                return bpy.data.node_groups.get(layer_group_node_name).nodes.get('Group Output')
            case 'INPUT':
                return bpy.data.node_groups.get(layer_group_node_name).nodes.get('Group Input')

def add_material_layer_slot():
    '''Adds a new slot to the material layer stack, and returns the index of the new layer slot.'''
    layers = bpy.context.scene.matlayer_layers
    layer_stack = bpy.context.scene.matlayer_layer_stack
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index

    layer_slot = layers.add()

    # Assign a random, unique number to the layer slot. This allows the layer slot array index to be found using the name of the layer slot as a key.
    unique_random_slot_id = str(random.randrange(0, 999999))
    while layers.find(unique_random_slot_id) != -1:
        unique_random_slot_id = str(random.randrange(0, 999999))
    layer_slot.name = unique_random_slot_id

    # If there is no layer selected, move the layer to the top of the stack.
    if selected_layer_index < 0:
        move_index = len(layers) - 1
        move_to_index = 0
        layers.move(move_index, move_to_index)
        layer_stack.layer_index = move_to_index
        selected_layer_index = len(layers) - 1

    # Moves the new layer above the currently selected layer and selects it.
    else: 
        move_index = len(layers) - 1
        move_to_index = max(0, min(selected_layer_index + 1, len(layers) - 1))
        layers.move(move_index, move_to_index)
        layer_stack.layer_index = move_to_index
        selected_layer_index = max(0, min(selected_layer_index + 1, len(layers) - 1))

    return bpy.context.scene.matlayer_layer_stack.selected_layer_index

def read_total_layers():
    '''Counts the total layers in the active material by reading the active material's node tree.'''
    active_material = bpy.context.active_object.active_material
    layer_count = 1
    while active_material.node_tree.nodes.get(str(layer_count)):
        layer_count += 1
    return layer_count

def organize_layer_group_nodes():
    '''Organizes all layer group nodes in the active material to ensure the node tree is easy to read.'''
    active_material = bpy.context.active_object.active_material
    layer_count = read_total_layers()

    position_x = -500
    for i in range(0, layer_count):
        layer_group_node = active_material.node_tree.nodes.get(str(i))
        if layer_group_node:
            layer_group_node.width = 300
            layer_group_node.location = (position_x, 0)
            position_x -= 500

def connect_layer_group_nodes():
    '''Connects all layer group nodes to other existing group nodes, and the principled BSDF shader.'''

    # Note: This may be able to be optimized by only diconnecting nodes that must be disconnected.
    # TODO: Disconnect all layer group nodes.

    # TODO: Re-connect all layer group nodes.

    layer_count = read_total_layers()

    active_material = bpy.context.active_object.active_material
    
    principled_bsdf = active_material.node_tree.nodes.get('MATLAYER_BSDF')
    normal_and_height_mix = active_material.node_tree.nodes.get('NORMAL_HEIGHT_MIX')
    layer_node = get_material_layer_node('LAYER', 0)

    '''
    active_material.node_tree.links.new(layer_node.outputs.get('Color'), principled_bsdf.inputs.get('Base Color'))
    active_material.node_tree.links.new(layer_node.outputs.get('Subsurface'), principled_bsdf.inputs.get('Subsurface'))
    active_material.node_tree.links.new(layer_node.outputs.get('Metallic'), principled_bsdf.inputs.get('Metallic'))
    active_material.node_tree.links.new(layer_node.outputs.get('Specular'), principled_bsdf.inputs.get('Specular'))
    active_material.node_tree.links.new(layer_node.outputs.get('Roughness'), principled_bsdf.inputs.get('Roughness'))
    active_material.node_tree.links.new(layer_node.outputs.get('Emission'), principled_bsdf.inputs.get('Emission'))
    active_material.node_tree.links.new(layer_node.outputs.get('Alpha'), principled_bsdf.inputs.get('Alpha'))
    active_material.node_tree.links.new(layer_node.outputs.get('Normal'), normal_and_height_mix.inputs.get('Normal'))
    active_material.node_tree.links.new(layer_node.outputs.get('Height'), normal_and_height_mix.inputs.get('Height'))
    '''
