import bpy
from bpy.types import Operator
from .import coater_node_info
from .import update_node_labels
from .import link_layers
from .import organize_layer_nodes

class COATER_OT_add_image_mask(Operator):
    '''Adds an image mask to the selected layer'''
    bl_idname = "coater.add_image_mask"
    bl_label = "Add Image Mask"
    bl_description = "Adds an image mask to the selected layer"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        # Create mask nodes.
        channel_node = coater_node_info.get_channel_node_group(context)

        if channel_node != None:
            mask_node = channel_node.nodes.new('ShaderNodeTexImage')
            mask_mix_node = channel_node.nodes.new('ShaderNodeMixRGB')
            mask_coord_node = channel_node.nodes.new(type='ShaderNodeTexCoord')
            mask_mapping_node = channel_node.nodes.new(type='ShaderNodeMapping')
            mask_levels_node = channel_node.nodes.new(type='ShaderNodeValToRGB')

            # Store mask nodes.
            layers[layer_index].mask_node_name = mask_node.name
            layers[layer_index].mask_mix_node_name = mask_mix_node.name
            layers[layer_index].mask_coord_node_name = mask_coord_node.name
            layers[layer_index].mask_mapping_node_name = mask_mapping_node.name
            layers[layer_index].mask_levels_node_name = mask_levels_node.name

            # Link new nodes.
            channel_node.links.new(mask_coord_node.outputs[2], mask_mapping_node.inputs[0])
            channel_node.links.new(mask_mapping_node.outputs[0], mask_node.inputs[0])
            channel_node.links.new(mask_node.outputs[0], mask_levels_node.inputs[0])
            channel_node.links.new(mask_levels_node.outputs[0], mask_mix_node.inputs[0])

            # Link mix layer node to the mix mask node.
            mix_layer_node = channel_node.nodes.get(layers[layer_index].mix_layer_node_name)
            channel_node.links.new(mix_layer_node.outputs[0], mask_mix_node.inputs[2])

            update_node_labels.update_node_labels(context)
            organize_layer_nodes.organize_layer_nodes(context)
            link_layers.link_layers(context)

            # Add the nodes to the frame.
            frame = channel_node.nodes.get(layers[layer_index].frame_name)
            if frame != None:
                mask_node.parent = frame
                mask_mix_node.parent = frame
                mask_coord_node.parent = frame
                mask_mapping_node.parent = frame
                mask_levels_node.parent = frame

        return{'FINISHED'}

class COATER_OT_delete_layer_mask(Operator):
    bl_idname = "coater.delete_layer_mask"
    bl_label = "Delete Layer Mask"
    bl_description = "Deletes the mask for the selected layer if one exists"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        channel_node_group = coater_node_info.get_channel_node_group(context)

        # Delete mask nodes for the selected layer if they exist.
        mask_node = channel_node_group.nodes.get(layers[layer_index].mask_node_name)
        if mask_node != None:
            channel_node_group.nodes.remove(mask_node)

        mask_mix_node = channel_node_group.nodes.get(layers[layer_index].mask_mix_node_name)
        if mask_mix_node != None:
            channel_node_group.nodes.remove(mask_mix_node)

        mask_coord_node = channel_node_group.nodes.get(layers[layer_index].mask_coord_node_name)
        if mask_coord_node != None:
            channel_node_group.nodes.remove(mask_coord_node)

        mask_mapping_node = channel_node_group.nodes.get(layers[layer_index].mask_mapping_node_name)
        if mask_mapping_node != None:
            channel_node_group.nodes.remove(mask_mapping_node)

        mask_levels_node = channel_node_group.nodes.get(layers[layer_index].mask_levels_node_name)
        if mask_levels_node != None:
            channel_node_group.nodes.remove(mask_levels_node)

        # Clear mask node names.
        layers[layer_index].mask_node_name = ""
        layers[layer_index].mask_mix_node_name = ""
        layers[layer_index].mask_coord_node_name = ""
        layers[layer_index].mask_mapping_node_name = ""
        layers[layer_index].mask_levels_node_name = ""

        # Relink nodes.
        link_layers.link_layers(context)

        return{'FINISHED'}