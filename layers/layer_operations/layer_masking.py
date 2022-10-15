import os
import bpy
from bpy.types import Operator, PropertyGroup
from ..nodes import layer_nodes
from ...texture_handling import image_file_handling
from ..nodes import material_channel_nodes

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

class COATER_OT_add_black_mask(Operator):
    '''Creates a fully black image and adds it as the selected layer's mask'''
    bl_idname = "coater.add_black_mask"
    bl_label = "Add Black Mask"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates a fully black image and adds it as the selected layer's mask"

    def execute(self, context):
        bpy.ops.coater.add_empty_mask()

        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        # Assign the new image a unique name.
        layer_name = layers[layer_index].name.replace(" ", "")
        image_mask_name = layer_name + "_" + "Mask_" + image_file_handling.get_random_image_id()

        while bpy.data.images.get(image_mask_name) != None:
            image_mask_name = layer_name + "_" + "Mask_" + image_file_handling.get_random_image_id()

        texture_set_settings = context.scene.coater_texture_set_settings

        image_width = 128
        if texture_set_settings.image_width == 'FIVE_TWELVE':
            image_width = 512
        if texture_set_settings.image_width == 'ONEK':
            image_width = 1024
        if texture_set_settings.image_width == 'TWOK':
            image_width = 2048
        if texture_set_settings.image_width == 'FOURK':
            image_width = 4096

        image_height = 128
        if texture_set_settings.image_height == 'FIVE_TWELVE':
            image_height = 512
        if texture_set_settings.image_height == 'ONEK':
            image_height = 1024
        if texture_set_settings.image_height == 'TWOK':
            image_height = 2048
        if texture_set_settings.image_height == 'FOURK':
            image_height = 4096

        image = bpy.ops.image.new(name=image_mask_name,
                                  width=image_width,
                                  height=image_height,
                                  color=(0.0, 0.0, 0.0, 1.0),
                                  alpha=False,
                                  generated_type='BLANK',
                                  float=False,
                                  use_stereo_3d=False,
                                  tiled=False)

        # If images are not being packed into the blend file, save them to a layer images folder.
        if texture_set_settings.pack_images == False:
            layers_folder_path = bpy.path.abspath("//") + 'Layers'

            if os.path.exists(layers_folder_path) == False:
                os.mkdir(layers_folder_path)

            layer_image = bpy.data.images[image_mask_name]
            layer_image.filepath = layers_folder_path + "/" + image_mask_name + ".png"
            layer_image.file_format = 'PNG'

            layer_image.pixels[0] = 1

            if layer_image != None:
                if layer_image.is_dirty:
                    layer_image.save()

        group_node = layer_nodes.get_channel_node_group(context)
        mask_node_name = layers[layer_index].mask_node_name
        mask_node = group_node.nodes.get(mask_node_name)

        if (mask_node != None):
            mask_node.image = bpy.data.images[image_mask_name]
        
        return {'FINISHED'}

class COATER_OT_add_white_mask(Operator):
    '''Creates a fully white image and adds it as the selected layer's mask'''
    bl_idname = "coater.add_white_mask"
    bl_label = "Add White Mask"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates a fully white image and adds it as the selected layer's mask"

    def execute(self, context):
        bpy.ops.coater.add_empty_mask()
        
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        # Assign the new image a unique name.
        layer_name = layers[layer_index].name.replace(" ", "")
        image_mask_name = layer_name + "_" + "Mask_" + image_file_handling.get_random_image_id()

        while bpy.data.images.get(image_mask_name) != None:
            image_mask_name = layer_name + "_" + "Mask_" + image_file_handling.get_random_image_id()

        texture_set_settings = context.scene.coater_texture_set_settings

        image_width = 128
        if texture_set_settings.image_width == 'FIVE_TWELVE':
            image_width = 512
        if texture_set_settings.image_width == 'ONEK':
            image_width = 1024
        if texture_set_settings.image_width == 'TWOK':
            image_width = 2048
        if texture_set_settings.image_width == 'FOURK':
            image_width = 4096

        image_height = 128
        if texture_set_settings.image_height == 'FIVE_TWELVE':
            image_height = 512
        if texture_set_settings.image_height == 'ONEK':
            image_height = 1024
        if texture_set_settings.image_height == 'TWOK':
            image_height = 2048
        if texture_set_settings.image_height == 'FOURK':
            image_height = 4096

        image = bpy.ops.image.new(name=image_mask_name,
                                  width=image_width,
                                  height=image_height,
                                  color=(1.0, 1.0, 1.0, 1.0),
                                  alpha=False,
                                  generated_type='BLANK',
                                  float=False,
                                  use_stereo_3d=False,
                                  tiled=False)

        group_node = layer_nodes.get_channel_node_group(context)
        mask_node_name = layers[layer_index].mask_node_name
        mask_node = group_node.nodes.get(mask_node_name)

        if (mask_node != None):
            mask_node.image = bpy.data.images[image_mask_name]
        return {'FINISHED'}

class COATER_OT_add_empty_mask(Operator):
    '''Adds an empty image mask to the selected layer'''
    bl_idname = "coater.add_empty_mask"
    bl_label = "Add Empty Mask"
    bl_description = "Adds an image mask to the selected layer"

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