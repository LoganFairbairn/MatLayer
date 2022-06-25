import bpy
from bpy.types import Operator

from ..nodes import layer_nodes
from ..nodes import material_channel_nodes
from ..nodes import update_layer_nodes
from ..layer_stack import add_layer_slot
from ..nodes import coater_materials
from ...viewport_settings import viewport_setting_adjuster

class COATER_OT_add_layer(Operator):
    '''Adds a layer with default numeric material values to the layer stack'''
    bl_idname = "coater.add_layer"
    bl_label = "Add Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds a layer with default numeric material values to the layer stack"

    def execute(self, context):
        # Prepare the material.
        coater_materials.prepare_material(context)
        material_channel_nodes.create_channel_group_nodes(context)

        # Add a layer slot and layer nodes.
        add_layer_slot.add_layer_slot(context)

        # Add default layer nodes.
        add_default_layer_nodes_new(context)

        # Set the viewport to material shading mode.
        viewport_setting_adjuster.set_material_shading(context)

        return {'FINISHED'}





def add_default_layer_nodes_new(context):
    '''Adds default layer nodes for all layers.'''

    # Update the new layers index within the layer stack (which is added to the node names).
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.selected_layer_index

    # Update the layer node indicies.
    update_layer_nodes.update_layer_indicies(context)


    # TODO: Add new nodes for all material channels.
    material_channels = material_channel_nodes.get_material_channel_list()
    for i in range(0, len(material_channels)):
        # Verify the material channel exists.
        material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channels[i])
        if material_channel_nodes.verify_material_channel(material_channel_node):

            # Create default nodes all layers will have.
            opacity_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeMath')
            mix_layer_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeMixRGB')
            coord_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeTexCoord')
            mapping_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeMapping')

            opacity_node.name = "OPACITY_"
            opacity_node.label = opacity_node.name
            layers[selected_layer_index].opacity_node_name = opacity_node.name
            
            mix_layer_node.name = "MIXLAYER_"
            mix_layer_node.label = mix_layer_node.name
            layers[selected_layer_index].mix_layer_node_name = mix_layer_node.name

            coord_node.name = "COORD_"
            coord_node.label = coord_node.name
            layers[selected_layer_index].coord_node_name = coord_node.name

            mapping_node.name = "MAPPING_"
            mapping_node.label = mapping_node.name
            layers[selected_layer_index].mapping_node_name = mapping_node.name

            opacity_node.inputs[0].default_value = 1.0
            opacity_node.inputs[1].default_value = 1.0
            opacity_node.use_clamp = True
            opacity_node.operation = 'MULTIPLY'
            mix_layer_node.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0)
            mix_layer_node.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
            mix_layer_node.use_clamp = True


            

            
            
            
            





            # Create nodes & set node settings specific to each material channel. *
            texture_node = None
            if material_channels[i] == "COLOR":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')
                texture_node.outputs[0].default_value = (0.25, 0.25, 0.25, 1.0)

            if material_channels[i] == "METALLIC":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeValue')
                texture_node.outputs[0].default_value = 0.0

            if material_channels[i] == "ROUGHNESS":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeValue')
                texture_node.outputs[0].default_value = 0.5

            if material_channels[i] == "NORMAL":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')
                texture_node.outputs[0].default_value = (0.0, 0.0, 1.0, 1.0)
                
            if material_channels[i] == "HEIGHT":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeValue')
                texture_node.outputs[0].default_value = 0.0
                mix_layer_node.blend_type = 'DODGE'

            if material_channels[i] == "SCATTERING":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')
                texture_node.outputs[0].default_value = (0.0, 0.0, 0.0, 1.0)

            if material_channels[i] == "EMISSION":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')
                texture_node.outputs[0].default_value = (0.0, 0.0, 0.0, 1.0)


            # Set the texture node name & label.
            texture_node_name = "TEXTURE_"
            texture_node.name = texture_node_name
            texture_node.label = texture_node_name
            layers[selected_layer_index].texture_node_name = texture_node_name
            

            # Link newly created nodes.
            link = material_channel_node.node_tree.links.new
            link(texture_node.outputs[0], mix_layer_node.inputs[2])
            link(opacity_node.outputs[0], mix_layer_node.inputs[0])
            link(coord_node.outputs[2], mapping_node.inputs[0])


            # Frame new nodes.
            frame = material_channel_node.node_tree.nodes.new(type='NodeFrame')
            frame.name = "New Layer Frame"
            frame.label = frame.name
            layers[selected_layer_index].frame_name = frame.name


            # Frame all the nodes in the given layer in the newly created frame.
            nodes = layer_nodes.get_all_nodes_in_layer(material_channel_node, layers, selected_layer_index)
            for n in nodes:
                n.parent = frame


            # TODO: Mute layer nodes for inactive channels.



            # Update the layer nodes.
            update_layer_nodes.update_layer_node_indicies(material_channels[i], context)
            update_layer_nodes.update_layer_node_indicies(material_channels[i], context)

            # Organize all layer nodes.
            update_layer_nodes.organize_material_channel_nodes(context)
            update_layer_nodes.organize_layer_nodes_in_material_channel(material_channels[i], context)

            # Link all layers.
            update_layer_nodes.link_layers_in_material_channel(material_channels[i], context)

        else:
            print("Error: Material channel node doesn't exist.")
            return