import bpy
from bpy.types import Operator
from bpy.props import BoolProperty
from . import material_channels
from ..core import layer_nodes
from . import matlay_materials
from ..utilities.viewport_setting_adjuster import set_material_shading
from ..utilities import info_messages
import random

def add_layer_slot(context):
    '''Creates a layer slot.'''
    layers = context.scene.matlay_layers
    layer_stack = context.scene.matlay_layer_stack
    selected_layer_index = context.scene.matlay_layer_stack.layer_index

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
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    layers = context.scene.matlay_layers
    new_layer_index = 0
    if len(layers) == 0:
        new_layer_index = 0
    else:
        new_layer_index = selected_layer_index

    # Add new nodes for all material channels.
    material_channel_list = material_channels.get_material_channel_list()
    for i in range(0, len(material_channel_list)):

        material_channel_node = material_channels.get_material_channel_node(context, material_channel_list[i])
        
        # Verify that the material channel node exists.
        if material_channels.verify_material_channel(material_channel_node):

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
            if material_channel_list[i] == "COLOR":
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
                layers[selected_layer_index].roughness_layer_color_preview = (0.5, 0.5, 0.5)

            if material_channel_list[i] == "NORMAL":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')
                texture_node.outputs[0].default_value = (0.5, 0.5, 1.0, 1.0)
                mix_layer_node.inputs[1].default_value = (0.5, 0.5, 1.0, 1.0)
                
            if material_channel_list[i] == "HEIGHT":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeValue')
                texture_node.outputs[0].default_value = 0.0
                mix_layer_node.blend_type = 'MIX'

            if material_channel_list[i] == "EMISSION":
                texture_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeRGB')
                texture_node.outputs[0].default_value = (0.0, 0.0, 0.0, 1.0)

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
    layers = context.scene.matlay_layers
    selected_layer_index = context.scene.matlay_layer_stack.layer_index

    # Rename layer frame and nodes before the layer stack is moved.
    if direction == "DOWN":
        # Get the layer under the selected layer (if one exists).
        under_layer_index = max(min(selected_layer_index - 1, len(layers) - 1), 0)

        # Don't move the selected layer down if this is already the bottom layer.
        if selected_layer_index - 1 < 0:
            return
        
        # Add a tilda to the end of the layer frame that will be moved down and the layer nodes names for the selected layer.
        layer_node_names = layer_nodes.get_layer_node_names()

        material_channel_names = material_channels.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channels.get_material_channel_node(context, material_channel)

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
        material_channel_names = material_channels.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channels.get_material_channel_node(context, material_channel)

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
        material_channel_names = material_channels.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channels.get_material_channel_node(context, material_channel)

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
        context.scene.matlay_layer_stack.layer_index = index_to_move_to


    if direction == "UP":
        # Get the next layers index (if one exists).
        over_layer_index = max(min(selected_layer_index + 1, len(layers) - 1), 0)

        # Don't move the layer up if the selected layer is already the top layer.
        if selected_layer_index + 1 > len(layers) - 1:
            return


        # Add a tilda to the end of the layer frame and the layer nodes names for the selected layer.
        layer_node_names = layer_nodes.get_layer_node_names()

        material_channel_names = material_channels.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channels.get_material_channel_node(context, material_channel)

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
        material_channel_names = material_channels.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channels.get_material_channel_node(context, material_channel)

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
        material_channel_names = material_channels.get_material_channel_list()
        for material_channel in material_channel_names:
            material_channel_node = material_channels.get_material_channel_node(context, material_channel)

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
        context.scene.matlay_layer_stack.layer_index = index_to_move_to

    # Update the layer nodes.
    layer_nodes.update_layer_nodes(context)

class MATLAY_OT_add_layer(Operator):
    '''Adds a layer with default numeric material values to the layer stack'''
    bl_idname = "matlay.add_layer"
    bl_label = "Add Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds a layer with default numeric material values to the layer stack"

    def execute(self, context):
        matlay_materials.prepare_material(context)
        material_channels.create_channel_group_nodes(context)
        material_channels.create_empty_group_node(context)
        add_layer_slot(context)
        add_default_layer_nodes(context)
        set_material_shading(context)       # Set the viewport to material shading mode (so users can see the applied material).
        return {'FINISHED'}

class MATLAY_OT_move_layer_up(Operator):
    """Moves the selected layer up on the layer stack."""
    bl_idname = "matlay.move_layer_up"
    bl_label = "Move Layer Up"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the currently selected layer"

    # Poll tests if the operator can be called or not.
    @ classmethod
    def poll(cls, context):
        return context.scene.matlay_layers

    def execute(self, context):
        move_layer(context, "UP")
        return{'FINISHED'}

class MATLAY_OT_move_layer_down(Operator):
    """Moves the selected layer down the layer stack."""
    bl_idname = "matlay.move_layer_down"
    bl_label = "Move Layer Down"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the currently selected layer"
    
    # Poll tests if the operator can be called or not.
    @ classmethod
    def poll(cls, context):
        return context.scene.matlay_layers

    def execute(self, context):
        move_layer(context, "DOWN")
        return{'FINISHED'}

class MATLAY_OT_delete_layer(Operator):
    '''Deletes the selected layer from the layer stack.'''
    bl_idname = "matlay.delete_layer"
    bl_label = "Delete Layer"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the currently selected layer"

    @ classmethod
    def poll(cls, context):
        return context.scene.matlay_layers

    def execute(self, context):
        layers = context.scene.matlay_layers
        selected_layer_index = context.scene.matlay_layer_stack.layer_index

        # Remove all nodes for all material channels.
        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)

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
        context.scene.matlay_layer_stack.layer_index = max(min(selected_layer_index - 1, len(layers) - 1), 0)

        # Update the layer nodes.
        layer_nodes.update_layer_nodes(context)


        return {'FINISHED'}

class MATLAY_OT_duplicate_layer(Operator):
    """Duplicates the selected layer."""
    bl_idname = "matlay.duplicate_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Duplicates the selected layer"

    @ classmethod
    def poll(cls, context):
        #return context.scene.matlay_layers
        return None

    def execute(self, context):
        layers = context.scene.matlay_layers
        selected_layer_index = context.scene.matlay_layer_stack.layer_index

        original_layer_index = selected_layer_index

        # Duplicate layer information into a new layer.

        # TODO: Create general nodes for the duplicated layer.

        # TODO: Add texture node for the duplicated layer based on the layer being copied.

        # TODO: Copy all the settings from the original layer.

        # TODO: Update layer nodes indicies.

        return{'FINISHED'}
    
class MATLAY_OT_bake_layer(Operator):
    '''Bakes the selected layer to an image layer.'''
    bl_idname = "matlay.bake_layer"
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

class MATLAY_OT_merge_layer(Operator):
    """Merges the selected layer with the layer below."""
    bl_idname = "matlay.merge_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Merges the selected layer with the layer below."

    @ classmethod
    def poll(cls, context):
        #return context.scene.matlay_layers
        return False

    def execute(self, context):
        return{'FINISHED'}

class MATLAY_OT_image_editor_export(Operator):
    '''Exports the selected image paint canvas to the image editor defined in Blender's preferences'''
    bl_idname = "matlay.image_editor_export"
    bl_label = "Export to External Image Editor"
    bl_description = "Exports the select image layer to the image editor defined in Blender's preferences"

    @ classmethod
    def poll(cls, context):
        return context.scene.matlay_layers
        False

    def execute(self, context):
        export_image = context.scene.tool_settings.image_paint.canvas

        if export_image != None:
            if export_image.packed_file == None:
                if export_image.file_format == '' or export_image.filepath == '':
                    if export_image.is_dirty:
                        export_image.save()
                else:
                    self.report({'ERROR'}, "Export image has no defined filepath.")
            else:
                self.report({'ERROR'}, "Export image can't be packed to export to an external image editor.")
            #bpy.ops.image.external_edit(filepath=export_image.filepath)

        return {'FINISHED'}

#----------------------------- READING / REFRESHING LAYER PROPERTIES -----------------------------#

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

def read_texture_node_values(material_channel_list, total_number_of_layers, layers, context):
    '''Updates texture node values stored in layers by reading the material node trees.'''
    for material_channel_name in material_channel_list:
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
        if material_channel_node:
            for i in range(total_number_of_layers):
                texture_node = layer_nodes.get_layer_node('TEXTURE', material_channel_name, i, context)
                if not texture_node:
                    info_messages.popup_message_box("Error reading texture node.", "Reading Node Error", 'ERROR')
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

def read_layer_projection_values(selected_layer, selected_layer_index, context):
    '''Update the projection values in the user interface for the selected layer.'''
    # Using the color material channel as the projection is the same among all material channels.
    material_channel_name = 'COLOR'
    material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
    if material_channel_node:
        # Update offset, rotation and scale values.
        mapping_node = layer_nodes.get_layer_node('MAPPING', material_channel_name, selected_layer_index, context)
        if mapping_node:
            selected_layer.projection.projection_offset_x = mapping_node.inputs[1].default_value[0]
            selected_layer.projection.projection_offset_y = mapping_node.inputs[1].default_value[1]
            selected_layer.projection.projection_rotation = mapping_node.inputs[2].default_value[2]
            selected_layer.projection.projection_scale_x = mapping_node.inputs[3].default_value[0]
            selected_layer.projection.projection_scale_y = mapping_node.inputs[3].default_value[1]
            if selected_layer.projection.projection_scale_x != selected_layer.projection.projection_scale_y:
                selected_layer.projection.match_layer_scale = False

        # Update the projection values specific to image texture projection.
        texture_node = layer_nodes.get_layer_node('TEXTURE', material_channel_name, selected_layer_index, context)
        if texture_node and texture_node.type == 'TEX_IMAGE':
            selected_layer.projection.projection_blend = texture_node.projection_blend
            selected_layer.projection.texture_extension = texture_node.extension
            selected_layer.projection.texture_interpolation = texture_node.interpolation
            selected_layer.projection.projection_mode = texture_node.projection
        else:
            selected_layer.projection.projection_mode = 'FLAT'
    else:
        info_messages.popup_message_box("Missing " + material_channel_name + " group node.", "Material Stack Corrupted", 'ERROR')

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

class MATLAY_OT_refresh_layer_nodes(Operator):
    bl_idname = "matlay.refresh_layer_nodes"
    bl_label = "Refresh Layer Nodes"
    bl_description = "Refreshes the material nodes by reading the material nodes in the active material updating the properties stored within the user interface"

    auto_called: BoolProperty(name="Auto Called", description="Should be true if refreshing layers was automatically called (i.e selecting a different object automatically refreshes the layer stack). This is used to avoid printing errors.", default=False)

    def execute(self, context):
        # Only read the layer stack for materials made with this add-on. 
        # Materials must follow a strict format to be able to be properly read, making materials not made with this add-on incompatible.
        if matlay_materials.verify_material(context) == False:
            if self.auto_called == False:
                self.report({'ERROR'}, "Material is not a MatLay material, can't read / refresh the layer stack.")
            return {'FINISHED'}
        
        # Remember the selected layer index before clearing the layer stack.
        original_selected_layer_index = context.scene.matlay_layer_stack.layer_index

        # Clear the layer stack.
        layers = context.scene.matlay_layers
        layers.clear()

        total_number_of_layers = layer_nodes.get_total_number_of_layers(context)
        material_channel_list = material_channels.get_material_channel_list()
        selected_material_channel = context.scene.matlay_layer_stack.selected_material_channel

        # After reading the layer stack, the number of layers may be different, reset the selected layer index if required.
        if total_number_of_layers >= original_selected_layer_index:
            selected_layer_index = original_selected_layer_index
        else:
            selected_layer_index = 0

        # Turn auto updating for layer properties off.
        # This is to avoid node types from automatically being replaced when the node type is updated as doing so can cause errors when reading values (likely due to blender parameter update functions not being thread safe).
        context.scene.matlay_layer_stack.auto_update_layer_properties = False

        read_layer_name_and_id(layers, context)
        read_layer_opacity(total_number_of_layers, layers, selected_material_channel, context)
        read_texture_node_values(material_channel_list, total_number_of_layers, layers, context)
        read_layer_projection_values(layers[selected_layer_index], selected_layer_index, context)
        read_globally_active_material_channels(context)
        read_hidden_layers(total_number_of_layers, layers, material_channel_list, context)
        read_active_layer_material_channels(material_channel_list, total_number_of_layers, layers, context)
        #layer_nodes.organize_all_matlay_materials(context)

        context.scene.matlay_layer_stack.auto_update_layer_properties = True

        self.report({'INFO'}, "Refreshed layer stack.")

        return {'FINISHED'}
