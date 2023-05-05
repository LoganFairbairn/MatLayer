import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty
from . import material_channels
from . import matlay_materials
from ..core import material_layers
from ..core import layer_nodes
from ..core import material_filters
from ..core import layer_masks
from ..core import texture_set_settings
from ..utilities import logging
from ..utilities import matlay_utils
import random
import os

def add_layer_slot(layer_type):
    '''Creates a layer slot.'''
    context = bpy.context
    layers = context.scene.matlay_layers
    layer_stack = context.scene.matlay_layer_stack
    selected_layer_index = context.scene.matlay_layer_stack.layer_index

    # Add a new layer slot.
    layers.add()

    # Set a new layer name.
    if layer_type == 'DECAL':
        number_of_decal_layers = 0
        for layer in layers:
            if layer.type == 'DECAL':
                number_of_decal_layers += 1
        layers[len(layers) - 1].name = "{0} {1}".format("Decal", str(number_of_decal_layers))
    else:
        number_of_material_layers = 0
        for layer in layers:
            if layer.type != 'DECAL':
                number_of_material_layers += 1
        layers[len(layers) - 1].name = "{0} {1}".format("Layer", str(number_of_material_layers))

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

    # Assign the layer a unique random ID number.
    number_of_layers = len(layers)
    new_id = random.randint(100000, 999999)
    id_exists = True

    while (id_exists):
        for i in range(number_of_layers):
            if layers[i].id == new_id:
                new_id += 1
                break

            if i == len(layers) - 1:
                id_exists = False
                layers[selected_layer_index].id = new_id

def add_default_layer_nodes(layer_type, decal_object):
    '''Adds default nodes based on the provided layer type.'''
    context = bpy.context
    new_layer_index = bpy.context.scene.matlay_layer_stack.layer_index

    material_channel_list = material_channels.get_material_channel_list()
    for i in range(0, len(material_channel_list)):
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_list[i])
        if not material_channels.verify_material_channel(material_channel_node):
            return
        
        new_nodes = []

        opacity_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeMath')
        opacity_node.name = layer_nodes.format_material_node_name("OPACITY", new_layer_index, True)
        opacity_node.label = opacity_node.name
        opacity_node.inputs[0].default_value = 1.0
        opacity_node.inputs[1].default_value = 1.0
        opacity_node.use_clamp = True
        opacity_node.operation = 'MULTIPLY'
        new_nodes.append(opacity_node)

        mix_layer_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeMixRGB')
        mix_layer_node.name = layer_nodes.format_material_node_name("MIXLAYER", new_layer_index, True)
        mix_layer_node.label = mix_layer_node.name
        mix_layer_node.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0)
        mix_layer_node.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
        mix_layer_node.use_clamp = True
        new_nodes.append(mix_layer_node)

        coord_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeTexCoord')
        coord_node.name = layer_nodes.format_material_node_name("COORD", new_layer_index, True)
        coord_node.label = coord_node.name
        if layer_type == 'DECAL':
            coord_node.object = decal_object
        new_nodes.append(coord_node)

        mapping_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeMapping')
        mapping_node.name = layer_nodes.format_material_node_name("MAPPING", new_layer_index, True)
        mapping_node.label = mapping_node.name
        if layer_type == 'DECAL':
            mapping_node.inputs[1].default_value = (0.5, 0.5, 0.0)
        new_nodes.append(mapping_node)

        texture_node = None
        if material_channel_list[i] == "COLOR":
            if layer_type == 'PAINT' or layer_type == 'DECAL':
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeTexImage')
                texture_node.extension = 'CLIP'
            else:
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')
                texture_node.outputs[0].default_value = (0.25, 0.25, 0.25, 1.0)

        if material_channel_list[i] == "SUBSURFACE":
            texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeValue')
            texture_node.outputs[0].default_value = 0.0

        if material_channel_list[i] == "SUBSURFACE_COLOR":
            texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')
            texture_node.outputs[0].default_value = (0.0, 0.0, 0.0, 1.0)

        if material_channel_list[i] == "METALLIC":
            texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeValue')
            texture_node.outputs[0].default_value = 0.0

        if material_channel_list[i] == "SPECULAR":
            texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeValue')
            texture_node.outputs[0].default_value = 0.5

        if material_channel_list[i] == "ROUGHNESS":
            texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeValue')
            texture_node.outputs[0].default_value = 0.5

        if material_channel_list[i] == "NORMAL":
            texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')
            texture_node.outputs[0].default_value = (0.5, 0.5, 1.0, 1.0)
            mix_layer_node.inputs[1].default_value = (0.5, 0.5, 1.0, 1.0)
            
        if material_channel_list[i] == "HEIGHT":
            texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeValue')
            texture_node.outputs[0].default_value = 0.0

        if material_channel_list[i] == "EMISSION":
            texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')
            texture_node.outputs[0].default_value = (0.0, 0.0, 0.0, 1.0)

        texture_node.name = layer_nodes.format_material_node_name("TEXTURE", new_layer_index, True)
        texture_node.label = texture_node.name
        new_nodes.append(texture_node)

        # Frame nodes.
        frame = material_channel_node.node_tree.nodes.new(type='NodeFrame')
        frame.name = layer_nodes.get_layer_frame_name(new_layer_index, True)
        frame.label = frame.name
        for n in new_nodes:
            n.parent = frame

def set_default_layer_properties(layer_type):
    '''Sets default layer properties based on the provided layer type.'''
    context = bpy.context
    new_layer = context.scene.matlay_layers[context.scene.matlay_layer_stack.layer_index]

    match layer_type:
        case 'FILL':
            new_layer.type = layer_type

        case 'PAINT':
            new_layer.type = 'FILL'

            context.scene.matlay_layer_stack.auto_update_layer_properties = False
            layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "SUBSURFACE", context)
            layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "SUBSURFACE_COLOR", context)
            layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "METALLIC", context)
            layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "SPECULAR", context)
            layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "ROUGHNESS", context)
            layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "EMISSION", context)
            layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "NORMAL", context)
            layer_nodes.mute_layer_material_channel(True, context.scene.matlay_layer_stack.layer_index, "HEIGHT", context)

            new_layer.material_channel_toggles.subsurface_channel_toggle = False
            new_layer.material_channel_toggles.subsurface_color_channel_toggle = False
            new_layer.material_channel_toggles.metallic_channel_toggle = False
            new_layer.material_channel_toggles.specular_channel_toggle = False
            new_layer.material_channel_toggles.roughness_channel_toggle = False
            new_layer.material_channel_toggles.emission_channel_toggle = False
            new_layer.material_channel_toggles.normal_channel_toggle = False
            new_layer.material_channel_toggles.height_channel_toggle = False

            new_layer.channel_node_types.color_node_type = 'TEXTURE'

            context.scene.matlay_layer_stack.auto_update_layer_properties = True

            # Add a new layer image for the paint layer.
            bpy.ops.matlay.add_layer_image(material_channel_name='COLOR')

        case 'DECAL':
            new_layer.type = layer_type

            context.scene.matlay_layer_stack.auto_update_layer_properties = False

            new_layer.channel_node_types.color_node_type = 'TEXTURE'

            context.scene.matlay_layer_stack.auto_update_layer_properties = True

def add_layer(layer_type, decal_object=None):
    '''Adds a material layer setup based on the provided layer type.'''
    context = bpy.context

    # Validate and prepare the material for the selected object.
    matlay_utils.set_valid_mode()
    if not matlay_materials.prepare_material(context):
        return
    material_channels.create_channel_group_nodes(context)
    material_channels.create_empty_group_node(context)

    # Add a new layer slot and default nodes.
    add_layer_slot(layer_type)
    add_default_layer_nodes(layer_type, decal_object)
    
    # Re-index, organize and relink nodes.
    layer_nodes.reindex_material_layer_nodes()
    layer_nodes.organize_all_layer_nodes()
    layer_nodes.relink_material_nodes(context.scene.matlay_layer_stack.layer_index)
    layer_nodes.relink_material_layers()

    # Set default layer properties.
    set_default_layer_properties(layer_type)    

    # Set a valid material shading mode and reset ui tabs.
    matlay_utils.set_valid_material_shading_mode(context)
    context.scene.matlay_layer_stack.layer_property_tab = 'MATERIAL'
    context.scene.matlay_layer_stack.material_property_tab = 'MATERIAL'

def duplicate_node(material_channel_node, original_node, new_material_layer_index):
    '''Duplicates the provided node.'''
    # Duplicate the node.
    duplicated_node = material_channel_node.node_tree.nodes.new(original_node.bl_idname)

    # Duplicate the node name and label, but add a tilda at the end of the name to signify the nodes are new and avoid naming conflicts.
    node_info = original_node.name.split('_')
    node_name = node_info[0]

    # Format node names based on their type.
    if node_name in layer_nodes.LAYER_NODE_NAMES:
        duplicated_node.name = layer_nodes.format_material_node_name(node_info[0], new_material_layer_index, True)

    elif node_name == material_filters.FILTER_NODE_NAME:
        duplicated_node.name = material_filters.format_filter_node_name(new_material_layer_index, node_info[2], True)

    elif node_name in layer_masks.MASK_NODE_NAMES:
        duplicated_node.name = layer_masks.format_mask_node_name(node_info[0], new_material_layer_index, node_info[2], True)

    elif node_name == layer_masks.MASK_FILTER_NAME:
        duplicated_node.name = layer_masks.format_mask_filter_node_name(new_material_layer_index, node_info[2], node_info[3], True)
    duplicated_node.label = duplicated_node.name

    # Copy muted values for nodes.
    if original_node.mute:
        duplicated_node.mute = True

    # Duplicate values specific to node types.
    match original_node.bl_static_type:
        case 'TEX_IMAGE':
            if original_node.image != None:
                duplicated_node.image = original_node.image
                duplicated_node.interpolation = original_node.interpolation
                duplicated_node.projection = original_node.projection
                duplicated_node.projection_blend = original_node.projection_blend
                duplicated_node.extension = original_node.extension
        
        case 'GROUP':
            if original_node.node_tree != None:
                duplicated_node.node_tree = original_node.node_tree

        case 'TEX_NOISE':
            duplicated_node.noise_dimensions = original_node.noise_dimensions

        case 'TEX_VORONOI':
            duplicated_node.voronoi_dimensions = original_node.voronoi_dimensions
            duplicated_node.feature = original_node.feature
            duplicated_node.distance = original_node.distance

        case 'TEX_MUSGRAVE':
            duplicated_node.musgrave_dimensions = original_node.musgrave_dimensions
            duplicated_node.musgrave_type = original_node.musgrave_type

        case 'MATH':
            duplicated_node.operation = original_node.operation
            duplicated_node.use_clamp = original_node.use_clamp

        case 'VALTORGB':
            for i in range(0, len(original_node.color_ramp.elements)):
                duplicated_node.color_ramp.elements[i].color = original_node.color_ramp.elements[i].color
                duplicated_node.color_ramp.elements[i].position = original_node.color_ramp.elements[i].position

        case 'MIXRGB':
            duplicated_node.use_clamp = original_node.use_clamp

    # Duplicate input values.
    for i in range(0, len(original_node.inputs)):
        duplicated_node.inputs[i].default_value = original_node.inputs[i].default_value

    # Duplicate output values.
    for i in range(0, len(original_node.outputs)):
        duplicated_node.outputs[i].default_value = original_node.outputs[i].default_value

    return duplicated_node

class MATLAY_OT_add_decal_layer(Operator):
    bl_idname = "matlay.add_decal_layer"
    bl_label = "Add Decal Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Opens a window from which you can choose an image to use as a decal (similar to a sticker) and adds it to the scene"

    def execute(self, context):
        # Add decal object (which allows the user to drag the decal around on the object).
        # Must be in object mode to add the decal object and select it after the decal layer is created.
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        previously_selected_object = bpy.context.active_object
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        bpy.ops.object.empty_add(type='CUBE', align='WORLD', location=(0, 0, 0), scale=(1, 1, 0.2))
        decal_object = bpy.context.active_object
        decal_object.scale = (1.0, 1.0, 0.2)
        bpy.context.active_object.select_set(False)
        previously_selected_object.select_set(True)
        bpy.context.view_layer.objects.active = previously_selected_object
        
        # Add a new decal layer.
        add_layer('DECAL', decal_object)

        # The layer stacks must be updated before adding a mask.
        read_layer_nodes(context)

        # Automatically add a mask for the decal set to use alpha.
        layer_masks.add_mask('DECAL', use_alpha=True)

        # Re-select the decal object so users can adjust it.
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        decal_object.select_set(True)
        bpy.context.view_layer.objects.active = decal_object

        return {'FINISHED'}

class MATLAY_OT_add_material_layer(Operator):
    bl_idname = "matlay.add_material_layer"
    bl_label = "Add Material Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds a layer with a full material"

    def execute(self, context):
        add_layer('MATERIAL')
        return {'FINISHED'}

class MATLAY_OT_add_paint_layer(Operator):
    bl_idname = "matlay.add_paint_layer"
    bl_label = "Add Paint Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Add a material layer with all material channels turned off, excluding color, and creates a new image texture for the color material channel. Use this operator to add layers you intend to manually paint onto"

    def execute(self, context):
        add_layer('PAINT')
        return {'FINISHED'}

class MATLAY_OT_add_layer_menu(Operator):
    bl_label = ""
    bl_idname = "matlay.add_layer_menu"
    bl_description = "Opens a menu of options to add a layer in different methods"

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
        col.operator("matlay.add_material_layer", text="Add Fill", icon='MATERIAL_DATA')
        col.operator("matlay.add_paint_layer", text="Add Paint", icon='BRUSHES_ALL')
        col.operator("matlay.add_decal_layer", text="Add Decal", icon='OUTLINER_OB_FONT')

class MATLAY_OT_move_material_layer(Operator):
    bl_idname = "matlay.move_material_layer"
    bl_label = "Move Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the currently selected layer"

    direction: StringProperty(default="", description="Direction to move the layer on the layer stack, either 'UP' or 'DOWN'.")
    _ValidDirections = ['UP', 'DOWN']

    # Poll tests if the operator can be called or not.
    @ classmethod
    def poll(cls, context):
        return context.scene.matlay_layers

    def execute(self, context):
        material_layers.validate_selected_material_layer_index()

        # If the direction given to move the layer on the layer stack is invalid, throw an error.
        if self.direction not in self._ValidDirections:
            print("Error: Direction given to move material layer is invalid.")
            return{'FINISHED'}

        matlay_utils.set_valid_mode()

        layers = context.scene.matlay_layers
        selected_material_layer_index = context.scene.matlay_layer_stack.layer_index
        material_channel_list = material_channels.get_material_channel_list()

        # Don't move the layer if the user is trying to move the layer out of range.
        if self.direction == 'UP' and selected_material_layer_index + 1 > len(layers) - 1:
            return{'FINISHED'}
        if self.direction == 'DOWN' and selected_material_layer_index - 1 < 0:
            return{'FINISHED'}
        
        # Get the layer index under or over the selected layer, depending on the direction the layer is being moved on the layer stack.
        if self.direction == 'UP':
            moving_to_layer_index = max(min(selected_material_layer_index + 1, len(layers) - 1), 0)
        else:
            moving_to_layer_index = max(min(selected_material_layer_index - 1, len(layers) - 1), 0)

        # Add a tilda to the end of the all layer nodes in the selected layer (including the frame). Adding a tilda to the end of the node name is the method used to signify which nodes are being actively changed, and is used for avoid naming conflicts with other nodes.
        for material_channel_name in material_channel_list:
            frame = layer_nodes.get_layer_frame(material_channel_name, selected_material_layer_index, context)
            frame.name = frame.name + "~"
            frame.label = frame.name

            material_nodes = layer_nodes.get_all_material_layer_nodes(material_channel_name, selected_material_layer_index, context)
            for material_node in material_nodes:
                material_node.name += '~'
                material_node.label = material_node.name

            filter_nodes = material_filters.get_all_material_filter_nodes(material_channel_name, selected_material_layer_index)
            for filter_node in filter_nodes:
                filter_node.name += '~'
                filter_node.label = filter_node.name

            mask_nodes = layer_masks.get_mask_nodes_in_material_layer(selected_material_layer_index, material_channel_name)
            for mask_node in mask_nodes:
                mask_node.name += '~'
                mask_node.label = mask_node.name

            mask_filter_nodes = layer_masks.get_all_mask_filter_nodes_in_layer(material_channel_name, selected_material_layer_index)
            for mask_filter_node in mask_filter_nodes:
                old_name = mask_filter_node.name
                new_name = mask_filter_node.name + '~'
                layer_masks.rename_mask_filter_node(material_channel_name, old_name, new_name)

        # Update the layer node names for the layer below or above with the selected layer (depending on the direction the layer is being moved in).
        for material_channel_name in material_channel_list:
            frame = layer_nodes.get_layer_frame(material_channel_name, moving_to_layer_index, context)
            frame.name = layers[moving_to_layer_index].name + "_" + str(layers[moving_to_layer_index].id) + "_" + str(selected_material_layer_index)
            frame.label = frame.name

            # Rename / re-index material nodes.
            material_nodes = layer_nodes.get_all_material_layer_nodes(material_channel_name, moving_to_layer_index, context, False)
            for material_node in material_nodes:
                node_info = material_node.name.split('_')
                material_node.name = node_info[0] + "_" + str(selected_material_layer_index)
                material_node.label = material_node.name

            # Rename / re-index filter nodes.
            filter_nodes = material_filters.get_all_material_filter_nodes(material_channel_name, moving_to_layer_index, False)
            for filter_node in filter_nodes:
                node_info = filter_nodes.name.split('_')
                filter_node.name = node_info[0] + "_" + str(selected_material_layer_index) + "_" + node_info[2]
                filter_node.label = filter_node.name

            # Rename / re-index mask nodes.
            mask_nodes = layer_masks.get_mask_nodes_in_material_layer(moving_to_layer_index, material_channel_name)
            for mask_node in mask_nodes:
                node_info = mask_node.name.split('_')
                mask_node.name = node_info[0] + "_" + str(selected_material_layer_index) + "_" + node_info[2]
                mask_node.label = mask_node.name

            # Rename / re-index mask filter nodes.
            mask_filter_nodes = layer_masks.get_all_mask_filter_nodes_in_layer(material_channel_name, moving_to_layer_index)
            for mask_filter_node in mask_filter_nodes:
                node_info = mask_filter_node.name.split('_')
                old_name = layer_masks.format_mask_filter_node_name(moving_to_layer_index, node_info[3], node_info[4])
                new_name = layer_masks.format_mask_filter_node_name(selected_material_layer_index, node_info[3], node_info[4])
                layer_masks.rename_mask_filter_node(material_channel_name, old_name, new_name)
        layers[moving_to_layer_index].cached_frame_name = frame.name

        # Remove the tilda from the end of the layer nodes names that belong to the moved layer and correct the index stored there.
        for material_channel_name in material_channel_list:
            frame = layer_nodes.get_layer_frame(material_channel_name, selected_material_layer_index, context, get_edited=True)
            frame.name = layers[selected_material_layer_index].name + "_" + str(layers[selected_material_layer_index].id) + "_" + str(moving_to_layer_index)
            frame.label = frame.name

            material_nodes = layer_nodes.get_all_material_layer_nodes(material_channel_name, selected_material_layer_index, context, True)
            for material_node in material_nodes:
                node_info = material_node.name.split('_')
                material_node.name = node_info[0] + "_" + str(moving_to_layer_index)
                material_node.label = material_node.name

            filter_nodes = material_filters.get_all_material_filter_nodes(material_channel_name, selected_material_layer_index, True)
            for filter_node in filter_nodes:
                node_info = filter_node.name.split('_')
                filter_node.name = material_filters.format_filter_node_name(moving_to_layer_index, node_info[2].replace('~', ''))
                filter_node.label = filter_node.name

            mask_nodes = layer_masks.get_mask_nodes_in_material_layer(selected_material_layer_index, material_channel_name, True)
            for mask_node in mask_nodes:
                node_info = mask_node.name.split('_')
                mask_node.name = node_info[0] + "_" + str(moving_to_layer_index) + "_" + node_info[2].replace('~', '')
                mask_node.label = mask_node.name

            mask_filter_nodes = layer_masks.get_all_mask_filter_nodes_in_layer(material_channel_name, selected_material_layer_index, True)
            for mask_filter_node in mask_filter_nodes:
                node_info = mask_filter_node.name.split('_')
                old_name = layer_masks.format_mask_filter_node_name(selected_material_layer_index, node_info[3], node_info[4])
                new_name = layer_masks.format_mask_filter_node_name(moving_to_layer_index, node_info[3], node_info[4]).replace('~', '')
                layer_masks.rename_mask_filter_node(material_channel_name, old_name, new_name)
                
        layers[selected_material_layer_index].cached_frame_name = frame.name

        # Move the selected layer on the ui layer stack.
        if self.direction == 'UP':
            index_to_move_to = max(min(selected_material_layer_index + 1, len(layers) - 1), 0)
        else:
            index_to_move_to = max(min(selected_material_layer_index - 1, len(layers) - 1), 0)
        layers.move(selected_material_layer_index, index_to_move_to)
        context.scene.matlay_layer_stack.layer_index = index_to_move_to

        # 6. Update the layer stack (organize, re-link).
        layer_nodes.reindex_material_layer_nodes()
        layer_nodes.organize_all_layer_nodes()
        layer_nodes.relink_material_layers()

        # Set a valid shading mode so users can see their change.
        matlay_utils.set_valid_material_shading_mode(context)

        return{'FINISHED'}

class MATLAY_OT_delete_layer(Operator):
    bl_idname = "matlay.delete_layer"
    bl_label = "Delete Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the currently selected layer"

    @ classmethod
    def poll(cls, context):
        return context.scene.matlay_layers

    def execute(self, context):
        material_layers.validate_selected_material_layer_index()

        layers = context.scene.matlay_layers
        selected_material_layer_index = context.scene.matlay_layer_stack.layer_index

        matlay_utils.set_valid_mode()

        # Remove the decal object if one exists.
        coord_node = layer_nodes.get_layer_node('COORD', 'COLOR', selected_material_layer_index, context)
        if coord_node:
            if coord_node.object != None:
                previously_selected_object = bpy.context.active_object
                bpy.ops.object.select_all(action='DESELECT')
                coord_node.object.select_set(True)
                bpy.context.view_layer.objects.active = coord_node.object
                bpy.ops.object.delete(use_global=False)
                if previously_selected_object:
                    previously_selected_object.select_set(True)
                    bpy.context.view_layer.objects.active = previously_selected_object

        # Remove all group nodes for all mask filters on all masks the layer being deleted.
        masks = bpy.context.scene.matlay_masks
        mask_filters = bpy.context.scene.matlay_mask_filters
        for i in range(0, len(masks)):
            for x in range(0, len(mask_filters)):
                mask_filter_name = layer_masks.format_mask_filter_node_name(selected_material_layer_index, i, x)
                mask_filter_node_tree = bpy.data.node_groups.get(mask_filter_name)
                if mask_filter_node_tree:
                    bpy.data.node_groups.remove(mask_filter_node_tree)
        
        # Remove all nodes for all material channels.
        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)

            # Remove layer frame and layer nodes.
            frame = layer_nodes.get_layer_frame(material_channel_name, selected_material_layer_index, context)
            if frame:
                material_channel_node.node_tree.nodes.remove(frame)

            node_list = layer_nodes.get_all_nodes_in_layer(material_channel_name, selected_material_layer_index, context)
            for node in node_list:
                material_channel_node.node_tree.nodes.remove(node)

        # Remove the layer slot from the layer stack.
        layers.remove(selected_material_layer_index)

        # Reset the layer stack index while keeping it within range of existing indicies in the layer stack.
        context.scene.matlay_layer_stack.layer_index = max(min(selected_material_layer_index - 1, len(layers) - 1), 0)

        # Update the layer nodes.
        layer_nodes.reindex_material_layer_nodes()
        layer_nodes.organize_all_layer_nodes()
        layer_nodes.relink_material_layers()

        # Set a valid material shading mode and reset ui tabs.
        matlay_utils.set_valid_material_shading_mode(context)
        context.scene.matlay_layer_stack.layer_property_tab = 'MATERIAL'
        context.scene.matlay_layer_stack.material_property_tab = 'MATERIAL'
        
        return {'FINISHED'}

class MATLAY_OT_duplicate_layer(Operator):
    bl_idname = "matlay.duplicate_layer"
    bl_label = "Duplicate Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Duplicates the selected layer"

    @ classmethod
    def poll(cls, context):
        return context.scene.matlay_layers

    def execute(self, context):
        material_layers.validate_selected_material_layer_index()
        layers = context.scene.matlay_layers
        original_material_layer_index = context.scene.matlay_layer_stack.layer_index

        # Must be in object mode to add the decal object and select it after the decal layer is created.
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        # Auto updating for layer properties should be off.
        context.scene.matlay_layer_stack.auto_update_layer_properties = False

        # If the original layer was a decal layer, create a new decal object (empty) and copy the transforms of the original.
        new_decal_object = None
        original_coord_node = layer_nodes.get_layer_node('COORD', 'COLOR', original_material_layer_index, context)
        if original_coord_node:
            if original_coord_node.object != None:
                previously_selected_object = bpy.context.active_object
                for obj in bpy.context.selected_objects:
                    obj.select_set(False)
                bpy.ops.object.empty_add(type='CUBE', align='WORLD', location=(0, 0, 0), scale=(1, 1, 0.2))
                new_decal_object = bpy.context.active_object
                new_decal_object.location = original_coord_node.object.location
                new_decal_object.rotation_euler = original_coord_node.object.rotation_euler
                new_decal_object.scale = original_coord_node.object.scale
                bpy.context.active_object.select_set(False)
                previously_selected_object.select_set(True)
                bpy.context.view_layer.objects.active = previously_selected_object

        # Count layer slot counts on the original layer.
        original_material_filter_count = len(bpy.context.scene.matlay_material_filters)
        original_mask_count = len(bpy.context.scene.matlay_masks)
        original_mask_filter_count = len(bpy.context.scene.matlay_mask_filters)

        # Store mask properties to transfer to new masks.
        mask_uses_alpha = []
        for i in range(0, original_mask_count):
            mask_uses_alpha.append(bpy.context.scene.matlay_masks[i].use_alpha)

        # Add a new layer slot and copy the name of the previous layer.
        original_layer_type = layers[original_material_layer_index].type
        add_layer_slot(original_layer_type)
        new_material_layer_index = context.scene.matlay_layer_stack.layer_index
        layers[new_material_layer_index].name = layers[original_material_layer_index].name
        layers[new_material_layer_index].type = layers[original_material_layer_index].type

        # Duplicate slots for material filters, masks and mask filters and their properties (this allow the newly duplicated nodes to reindex properly).
        for i in range(0, original_material_filter_count):
            material_filters.add_material_filter_slot()

        for i in range(0, original_mask_count):
            layer_masks.add_mask_slot(context)
            bpy.context.scene.matlay_masks[i].use_alpha = mask_uses_alpha[i]

        for i in range(0, original_mask_filter_count):
            layer_masks.add_mask_filter_slot()
        
        # Duplicate all layer nodes.
        for material_channel_name in material_channels.get_material_channel_list():
            material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
            original_nodes = layer_nodes.get_all_nodes_in_layer(material_channel_name, original_material_layer_index, context)
            new_nodes = []
            for node in original_nodes:
                duplicated_node = duplicate_node(material_channel_node, node, new_material_layer_index)
                new_nodes.append(duplicated_node)

            # Create a new layer frame for the new nodes.
            new_frame = material_channel_node.node_tree.nodes.new('NodeFrame')
            new_frame.name = layer_nodes.get_layer_frame_name(new_material_layer_index) + '~'
            new_frame.label = new_frame.name
            layers[new_material_layer_index].cached_frame_name = layers[new_material_layer_index].name
            for node in new_nodes:
                node.parent = new_frame

        # Reindex all nodes.
        layer_nodes.reindex_material_layer_nodes()
        material_filters.reindex_material_filter_nodes()
        layer_masks.reindex_mask_nodes(context)
        layer_masks.reindex_mask_filters_nodes()

        # For decal layers, assign the new decal object to all coord nodes.
        if layers[new_material_layer_index].type == 'DECAL':
            for material_channel_name in material_channels.get_material_channel_list():
                new_coord_node = layer_nodes.get_layer_node('COORD', material_channel_name, new_material_layer_index, context)
                if new_coord_node:
                    new_coord_node.object = new_decal_object
                
                for i in range(0, original_mask_count):
                    mask_coord_node = layer_masks.get_mask_node('MaskCoord', material_channel_name, new_material_layer_index, i)
                    if mask_coord_node:
                        mask_coord_node.object = new_decal_object

        # Duplicate properties of original layers and masks.
        if new_decal_object == None:
            layers[new_material_layer_index].projection.projection_mode = layers[original_material_layer_index].projection.projection_mode

        # Relink all nodes.
        layer_nodes.relink_material_nodes(new_material_layer_index)
        layer_nodes.relink_material_layers()
        material_filters.relink_material_filter_nodes(new_material_layer_index)
        layer_masks.relink_mask_nodes(new_material_layer_index)

        # Organize all nodes.
        layer_nodes.organize_all_layer_nodes()

        # Read the properties of the duplicated nodes by refreshing the layer nodes.
        read_layer_nodes(context)

        # For decal layers, select the decal object.
        if new_decal_object != None:
            for obj in bpy.context.selected_objects:
                obj.select_set(False)
            new_decal_object.select_set(True)
            bpy.context.view_layer.objects.active = new_decal_object

        context.scene.matlay_layer_stack.auto_update_layer_properties = True
        matlay_utils.set_valid_material_shading_mode(context)
        return{'FINISHED'}

class MATLAY_OT_edit_uvs_externally(Operator):
    bl_idname = "matlay.edit_uvs_externally"
    bl_label = "Edit UVs Externally"
    bl_description = "Exports the selected object's UV layout to the image editor defined in Blender's preferences (Edit -> Preferences -> File Paths -> Applications -> Image Editor)"

    def execute(self, context):
        material_layers.validate_selected_material_layer_index()
        matlay_utils.set_valid_mode()

        original_mode = bpy.context.object.mode
        active_object = bpy.context.active_object

        # Validate the selected object can export a uv layout.
        if active_object == None:
            self.report({'ERROR'}, "No active object is selected, please select an object to export the uv layout for.")
            return{'FINISHED'}
        
        if active_object.type != 'MESH':
            self.report({'ERROR'}, "The active object isn't a mesh, please select a mesh type object to export the uv layout for.")
            return{'FINISHED'}

        if active_object.data.uv_layers.active == None:
            self.report({'ERROR'}, "Active object has no active UV layout to export UVs for. Add one, or select a different object.")
            return{'FINISHED'}

        # Set edit mode and select all uvs.
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.uv.select_all(action='SELECT')

        # Save UV layout to folder.
        matlay_image_path = os.path.join(bpy.path.abspath("//"), "Matlay")
        if os.path.exists(matlay_image_path) == False:
            os.mkdir(matlay_image_path)

        uv_layout_path = os.path.join(matlay_image_path, "UVLayouts")
        if os.path.exists(uv_layout_path) == False:
            os.mkdir(uv_layout_path)
    
        uv_image_name = bpy.context.active_object.name + "_" + "UVLayout"
        uv_layout_path += "/" + uv_image_name + ".png"
        bpy.ops.uv.export_layout(filepath=uv_layout_path, size=(texture_set_settings.get_texture_width(), texture_set_settings.get_texture_height()))

        # Load the UV layout into Blender's data so it can be exported directly from Blender.
        uv_image = bpy.data.images.get(uv_image_name + ".png")
        if uv_image:
            bpy.data.images.remove(uv_image)
        uv_layout_image = bpy.data.images.load(uv_layout_path)

        # Select and export UV layout.
        context.scene.tool_settings.image_paint.canvas = uv_layout_image
        bpy.ops.image.external_edit(filepath=uv_layout_image.filepath)

        # Reset mode.
        bpy.ops.object.mode_set(mode = original_mode)
        
        return{'FINISHED'}

class MATLAY_OT_edit_image_externally(Operator):
    bl_idname = "matlay.edit_image_externally"
    bl_label = "Edit Image Externally"
    bl_description = "Exports the selected image to the image editor defined in Blender's preferences (Edit -> Preferences -> File Paths -> Applications -> Image Editor)"

    image_type: bpy.props.StringProperty()
    material_channel_name: bpy.props.StringProperty()

    @ classmethod
    def poll(cls, context):
        return context.scene.matlay_layers

    def execute(self, context):
        material_layers.validate_selected_material_layer_index()
        
        # Validate the provided image type & material channel name.
        if self.image_type != 'LAYER' and self.image_type != 'MASK':
            self.report({'ERROR'}, "Programming error, invalid type provided to edit image externally operator.")
            return {'FINISHED'}
    
        matlay_utils.set_valid_mode()

        # Get the texture node to export the image from based on the provided type.
        if self.image_type == 'LAYER':
            selected_layer_index = context.scene.matlay_layer_stack.layer_index
            texture_node = layer_nodes.get_layer_node("TEXTURE", self.material_channel_name, selected_layer_index, context)

        else:
            selected_layer_index = context.scene.matlay_layer_stack.layer_index
            selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
            texture_node = layer_masks.get_mask_node('MaskTexture', 'COLOR', selected_layer_index, selected_mask_index, False)

        # Select the image texture for exporting.
        if texture_node:
            if texture_node.bl_static_type == 'TEX_IMAGE':
                context.scene.tool_settings.image_paint.canvas = texture_node.image
            else:
                self.report({'ERROR'}, "Texture node type incorrect for exporting image to an image editor.")

        # Adjust to correct modes, and validate image being exported before exporting the image to an external image editor.
        export_image = context.scene.tool_settings.image_paint.canvas
        if export_image:
            if not export_image.packed_file:
                if export_image.file_format != '':
                    if export_image.filepath != '':
                        if export_image.is_dirty:
                            export_image.save()
                    else:
                        self.report({'ERROR'}, "Export image has no defined filepath.")
                else:
                    self.report({'ERROR'}, "Export image has no defined file format.")
            else:
                self.report({'ERROR'}, "Export image is packed, unpack and save the image to a folder to export to an external image editor.")
            bpy.ops.image.external_edit(filepath=export_image.filepath)
            matlay_utils.set_valid_material_shading_mode(context)
        
        return {'FINISHED'}

class MATLAY_OT_reload_image(Operator):
    bl_idname = "matlay.reload_image"
    bl_label = "Reload Image"
    bl_description = "Reloads the selected image from the disk"

    reload_mask: bpy.props.BoolProperty(default=False)
    material_channel_name: bpy.props.StringProperty(default='COLOR')

    @ classmethod
    def poll(cls, context):
        return context.scene.matlay_layers

    def execute(self, context):
        material_layers.validate_selected_material_layer_index()

        # Set the active image to the one that needs to be reloaded, relative to the position of the reload button in the user interface.
        selected_material_layer_index = context.scene.matlay_layer_stack.layer_index
        if self.reload_mask:
            selected_mask_index = context.scene.matlay_mask_stack.selected_mask_index
            texture_node = layer_masks.get_mask_node('MaskTexture', 'COLOR', selected_material_layer_index, selected_mask_index)
        else:
            texture_node = layer_nodes.get_layer_node('TEXTURE', self.material_channel_name, selected_material_layer_index, context)

        if texture_node:
            if texture_node.image != None:
                # Temporarily switch to the correct ui area / context and select the texture that needs to be reloaded.
                previously_selected_image = context.scene.tool_settings.image_paint.canvas
                context.scene.tool_settings.image_paint.canvas = texture_node.image
                previous_context = bpy.context.area.ui_type
                bpy.context.area.ui_type = 'IMAGE_EDITOR'
                bpy.ops.image.reload()
                bpy.context.area.ui_type = previous_context
                context.scene.tool_settings.image_paint.canvas = previously_selected_image
            else:
                self.report({'ERROR'}, "No valid texture to reload.")

        return{'FINISHED'}

#----------------------------- READING / REFRESHING USER INTERFACE PROPERTIES -----------------------------#

def read_layer_name_and_id(layers, context):
    '''Reads the name and id of layers from the material channel.'''
    layer_frame_nodes = layer_nodes.get_layer_frame_nodes(context)
    for i in range (len(layer_frame_nodes)):
        layers.add()
        layer_frame_info = layer_frame_nodes[i].label.split('_')
        layers[i].name = layer_frame_info[0]
        layers[i].cached_frame_name = layers[i].name + "_" + layer_frame_info[1] + "_" + str(i)
        layers[i].id = int(layer_frame_info[1])
        layers[i].layer_stack_array_index = i

def read_layer_opacity(total_number_of_layers, layers, selected_material_channel, context):
    '''Reads layer opacity for the selected material channel.'''
    for i in range(total_number_of_layers):
        opacity_node = layer_nodes.get_layer_node('OPACITY', selected_material_channel, i, context)
        layers[i].opacity = opacity_node.inputs[1].default_value

def read_decal_layer_properties(material_channel_list, total_number_of_layers, layers, context):
    '''Read properties for decal layers.'''
    # Check for a valid object in the coord node if one is provided, this is a decal layer update the layer type.
    for material_channel_name in material_channel_list:
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
        if material_channel_node:
            for i in range(total_number_of_layers):
                coord_node = layer_nodes.get_layer_node('COORD', material_channel_name, i, context)
                if not coord_node:
                    logging.popup_message_box("Error reading coord node.", "Reading Node Error", 'ERROR')
                    return
                
                if coord_node.object != None:
                    layers[i].type = 'DECAL'
                    layers[i].decal_object = coord_node.object

                else:
                    layers[i].type = 'FILL'

def read_texture_node_values(material_channel_list, total_number_of_layers, layers, context):
    '''Updates texture node values stored in layers by reading the material node trees.'''
    for material_channel_name in material_channel_list:
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
        if material_channel_node:
            for i in range(total_number_of_layers):
                texture_node = layer_nodes.get_layer_node('TEXTURE', material_channel_name, i, context)
                if not texture_node:
                    logging.popup_message_box("Error reading texture node.", "Reading Node Error", 'ERROR')
                    return

                match texture_node.type:
                    case 'VALUE':
                        setattr(layers[i].channel_node_types, material_channel_name.lower() + "_node_type", 'VALUE')
                        setattr(layers[i].uniform_channel_values, "uniform_" + material_channel_name.lower() + "_value", texture_node.outputs[0].default_value)

                    case 'RGB':
                        setattr(layers[i].channel_node_types, material_channel_name.lower() + "_node_type", 'COLOR')
                        color = texture_node.outputs[0].default_value
                        setattr(layers[i].color_channel_values, material_channel_name.lower() + "_channel_color", (color[0], color[1], color[2]))

                    case 'GROUP':
                        setattr(layers[i].channel_node_types, material_channel_name.lower() + "_node_type", 'GROUP_NODE')

                    case 'TEX_IMAGE':
                        setattr(layers[i].channel_node_types, material_channel_name.lower() + "_node_type", 'TEXTURE')

                    case 'TEX_NOISE':
                        setattr(layers[i].channel_node_types, material_channel_name.lower() + "_node_type", 'NOISE')

                    case 'TEX_MUSGRAVE':
                        setattr(layers[i].channel_node_types, material_channel_name.lower() + "_node_type", 'MUSGRAVE')

                    case 'TEX_VORONOI':
                        setattr(layers[i].channel_node_types, material_channel_name.lower() + "_node_type", 'VORONOI')

def read_layer_projection_values(material_layers, context):
    '''Update the projection values in the user interface for the selected layer.'''
    # Read the projection values from the color material channel because projection values among all material channels should be identical.
    material_channel_name = 'COLOR'
    material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
    if material_channel_node:
        for i in range(0, len(material_layers)):
            # Update offset, rotation and scale values.
            mapping_node = layer_nodes.get_layer_node('MAPPING', material_channel_name, i, context)
            if mapping_node:
                material_layers[i].projection.projection_offset_x = mapping_node.inputs[1].default_value[0]
                material_layers[i].projection.projection_offset_y = mapping_node.inputs[1].default_value[1]
                material_layers[i].projection.projection_offset_z = mapping_node.inputs[1].default_value[2]
                material_layers[i].projection.projection_rotation = mapping_node.inputs[2].default_value[2]
                material_layers[i].projection.projection_scale_x = mapping_node.inputs[3].default_value[0]
                material_layers[i].projection.projection_scale_y = mapping_node.inputs[3].default_value[1]
                material_layers[i].projection.projection_scale_z = mapping_node.inputs[3].default_value[2]
                if material_layers[i].projection.projection_scale_x != material_layers[i].projection.projection_scale_y:
                    material_layers[i].projection.match_layer_scale = False

            # Update the projection values specific to image texture projection.
            texture_node = layer_nodes.get_layer_node('TEXTURE', material_channel_name, i, context)
            if texture_node:
                if texture_node.type == 'TEX_IMAGE':
                    material_layers[i].projection.projection_blend = texture_node.projection_blend
                    material_layers[i].projection.texture_extension = texture_node.extension
                    material_layers[i].projection.texture_interpolation = texture_node.interpolation
                    material_layers[i].projection.projection_mode = texture_node.projection
                else:
                    material_layers[i].projection.projection_mode = 'FLAT'
    else:
        logging.popup_message_box("Missing " + material_channel_name + " group node.", "Material Stack Corrupted", 'ERROR')

def read_globally_active_material_channels(context):
    '''Updates globally active / inactive material channels per layer by reading the material node trees.'''
    # Globally active material channels are determined by checking if the material channel group node is connected.
    texture_set_settings = context.scene.matlay_texture_set_settings
    material_links = context.active_object.active_material.node_tree.links
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
        if material_channel_node:
            material_channel_linked = False
            for l in material_links:
                if l.from_node == material_channel_node:
                    material_channel_linked = True
                    setattr(texture_set_settings.global_material_channel_toggles, material_channel_name.lower() + "_channel_toggle", True)
                    break
            if not material_channel_linked:
                setattr(texture_set_settings.global_material_channel_toggles, material_channel_name.lower() + "_channel_toggle", False)

def read_hidden_layers(total_number_of_layers, layers, material_channel_list, context):
    '''Updates hidden material channels by reading the material node trees.'''

    # Hidden layers are determined by having all the material nodes in all material channels for a layer muted.
    for i in range(total_number_of_layers):
        for material_channel_name in material_channel_list:
            layer_hidden = True
            texture_node = layer_nodes.get_layer_node('TEXTURE', material_channel_name, i, context)
            if texture_node:
                if texture_node.mute == False:
                    layer_hidden = False
                    break
        layers[i].hidden = layer_hidden

def read_active_layer_material_channels(material_channel_list, total_number_of_layers, layers, context):
    '''Updates active / inactive material channels per layer by reading the material node trees.'''

    # Inactive material channels for a layer is determined by checking if the texture node is muted.
    for i in range(total_number_of_layers):
        for material_channel_name in material_channel_list:
            texture_node = layer_nodes.get_layer_node('TEXTURE', material_channel_name, i, context)
            
            if texture_node.mute:
                material_channel_active = False
            else:
                material_channel_active = True

            setattr(layers[i].material_channel_toggles, material_channel_name.lower() + "_channel_toggle", material_channel_active)

def read_layer_nodes(context):
    '''Reads the material node tree to define the layer stack user interface properties.'''

    # Only read layer nodes if there is an active object.
    if not bpy.context.active_object:
        return

    # Only read layer nodes if the active object is a mesh.
    if bpy.context.active_object.type != 'MESH':
        return
    
    # Turn auto updating for layer properties off.
    # This is to avoid node types from automatically being replaced when the node type is updated as doing so can cause errors when reading values (likely due to blender parameter update functions not being thread safe).
    context.scene.matlay_layer_stack.auto_update_layer_properties = False

    # Remember the selected layer index before clearing the layer stack.
    original_selected_layer_index = context.scene.matlay_layer_stack.layer_index

    # Clear the material stack.
    material_layers = context.scene.matlay_layers
    material_layers.clear()

    total_number_of_layers = layer_nodes.get_total_number_of_layers(context)
    material_channel_list = material_channels.get_material_channel_list()
    selected_material_channel = context.scene.matlay_layer_stack.selected_material_channel

    # After reading the layer stack, the number of layers may be different, reset the selected layer index if required.
    if total_number_of_layers >= original_selected_layer_index:
        context.scene.matlay_layer_stack.layer_index = original_selected_layer_index
    else:
        context.scene.matlay_layer_stack.layer_index = 0

    # Read material layer stuff.
    read_layer_name_and_id(material_layers, context)
    read_layer_opacity(total_number_of_layers, material_layers, selected_material_channel, context)
    read_decal_layer_properties(material_channel_list, total_number_of_layers, material_layers, context)
    read_texture_node_values(material_channel_list, total_number_of_layers, material_layers, context)
    read_layer_projection_values(material_layers, context)
    read_globally_active_material_channels(context)
    read_hidden_layers(total_number_of_layers, material_layers, material_channel_list, context)
    read_active_layer_material_channels(material_channel_list, total_number_of_layers, material_layers, context)
    material_filters.read_material_filter_nodes(context)
    layer_masks.read_mask_nodes(context)
    layer_masks.read_mask_filter_nodes(context)
    layer_nodes.organize_all_layer_nodes()

    context.scene.matlay_layer_stack.auto_update_layer_properties = True

class MATLAY_OT_read_layer_nodes(Operator):
    bl_idname = "matlay.read_layer_nodes"
    bl_label = "Read Layer Nodes"
    bl_description = "Updates the user interface to match the active material's node tree. This is called automatically when selecting an object"

    auto_called: BoolProperty(name="Auto Called", description="Should be true if refreshing layers was automatically called (i.e selecting a different object automatically refreshes the layer stack). This is used to avoid printing errors.", default=False)

    def execute(self, context):
        # Only read the layer stack for materials made with this add-on. 
        # Materials must follow a strict format to be able to be properly read, making materials not made with this add-on incompatible.
        if matlay_materials.verify_material(context) == False:
            bpy.context.scene.matlay_layers.clear()
            if self.auto_called == False:
                self.report({'ERROR'}, "Material is not a MatLay material, a material doesn't exist on the selected object, or the material is corrupted; ui can't be refreshed.")
            return {'FINISHED'}
        
        read_layer_nodes(context)

        # If read layer nodes is manually called, also relink material layers.
        if not self.auto_called:
            selected_material_layer_index = context.scene.matlay_layer_stack.layer_index
            material_filters.relink_material_filter_nodes(selected_material_layer_index)
            layer_masks.relink_mask_nodes(selected_material_layer_index)
            layer_masks.relink_mask_filter_nodes()
            layer_nodes.relink_material_layers()

        self.report({'INFO'}, "Refreshed layer stack.")

        return {'FINISHED'}
