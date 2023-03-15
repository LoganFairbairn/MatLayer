from bpy.types import Operator
from . import material_channel_nodes
from . import layer_nodes
from . import coater_materials
import random
from ..viewport_settings.viewport_setting_adjuster import set_material_shading

def add_layer_slot(context):
    '''Creates a layer slot.'''
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    # Add a new layer slot.
    layers.add()
    layers[len(layers) - 1].name = "Layer"

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

def add_default_layer_nodes(context):
    '''Adds default layer nodes for all layers.'''

    # Get the new layer index within the layer stack (which is added to the node names).
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    layers = context.scene.coater_layers
    new_layer_index = 0
    if len(layers) == 0:
        new_layer_index = 0
    else:
        new_layer_index = selected_layer_index

    # Add new nodes for all material channels.
    material_channels = material_channel_nodes.get_material_channel_list()
    for i in range(0, len(material_channels)):

        material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channels[i])
        
        # Verify that the material channel node exists.
        if material_channel_nodes.verify_material_channel(material_channel_node):

            new_nodes = []

            # Create default nodes all layers will have.
            opacity_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeMath')
            opacity_node.name = layer_nodes.get_layer_node_name("OPACITY", new_layer_index) + "~"
            opacity_node.label = opacity_node.name
            opacity_node.inputs[0].default_value = 1.0
            opacity_node.inputs[1].default_value = 1.0
            opacity_node.use_clamp = True
            opacity_node.operation = 'MULTIPLY'
            new_nodes.append(opacity_node)

            mix_layer_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeMixRGB')
            mix_layer_node.name = layer_nodes.get_layer_node_name("MIXLAYER", new_layer_index) + "~"
            mix_layer_node.label = mix_layer_node.name
            mix_layer_node.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0)
            mix_layer_node.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
            mix_layer_node.use_clamp = True
            new_nodes.append(mix_layer_node)

            coord_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeTexCoord')
            coord_node.name = layer_nodes.get_layer_node_name("COORD", new_layer_index) + "~"
            coord_node.label = coord_node.name
            new_nodes.append(coord_node)

            mapping_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeMapping')
            mapping_node.name = layer_nodes.get_layer_node_name("MAPPING", new_layer_index) + "~"
            mapping_node.label = mapping_node.name
            new_nodes.append(mapping_node)

            # Create nodes & set node settings specific to each material channel. *
            texture_node = None
            if material_channels[i] == "COLOR":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')
                texture_node.outputs[0].default_value = (0.25, 0.25, 0.25, 1.0)
                layers[selected_layer_index].color_layer_color_preview = (0.25, 0.25, 0.25)

            if material_channels[i] == "METALLIC":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeValue')
                texture_node.outputs[0].default_value = 0.0
                layers[selected_layer_index].metallic_layer_color_preview = (0, 0, 0)

            if material_channels[i] == "ROUGHNESS":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeValue')
                texture_node.outputs[0].default_value = 0.5
                layers[selected_layer_index].roughness_layer_color_preview = (0.5, 0.5, 0.5)

            if material_channels[i] == "NORMAL":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')
                texture_node.outputs[0].default_value = (0.5, 0.5, 1.0, 1.0)
                layers[selected_layer_index].normal_layer_color_preview = (0.5, 0.5, 1)
                
            if material_channels[i] == "HEIGHT":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeValue')
                texture_node.outputs[0].default_value = 0.0
                layers[selected_layer_index].height_layer_color_preview = (0, 0, 0)
                mix_layer_node.blend_type = 'DODGE'

            if material_channels[i] == "SCATTERING":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')
                texture_node.outputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
                layers[selected_layer_index].scattering_layer_color_preview = (1, 1, 1)

            if material_channels[i] == "EMISSION":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')
                texture_node.outputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
                layers[selected_layer_index].emission_layer_color_preview = (0, 0, 0)

            # Set the texture node name & label.
            texture_node_name = layer_nodes.get_layer_node_name("TEXTURE", new_layer_index) + "~"
            texture_node.name = texture_node_name
            texture_node.label = texture_node_name
            new_nodes.append(texture_node)

            # Link newly created nodes.
            link = material_channel_node.node_tree.links.new
            link(texture_node.outputs[0], mix_layer_node.inputs[2])
            link(opacity_node.outputs[0], mix_layer_node.inputs[0])
            link(coord_node.outputs[2], mapping_node.inputs[0])

            # Create a layer frame and frame layer nodes.
            frame = material_channel_node.node_tree.nodes.new(type='NodeFrame')
            frame.name = layer_nodes.get_frame_name(new_layer_index, context) + "~"
            frame.label = frame.name

            for n in new_nodes:
                n.parent = frame

        else:
            print("Error: Material channel node doesn't exist.")
            return

    # Update the layer nodes.
    layer_nodes.update_layer_nodes(context)

def move_layer(context, direction):
    '''Moves a layer up or down the layer stack.'''
    layers = context.scene.coater_layers
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    # Rename layer frame and nodes before the layer stack is moved.
    if direction == "DOWN":
        # Get the layer under the selected layer (if one exists).
        under_layer_index = max(min(selected_layer_index - 1, len(layers) - 1), 0)

        # Don't move the selected layer down if this is already the bottom layer.
        if selected_layer_index - 1 < 0:
            return
        
        # Add a tilda to the end of the layer frame that will be moved down and the layer nodes names for the selected layer.
        layer_node_names = layer_nodes.get_layer_node_names()

        material_channel_names = material_channel_nodes.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

            old_frame_name = layers[selected_layer_index].name + "_" + str(layers[selected_layer_index].id) + "_" + str(selected_layer_index)
            frame = material_channel_node.node_tree.nodes.get(old_frame_name)

            new_frame_name = old_frame_name + "~"
            frame.name = new_frame_name
            frame.label = frame.name

            for node_name in layer_node_names:
                node = layer_nodes.get_layer_node(node_name, material_channel, selected_layer_index, context)
                node.name = node.name + "~"
                node.label = node.name
        
        # Update the layer nodes for the layer below to have the selected layer index.
        material_channel_names = material_channel_nodes.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

            old_frame_name = layers[under_layer_index].name + "_" + str(layers[under_layer_index].id) + "_" + str(under_layer_index)
            frame = material_channel_node.node_tree.nodes.get(old_frame_name)

            new_frame_name = layers[under_layer_index].name + "_" + str(layers[under_layer_index].id) + "_" + str(selected_layer_index)
            frame.name = new_frame_name
            frame.label = frame.name

            # Update the cached layer frame name.
            layers[under_layer_index].cached_frame_name = frame.name

            for node_name in layer_node_names:
                node = layer_nodes.get_layer_node(node_name, material_channel, under_layer_index, context)
                layer_nodes.rename_layer_node(node, node_name, selected_layer_index)

        # Remove the tilda from the end of the layer frame and the layer node names for the selected layer and reduce their indicies by 1.
        material_channel_names = material_channel_nodes.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

            old_frame_name = layers[selected_layer_index].name + "_" + str(layers[selected_layer_index].id) + "_" + str(selected_layer_index) + "~"
            frame = material_channel_node.node_tree.nodes.get(old_frame_name)

            new_frame_name = layers[selected_layer_index].name + "_" + str(layers[selected_layer_index].id) + "_" + str(under_layer_index)
            frame.name = new_frame_name
            frame.label = frame.name

            # Update the cached layer frame name.
            layers[selected_layer_index].cached_frame_name = frame.name

            for node_name in layer_node_names:
                node = material_channel_node.node_tree.nodes.get(node_name + "_" + str(selected_layer_index) + "~")
                layer_nodes.rename_layer_node(node, node_name, under_layer_index)

        index_to_move_to = max(min(selected_layer_index - 1, len(layers) - 1), 0)
        layers.move(selected_layer_index, index_to_move_to)
        context.scene.coater_layer_stack.layer_index = index_to_move_to


    if direction == "UP":
        # Get the next layers index (if one exists).
        over_layer_index = max(min(selected_layer_index + 1, len(layers) - 1), 0)

        # Don't move the layer up if the selected layer is already the top layer.
        if selected_layer_index + 1 > len(layers) - 1:
            return


        # Add a tilda to the end of the layer frame and the layer nodes names for the selected layer.
        layer_node_names = layer_nodes.get_layer_node_names()

        material_channel_names = material_channel_nodes.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

            old_frame_name = layers[selected_layer_index].name + "_" + str(layers[selected_layer_index].id) + "_" + str(selected_layer_index)
            frame = material_channel_node.node_tree.nodes.get(old_frame_name)

            new_frame_name = old_frame_name + "~"
            frame.name = new_frame_name
            frame.label = frame.name

            for node_name in layer_node_names:
                node = layer_nodes.get_layer_node(node_name, material_channel, selected_layer_index, context)
                node.name = node.name + "~"
                node.label = node.name
        
        # Update the layer nodes for the layer below to have the selected layer index.
        material_channel_names = material_channel_nodes.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

            old_frame_name = layers[over_layer_index].name + "_" + str(layers[over_layer_index].id) + "_" + str(over_layer_index)
            frame = material_channel_node.node_tree.nodes.get(old_frame_name)

            new_frame_name = layers[over_layer_index].name + "_" + str(layers[over_layer_index].id) + "_" + str(selected_layer_index)
            frame.name = new_frame_name
            frame.label = frame.name

            # Update the cached layer frame name.
            layers[over_layer_index].cached_frame_name = frame.name

            for node_name in layer_node_names:
                node = layer_nodes.get_layer_node(node_name, material_channel, over_layer_index, context)
                layer_nodes.rename_layer_node(node, node_name, selected_layer_index)

        # Remove the tilda from the end of the layer frame and the layer node names for the selected layer and reduce their indicies by 1.
        material_channel_names = material_channel_nodes.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)

            old_frame_name = layers[selected_layer_index].name + "_" + str(layers[selected_layer_index].id) + "_" + str(selected_layer_index) + "~"
            frame = material_channel_node.node_tree.nodes.get(old_frame_name)

            new_frame_name = layers[selected_layer_index].name + "_" + str(layers[selected_layer_index].id) + "_" + str(over_layer_index)
            frame.name = new_frame_name
            frame.label = frame.name

            # Update the cached layer frame name.
            layers[selected_layer_index].cached_frame_name = frame.name

            for node_name in layer_node_names:
                node = material_channel_node.node_tree.nodes.get(node_name + "_" + str(selected_layer_index) + "~")
                layer_nodes.rename_layer_node(node, node_name, over_layer_index)


        # Move the layer in the layer stack. 
        index_to_move_to = max(min(selected_layer_index + 1, len(layers) - 1), 0)
        layers.move(selected_layer_index, index_to_move_to)
        context.scene.coater_layer_stack.layer_index = index_to_move_to

    # Update the layer nodes.
    layer_nodes.update_layer_nodes(context)

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

        # Add a layer slot within the layer stack.
        add_layer_slot(context)

        # Add default layer nodes.
        add_default_layer_nodes(context)

        # Set the viewport to material shading mode.
        set_material_shading(context)

        return {'FINISHED'}

class COATER_OT_move_layer_up(Operator):
    """Moves the selected layer up on the layer stack."""
    bl_idname = "coater.move_layer_up"
    bl_label = "Move Layer Up"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the currently selected layer"

    # Poll tests if the operator can be called or not.
    @ classmethod
    def poll(cls, context):
        return context.scene.coater_layers

    def execute(self, context):
        move_layer(context, "UP")
        return{'FINISHED'}

class COATER_OT_move_layer_down(Operator):
    """Moves the selected layer down the layer stack."""
    bl_idname = "coater.move_layer_down"
    bl_label = "Move Layer Down"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the currently selected layer"
    
    # Poll tests if the operator can be called or not.
    @ classmethod
    def poll(cls, context):
        return context.scene.coater_layers

    def execute(self, context):
        move_layer(context, "DOWN")
        return{'FINISHED'}

class COATER_OT_delete_layer(Operator):
    '''Deletes the selected layer from the layer stack.'''
    bl_idname = "coater.delete_layer"
    bl_label = "Delete Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the currently selected layer"

    @ classmethod
    def poll(cls, context):
        return context.scene.coater_layers

    def execute(self, context):
        layers = context.scene.coater_layers
        selected_layer_index = context.scene.coater_layer_stack.layer_index

        # Remove all nodes for all material channels.
        material_channel_list = material_channel_nodes.get_material_channel_list()
        for material_channel_name in material_channel_list:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)

            # Remove layer frame.
            frame = layer_nodes.get_layer_frame(material_channel_name, selected_layer_index, context)
            if frame != None:
                material_channel_node.node_tree.nodes.remove(frame)

            # Removed layer nodes.
            node_list = layer_nodes.get_all_nodes_in_layer(material_channel_name, selected_layer_index, context)
            for node in node_list:
                material_channel_node.node_tree.nodes.remove(node)

        # Remove the layer slot from the layer stack.
        layers.remove(selected_layer_index)

        # Reset the layer stack index while keeping it within range of existing indicies in the layer stack.
        context.scene.coater_layer_stack.layer_index = max(min(selected_layer_index - 1, len(layers) - 1), 0)

        # Update the layer nodes.
        layer_nodes.update_layer_nodes(context)


        return {'FINISHED'}

class COATER_OT_duplicate_layer(Operator):
    """Duplicates the selected layer."""
    bl_idname = "coater.duplicate_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Duplicates the selected layer"

    @ classmethod
    def poll(cls, context):
        #return context.scene.coater_layers
        return None

    def execute(self, context):
        layers = context.scene.coater_layers
        selected_layer_index = context.scene.coater_layer_stack.layer_index

        original_layer_index = selected_layer_index

        # Duplicate layer information into a new layer.

        # TODO: Create general nodes for the duplicated layer.

        # TODO: Add texture node for the duplicated layer based on the layer being copied.

        # TODO: Copy all the settings from the original layer.

        # TODO: Update layer nodes indicies.

        return{'FINISHED'}
    
class COATER_OT_bake_layer(Operator):
    '''Bakes the selected layer to an image layer.'''
    bl_idname = "coater.bake_layer"
    bl_label = "Bake Layer"
    bl_description = "Bakes the selected layer to an image layer"

    @ classmethod
    def poll(cls, context):
        return False

    def execute(self, context):
        # TODO: Turn off all layers excluding the selected one.

        # TODO: Create an image to bake to.

        # TODO: Create an image layer and add the image to it.
        return {'FINISHED'}

class COATER_OT_merge_layer(Operator):
    """Merges the selected layer with the layer below."""
    bl_idname = "coater.merge_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Merges the selected layer with the layer below."

    @ classmethod
    def poll(cls, context):
        #return context.scene.coater_layers
        return False

    def execute(self, context):
        return{'FINISHED'}

class COATER_OT_read_layer_nodes(Operator):
    bl_idname = "coater.read_layer_nodes"
    bl_label = "Read Layer Nodes"
    bl_description = "Reads the material nodes in the active material and updates the layer stack with that"

    def execute(self, context):
        # Make sure the active material is a Coater material before attempting to refresh the layer stack.
        if coater_materials.verify_material(context) == False:
            self.report({'ERROR'}, "Material is not a Coater material, can't read layer stack.")
            return {'FINISHED'}

        # TODO: Read the layer stack nodes and update values.

        # Update layer nodes.
        layer_nodes.update_layer_nodes(context)

        return {'FINISHED'}
