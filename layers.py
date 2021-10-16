# Copyright (c) 2021 Logan Fairbairn
# logan-fairbairn@outlook.com
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# All layer functionality is handled here.

import bpy

# When a property in the Coater UI is changed, these functions are triggered and their respective properties are updated.
# Updates the RGBA color of a color layer.
def update_layer_color(self, context):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    layer_index = context.scene.coater_layer_stack.layer_index
    active_material = context.active_object.active_material

    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)

    color = layers[layer_index].color

    color_node = node_group.nodes.get(layers[layer_index].color_node_name)
    if color_node != None:
        color_node.outputs[0].default_value = (color[0], color[1], color[2], 1.0)

# Updates the layer opacity
def update_layer_opactity(self, context):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    layer_index = context.scene.coater_layer_stack.layer_index
    active_material = context.active_object.active_material

    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)

    opacity = layers[layer_index].layer_opacity

    opacity_node = node_group.nodes.get(layers[layer_index].opacity_node_name)
    if opacity_node != None:
        opacity_node.inputs[1].default_value = opacity

# Updates the layer channel.
def update_layer_channel(self, context):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    print("Channel: " + layer_stack.channel)

    # Clear all layers.
    layers.clear()

    # TODO: If there is nodes in the new layer channel group, re-build the layer stack by reading the node label's.
    node_group = get_current_group_node(self, context)

    if node_group != None:
        # Get the total number of layers.
        total_layers = 0
        for x in range(0, 100):
            node = node_group.nodes.get("MixLayer_" + str(x))
            if(node != None):
                total_layers += 1
            else:
                break
        print("Total Layers: " + str(total_layers))

        # Rebuild each layer in the layer stack.
        for l in range(0, int(total_layers)):

            # Add a layer slot.
            add_layer_slot(self, context)

            # Get nodes using their names
            node = node_group.nodes.get("Color_" + str(l))

# Properties for the layer stack are stored here.
class COATER_layer_stack(bpy.types.PropertyGroup):
    layer_index: bpy.props.IntProperty(default=-1)
    
    channel: bpy.props.EnumProperty(
        items=[('BASE_COLOR', "Base Color", "Set to show all layers for the base color channel"),
               ('ROUGHNESS', "Roughness", "Set to show all layers in the roughness channel"),
               ('METALLIC', "Metallic", "Set to show all layers in the metallic channel"),
               ('HEIGHT', "Height", "Set to show all layers in the height channel")],
        name="",
        description="Type of the layer",
        default=None,
        options={'HIDDEN'},
        update=update_layer_channel
    )

    channel_preview: bpy.props.BoolProperty(name="", default=False)
    node_default_width: bpy.props.IntProperty(default=200)
    node_spacing: bpy.props.IntProperty(default=50)

# Individual layer properties are stored here.
class COATER_layers(bpy.types.PropertyGroup):
    '''Layer stack item.'''
    layer_name: bpy.props.StringProperty(
        name="",
        description="The name of the layer",
        default="Layer naming error")

    layer_type: bpy.props.EnumProperty(
        items=[('COLOR_LAYER', "", ""),
               ('IMAGE_LAYER', "", "")],
        name="",
        description="Type of the layer",
        default=None,
        options={'HIDDEN'}
    )

    blending_mode: bpy.props.EnumProperty(
        items=[('NORMAL', "Normal", "Set this layer's blending mode to normal (mix)"),
               ('DARKEN', "Darken","Set this layer's blending mode to darken"),
               ('MULTIPLY', "Multiply", "Set this layer's blending mode to multiply"),
               ('COLOR_BURN', "Color Burn", "Set this layer's blending mode to color burn"),
               ('LIGHTEN', "Lighten", "Set this layer's blending mode to lighten"),
               ('SCREEN', "Screen", "Set this layer's blending mode to screen"),
               ('COLOR_DODGE', "Color Dodge", "Set this layer's blending mode to Color Dodge"),
               ('ADD', "Add", "Set this layer's blending mode to add"),
               ('OVERLAY', "Overlay", "Set this layer's blending mode to overlay"),
               ('SOFT_LIGHT', "Soft Light", "Set this layer's blending mode to softlight"),
               ('LINEAR_LIGHT', "Linear Light", "Set this layer's blending mode to linear light"),
               ('DIFFERENCE', "Difference", "Set this layer's blending mode to difference"),
               ('SUBTRACT', "Subtract", "Set this layer's blending mode to subtract"),
               ('DIVIDE', "Divide", "Set this layer's blending mode to divide"),
               ('HUE', "Hue", "Set this layer's blending mode to hue"),
               ('SATURATION', "Saturation", "Set this layers blending mode to saturation"),
               ('COLOR', "Color", "Set this layer's blending mode to color"),
               ('VALUE', "Value", "Set this layer's blending mode to value")],
        name="",
        description="Blending mode of the layer.",
        default=None,
        options={'HIDDEN'}
    )

    layer_hidden: bpy.props.BoolProperty(name="")
    masked: bpy.props.BoolProperty(name="", default=True)

    layer_opacity: bpy.props.FloatProperty(name="Opacity",
                                           description="Opacity of the currently selected layer.",
                                           default=1.0,
                                           min=0.0,
                                           max=1.0,
                                           subtype='FACTOR',
                                           update=update_layer_opactity)

    color: bpy.props.FloatVectorProperty(name="", subtype='COLOR_GAMMA', min=0.0, max=1.0, update=update_layer_color)

    # Store nodes using their names.
    color_node_name: bpy.props.StringProperty(default="")
    opacity_node_name: bpy.props.StringProperty(default="")
    mix_layer_node_name: bpy.props.StringProperty(default="")
    mask_node_name: bpy.props.StringProperty(default="")
    mix_mask_node_name: bpy.props.StringProperty(default="")
    node_frame_name: bpy.props.StringProperty(default="")

# Draws the layer stack.
class COATER_UL_layer_list(bpy.types.UIList):
    '''Draws the layer stack.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align = True)
            # Draw the layer hide icon.
            if item.layer_hidden == True:
                row.prop(item, "layer_hidden", text="", emboss=False, icon='HIDE_ON')

            elif item.layer_hidden == False:
                row.prop(item, "layer_hidden", text="", emboss=False, icon='HIDE_OFF')
            
            # Draw the layer's type.
            row = layout.row()
            if item.layer_type == "COLOR_LAYER":
                row.prop(item, "color", expand=False)
            row.scale_x = 0.2

            # TODO: If the layer is masked, draw a mask icon.

            # Draw the layer's name.
            row = layout.row()
            row.prop(item, "layer_name", text="", emboss=False, icon_value=icon)

            # Draw the layer's blending mode and opacity.
            row = layout.row()
            split = layout.split()
            col = split.column()
            col.prop(item, "blending_mode")
            col.prop(item, "layer_opacity")
            col.scale_y = 0.5

# Adds a color layer to the layer stack.
class COATER_OT_add_layer(bpy.types.Operator):
    '''Adds a new layer to the layer stack'''
    bl_idname = "coater.add_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds a new color layer"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.active_object

    # Makes sure that the material is ready for layer nodes to be added.
    def ready_material(self, context):
        active_object = context.active_object
        active_material = context.active_object.active_material

        # Add a new Coater material if there is none.
        if active_object != None:
            if active_material == None:
                new_material = bpy.data.materials.new(name=active_object.name)
                active_object.data.materials.append(new_material)

                # The active material MUST use nodes.
                new_material.use_nodes = True

                # Organize the principled BSDF nodes.
                material_nodes = context.active_object.active_material.node_tree.nodes
                principled_bsdf_node = material_nodes.get('Principled BSDF')
                material_output_node = material_nodes.get('Material Output')

                # Reset the label of the Principled BSDF node to allow this material to be identified as a Coater material.
                principled_bsdf_node.label = "Coater PBR"

                node_spacing = context.scene.coater_layer_stack.node_spacing
                principled_bsdf_node.location = (0.0, 0.0)
                material_output_node.location = (principled_bsdf_node.width + node_spacing, 0.0)

        # If for some reason there is no object selected, stop the script.
        else:
            self.report({'WARNING'}, "Select an object.")
            return {'FINISHED'}

    # Creates a group node for the selected channel, if one does not exist.
    def ready_channel_group_node(self, context):
        active_material = context.active_object.active_material
        material_nodes = context.active_object.active_material.node_tree.nodes
        layer_stack = context.scene.coater_layer_stack
        node_spacing = context.scene.coater_layer_stack.node_spacing

        # Create a node group for the selected channel if one does not exist.
        group_node_name = active_material.name + "_" + str(layer_stack.channel)

        if(bpy.data.node_groups.get(group_node_name) == None):
            new_node_group = bpy.data.node_groups.new(group_node_name, 'ShaderNodeTree')

            group_output_node = new_node_group.nodes.new('NodeGroupOutput')
            new_node_group.outputs.new('NodeSocketColor', 'Base Color')

            group_output_node.width = layer_stack.node_default_width

        # Add the group node to the active material if there is there isn't a group node already.
        if material_nodes.get(group_node_name) == None:
            group_node = material_nodes.new('ShaderNodeGroup')
            group_node.node_tree = bpy.data.node_groups[group_node_name]
            group_node.name = group_node_name
            group_node.label = group_node_name
            group_node.width = layer_stack.node_default_width * 1.2

            # Link the group node with the Principled BSDF node.
            principled_bsdf_node = material_nodes.get('Principled BSDF')

            if principled_bsdf_node != None:
                node_links = active_material.node_tree.links

                # Link the group node to the correct channel.
                if layer_stack.channel == "BASE_COLOR":
                    node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[0])

                if layer_stack.channel == "ROUGHNESS":
                    node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[7])

                if layer_stack.channel == "METALLIC":
                    node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[4])

                if layer_stack.channel == "HEIGHT":
                    node_links.new(group_node.outputs[0], principled_bsdf_node.inputs[20])

    # Adds nodes for a color layer.
    def add_color_layer_nodes(self, context):
        active_material = context.active_object.active_material
        layers = context.scene.coater_layers
        layer_stack = context.scene.coater_layer_stack
        layer_index = context.scene.coater_layer_stack.layer_index

        # Get the node group.
        group_node_name = active_material.name + "_" + str(layer_stack.channel)
        node_group = bpy.data.node_groups.get(group_node_name)
        
        # Create new nodes in the group.
        color_node = node_group.nodes.new(type='ShaderNodeRGB')
        opacity_node = node_group.nodes.new(type='ShaderNodeMath')
        mix_layer_node = node_group.nodes.new(type='ShaderNodeMixRGB')

        # Store new nodes in the selected layer.
        layers[layer_index].mix_layer_node_name = mix_layer_node.name
        layers[layer_index].opacity_node_name = opacity_node.name
        layers[layer_index].color_node_name = color_node.name

        # Update the labels for all layers.
        update_node_labels(self, context)

        # Set node default values.
        default_color = layers[layer_index].color
        color_node.outputs[0].default_value = (default_color[0], default_color[1], default_color[2], 1.0)
        opacity_node.operation = 'SUBTRACT'
        opacity_node.inputs[0].default_value = 1
        opacity_node.inputs[1].default_value = 1
        mix_layer_node.inputs[0].default_value = 1

        # Link nodes in this layer.
        link = node_group.links.new
        link(color_node.outputs[0], mix_layer_node.inputs[1])
        link(opacity_node.outputs[0], mix_layer_node.inputs[0])

        # TODO: Frame nodes.
        material_nodes = context.active_object.active_material.node_tree.nodes
        group_node_name = active_material.name + "_" + str(layer_stack.channel)

        group_node = material_nodes.get(group_node_name)
        if group_node != None:
            material_nodes.active = group_node

        #bpy.context.area.type = 'NODE_EDITOR'
        #color_node.select = True
        #opacity_node.select = True
        #mix_layer_node.select = True
        #bpy.ops.node.join()

        #bpy.context.area.ui_type = 'VIEW_3D'

    # Runs the function.
    def execute(self, context):
        # Change the layer mode to material so the user can see the layer they just applied.
        context.space_data.shading.type = 'MATERIAL'

        # Add a new layer slot to the layer stack.
        add_layer_slot(self, context)
        
        # Make sure the material is ready for layer nodes to be added.
        self.ready_material(context)

        # Create a group node for the selected channel if one does not exist.
        self.ready_channel_group_node(context)

        # Add color layer nodes.
        self.add_color_layer_nodes(context)

        # Organize all layer nodes in the group
        organize_nodes(self, context)

        # Link all layers together by connecting their mix nodes.
        link_layers(self, context)

        return {'FINISHED'}

# Adds a mask to the selected layer.
class COATER_OT_add_mask(bpy.types.Operator):
    bl_idname = "coater.add_mask"
    bl_label = ""
    bl_description = "Adds a mask of the selected type to the selected layer."

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.active_object

    def execute(self, context):
        return{'FINISHED'}

# Deletes the selected layer.
class COATER_OT_delete_layer(bpy.types.Operator):
    '''Deletes the currently selected layer from the layer stack.'''
    bl_idname = "coater.delete_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the currently selected layer"

    @ classmethod
    def poll(cls, context):
        return context.scene.coater_layers

    def execute(self, context):
        # Delete the nodes stored in this layer.
        layers = context.scene.coater_layers
        layer_stack = context.scene.coater_layer_stack
        layer_index = context.scene.coater_layer_stack.index

        node_group = get_current_group_node(self, context)

        # Remove all nodes for this layer if they exist.
        if(node_group != None):
            color_node = node_group.nodes.get("Color_" + str(layer_index))
            opacity_node = node_group.nodes.get("Opacity_" + str(layer_index))
            
            if(color_node != None):
                node_group.nodes.remove(color_node)


        # Remove the layer from the list.
        layers.remove(layer_stack.layer_index)
        layer_stack.layer_index = min(max(0, layer_stack.layer_index - 1), len(layers) - 1)

        # Organize all nodes.
        organize_nodes(self, context)

        # Connect layers.
        link_layers(self, context)

        # If there are no layers left, delete the channel's node group from the blend file.
        active_material = context.active_object.active_material
        material_nodes = active_material.node_tree.nodes
        if layer_stack.layer_index == -1:
            group_node_name = active_material.name + "_" + str(layer_stack.channel)
            node_group = bpy.data.node_groups.get(group_node_name)
            group_node = material_nodes.get(group_node_name)

            if group_node != None:
                material_nodes.remove(group_node)

            if node_group != None:
                bpy.data.node_groups.remove(node_group)

        # Update the node lables.
        update_node_labels(self, context)

        return {'FINISHED'}

# Moves the selected layer up or down the layer stack.
class COATER_OT_move_layer(bpy.types.Operator):
    """Moves the selecter layer up on the layer stack."""
    bl_idname = "coater.move_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the currently selected layer"

    # Use enums, to go up or down in the list.
    direction = bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))

    # Poll tests if the operator can be called or not.
    @ classmethod
    def poll(cls, context):
        return context.scene.coater_layers

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_stack = context.scene.coater_layer_stack
        layer_index = context.scene.coater_layer_stack.layer_index

        index_to_move_to = max(0, min(layer_index + (-1 if self.direction == 'UP' else 1), len(layers) - 1))
        layers.move(layer_index, index_to_move_to)
        layer_stack.layer_index = index_to_move_to

        # Organize all nodes.
        organize_nodes(self, context)

        # Connect layers.
        link_layers(self, context)

        # Update node labels.
        update_node_labels(self, context)

        return{'FINISHED'}

# Merges the selected layer with the layer below.
class COATER_OT_merge_layer(bpy.types.Operator):
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

# Duplicated the selected layer.
class COATER_OT_duplicate_layer(bpy.types.Operator):
    """Duplicates the selected layer."""
    bl_idname = "coater.duplicate_layer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Duplicates the selected layer."

    @ classmethod
    def poll(cls, context):
        #return context.scene.coater_layers
        return False

    def execute(self, context):
        return{'FINISHED'}

# Toggles the layer channel preview.
class COATER_OT_toggle_channel_preview(bpy.types.Operator):
    bl_idname = "coater.toggle_channel_preview"
    bl_label = ""
    bl_description = "Toggles the preview for the current material channel"

    def execute(self, context):
        # TODO: Disconnect all channels (group nodes) and connect only the selected channel.
        layer_stack = context.scene.coater_layer_stack
        material_nodes = context.active_object.active_material.node_tree.nodes
        node_links = context.active_object.active_material.node_tree.links

        if layer_stack.channel_preview == True:
            layer_stack.channel_preview = False
            # If an emission shader exists, delete it.
            emission_node = material_nodes.get('Emission')
            if emission_node != None:
                material_nodes.remove(emission_node)

            # Detach all channels from Principled BSDF shader.
            channel_nodes = get_channel_nodes(self, context)
            for node in channel_nodes:
                node_links.clear()

        elif layer_stack.channel_preview == False:
            layer_stack.channel_preview = True
            # If there is no emission node, make one.
            emission_node = material_nodes.new('ShaderNodeEmission')

            # Position the emission node over the Material Output node.
            material_output_node = material_nodes.get('Material Output')

            emission_node.width = material_output_node.width

            node_spacing = layer_stack.node_spacing
            emission_node.location = (material_output_node.location[0], material_output_node.location[1] + node_spacing)

            # TODO: Attach all channels from Principled BSDF shader.

        return{'FINISHED'}

# Organizes all nodes.
def organize_nodes(self, context):
    layer_stack = context.scene.coater_layer_stack
    active_material = context.active_object.active_material
    node_spacing = layer_stack.node_spacing

    # Organize channel nodes.
    group_nodes = get_channel_nodes(self, context)

    header_position = [0.0, 0.0]
    for node in group_nodes:
        if node != None:
            node.location = (-node.width + -node_spacing, header_position[1])
            header_position[1] -= node.height

    # TODO: Organize group output node for each channel.
    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)
    group_output_node = node_group.nodes.get('Group Output')
    group_output_node.location = (0.0, 0.0)

    # Organize all layer nodes.
    layers = context.scene.coater_layers
    
    header_position = [0.0, 0.0]
    for layer in range(0, len(layers)):
        node_list = layers[layer].nodes.split(',')
        header_position[0] -= layer_stack.node_default_width + node_spacing
        header_position[1] = 0.0

        # Organize all nodes in the layer.
        for x in node_list:
            node = node_group.nodes.get(x)
            if (node != None):
                node.width = layer_stack.node_default_width
                node.location = (header_position[0], header_position[1])
                header_position[1] -= (node.height * 2) + node_spacing

# Links all layers together by connecting their mix nodes.
def link_layers(self, context):
    # Get the group node.
    layer_stack = context.scene.coater_layer_stack
    active_material = context.active_object.active_material
    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)

    # Organize all coater layer nodes.
    layers = context.scene.coater_layers
    link = node_group.links.new
    group_output_node = node_group.nodes.get('Group Output')

    print(node_group.nodes)
    for x in range(len(layers), 0, -1):
        mix_layer_node = node_group.nodes.get(layers[x - 1].mix_layer_node_name)
        next_mix_layer_node = node_group.nodes.get(layers[x - 2].mix_layer_node_name)

        # Connect to the next layer if one exists.
        if x - 2 >= 0:
            link(mix_layer_node.outputs[0], next_mix_layer_node.inputs[2])

        # Connect to the Principled BSDF if there are no more layers.
        else:
            link(mix_layer_node.outputs[0], group_output_node.inputs[0])

# Returns a list of all channel group nodes.
def get_channel_nodes(self, context):
    active_material = context.active_object.active_material
    material_nodes = context.active_object.active_material.node_tree.nodes
        
    # Get references to all group nodes for all channels by their name.
    group_nodes = []
    group_nodes.append(material_nodes.get(active_material.name + "_" + "BASE_COLOR"))
    group_nodes.append(material_nodes.get(active_material.name + "_" + "METALLIC"))
    group_nodes.append(material_nodes.get(active_material.name + "_" + "ROUGHNESS"))
    group_nodes.append(material_nodes.get(active_material.name + "_" + "HEIGHT"))

    return group_nodes

# Assigning the type and layer index to the label of each node allows the nodes to be read into layers when the layer stack needs to be updated.
# Update the labels for all layer nodes.
def update_node_labels(self, context):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    active_material = context.active_object.active_material

    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)

    for i in range(0, len(layers)):
        color_node = node_group.nodes.get(layers[i].color_node_name)
        opacity_node = node_group.nodes.get(layers[i].opacity_node_name)
        mix_layer_node = node_group.nodes.get(layers[i].mix_layer_node_name)

        color_node.label = "Color_" + str(i)
        opacity_node.label = "Opacity_" + str(i)
        mix_layer_node.label = "MixLayer_" + str(i)

        # Update the node names.
        color_node.name = "Color_" + str(i)
        opacity_node.name = "Opacity_" + str(i)
        mix_layer_node.name = "MixLayer_" + str(i)

        # Assign nodes to their layers.
        layers[i].color_node_name = color_node.name
        layers[i].opacity_node = opacity_node.name
        layers[i].mix_layer_node = mix_layer_node.name

        # Update the node list.
        layers[i].nodes = ""
        layers[i].nodes += color_node.name + ","
        layers[i].nodes += opacity_node.name + ","
        layers[i].nodes += mix_layer_node.name + ","

# Returns the active node group or none, if one does not exist.
def get_current_group_node(self, context):
    layer_stack = context.scene.coater_layer_stack
    active_material = context.active_object.active_material

    group_node_name = active_material.name + "_" + str(layer_stack.channel)
    node_group = bpy.data.node_groups.get(group_node_name)
    return node_group

# Adds a slot to the layer stack.
def add_layer_slot(self, context):
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    layer_index = context.scene.coater_layer_stack.layer_index

    # Add a new layer.
    layers.add()
    layers[len(layers) - 1].layer_name = "Layer " + str(len(layers) - 1)

    # Moves the new layer above the currently selected layer and selects it.
    if(layer_index != -1):
        move_index = len(layers) - 1
        move_to_index = max(0, min(layer_index, len(layers) - 1))
        layers.move(move_index, move_to_index)
        layer_index = move_to_index

    else:
        move_index = len(layers) - 1
        move_to_index = 0
        layers.move(move_index, move_to_index)
        layer_stack.layer_index = move_to_index 