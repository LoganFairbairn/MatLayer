import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import BoolProperty, IntProperty, StringProperty
import random
from ..core import texture_set_settings as tss
from ..core import material_layers
from ..core import blender_addon_utils
from ..core import debug_logging

def update_selected_mask_index(self, context):
    '''Updates properties when the selected mask slot is changed.'''
    selected_layer_index = context.scene.matlayer_layer_stack.selected_layer_index
    selected_mask_index = context.scene.matlayer_mask_stack.selected_index
    mask_texture_node = get_mask_node('TEXTURE', selected_layer_index, selected_mask_index)
    if mask_texture_node:
        blender_addon_utils.set_texture_paint_image(mask_texture_node.image)

def format_mask_name(layer_index, mask_index, material_name=""):
    '''Returns a properly formatted name for a mask node created with this add-on.'''
    if material_name == "":
        material_name = bpy.context.active_object.active_material.name
    return "{0}_{1}_{2}".format(material_name, str(layer_index), str(mask_index))

def get_mask_node_tree(layer_index, mask_index, active_material_name=""):
    '''Returns the mask node tree / node group at the provided layer and mask index.'''
    if active_material_name == "":
        active_material_name = bpy.context.active_object.active_material.name
    mask_node_tree_name = format_mask_name(layer_index, mask_index, active_material_name)
    return bpy.data.node_groups.get(mask_node_tree_name)

def get_mask_id_name(layer_index, mask_index):
    '''Returns the ID name of the mask if one exists (ID name exists on a value node stored in the masks node tree).'''
    if bpy.context.active_object == None:
        return ""
    
    active_material = bpy.context.active_object.active_material
    if active_material == None:
        return ""
    
    mask_group_node_name = format_mask_name(layer_index, mask_index)
    node_tree = bpy.data.node_groups.get(mask_group_node_name)
    if node_tree:
        id_node = node_tree.nodes.get('ID_NODE')
        if id_node:
            return id_node.label
    return ""

def get_mask_node(node_name, layer_index, mask_index, node_number=1, get_changed=False):
    if bpy.context.active_object == None:
        return None
    
    active_material = bpy.context.active_object.active_material
    if active_material == None:
        return None

    match node_name:
        case 'MASK':
            mask_node_name = format_mask_name(layer_index, mask_index)
            if get_changed:
                mask_node_name += "~"
            return active_material.node_tree.nodes.get(mask_node_name)
    
        case 'MASK_MIX':
            mask_group_node_name = format_mask_name(layer_index, mask_index)
            node_tree = bpy.data.node_groups.get(mask_group_node_name)
            if node_tree:
                return node_tree.nodes.get('MASK_MIX')
            return None

        case 'FILTER':
            mask_group_node_name = format_mask_name(layer_index, mask_index)
            node_tree = bpy.data.node_groups.get(mask_group_node_name)
            if node_tree:
                return node_tree.nodes.get('FILTER')
            return None

        case 'PROJECTION':
            mask_group_node_name = format_mask_name(layer_index, mask_index)
            node_tree = bpy.data.node_groups.get(mask_group_node_name)
            if node_tree:
                return node_tree.nodes.get('PROJECTION')
            return None

        case 'COORDINATES':
            mask_group_node_name = format_mask_name(layer_index, mask_index)
            node_tree = bpy.data.node_groups.get(mask_group_node_name)
            if node_tree:
                return node_tree.nodes.get('COORDINATES')
            return None

        case 'DECAL_COORDINATES':
            mask_group_node_name = format_mask_name(layer_index, mask_index)
            node_tree = bpy.data.node_groups.get(mask_group_node_name)
            if node_tree:
                return node_tree.nodes.get('DECAL_COORDINATES')
            return None

        case 'DECAL_OFFSET':
            mask_group_node_name = format_mask_name(layer_index, mask_index)
            node_tree = bpy.data.node_groups.get(mask_group_node_name)
            if node_tree:
                return node_tree.nodes.get('DECAL_OFFSET')
            return None

        case 'TRIPLANAR_BLEND':
            mask_group_node_name = format_mask_name(layer_index, mask_index)
            node_tree = bpy.data.node_groups.get(mask_group_node_name)
            if node_tree:
                return node_tree.nodes.get('TRIPLANAR_BLEND')
            return None

        case 'TEXTURE':
            mask_group_node_name = format_mask_name(layer_index, mask_index)
            node_tree = bpy.data.node_groups.get(mask_group_node_name)
            if node_tree:
                return node_tree.nodes.get("TEXTURE_{0}".format(node_number))
            return None
        
        case 'BLUR':
            mask_group_node_name = format_mask_name(layer_index, mask_index)
            node_tree = bpy.data.node_groups.get(mask_group_node_name)
            if node_tree:
                return node_tree.nodes.get('BLUR')
            return None        

        case 'AMBIENT_OCCLUSION':
            mask_group_node_name = format_mask_name(layer_index, mask_index)
            node_tree = bpy.data.node_groups.get(mask_group_node_name)
            if node_tree:
                return node_tree.nodes.get('AMBIENT_OCCLUSION')
            return None

        case 'CURVATURE':
            mask_group_node_name = format_mask_name(layer_index, mask_index)
            node_tree = bpy.data.node_groups.get(mask_group_node_name)
            if node_tree:
                return node_tree.nodes.get('CURVATURE')
            return None
        
        case 'THICKNESS':
            mask_group_node_name = format_mask_name(layer_index, mask_index)
            node_tree = bpy.data.node_groups.get(mask_group_node_name)
            if node_tree:
                return node_tree.nodes.get('THICKNESS')
            return None
        
        case 'NORMALS':
            mask_group_node_name = format_mask_name(layer_index, mask_index)
            node_tree = bpy.data.node_groups.get(mask_group_node_name)
            if node_tree:
                return node_tree.nodes.get('NORMALS')
            return None
        
        case 'WORLD_SPACE_NORMALS':
            mask_group_node_name = format_mask_name(layer_index, mask_index)
            node_tree = bpy.data.node_groups.get(mask_group_node_name)
            if node_tree:
                return node_tree.nodes.get('WORLD_SPACE_NORMALS')
            return None

def count_masks(layer_index, material_name=""):
    '''Counts the total number of masks for the specified material by applied to the specified layer by counting existing material node groups in the blend data.'''
    mask_count = 0

    # If a specific material name is provided, count for the material name.
    if material_name != "":
        while bpy.data.node_groups.get(format_mask_name(layer_index, mask_count, material_name)):
            mask_count += 1
    else:
        active_object = bpy.context.active_object
        if active_object:
            if active_object.active_material:
                while bpy.data.node_groups.get(format_mask_name(layer_index, mask_count, active_object.active_material.name)):
                    mask_count += 1

    return mask_count

def add_mask_slot():
    '''Adds a new mask slot to the mask stack.'''
    masks = bpy.context.scene.matlayer_masks
    mask_stack = bpy.context.scene.matlayer_mask_stack

    mask_slot = masks.add()

    # Assign a random, unique number to the layer slot. This allows the layer slot array index to be found using the name of the layer slot as a key.
    unique_random_slot_id = str(random.randrange(0, 999999))
    while masks.find(unique_random_slot_id) != -1:
        unique_random_slot_id = str(random.randrange(0, 999999))
    mask_slot.name = unique_random_slot_id

    # If there is no layer selected, move the layer to the top of the stack.
    if bpy.context.scene.matlayer_mask_stack.selected_index < 0:
        move_index = len(masks) - 1
        move_to_index = 0
        masks.move(move_index, move_to_index)
        mask_stack.layer_index = move_to_index
        bpy.context.scene.matlayer_mask_stack.selected_index = len(masks) - 1

    # Moves the new layer above the currently selected layer and selects it.
    else: 
        move_index = len(masks) - 1
        move_to_index = max(0, min(bpy.context.scene.matlayer_mask_stack.selected_index + 1, len(masks) - 1))
        masks.move(move_index, move_to_index)
        mask_stack.layer_index = move_to_index
        bpy.context.scene.matlayer_mask_stack.selected_index = max(0, min(bpy.context.scene.matlayer_mask_stack.selected_index + 1, len(masks) - 1))

    return bpy.context.scene.matlayer_mask_stack.selected_index

def add_layer_mask(type, self):
    '''Adds a mask of the specified type to the selected material layer.'''

    if blender_addon_utils.verify_material_operation_context(self) == False:
        return

    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    new_mask_slot_index = add_mask_slot()
    active_material = bpy.context.active_object.active_material

    new_mask_group_node = None
    match type:
        case 'EMPTY':
            default_node_group = blender_addon_utils.append_group_node("ML_ImageMask", never_auto_delete=True)
            default_node_group.name = format_mask_name(selected_layer_index, new_mask_slot_index) + "~"

            new_mask_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
            new_mask_group_node.node_tree = default_node_group
            new_mask_group_node.name = format_mask_name(selected_layer_index, new_mask_slot_index) + "~"
            new_mask_group_node.label = "Image Mask"
            
            reindex_masks('ADDED_MASK', selected_layer_index, new_mask_slot_index)
            organize_mask_nodes()
            link_mask_nodes(selected_layer_index)
            debug_logging.log("Added empty layer mask.")
                
        case 'BLACK':
            default_node_group = blender_addon_utils.append_group_node("ML_ImageMask", never_auto_delete=True)
            default_node_group.name = format_mask_name(selected_layer_index, new_mask_slot_index) + "~"

            new_mask_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
            new_mask_group_node.node_tree = default_node_group
            new_mask_group_node.name = format_mask_name(selected_layer_index, new_mask_slot_index) + "~"
            new_mask_group_node.label = "Image Mask"

            image_name = "Mask_" + str(random.randrange(10000,99999))
            while bpy.data.images.get(image_name) != None:
                image_name = "Mask_" + str(random.randrange(10000,99999))
            bpy.ops.image.new(name=image_name, 
                              width=tss.get_texture_width(), 
                              height=tss.get_texture_height(), 
                              color=(0.0, 0.0, 0.0, 1.0), 
                              alpha=False, generated_type='BLANK', 
                              float=True, 
                              use_stereo_3d=False, 
                              tiled=False)
            
            reindex_masks('ADDED_MASK', selected_layer_index, new_mask_slot_index)
            organize_mask_nodes()
            link_mask_nodes(selected_layer_index)

            texture_node = get_mask_node('TEXTURE', selected_layer_index, new_mask_slot_index)
            new_image = bpy.data.images.get(image_name)
            if texture_node and new_image:
                texture_node.image = new_image

            bpy.context.scene.tool_settings.image_paint.canvas = new_image
            debug_logging.log("Added black layer mask.")

        case 'WHITE':
            default_node_group = blender_addon_utils.append_group_node("ML_ImageMask", never_auto_delete=True)
            default_node_group.name = format_mask_name(selected_layer_index, new_mask_slot_index) + "~"

            new_mask_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
            new_mask_group_node.node_tree = default_node_group
            new_mask_group_node.name = format_mask_name(selected_layer_index, new_mask_slot_index) + "~"
            new_mask_group_node.label = "Image Mask"

            image_name = "Mask_" + str(random.randrange(10000,99999))
            while bpy.data.images.get(image_name) != None:
                image_name = "Mask_" + str(random.randrange(10000,99999))
            bpy.ops.image.new(name=image_name, 
                              width=tss.get_texture_width(), 
                              height=tss.get_texture_height(), 
                              color=(1.0, 1.0, 1.0, 1.0), 
                              alpha=False, generated_type='BLANK', 
                              float=True, 
                              use_stereo_3d=False, 
                              tiled=False)
            
            reindex_masks('ADDED_MASK', selected_layer_index, new_mask_slot_index)
            organize_mask_nodes()
            link_mask_nodes(selected_layer_index)

            texture_node = get_mask_node('TEXTURE', selected_layer_index, new_mask_slot_index)
            new_image = bpy.data.images.get(image_name)
            if texture_node and new_image:
                texture_node.image = new_image

            bpy.context.scene.tool_settings.image_paint.canvas = new_image
            debug_logging.log("Added white layer mask.")

        case 'LINEAR_GRADIENT':
            default_node_group = blender_addon_utils.append_group_node("ML_LinearGradient", never_auto_delete=True)
            default_node_group.name = format_mask_name(selected_layer_index, new_mask_slot_index) + "~"

            new_mask_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
            new_mask_group_node.node_tree = default_node_group
            new_mask_group_node.name = format_mask_name(selected_layer_index, new_mask_slot_index) + "~"
            new_mask_group_node.label = "Linear Gradient"
    
            reindex_masks('ADDED_MASK', selected_layer_index, new_mask_slot_index)
            organize_mask_nodes()
            link_mask_nodes(selected_layer_index)
            debug_logging.log("Added a linear gradient mask.")

        case 'DECAL':
            default_node_group = blender_addon_utils.append_group_node("ML_DecalMask", never_auto_delete=True)
            default_node_group.name = format_mask_name(selected_layer_index, new_mask_slot_index) + "~"

            new_mask_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
            new_mask_group_node.node_tree = default_node_group
            new_mask_group_node.name = format_mask_name(selected_layer_index, new_mask_slot_index) + "~"
            new_mask_group_node.label = "Decal Mask"
            
            reindex_masks('ADDED_MASK', selected_layer_index, new_mask_slot_index)
            organize_mask_nodes()
            link_mask_nodes(selected_layer_index)

            # Add the decal object from the layer decal projection to the mask projection.
            decal_coordinates_node = material_layers.get_material_layer_node('DECAL_COORDINATES', selected_layer_index)
            if decal_coordinates_node:
                mask_coordinates_node = get_mask_node('DECAL_COORDINATES', selected_layer_index, new_mask_slot_index)
                if mask_coordinates_node:
                    mask_coordinates_node.object = decal_coordinates_node.object

            debug_logging.log("Added a decal mask.")

        case 'GRUNGE':
            default_node_group = blender_addon_utils.append_group_node("ML_Grunge", never_auto_delete=True)
            default_node_group.name = format_mask_name(selected_layer_index, new_mask_slot_index) + "~"

            new_mask_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
            new_mask_group_node.node_tree = default_node_group
            new_mask_group_node.name = format_mask_name(selected_layer_index, new_mask_slot_index) + "~"
            new_mask_group_node.label = "Grunge"
    
            reindex_masks('ADDED_MASK', selected_layer_index, new_mask_slot_index)
            organize_mask_nodes()
            link_mask_nodes(selected_layer_index)
            material_layers.apply_mesh_maps()

            # Add a default grunge texture to the mask.
            default_grunge_texture = blender_addon_utils.append_image('DefaultGrunge')
            for i in range(0, 3):
                texture_sample_node = get_mask_node('TEXTURE', selected_layer_index, new_mask_slot_index, node_number=i + 1)
                if texture_sample_node:
                    texture_sample_node.image = default_grunge_texture

            debug_logging.log("Added a grunge mask.") 

        case 'EDGE_WEAR':
            default_node_group = blender_addon_utils.append_group_node("ML_EdgeWear", never_auto_delete=True)
            default_node_group.name = format_mask_name(selected_layer_index, new_mask_slot_index) + "~"

            new_mask_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
            new_mask_group_node.node_tree = default_node_group
            new_mask_group_node.name = format_mask_name(selected_layer_index, new_mask_slot_index) + "~"
            new_mask_group_node.label = "Edge Wear"
    
            reindex_masks('ADDED_MASK', selected_layer_index, new_mask_slot_index)
            organize_mask_nodes()
            link_mask_nodes(selected_layer_index)
            material_layers.apply_mesh_maps()

            # Add a default edge wear texture to the mask.
            default_grunge_texture = blender_addon_utils.append_image('DefaultGrunge')
            for i in range(0, 3):
                texture_sample_node = get_mask_node('TEXTURE', selected_layer_index, new_mask_slot_index, node_number=i + 1)
                if texture_sample_node:
                    texture_sample_node.image = default_grunge_texture
                    
            debug_logging.log("Added edge wear mask.")

def duplicate_mask(self, mask_index=-1):
    '''Duplicates the mask at the provided mask index.'''
    if blender_addon_utils.verify_material_operation_context(self) == False:
        return
    
    # Duplicate the selected mask index if a mask index to duplicate is not specified.
    if mask_index == -1:
        mask_index = bpy.context.scene.matlayer_mask_stack.selected_index

    # Duplicate the mask node, mask node tree and add it to the mask stack.
    active_material = bpy.context.active_object.active_material
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    mask_node = get_mask_node('MASK', selected_layer_index, mask_index)
    mask_node_tree = get_mask_node_tree(selected_layer_index, mask_index)
    if mask_node_tree:
        duplicated_node_tree = blender_addon_utils.duplicate_node_group(mask_node_tree.name)

        if duplicated_node_tree:
            new_mask_slot_index = add_mask_slot()
            duplicated_node_tree.name = format_mask_name(selected_layer_index, new_mask_slot_index)
            new_mask_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
            new_mask_group_node.node_tree = duplicated_node_tree
            new_mask_group_node.name = format_mask_name(selected_layer_index, new_mask_slot_index) + "~"
            new_mask_group_node.label = mask_node.label

            reindex_masks(change_made='ADDED_MASK', layer_index=selected_layer_index, affected_mask_index=new_mask_slot_index)
            organize_mask_nodes()
            link_mask_nodes(selected_layer_index)

        debug_logging.log("Duplicated layer mask.")

def delete_layer_mask(self):
    '''Removed the selected layer mask from the mask stack.'''
    if blender_addon_utils.verify_material_operation_context(self) == False:
        return

    masks = bpy.context.scene.matlayer_masks
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    selected_mask_index = bpy.context.scene.matlayer_mask_stack.selected_index
    active_material = bpy.context.active_object.active_material

    # Remove the mask node and it's node tree.
    mask_node = get_mask_node('MASK', selected_layer_index, selected_mask_index)
    if mask_node:
        if mask_node.node_tree:
            bpy.data.node_groups.remove(mask_node.node_tree)
        active_material.node_tree.nodes.remove(mask_node)

    reindex_masks('DELETED_MASK', selected_layer_index, selected_mask_index)
    organize_mask_nodes()
    link_mask_nodes(selected_layer_index)

    # Remove the mask slot and reset the mask index.
    masks.remove(selected_mask_index)
    bpy.context.scene.matlayer_mask_stack.selected_index = max(min(selected_mask_index - 1, len(masks) - 1), 0)
    debug_logging.log("Deleted layer mask.")

def move_mask(direction, self):
    '''Moves the selected mask up / down on the material layer stack.'''
    if blender_addon_utils.verify_material_operation_context(self) == False:
        return

    masks = bpy.context.scene.matlayer_masks
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index

    match direction:
        case 'UP':
            # Swap the mask node and node tree index for the selected mask node with the mask above it (if one exists).
            selected_mask_index = bpy.context.scene.matlayer_mask_stack.selected_index

            if selected_mask_index < len(masks) - 1:
                mask_node = get_mask_node('MASK', selected_layer_index, selected_mask_index)
                mask_node.name += "~"
                mask_node.node_tree.name += "~"

                above_mask_node = get_mask_node('MASK', selected_layer_index, selected_mask_index + 1)
                above_mask_node.name = format_mask_name(selected_layer_index, selected_mask_index)
                above_mask_node.node_tree.name = above_mask_node.name

                mask_node.name = format_mask_name(selected_layer_index, selected_mask_index + 1)
                mask_node.node_tree.name = mask_node.name

                bpy.context.scene.matlayer_mask_stack.selected_index = selected_mask_index + 1

                debug_logging.log("Moved mask up on the mask stack.")

        case 'DOWN':
            # Swap the mask node and node tree index for the selected mask node with the mask below it (if one exists).
            selected_mask_index = bpy.context.scene.matlayer_mask_stack.selected_index

            if selected_mask_index - 1 >= 0:
                mask_node = get_mask_node('MASK', selected_layer_index, selected_mask_index)
                mask_node.name += "~"
                mask_node.node_tree.name += "~"

                above_mask_node = get_mask_node('MASK', selected_layer_index, selected_mask_index - 1)
                above_mask_node.name = format_mask_name(selected_layer_index, selected_mask_index)
                above_mask_node.node_tree.name = above_mask_node.name

                mask_node.name = format_mask_name(selected_layer_index, selected_mask_index - 1)
                mask_node.node_tree.name = mask_node.name

                bpy.context.scene.matlayer_mask_stack.selected_index = selected_mask_index - 1

                debug_logging.log("Moved mask down on the mask stack.")

    organize_mask_nodes()
    link_mask_nodes(selected_layer_index)
    
def reindex_masks(change_made, layer_index, affected_mask_index):
    '''Reindexes mask nodes and node trees. This should be called after a change is made that effects the mask stack order (adding, duplicating, deleting a mask).'''
    match change_made:
        case 'ADDED_MASK':
            # Increase the layer index for all layer group nodes and their node trees that exist above the affected layer.
            total_masks = len(bpy.context.scene.matlayer_masks)
            for i in range(total_masks, affected_mask_index, -1):
                mask_node = get_mask_node('MASK', layer_index, i - 1)
                if mask_node:
                    mask_node_name = format_mask_name(layer_index, int(mask_node.name.split('_')[2]) + 1)
                    mask_node.name = mask_node_name
                    mask_node.node_tree.name = mask_node_name

            new_mask_node = get_mask_node('MASK', layer_index, affected_mask_index, get_changed=True)
            if new_mask_node:
                mask_node_name = format_mask_name(layer_index, affected_mask_index)
                new_mask_node.name = mask_node_name
                new_mask_node.node_tree.name = mask_node_name
            debug_logging.log("Re-indexed masks for a new added / duplicated mask.")

        case 'DELETED_MASK':
            # Reduce the layer index for all layer group nodes and their nodes trees that exist above the affected layer.
            mask_count = len(bpy.context.scene.matlayer_masks)
            for i in range(affected_mask_index + 1, mask_count):
                mask_node = get_mask_node('MASK', layer_index, i)
                mask_node.name = format_mask_name(layer_index, int(mask_node.name.split('_')[2]) - 1)
                mask_node.node_tree.name = mask_node.name
            debug_logging.log("Re-indexed mask nodes for after a mask was deleted.")

def organize_mask_nodes():
    '''Organizes the position of all mask nodes in the active materials node tree.'''
    layer_count = material_layers.count_layers()
    for i in range(0, layer_count):
        layer_node = material_layers.get_material_layer_node('LAYER', i)
        position_y = layer_node.location[1] - 600
        mask_count = count_masks(i)
        for c in range(mask_count, 0, -1):
            mask_node = get_mask_node('MASK', i, c - 1)
            if mask_node:
                mask_node.location = (layer_node.location[0], position_y)
                mask_node.width = 300
                position_y -= 300
    debug_logging.log("Organized masks nodes.")

def link_mask_nodes(layer_index):
    '''Links existing mask nodes together and to their respective material layer.'''
    if not bpy.context.active_object:
        return

    if not bpy.context.active_object.active_material:
        return

    active_material = bpy.context.active_object.active_material
    node_tree = active_material.node_tree
    mask_count = count_masks(layer_index)

    # Disconnect all mask group nodes.
    for i in range(0, mask_count):
        mask_node = get_mask_node('MASK', layer_index, i)
        if mask_node:
            for input in mask_node.inputs:
                for link in input.links:
                    node_tree.links.remove(link)

    # Re-connect all mask group nodes.
    for i in range(0, mask_count):
        mask_node = get_mask_node('MASK', layer_index, i)
        next_mask_node = get_mask_node('MASK', layer_index, i + 1)
        if next_mask_node:
            last_input_index = len(next_mask_node.inputs) - 1
            node_tree.links.new(mask_node.outputs[0], next_mask_node.inputs[last_input_index])

    # Connect the last layer node.
    layer_node = material_layers.get_material_layer_node('LAYER', layer_index)
    last_mask_node = get_mask_node('MASK', layer_index, mask_count - 1)
    if last_mask_node and last_mask_node:
        node_tree.links.new(last_mask_node.outputs[0], layer_node.inputs.get('LayerMask'))

    debug_logging.log("Re-linked mask nodes.")

def refresh_mask_slots():
    '''Refreshes the number of mask slots in the mask stack by counting the number of mask nodes in the active materials node tree.'''
    masks = bpy.context.scene.matlayer_masks
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    masks.clear()
    mask_count = count_masks(selected_layer_index)
    for i in range(0, mask_count):
        add_mask_slot()

def relink_image_mask_projection():
    '''Relinks projection nodes based on the projection mode for image masks.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    selected_mask_index = bpy.context.scene.matlayer_mask_stack.selected_index
    mask_node = get_mask_node('MASK', selected_layer_index, selected_mask_index)
    projection_node = get_mask_node('PROJECTION', selected_layer_index, selected_mask_index)
    blur_node = get_mask_node('BLUR', selected_layer_index, selected_mask_index)

    # Disconnect the projection and blur nodes.
    blender_addon_utils.unlink_node(projection_node, mask_node.node_tree, unlink_inputs=False, unlink_outputs=True)
    blender_addon_utils.unlink_node(blur_node, mask_node.node_tree, unlink_inputs=True, unlink_outputs=True)

    original_output_channel = get_mask_output_channel()

    # Link mask nodes based on the mask projection mode.
    match projection_node.node_tree.name:
        case "ML_TriplanarProjection":
            # Always connect the projection node to the blur node.
            mask_node.node_tree.links.new(projection_node.outputs[0], blur_node.inputs[0])
            mask_node.node_tree.links.new(projection_node.outputs[1], blur_node.inputs[1])
            mask_node.node_tree.links.new(projection_node.outputs[2], blur_node.inputs[2])
            
            mask_filter_node = get_mask_node('FILTER', selected_layer_index, selected_mask_index)
            triplanar_blend_node = get_mask_node('TRIPLANAR_BLEND', selected_layer_index, selected_mask_index)

            if blender_addon_utils.get_node_active(blur_node):
                for i in range(0, 3):
                    texture_node = get_mask_node('TEXTURE', selected_layer_index, selected_mask_index, node_number=i + 1)
                    if texture_node:
                        mask_node.node_tree.links.new(blur_node.outputs[i], texture_node.inputs[0])
                        mask_node.node_tree.links.new(texture_node.outputs[0], triplanar_blend_node.inputs[i])
                        mask_node.node_tree.links.new(texture_node.outputs[1], triplanar_blend_node.inputs[i + 3])
                mask_node.node_tree.links.new(projection_node.outputs.get('AxisMask'), triplanar_blend_node.inputs.get('AxisMask'))

                if mask_filter_node:
                    mask_node.node_tree.links.new(triplanar_blend_node.outputs.get('Color'), mask_filter_node.inputs[0])
            
            else:
                for i in range(0, 3):
                    texture_node = get_mask_node('TEXTURE', selected_layer_index, selected_mask_index, node_number=i + 1)
                    if texture_node:
                        mask_node.node_tree.links.new(projection_node.outputs[i], texture_node.inputs[0])
                        mask_node.node_tree.links.new(texture_node.outputs[0], triplanar_blend_node.inputs[i])
                        mask_node.node_tree.links.new(texture_node.outputs[1], triplanar_blend_node.inputs[i + 3])
                mask_node.node_tree.links.new(projection_node.outputs.get('AxisMask'), triplanar_blend_node.inputs.get('AxisMask'))
                
                if mask_filter_node:
                    blender_addon_utils.unlink_node(mask_filter_node, mask_node.node_tree, unlink_inputs=False, unlink_outputs=True)
                    mask_node.node_tree.links.new(triplanar_blend_node.outputs[0], mask_filter_node.inputs[0])

            # Unlink and re-link the mask filter node to trigger a re-compile of the material.
            if mask_filter_node:
                blender_addon_utils.unlink_node(mask_filter_node, mask_node.node_tree, unlink_inputs=False, unlink_outputs=True)
                mix_node = get_mask_node('MASK_MIX', selected_layer_index, selected_mask_index)
                if mix_node:
                    mask_node.node_tree.links.new(mask_filter_node.outputs[0], mix_node.inputs[7])

        case "ML_UVProjection":
            mask_node.node_tree.links.new(projection_node.outputs[0], blur_node.inputs[0])

            texture_node = get_mask_node('TEXTURE', selected_layer_index, selected_mask_index)
            if blender_addon_utils.get_node_active(blur_node):
                mask_node.node_tree.links.new(blur_node.outputs[0], texture_node.inputs[0])

            else:
                mask_node.node_tree.links.new(projection_node.outputs[0], texture_node.inputs[0])

            mask_filter_node = get_mask_node('FILTER', selected_layer_index, selected_mask_index)
            mask_node.node_tree.links.new(texture_node.outputs[0], mask_filter_node.inputs[0])

            # Unlink and re-link the mask filter node to trigger a re-compile of the material.
            blender_addon_utils.unlink_node(mask_filter_node, mask_node.node_tree, unlink_inputs=False, unlink_outputs=True)
            mix_node = get_mask_node('MASK_MIX', selected_layer_index, selected_mask_index)
            if mix_node:
                mask_node.node_tree.links.new(mask_filter_node.outputs[0], mix_node.inputs[7])

        case "ML_DecalProjection":
            mask_node.node_tree.links.new(projection_node.outputs[0], blur_node.inputs[0])

            texture_node = get_mask_node('TEXTURE', selected_layer_index, selected_mask_index)
            if blender_addon_utils.get_node_active(blur_node):
                mask_node.node_tree.links.new(blur_node.outputs[0], texture_node.inputs[0])

            else:
                mask_node.node_tree.links.new(projection_node.outputs[0], texture_node.inputs[0])

            mask_filter_node = get_mask_node('FILTER', selected_layer_index, selected_mask_index)
            mask_node.node_tree.links.new(texture_node.outputs[0], mask_filter_node.inputs[0])

            linear_mask_blend_node = mask_node.node_tree.nodes.get('LINEAR_MASK_BLEND')
            mask_node.node_tree.links.new(mask_filter_node.outputs[0], linear_mask_blend_node.inputs[0])
            mask_node.node_tree.links.new(projection_node.outputs[1], linear_mask_blend_node.inputs[1])

    set_mask_output_channel(original_output_channel)

def set_mask_projection_mode(projection_mode):
    '''Sets the projection mode of the mask. Only image masks can have their projection mode swapped.'''
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    selected_mask_index = bpy.context.scene.matlayer_mask_stack.selected_index
    
    match projection_mode:
        case 'UV':
            mask_node = get_mask_node('MASK', selected_layer_index, selected_mask_index)
            projection_node = get_mask_node('PROJECTION', selected_layer_index, selected_mask_index)

            # Replace triplanar mask node setup.
            mask_texture_node = get_mask_node('TEXTURE', selected_layer_index, selected_mask_index)
            if mask_texture_node:
                original_texture_node_location = mask_texture_node.location
                original_texture_node_image = mask_texture_node.image

                for i in range(0, 3):
                    texture_node = get_mask_node('TEXTURE', selected_layer_index, selected_mask_index, node_number=i + 1)
                    if texture_node:
                        mask_node.node_tree.nodes.remove(texture_node)

                triplanar_blend_node = get_mask_node('TRIPLANAR_BLEND', selected_layer_index, selected_mask_index)
                if triplanar_blend_node:
                    mask_node.node_tree.nodes.remove(triplanar_blend_node)

                new_mask_texture_node = mask_node.node_tree.nodes.new('ShaderNodeTexImage')
                new_mask_texture_node.name = "TEXTURE_1"
                new_mask_texture_node.label = new_mask_texture_node.name
                new_mask_texture_node.location = original_texture_node_location
                new_mask_texture_node.image = original_texture_node_image

            # Set the projection and blur nodes to use triplanar setups.
            projection_node.node_tree = blender_addon_utils.append_group_node('ML_UVProjection')
            blur_node = get_mask_node('BLUR', selected_layer_index, selected_mask_index)
            if blur_node:
                blur_node.node_tree = blender_addon_utils.append_group_node('ML_NoiseBlur')

        case 'TRIPLANAR':
            mask_node = get_mask_node('MASK', selected_layer_index, selected_mask_index)
            projection_node = get_mask_node('PROJECTION', selected_layer_index, selected_mask_index)
            if projection_node.node_tree.name != 'ML_TriplanarProjection':

                # Replace the UV mask texture node setup with a triplanar texture node setup.
                mask_texture_node = get_mask_node('TEXTURE', selected_layer_index, selected_mask_index)
                if mask_texture_node:
                    original_texture_node_location = mask_texture_node.location
                    original_texture_node_image = mask_texture_node.image

                    mask_node.node_tree.nodes.remove(mask_texture_node)

                    location_x = original_texture_node_location[0]
                    location_y = original_texture_node_location[1]
                    for i in range(0, 3):
                        new_mask_texture_node = mask_node.node_tree.nodes.new('ShaderNodeTexImage')
                        new_mask_texture_node.name = "TEXTURE_{0}".format(i + 1)
                        new_mask_texture_node.label = new_mask_texture_node.name
                        new_mask_texture_node.location = (location_x, location_y)
                        new_mask_texture_node.hide = True
                        new_mask_texture_node.width = 200
                        new_mask_texture_node.image = original_texture_node_image
                        location_y -= 50

                    # Add a triplanar blending node.
                    triplanar_blend_node = mask_node.node_tree.nodes.new('ShaderNodeGroup')
                    triplanar_blend_node.node_tree = blender_addon_utils.append_group_node("ML_TriplanarBlend")
                    triplanar_blend_node.name = "TRIPLANAR_BLEND"
                    triplanar_blend_node.label = triplanar_blend_node.name
                    triplanar_blend_node.width = 200
                    triplanar_blend_node.hide = True
                    triplanar_blend_node.location = (location_x, location_y)

                # Set the projection and blur nodes to use triplanar setups.
                projection_node.node_tree = blender_addon_utils.append_group_node('ML_TriplanarProjection')
                blur_node = get_mask_node('BLUR', selected_layer_index, selected_mask_index)
                if blur_node:
                    blur_node.node_tree = blender_addon_utils.append_group_node('ML_TriplanarBlur')

def get_mask_output_channel():
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    selected_mask_index = bpy.context.scene.matlayer_mask_stack.selected_index
    filter_node = get_mask_node('FILTER', selected_layer_index, selected_mask_index)

    output_channel = ''
    if filter_node:
        output_channel = filter_node.inputs[0].links[0].from_socket.name.upper()

    return output_channel

def set_mask_output_channel(output_channel):
    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
    selected_mask_index = bpy.context.scene.matlayer_mask_stack.selected_index

    mask_node = get_mask_node('MASK', selected_layer_index, selected_mask_index)
    mask_texture_node = get_mask_node('TEXTURE', selected_layer_index, selected_mask_index)
    mask_filter_node = get_mask_node('FILTER', selected_layer_index, selected_mask_index)
    mask_projection_node = get_mask_node('PROJECTION', selected_layer_index, selected_mask_index)
    separate_color_node = mask_node.node_tree.nodes.get('SEPARATE_COLOR')

    # Find the main mask output node based on the mask projection.
    output_node = None
    match mask_projection_node.node_tree.name:
        case 'ML_TriplanarProjection':
            output_node = get_mask_node('TRIPLANAR_BLEND', selected_layer_index, selected_mask_index)
        case _:
            output_node = mask_texture_node

    # Disconnect the mask nodes.
    blender_addon_utils.unlink_node(output_node, mask_node.node_tree, unlink_inputs=False, unlink_outputs=True)
    blender_addon_utils.unlink_node(separate_color_node, mask_node.node_tree, unlink_inputs=True, unlink_outputs=True)

    # Connect the specified channel to the mask filter.
    match output_channel:
        case 'COLOR':
            mask_node.node_tree.links.new(output_node.outputs[0], mask_filter_node.inputs[0])

        case 'ALPHA':
            mask_node.node_tree.links.new(output_node.outputs[1], mask_filter_node.inputs[0])

        case 'RED':
            mask_node.node_tree.links.new(output_node.outputs[0], separate_color_node.inputs[0])
            mask_node.node_tree.links.new(separate_color_node.outputs[0], mask_filter_node.inputs[0])

        case 'GREEN':
            mask_node.node_tree.links.new(output_node.outputs[0], separate_color_node.inputs[0])
            mask_node.node_tree.links.new(separate_color_node.outputs[1], mask_filter_node.inputs[0])

        case 'BLUE':
            mask_node.node_tree.links.new(output_node.outputs[0], separate_color_node.inputs[0])
            mask_node.node_tree.links.new(separate_color_node.outputs[2], mask_filter_node.inputs[0])

#----------------------------- OPERATORS -----------------------------#

class MATLAYER_mask_stack(PropertyGroup):
    '''Properties for the layer stack.'''
    selected_index: IntProperty(default=-1, description="Selected material filter index", update=update_selected_mask_index)

class MATLAYER_masks(PropertyGroup):
    hidden: BoolProperty(name="Hidden", description="Show if the layer is hidden")
    sync_projection_scale: BoolProperty(name="Sync Projection Scale", description="When enabled Y and Z projection (if the projection mode has a z projection) will be synced with the X projection", default=True)

class MATLAYER_UL_mask_list(bpy.types.UIList):
    '''Draws the mask stack.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)

            # Hidden Toggle
            row = layout.row(align=True)
            row.ui_units_x = 1
            if item.hidden == True:
                row.prop(item, "hidden", text="", emboss=False, icon='HIDE_ON')

            elif item.hidden == False:
                row.prop(item, "hidden", text="", emboss=False, icon='HIDE_OFF')

            # Isolate Mask
            row = layout.row(align=True)
            row.ui_units_x = 1
            masks = bpy.context.scene.matlayer_masks
            item_index = masks.find(item.name)
            operator = row.operator("matlayer.isolate_mask", text="", icon='MOD_MASK', emboss=False)
            operator.mask_index = item_index

            # Mask Name
            selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
            mask_node = get_mask_node('MASK', selected_layer_index, item_index)
            if mask_node:
                row = layout.row()
                row.ui_units_x = 3
                row.prop(mask_node, "label", text="", emboss=False)

            # Mask opacity and blending mode.
            mask_mix_node = get_mask_node('MASK_MIX', selected_layer_index, item_index)
            if mask_mix_node:
                row = layout.row(align=True)
                row.ui_units_x = 2

                split = layout.split()
                col = split.column(align=True)
                col.ui_units_x = 1.6
                col.scale_y = 0.5
                col.prop(mask_mix_node.inputs[0], "default_value", text="", emboss=True)
                col.prop(mask_mix_node, "blend_type", text="")

class MATLAYER_OT_add_empty_layer_mask(Operator):
    bl_label = "Add Empty Layer Mask"
    bl_idname = "matlayer.add_empty_layer_mask"
    bl_description = "Adds an default image based node group mask with to the selected material layer and fills the image slot with a no image"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        add_layer_mask('EMPTY', self)
        return {'FINISHED'}

class MATLAYER_OT_add_black_layer_mask(Operator):
    bl_label = "Add Black Layer Mask"
    bl_idname = "matlayer.add_black_layer_mask"
    bl_description = "Adds an default image based node group mask with to the selected material layer and fills the image slot with a black image"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_layer_mask('BLACK', self)
        return {'FINISHED'}
    
class MATLAYER_OT_add_white_layer_mask(Operator):
    bl_label = "Add White Layer Mask"
    bl_idname = "matlayer.add_white_layer_mask"
    bl_description = "Adds an default image based node group mask with to the selected material layer and fills the image slot with a white image"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_layer_mask('WHITE', self)
        return {'FINISHED'}

class MATLAYER_OT_add_linear_gradient_mask(Operator):
    bl_label = "Add Linear Gradient Mask"
    bl_idname = "matlayer.add_linear_gradient_mask"
    bl_description = "Adds a non-destructive linear gradient mask to the selected material layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_layer_mask('LINEAR_GRADIENT', self)
        return {'FINISHED'}

class MATLAYER_OT_add_grunge_mask(Operator):
    bl_label = "Add Grunge Mask"
    bl_idname = "matlayer.add_grunge_mask"
    bl_description = "Adds a mask that simulates grunge / dirt to the selected material layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_layer_mask('GRUNGE', self)
        return {'FINISHED'}

class MATLAYER_OT_add_edge_wear_mask(Operator):
    bl_label = "Add Edge Wear Mask"
    bl_idname = "matlayer.add_edge_wear_mask"
    bl_description = "Adds a mask that simulates edge wear to the selected material layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_layer_mask('EDGE_WEAR', self)
        return {'FINISHED'}

class MATLAYER_OT_add_decal_mask(Operator):
    bl_label = "Add Decal Mask"
    bl_idname = "matlayer.add_decal_mask"
    bl_description = "Adds a mask with decal projection to the selected material layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_layer_mask('DECAL', self)
        return {'FINISHED'}

class MATLAYER_OT_move_layer_mask_up(Operator):
    bl_label = "Move Layer Mask Up"
    bl_idname = "matlayer.move_layer_mask_up"
    bl_description = "Moves the selected layer mask up on the mask stack"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        move_mask('UP', self)
        return {'FINISHED'}

class MATLAYER_OT_move_layer_mask_down(Operator):
    bl_label = "Move Layer Mask Down"
    bl_idname = "matlayer.move_layer_mask_down"
    bl_description = "Moves the selected layer mask down on the mask stack"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        move_mask('DOWN', self)
        return {'FINISHED'}

class MATLAYER_OT_duplicate_layer_mask(Operator):
    bl_label = "Duplicate Layer Mask"
    bl_idname = "matlayer.duplicate_layer_mask"
    bl_description = "Duplicates the selected mask"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        duplicate_mask(self)
        return {'FINISHED'}

class MATLAYER_OT_delete_layer_mask(Operator):
    bl_label = "Delete Layer Mask"
    bl_idname = "matlayer.delete_layer_mask"
    bl_description = "Deletes the selected mask from the selected material layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        delete_layer_mask(self)
        return {'FINISHED'}

class MATLAYER_OT_set_mask_projection_uv(Operator):
    bl_label = "Set Mask Projection UV"
    bl_idname = "matlayer.set_mask_projection_uv"
    bl_description = "Sets the projection mode for the selected mask to UV projection, which uses the UV layout of the object to project textures used on this material layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        output_channel = get_mask_output_channel()
        set_mask_projection_mode('UV')
        relink_image_mask_projection()
        set_mask_output_channel(output_channel)
        return {'FINISHED'}

class MATLAYER_OT_set_mask_projection_triplanar(Operator):
    bl_label = "Set Mask Projection Triplanar"
    bl_idname = "matlayer.set_mask_projection_triplanar"
    bl_description = "Sets the projection mode for the mask to triplanar projection which projects the textures onto the object from each axis. This projection method can be used to apply materials to objects without needing to manually blend seams"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        output_channel = get_mask_output_channel()
        set_mask_projection_mode('TRIPLANAR')
        relink_image_mask_projection()
        set_mask_output_channel(output_channel)
        return {'FINISHED'}

class MATLAYER_OT_set_mask_output_channel(Operator):
    bl_label = "Set Mask Output Channel"
    bl_idname = "matlayer.set_mask_output_channel"
    bl_description = "Sets the channel used for the mask to the specified value. This allows for the use of RGBA channel packed masks, and using image transparency as a mask"
    bl_options = {'REGISTER', 'UNDO'}

    channel_name: StringProperty(default='COLOR')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        set_mask_output_channel(self.channel_name)
        return {'FINISHED'}

class MATLAYER_OT_isolate_mask(Operator):
    bl_label = "Isolate Mask"
    bl_idname = "matlayer.isolate_mask"
    bl_description = "Isolates the specified mask. Select a material layer to de-isolate"
    bl_options = {'REGISTER', 'UNDO'}

    mask_index: IntProperty(default=-1)

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        if blender_addon_utils.verify_material_operation_context(self) == False:
            return

        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        selected_mask_index = bpy.context.scene.matlayer_mask_stack.selected_index
        active_node_tree = bpy.context.active_object.active_material.node_tree

        mask_node = get_mask_node('MASK', selected_layer_index, selected_mask_index)
        emission_node = active_node_tree.nodes.get('EMISSION')
        material_output = active_node_tree.nodes.get('MATERIAL_OUTPUT')

        blender_addon_utils.unlink_node(emission_node, active_node_tree, unlink_inputs=True, unlink_outputs=True)

        active_node_tree.links.new(mask_node.outputs[0], emission_node.inputs[0])
        active_node_tree.links.new(emission_node.outputs[0], material_output.inputs[0])

        return {'FINISHED'}

class MATLAYER_OT_toggle_mask_blur(Operator):
    bl_label = "Toggle Mask Blur"
    bl_idname = "matlayer.toggle_mask_blur"
    bl_description = "Toggles blurring for masks. Keep mask blur disabled when blurring is not beind used for improved shader compilation speed and viewport performance"
    bl_options = {'REGISTER', 'UNDO'}

    mask_index: IntProperty(default=-1)

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        if blender_addon_utils.verify_material_operation_context(self) == False:
            return
        
        # Toggle the blur node active state.
        selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
        selected_mask_index = bpy.context.scene.matlayer_mask_stack.selected_index
        blur_node = get_mask_node('BLUR', selected_layer_index, selected_mask_index)
        if blur_node:
            if blender_addon_utils.get_node_active(blur_node):
                blender_addon_utils.set_node_active(blur_node, False)
            else:
                blender_addon_utils.set_node_active(blur_node, True)

            # Relink projection.
            relink_image_mask_projection()
        else:
            debug_logging.log("Error: Toggling mask blur failed, blur node not found.")

        return {'FINISHED'}