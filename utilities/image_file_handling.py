# This file provides functions to assist with importing, saving, or editing image files / textures made with this add-on.

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper        # For importing images.
import random
import os                                           # For saving layer images.
import re                                           # For splitting strings to identify material channels.
from ..import layer_nodes
from .. import logging


# Dictionary of words / tags that may be in image texture names that could be used to identify material channels.
material_channel_tags = {
    "color": 'COLOR',
    "colour": 'COLOR',
    "couleur": 'COLOR',
    "diffuse": 'COLOR',
    "diff": 'COLOR',
    "dif": 'COLOR',
    "subsurface": 'SUBSURFACE',
    "subsurf": 'SUBSURFACE',
    "ss": 'SUBSURFACE',
    "metallic": 'METALLIC',
    "metalness": 'METALLIC',
    "metal": 'METALLIC',
    "métalique": 'METALLIC',
    "metalique": 'METALLIC',
    "specular": 'SPECULAR',
    "specularité": 'SPECULAR',
    "specularite": 'SPECULAR',
    "spec": 'SPECULAR',
    "roughness": 'ROUGHNESS',
    "rough": 'ROUGHNESS',
    "rugosité": 'ROUGHNESS',
    "rugosite": 'ROUGHNESS',
    "emission": 'EMISSION',
    "émission": 'EMISSION',
    "emit": 'EMISSION',
    "normal": 'NORMAL',
    "normale": 'NORMAL',
    "nor": 'NORMAL',
    "ngl": 'NORMAL',
    "ndx": 'NORMAL',
    "height": 'HEIGHT',
    "hauteur": 'HEIGHT',
    "bump": 'HEIGHT'
}

def get_random_image_id():
    '''Generates a random image id number.'''
    return str(random.randrange(10000,99999))

def set_image_colorspace(image, material_channel_name):
    '''Correctly sets an image's colorspace based on the provided material channel.'''
    match material_channel_name:
        case 'COLOR':
            image.colorspace_settings.name = 'sRGB'

        case 'METALLIC':
            image.colorspace_settings.name = 'Non-Color'

        case 'ROUGHNESS':
            image.colorspace_settings.name = 'Non-Color'

        case 'NORMAL':
            image.colorspace_settings.name = 'Non-Color'

        case 'HEIGHT':
            image.colorspace_settings.name = 'Non-Color'
    
        case 'EMISSION':
            image.colorspace_settings.name = 'sRGB'

        case 'SCATTERING':
            image.colorspace_settings.name = 'sRGB'

def check_for_directx(filename):
    if "NormalDX" in filename or "NDX" in filename:
        return True
    else:
        return False

class MATLAYER_OT_add_layer_image(Operator):
    bl_idname = "matlayer.add_layer_image"
    bl_label = "Add Layer Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates a image within Blender's data and adds it to the selected layer"

    # Specified material channel.
    material_channel_name: bpy.props.StringProperty()

    def execute(self, context):
        active_object = bpy.context.active_object
        if not active_object:
            logging.popup_message_box("No selected object when adding a layer image.", 'User Error', 'ERROR')
            return
        
        # Assign the new image the layer name + a random image id number.
        image_name = active_object.name + "_" + get_random_image_id()
        while bpy.data.images.get(image_name) != None:
            image_name = active_object.name + "_" + get_random_image_id()

        # Create a new image of the texture size defined in the texture set settings.
        texture_set_settings = context.scene.matlayer_texture_set_settings
        match texture_set_settings.image_width:
            case 'FIVE_TWELVE':
                image_width = 512
            case 'ONEK':
                image_width = 1024
            case'TWOK':
                image_width = 2048
            case 'FOURK':
                image_width = 4096
            case _:
                image_width = 2048

        image_height = 128
        match texture_set_settings.image_height:
            case 'FIVE_TWELVE':
                image_height = 512
            case 'ONEK':
                image_height = 1024
            case 'TWOK':
                image_height = 2048
            case 'FOURK':
                image_height = 4096
            case _:
                image_width = 2048

        image = bpy.ops.image.new(name=image_name,
                                  width=image_width,
                                  height=image_height,
                                  color=(0.0, 0.0, 0.0, 0.0),
                                  alpha=True,
                                  generated_type='BLANK',
                                  float=False,
                                  use_stereo_3d=False,
                                  tiled=False)
        
        # Save to a folder. This allows users to use the edit externally function (to edit within a 2D image editor of their choice) later if desired.
        matlayer_image_path = os.path.join(bpy.path.abspath("//"), "Matlayer")
        if os.path.exists(matlayer_image_path) == False:
            os.mkdir(matlayer_image_path)

        layer_image_path = os.path.join(matlayer_image_path, "Layers")
        if os.path.exists(layer_image_path) == False:
            os.mkdir(layer_image_path)

        image = bpy.data.images[image_name]
        image.filepath = layer_image_path + "/" + image_name + ".png"
        image.file_format = 'PNG'
        if image:
            image.save()

        # Add the new image to the selected layer.
        selected_layer_index = context.scene.matlayer_layer_stack.layer_index
        texture_node = layer_nodes.get_layer_node("TEXTURE", self.material_channel_name, selected_layer_index, context)
        new_image = bpy.data.images[image_name]
        if texture_node:
            texture_node.image = new_image
            context.scene.matlayer_layers[selected_layer_index].material_channel_textures.color_channel_texture = new_image

        # Select the new texture for painting.
        context.scene.tool_settings.image_paint.canvas = texture_node.image
        
        return {'FINISHED'}

class MATLAYER_OT_import_texture(Operator, ImportHelper):
    bl_idname = "matlayer.import_texture"
    bl_label = "Import Texture"
    bl_description = "Opens a menu that allows the user to import a texture file into a specific material channel"
    bl_options = {'REGISTER', 'UNDO'}

    # Specified material channel.
    material_channel_name: bpy.props.StringProperty()

    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp;*.exr',
        options={'HIDDEN'}
    )

    def execute(self, context):
        selected_material_layer_index = context.scene.matlayer_layer_stack.layer_index
        selected_material_layer = context.scene.matlayer_layers[selected_material_layer_index]

        # Open a window to import an image into blender.
        head_tail = os.path.split(self.filepath)
        image_name = head_tail[1]
        bpy.ops.image.open(filepath=self.filepath)

        # Apply the selected image texture to the selected layer based on projection mode.
        context.scene.matlayer_layer_stack.auto_update_layer_properties = False
        image = bpy.data.images[image_name]
        if selected_material_layer.projection.mode == 'TRIPLANAR':
            triplanar_texture_sample_nodes = layer_nodes.get_triplanar_texture_sample_nodes(self.material_channel_name, selected_material_layer_index)
            for node in triplanar_texture_sample_nodes:
                if node:
                    node.image = image
        else:
            texture_node = layer_nodes.get_layer_node("TEXTURE", self.material_channel_name, selected_material_layer_index, context)
            if texture_node:
                texture_node.image = image
        
        setattr(selected_material_layer.material_channel_textures, self.material_channel_name.lower() + "_channel_texture", image)
        context.scene.matlayer_layer_stack.auto_update_layer_properties = True

        # For specific material channels, imported textures automatically have their color space corrected.
        set_image_colorspace(image, self.material_channel_name)

        # Print information about using DirectX normal maps for users if it's detected they are using one.
        if check_for_directx(image_name) and self.material_channel_name == 'NORMAL':
            self.report({'INFO'}, "You may have imported a DirectX normal map which will cause your imported normal map to appear inverted. You should use an OpenGL normal map instead or fix the textures name if it's already an OpenGL normal map.")

        return {'FINISHED'}

class MATLAYER_OT_import_texture_set(Operator, ImportHelper):
    bl_idname = "matlayer.import_texture_set"
    bl_label = "Import Texture Set"
    bl_description = "Imports multiple selected textures into material channels based on file names. This function requires decent texture file naming conventions to work properly"
    bl_options = {'REGISTER', 'UNDO'}
    
    files: bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'}
    )

    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp;*.exr',
        options={'HIDDEN'}
    )

    def execute(self, context):
        # Helper function to split the file name into components.
        def split_filename_by_components(filename):
            # Remove file extension.
            filename = os.path.splitext(filename)[0]

            # Remove numbers (these can't be used to identify a material channel from the texture name).
            filename = ''.join(i for i in filename if not i.isdigit())
            
            # Separate camel case by space.
            filename = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', filename))

            # Replace common separators with a space.
            separators = ['_', '.', '-', '__', '--', '#']
            for seperator in separators:
                filename = filename.replace(seperator, ' ')

            # Return all components split by a space with lowercase characters.
            components = filename.split(' ')
            components = [c.lower() for c in components]
            return components

        # Assign points to all material channel id tags that appear in selected file names. Material channels that appear more than once are assigned a lower point value.
        material_channel_occurance = {}
        for file in self.files:
            tags = split_filename_by_components(file.name)
            for tag in tags:
                if tag not in material_channel_occurance and tag in material_channel_tags:
                    material_channel = material_channel_tags[tag]
                    material_channel_occurance[material_channel] = 0

        for file in self.files:
            tags = split_filename_by_components(file.name)
            for tag in tags:
                if tag in material_channel_tags:
                    material_channel = material_channel_tags[tag]
                    if material_channel in material_channel_occurance:
                        material_channel_occurance[material_channel] += 1

        selected_image_file = False
        for file in self.files:
            # Start by assuming the correct material channel is the one that appears the least in the file name.
            # I.E: Selected files: RoughMetal_002_2k_Color, RoughMetal_002_2k_Normal, RoughMetal_002_2k_Metalic, RoughMetal_002_2k_Rough
            # Color material channel file = RoughMetal_002_2k_Color (because the 'color' tag appears the least among all selected files).
            tags = split_filename_by_components(file.name)
            material_channel_names_in_filename = []
            for tag in tags:
                if tag in material_channel_tags:
                    material_channel_names_in_filename.append(material_channel_tags[tag])

            # Only import files that have a material channel name detected in the file name.
            if len(material_channel_names_in_filename) > 0:
                selected_material_channel_name = material_channel_names_in_filename[0]
                material_channel_occurances_equal = True
                for material_channel_name in material_channel_names_in_filename:
                    if material_channel_occurance[material_channel_name] < material_channel_occurance[selected_material_channel_name]:
                        selected_material_channel_name = material_channel_name
                        material_channel_occurances_equal = False
                
                # If all material channels identified in the files name occur equally throughout all selected filenames, use the material channel that occurs the most in the files name.
                # I.E: Selected files: RoughMetal_002_2k_Color, RoughMetal_002_2k_Normal, RoughMetal_002_2k_Metalic, RoughMetal_002_2k_Rough
                # Roughness material channel file = RoughMetal_002_2k_Rough (because roughness appears twice)
                selected_material_channel_name = material_channel_names_in_filename[0]
                if material_channel_occurances_equal:
                    for material_channel_name in material_channel_names_in_filename:
                        if material_channel_occurance[material_channel_name] > material_channel_occurance[selected_material_channel_name]:
                            selected_material_channel_name = material_channel_name
                            
                # Change the material channels node type to a texture node.
                material_layers = context.scene.matlayer_layers
                selected_material_layer_index = context.scene.matlayer_layer_stack.layer_index
                attribute_name = material_channel_name.lower() + "_node_type"
                material_channel_node_type = getattr(material_layers[selected_material_layer_index].channel_node_types, attribute_name)
                if material_channel_node_type != 'TEXTURE':
                    setattr(material_layers[selected_material_layer_index].channel_node_types, attribute_name, 'TEXTURE')

                # Import the image.
                folder_directory = os.path.split(self.filepath)
                image_path = os.path.join(folder_directory[0], file.name)
                bpy.ops.image.open(filepath=image_path)
                imported_image = bpy.data.images[file.name]

                # Select the first image file in the canvas painting window.
                if selected_image_file == False:
                    context.scene.tool_settings.image_paint.canvas = imported_image
                    selected_image_file = True

                # Place the image into a material channel and nodes based on texture projection and inferred material channel name.
                selected_material_layer = material_layers[selected_material_layer_index]
                if selected_material_layer.projection.mode == 'TRIPLANAR':
                    triplanar_texture_sample_nodes = layer_nodes.get_triplanar_texture_sample_nodes(material_channel_name, selected_material_layer_index)
                    for node in triplanar_texture_sample_nodes:
                        if node:
                            node.image = imported_image
                            setattr(selected_material_layer.material_channel_textures, material_channel_name.lower() + "_channel_texture", imported_image)
                else:
                    texture_node = layer_nodes.get_layer_node('TEXTURE', material_channel_name, selected_material_layer_index, context)
                    if texture_node:
                        texture_node.image = imported_image
                        setattr(selected_material_layer.material_channel_textures, material_channel_name.lower() + "_channel_texture", imported_image)

                # Update the imported images colorspace based on it's specified material channel.
                set_image_colorspace(imported_image, material_channel_name)

                # Print information about using DirectX normal maps for users if it's detected they are using one.
                if check_for_directx(file.name):
                    self.report({'INFO'}, "You may have imported a DirectX normal map which will cause your imported normal map to appear inverted. You should use an OpenGL normal map instead or fix the textures name if it's already an OpenGL normal map.")
        return {'FINISHED'}

class MATLAYER_OT_delete_layer_image(Operator):
    '''Deletes the current layer image from Blender's data'''
    bl_idname = "matlayer.delete_layer_image"
    bl_label = "Delete Layer Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the current layer image from Blender's data and saved texture files. If you want to unlink the image from the texture node without deleting the image, use the 'x' button inside the image texture block"

    # Specified material channel.
    material_channel_name: bpy.props.StringProperty()

    def execute(self, context):
        selected_material_layer_index = context.scene.matlayer_layer_stack.layer_index
        texture_node = layer_nodes.get_layer_node("TEXTURE", self.material_channel_name, selected_material_layer_index, context)
        if texture_node:
            if texture_node.image:
                bpy.data.images.remove(texture_node.image)
        return {'FINISHED'}