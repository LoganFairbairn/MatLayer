import os
import bpy
from bpy.types import Operator, PropertyGroup
from . import layer_nodes
from . import material_channel_nodes

MASK_NODE_TYPES = [
    ("VALUE", "Value", ""),
    ("TEXTURE", "Texture", ""),
    ("NOISE", "Noise", ""),
    ("VORONOI", "Voronoi", ""),
    ("MUSGRAVE", "Musgrave", "")
    ]

class COATER_mask_stack(PropertyGroup):
    '''Properties for the mask stack.'''
    selected_mask_index: bpy.props.IntProperty(default=-1)

class COATER_UL_mask_stack(bpy.types.UIList):
    '''Draws the mask stack for the selected layer.'''
    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text="SOMETHING HERE")

class COATER_masks(PropertyGroup):
    # Mask Projection Settings
    mask_projection_mode: bpy.props.EnumProperty(items=[('FLAT', "Flat", ""), ('BOX', "Box (Tri-Planar)", ""), ('SPHERE', "Sphere", ""),('TUBE', "Tube", "")], name="Projection", description="Projection type of the mask attached to the selected layer", default='FLAT')
    mask_projection_blend: bpy.props.FloatProperty(name="Mask Projection Blend", description="The mask projection blend amount", default=0.5, min=0.0, max=1.0, subtype='FACTOR')
    projection_mask_offset_x: bpy.props.FloatProperty(name="Offset X", description="Projected x offset of the selected mask", default=0.0, min=-1.0, max=1.0, subtype='FACTOR')
    projection_mask_offset_y: bpy.props.FloatProperty(name="Offset Y", description="Projected y offset of the selected mask", default=0.0, min=-1.0, max=1.0, subtype='FACTOR')
    projection_mask_rotation: bpy.props.FloatProperty(name="Rotation", description="Projected rotation of the selected mask", default=0.0, min=-6.283185, max=6.283185, subtype='ANGLE')
    projection_mask_scale_x: bpy.props.FloatProperty(name="Scale X", description="Projected x scale of the selected mask", default=1.0, soft_min=-4.0, soft_max=4.0, subtype='FACTOR')
    projection_mask_scale_y: bpy.props.FloatProperty(name="Scale Y", description="Projected y scale of the selected mask", default=1.0, soft_min=-4.0, soft_max=4.0, subtype='FACTOR')

    # Node Types (used for properly drawing user interface for node properties)
    mask_texture_types: bpy.props.EnumProperty(items=MASK_NODE_TYPES, name="Mask Texture Node Type", description="The node type for the mask", default='TEXTURE')

class COATER_OT_add_mask(Operator):
    '''Adds a mask to the selected layer'''
    bl_idname = "coater.add_mask"
    bl_label = "Add Mask"
    bl_description = "Adds a mask to the selected layer"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
        selected_layer_index = context.scene.coater_layer_stack.layer_index

        material_channel_list = material_channel_nodes.get_material_channel_list()
        for material_channel_name in material_channel_list:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)
            if material_channel_node:
                
                # Create default mask nodes.
                mask_node = material_channel_node.node_tree.nodes.new('ShaderNodeTexImage')
                mask_node.name = "MASK_TEXTURE_" + str(selected_layer_index) + "~"
                mask_node.label = mask_node.name
                
                mask_coord_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeTexCoord')
                mask_coord_node.name = "MASK_COORD_" + str(selected_layer_index) + "~"
                mask_coord_node.label = mask_coord_node.name

                mask_mapping_node = material_channel_node.node_tree.nodes.new(type='ShaderNodeMapping')
                mask_mapping_node.name = "MASK_MAPPING_" + str(selected_layer_index) + "~"
                mask_mapping_node.label = mask_mapping_node.name

                mask_mix_node = material_channel_node.node_tree.nodes.new('ShaderNodeMixRGB')
                mask_mix_node.name = "MASK_MIX_LAYER_" + str(selected_layer_index) + "~"
                mask_mix_node.label = mask_mix_node.name
                
                # Link new nodes.
                material_channel_node.node_tree.links.new(mask_coord_node.outputs[2], mask_mapping_node.inputs[0])
                material_channel_node.node_tree.links.new(mask_mapping_node.outputs[0], mask_node.inputs[0])

                # Link mix layer node to the mix mask node.
                mix_layer_node = layer_nodes.get_layer_node("MIXLAYER", material_channel_name, selected_layer_index, context)
                material_channel_node.node_tree.links.new(mix_layer_node.outputs[0], mask_mix_node.inputs[1])

                # Add the nodes to the layer frame.
                frame = layer_nodes.get_layer_frame(material_channel_name, selected_layer_index, context)
                if frame:
                    mask_node.parent = frame
                    mask_mix_node.parent = frame
                    mask_coord_node.parent = frame
                    mask_mapping_node.parent = frame
                
                # Update the layer nodes.
                #layer_nodes.update_layer_nodes(context)

            return{'FINISHED'}





#------------------- Layer Mask Filters -------------------#

class COATER_OT_add_mask_filter_invert(Operator):
    '''Adds an invert adjustment to the masks applied to the selected layer'''
    bl_idname = "coater.add_mask_filter_invert"
    bl_label = "Add Invert Mask Filter"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds an invert adjustment to the masks applied to the selected layer"

    def execute(self, context):
        return {'FINISHED'}

class COATER_OT_add_mask_filter_levels(Operator):
    '''Adds a level adjustment to the masks applied to the selected layer'''
    bl_idname = "coater.add_mask_filter_levels"
    bl_label = "Add Levels Mask Filter"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds a level adjustment to the masks applied to the selected layer"

    def execute(self, context):
        return {'FINISHED'}

class COATER_OT_add_layer_mask_filter_menu(Operator):
    '''Opens a menu of layer filters that can be added to the selected layer.'''
    bl_label = ""
    bl_idname = "coater.add_layer_mask_filter_menu"
    bl_description = "Opens a menu of layer filters that can be added to the selected mask stack"

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

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
        col.operator("coater.add_mask_filter_invert")
        col.operator("coater.add_mask_filter_levels")

#------------------- Layer Mask Stack Operations -------------------#

class COATER_OT_move_layer_mask_up(Operator):
    '''Moves the selected layer up on the layer stack'''
    bl_idname = "coater.move_layer_mask_up"
    bl_label = "Move Layer Mask Up"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the selected layer up on the layer stack"

    def execute(self, context):
        return {'FINISHED'}

class COATER_OT_move_layer_mask_down(Operator):
    '''Moves the selected layer down on the layer stack'''
    bl_idname = "coater.move_layer_mask_down"
    bl_label = "Move Layer Mask Down"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Moves the selected layer down on the layer stack"

    def execute(self, context):
        return {'FINISHED'}

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

        material_channel_node = material_channel_nodes.get_material_channel_node(context, "COLOR")

        # Delete mask nodes for the selected layer if they exist.
        mask_node = material_channel_node.node_tree.nodes.get(layers[layer_index].mask_node_name)
        if mask_node != None:
            material_channel_node.node_tree.nodes.remove(mask_node)

        mask_mix_node = material_channel_node.node_tree.nodes.get(layers[layer_index].mask_mix_node_name)
        if mask_mix_node != None:
            material_channel_node.node_tree.nodes.remove(mask_mix_node)

        mask_coord_node = material_channel_node.node_tree.nodes.get(layers[layer_index].mask_coord_node_name)
        if mask_coord_node != None:
            material_channel_node.node_tree.nodes.remove(mask_coord_node)

        mask_mapping_node = material_channel_node.nodes.get(layers[layer_index].mask_mapping_node_name)
        if mask_mapping_node != None:
            material_channel_node.node_tree.nodes.remove(mask_mapping_node)

        mask_levels_node = material_channel_node.node_tree.nodes.get(layers[layer_index].mask_levels_node_name)
        if mask_levels_node != None:
            material_channel_node.node_tree.nodes.remove(mask_levels_node)

        # Clear mask node names.
        layers[layer_index].mask_node_name = ""
        layers[layer_index].mask_mix_node_name = ""
        layers[layer_index].mask_coord_node_name = ""
        layers[layer_index].mask_mapping_node_name = ""
        layers[layer_index].mask_levels_node_name = ""

        # Relink nodes.
        layer_nodes.update_layer_nodes(context)

        return{'FINISHED'}