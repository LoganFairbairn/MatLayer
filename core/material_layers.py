# This file contains layer properties and functions for updating layer properties.

import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import BoolProperty, IntProperty, EnumProperty, StringProperty, PointerProperty
from ..core import layer_masks
from ..core import baking
from ..core import blender_addon_utils
from ..core import debug_logging
import random

# List of node types that can be used in the texture slot.

PROJECTION_MODES = [
    ("UV", "UV / Flat", "Projects the texture using the model's UV map."),
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

#----------------------------- UPDATING NODE TYPES -----------------------------#

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

#----------------------------- HELPER FUNCTIONS -----------------------------#

def update_layer_projection_mode(self, context):
    '''Updates the projection mode for the selected layer'''
    print("Placeholder...")

def update_sync_layer_projection_scale(self, context):
    print("Placeholder...")

#----------------------------- HELPER FUNCTIONS -----------------------------#

def format_layer_group_node_name(active_material_name, layer_index):
    '''Properly formats the layer group node names for this add-on.'''
    return "{0}_{1}".format(active_material_name, layer_index)

def get_layer_node_tree(layer_index):
    '''Returns the node group for the specified layer (from Blender data) if it exists'''
    
    if not bpy.context.active_object:
        return None
    
    if not bpy.context.active_object.active_material:
        return None
    
    layer_group_name = format_layer_group_node_name(bpy.context.active_object.active_material.name, layer_index)

    return bpy.data.node_groups.get(layer_group_name)

def get_material_layer_node(layer_node_name, layer_index=0, material_channel_name='COLOR', get_changed=False):
    '''Returns the desired material node if it exists. Supply the material channel name to get nodes specific to material channels.'''
    if bpy.context.active_object == None:
        return
    
    active_material = bpy.context.active_object.active_material
    if active_material == None:
        return
    
    layer_group_node_name = format_layer_group_node_name(active_material.name, layer_index)

    match layer_node_name:
        case 'LAYER':
            if get_changed:
                return active_material.node_tree.nodes.get(str(layer_index) + "~")
            else:
                return active_material.node_tree.nodes.get(str(layer_index))
            
        case 'GLOBAL':
            global_channel_toggle_node_name = "GLOBAL_{0}_TOGGLE".format(material_channel_name)
            return active_material.node_tree.nodes.get(global_channel_toggle_node_name)
        
        case 'PROJECTION':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get("PROJECTION")
            return None
        
        case 'MIX':
            mix_node_name = "{0}_MIX".format(material_channel_name)
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get(mix_node_name)
            return None
        
        case 'OPACITY':
            opacity_node_name = "{0}_OPACITY".format(material_channel_name)
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get(opacity_node_name)
            return None
        
        case 'VALUE':
            value_node_name = "{0}_VALUE".format(material_channel_name)
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                return node_tree.nodes.get(value_node_name)
            return None
        
        case 'OUTPUT':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                node_tree.nodes.get('Group Output')
            return None
        
        case 'INPUT':
            node_tree = bpy.data.node_groups.get(layer_group_node_name)
            if node_tree:
                node_tree.nodes.get('Group Input')
            return None

def add_material_layer_slot():
    '''Adds a new slot to the material layer stack, and returns the index of the new layer slot.'''
    layers = bpy.context.scene.matlayer_layers
    layer_stack = bpy.context.scene.matlayer_layer_stack

    layer_slot = layers.add()

    # Assign a random, unique number to the layer slot. This allows the layer slot array index to be found using the name of the layer slot as a key.
    unique_random_slot_id = str(random.randrange(0, 999999))
    while layers.find(unique_random_slot_id) != -1:
        unique_random_slot_id = str(random.randrange(0, 999999))
    layer_slot.name = unique_random_slot_id

    # If there is no layer selected, move the layer to the top of the stack.
    if bpy.context.scene.matlayer_layer_stack.selected_layer_index < 0:
        move_index = len(layers) - 1
        move_to_index = 0
        layers.move(move_index, move_to_index)
        layer_stack.layer_index = move_to_index
        bpy.context.scene.matlayer_layer_stack.selected_layer_index = len(layers) - 1

    # Moves the new layer above the currently selected layer and selects it.
    else: 
        move_index = len(layers) - 1
        move_to_index = max(0, min(bpy.context.scene.matlayer_layer_stack.selected_layer_index + 1, len(layers) - 1))
        layers.move(move_index, move_to_index)
        layer_stack.layer_index = move_to_index
        bpy.context.scene.matlayer_layer_stack.selected_layer_index = max(0, min(bpy.context.scene.matlayer_layer_stack.selected_layer_index + 1, len(layers) - 1))

    return bpy.context.scene.matlayer_layer_stack.selected_layer_index

def read_total_layers():
    '''Counts the total layers in the active material by reading the active material's node tree.'''
    if not bpy.context.active_object:
        return 0
    if not bpy.context.active_object.active_material:
        return 0
    
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
    for i in range(layer_count, 0, -1):
        layer_group_node = active_material.node_tree.nodes.get(str(i - 1))
        if layer_group_node:
            layer_group_node.width = 300
            layer_group_node.location = (position_x, 0)
            position_x -= 500

def link_layer_group_nodes():
    '''Connects all layer group nodes to other existing group nodes, and the principled BSDF shader.'''
    # Note: This function may be able to be optimized by only diconnecting nodes that must be disconnected, potentially reducing re-compile time for shaders.

    if not bpy.context.active_object:
        return

    if not bpy.context.active_object.active_material:
        return

    active_material = bpy.context.active_object.active_material
    node_tree = active_material.node_tree
    layer_count = read_total_layers()

    # Disconnect all layer group nodes.
    for i in range(0, layer_count):
        layer_node = get_material_layer_node('LAYER', i)
        if layer_node:
            for input in layer_node.inputs:
                for link in input.links:
                    node_tree.links.remove(link)

    # Re-connect all layer group nodes.
    for i in range(0, layer_count):
        layer_node = get_material_layer_node('LAYER', i)
        next_layer_node = get_material_layer_node('LAYER', i + 1)
        if next_layer_node:
            for material_channel_name in MATERIAL_CHANNEL_LIST:
                output_socket_name = material_channel_name.capitalize()
                input_socket_name = "{0}Mix".format(material_channel_name.capitalize())
                node_tree.links.new(layer_node.outputs.get(output_socket_name), next_layer_node.inputs.get(input_socket_name))

    # TODO: Only connect active material channels.
    # Connect the last layer node to the principled BSDF.
    normal_and_height_mix = active_material.node_tree.nodes.get('NORMAL_HEIGHT_MIX')
    principled_bsdf = active_material.node_tree.nodes.get('MATLAYER_BSDF')
    last_layer_node = get_material_layer_node('LAYER', layer_count - 1)
    for material_channel_name in MATERIAL_CHANNEL_LIST:
        match material_channel_name:
            case 'COLOR':
                node_tree.links.new(last_layer_node.outputs.get(material_channel_name.capitalize()), principled_bsdf.inputs.get('Base Color'))

            case 'NORMAL':
                node_tree.links.new(last_layer_node.outputs.get(material_channel_name.capitalize()), normal_and_height_mix.inputs.get(material_channel_name.capitalize()))
        
            case 'HEIGHT':
                node_tree.links.new(last_layer_node.outputs.get(material_channel_name.capitalize()), normal_and_height_mix.inputs.get(material_channel_name.capitalize()))

            case _:
                node_tree.links.new(last_layer_node.outputs.get(material_channel_name.capitalize()), principled_bsdf.inputs.get(material_channel_name.capitalize()))

def reindex_layer_nodes(change_made, affected_layer_index):
    '''Reindexes layer group nodes to keep them properly indexed. This should be called after a change is made that effects the layer stack order such as adding, duplicating, deleting, or moving a material layer on the layer stack.'''
    match change_made:
        case 'ADDED_LAYER':
            # Increase the layer index for all layer group nodes and their node trees that exist above the affected layer.
            total_layers = read_total_layers()
            for i in range(total_layers, affected_layer_index, -1):
                layer_node = get_material_layer_node('LAYER', i - 1)
                if layer_node:
                    layer_node.name = str(int(layer_node.name) + 1)
                    split_node_tree_name = layer_node.node_tree.name.split('_')
                    layer_node.node_tree.name = "{0}_{1}".format(split_node_tree_name[0], str(int(split_node_tree_name[1]) + 1))

            new_layer_node = get_material_layer_node('LAYER', affected_layer_index, get_changed=True)
            if new_layer_node:
                new_layer_node.name = str(affected_layer_index)
                split_node_tree_name = new_layer_node.node_tree.name.split('_')
                new_layer_node.node_tree.name = "{0}_{1}".format(split_node_tree_name[0], str(affected_layer_index))

        case 'DELETED_LAYER':
            # Reduce the layer index for all layer group nodes and their nodes trees that exist above the affected layer.
            layer_count = len(bpy.context.scene.matlayer_layers)
            for i in range(layer_count, affected_layer_index + 1, -1):
                layer_node = get_material_layer_node('LAYER', i - 1)
                layer_node.name = str(int(layer_node.name) - 1)
                split_node_tree_name = layer_node.node_tree.name.split('_')
                layer_node.node_tree.name = "{0}_{1}".format(split_node_tree_name[0], str(int(split_node_tree_name[1]) - 1))

def apply_mesh_maps():
    '''Searches for all mesh map texture nodes in the node tree and applies mesh maps if they exist.'''
    # Apply baked mesh maps to all group nodes used as masks for all material layers.
    layers = bpy.context.scene.matlayer_layers
    for layer_index in range(0, len(layers)):
        mask_count = layer_masks.count_masks(layer_index)
        for mask_index in range(0, mask_count):
            for mesh_map_type in baking.MESH_MAP_TYPES:
                mask_node = layer_masks.get_mask_node('MASK', layer_index, mask_index)
                mesh_map_node = mask_node.node_tree.get(mesh_map_type)
                if mesh_map_node:
                    if mesh_map_node.bl_static_type == 'TEX_IMAGE':
                        mesh_map_node.image = baking.get_meshmap_image(bpy.context.active_object.name, mesh_map_type)
    debug_logging.log("Applied baked mesh maps.")

#----------------------------- OPERATORS -----------------------------#

class MATLAYER_layer_stack(PropertyGroup):
    '''Properties for the layer stack.'''
    selected_layer_index: IntProperty(default=-1, description="Selected material layer")
    material_channel_preview: BoolProperty(name="Material Channel Preview", description="If true, only the rgb output values for the selected material channel will be used on the object.", default=False)
    selected_material_channel: EnumProperty(items=MATERIAL_CHANNEL, name="Material Channel", description="The currently selected material channel", default='COLOR')

class ProjectionSettings(PropertyGroup):
    '''Projection settings for this add-on.'''
    mode: EnumProperty(items=PROJECTION_MODES, name="Projection", description="Projection type of the image attached to the selected layer", default='UV', update=update_layer_projection_mode)
    sync_projection_scale: BoolProperty(name="Sync Projection Scale", description="When enabled Y and Z projection (if the projection mode has a z projection) will be synced with the X projection", default=True,update=update_sync_layer_projection_scale)

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
    projection: PointerProperty(type=ProjectionSettings)

class MATLAYER_OT_add_material_layer(Operator):
    bl_idname = "matlayer.add_material_layer"
    bl_label = "Add Material Layer"
    bl_description = "Adds a material layer to the active material (if the material is created with this add-on)"
    bl_options = {'REGISTER', 'UNDO'}

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
        new_layer_group_node.name = str(new_layer_slot_index) + "~"
        new_layer_group_node.label = "Layer " + str(new_layer_slot_index + 1)
        
        reindex_layer_nodes(change_made='ADDED_LAYER', affected_layer_index=new_layer_slot_index)
        organize_layer_group_nodes()
        link_layer_group_nodes()

        return {'FINISHED'}

class MATLAYER_OT_add_paint_material_layer(Operator):
    bl_idname = "matlayer.add_paint_material_layer"
    bl_label = "Add Paint Material Layer"
    bl_description = "Creates a material layer and an image texture that's placed in the materials color channel"
    bl_options = {'REGISTER', 'UNDO'}

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
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}

class MATLAYER_OT_delete_layer(Operator):
    bl_idname = "matlayer.delete_layer"
    bl_label = "Delete Layer"
    bl_description = "Deletes the selected material layer from the active material"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        layers = context.scene.matlayer_layers
        selected_layer_index = context.scene.matlayer_layer_stack.selected_layer_index

        # Remove the layer group node (node tree) from Blender's data.
        layer_node_tree = get_layer_node_tree(selected_layer_index)
        if layer_node_tree:
            bpy.data.node_groups.remove(layer_node_tree)

        # Remove the layer node from the active materials node tree.
        layer_group_node = get_material_layer_node('LAYER', selected_layer_index)
        if layer_group_node:
            active_material = bpy.context.active_object.active_material
            active_material.node_tree.nodes.remove(layer_group_node)

        reindex_layer_nodes(change_made='DELETED_LAYER', affected_layer_index=selected_layer_index)
        organize_layer_group_nodes()
        link_layer_group_nodes()

        # Remove the layer slot.
        layers.remove(selected_layer_index)
        context.scene.matlayer_layer_stack.selected_layer_index = max(min(selected_layer_index - 1, len(layers) - 1), 0)

        return {'FINISHED'}
    
class MATLAYER_OT_duplicate_layer(Operator):
    bl_idname = "matlayer.duplicate_layer"
    bl_label = "Duplicate Layer"
    bl_description = "Duplicates the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):

        return {'FINISHED'}
    
class MATLAYER_OT_move_material_layer_up(Operator):
    bl_idname = "matlayer.move_material_layer_up"
    bl_label = "Move Layer Up"
    bl_description = "Moves the material layer up on the layer stack"
    bl_options = {'REGISTER', 'UNDO'}

    direction: StringProperty(default='UP')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):

        return {'FINISHED'}

class MATLAYER_OT_move_material_layer_down(Operator):
    bl_idname = "matlayer.move_material_layer_down"
    bl_label = "Move Layer Down"
    bl_description = "Moves the material layer down on the layer stack"
    bl_options = {'REGISTER', 'UNDO'}

    direction: StringProperty(default='UP')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):

        return {'FINISHED'}

class MATLAYER_OT_toggle_material_channel_preview(Operator):
    bl_idname = "matlayer.toggle_material_channel_preview"
    bl_label = "Toggle Material Channel Preview"
    bl_description = "Toggle on / off a preview for the selected material channel"
    bl_options = {'REGISTER', 'UNDO'}

    direction: StringProperty(default='UP')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}
