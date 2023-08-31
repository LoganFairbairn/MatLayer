# This file provides functions to assist with importing, saving, or editing image files / textures for this add-on.

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper        # For importing images.
from ..core import texture_set_settings as tss
from ..core import material_layers
from ..core import debug_logging
from ..core import blender_addon_utils
import random
import os                                           # For saving layer images.
import re                                           # For splitting strings to identify material channels.

# Dictionary of words / tags that may be in image texture names that could be used to identify material channels.
MATERIAL_CHANNEL_TAGS = {
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

def set_image_colorspace_by_material_channel(image, material_channel_name):
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

class MATLAYER_OT_add_texture_node_image(Operator):
    bl_idname = "matlayer.add_texture_node_image"
    bl_label = "Add Texture Node Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates a new image (uses texture set pixel resolution) and adds it to the specified texture node"

    node_tree_name: StringProperty(default="")
    node_name: StringProperty(default="")

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status("Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        if self.node_name == "":
            debug_logging.log_status("Provided texture node name is blank when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if not texture_node:
            debug_logging.log_status("Can't find the specified texture node when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        # Assign the new image a random name.
        image_name = "Image_" + get_random_image_id()
        while bpy.data.images.get(image_name) != None:
            image_name = "Image_" + get_random_image_id()

        # Create a new image of the texture size defined in the texture set settings.
        image_width = tss.get_texture_width()
        image_height = tss.get_texture_height()
        new_image = blender_addon_utils.create_image(image_name, image_width, image_height, alpha_channel=True, thirty_two_bit=True)
        
        # Save the new image to a folder. This allows users to easily edit their image in a 2D image editor later.
        matlayer_image_path = os.path.join(bpy.path.abspath("//"), "Assets")
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

        texture_node.image = new_image                                              # Add the new image to the image node.
        context.scene.tool_settings.image_paint.canvas = texture_node.image         # Select the new texture for painting.
        
        return {'FINISHED'}

class MATLAYER_OT_import_texture_node_image(Operator, ImportHelper):
    bl_idname = "matlayer.import_texture_node_image"
    bl_label = "Import Texture"
    bl_description = "Opens a menu that allows the user to import a texture file into the specified texture node"
    bl_options = {'REGISTER', 'UNDO'}

    node_tree_name: StringProperty(default="")
    node_name: StringProperty(default="")
    material_channel_name: StringProperty(default="COLOR")

    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp;*.exr',
        options={'HIDDEN'}
    )

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status("Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        if self.node_name == "":
            debug_logging.log_status("Provided texture node name is blank when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if not texture_node:
            debug_logging.log_status("Can't find the specified texture node when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        # Open a window to import an image into blender.
        head_tail = os.path.split(self.filepath)
        image_name = head_tail[1]
        bpy.ops.image.open(filepath=self.filepath)
        image = bpy.data.images[image_name]

        # Apply the selected image texture to the selected layer based on projection mode.
        selected_material_layer = context.scene.matlayer_layers[context.scene.matlayer_layer_stack.selected_layer_index]
        match selected_material_layer.projection.mode:
            case 'UV':
                texture_node.image = image

            case 'TRIPLANAR':
                # TODO: Fill triplanar out.
                print("Placeholder...")
                
        # If a material channel is defined, set the color space.
        if self.material_channel_name != "":
            set_image_colorspace_by_material_channel(image, self.material_channel_name)

        # Print a warning about using DirectX normal maps for users if it's detected they are using one.
        if check_for_directx(image_name) and self.material_channel_name == 'NORMAL':
            debug_logging.log_status("You may have imported a DirectX normal map which will cause your imported normal map to appear inverted.", self, type='WARNING')

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
                if tag not in material_channel_occurance and tag in MATERIAL_CHANNEL_TAGS:
                    material_channel = MATERIAL_CHANNEL_TAGS[tag]
                    material_channel_occurance[material_channel] = 0

        for file in self.files:
            tags = split_filename_by_components(file.name)
            for tag in tags:
                if tag in MATERIAL_CHANNEL_TAGS:
                    material_channel = MATERIAL_CHANNEL_TAGS[tag]
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
                if tag in MATERIAL_CHANNEL_TAGS:
                    material_channel_names_in_filename.append(MATERIAL_CHANNEL_TAGS[tag])

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
                set_image_colorspace_by_material_channel(imported_image, material_channel_name)

                # Print information about using DirectX normal maps for users if it's detected they are using one.
                if check_for_directx(file.name):
                    self.report({'INFO'}, "You may have imported a DirectX normal map which will cause your imported normal map to appear inverted. You should use an OpenGL normal map instead or fix the textures name if it's already an OpenGL normal map.")
        return {'FINISHED'}

class MATLAYER_OT_edit_texture_node_image_externally(Operator):
    bl_idname = "matlayer.edit_texture_node_image_externally"
    bl_label = "Edit Image Externally"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Exports the specified material channel image to the external image editing software defined in Blenders preferences"

    node_tree_name: StringProperty(default="")
    node_name: StringProperty(default="")

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status("Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        if self.node_name == "":
            debug_logging.log_status("Provided texture node name is blank when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if not texture_node:
            debug_logging.log_status("Can't find the specified texture node when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        # Save the image if it needs saving.
        if texture_node.image.is_dirty:
            texture_node.image.save()

        # Select and then export the image to the external image editing software.
        context.scene.tool_settings.image_paint.canvas = texture_node.image
        bpy.ops.image.external_edit(filepath=texture_node.image.filepath)

        return {'FINISHED'}

class MATLAYER_OT_reload_texture_node_image(Operator):
    bl_idname = "matlayer.reload_texture_node_image"
    bl_label = "Reload Texture Node Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Reloads the texture node image from it's associated saved file"

    node_tree_name: StringProperty(default="")
    node_name: StringProperty(default="")

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status("Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        if self.node_name == "":
            debug_logging.log_status("Provided texture node name is blank when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if not texture_node:
            debug_logging.log_status("Can't find the specified texture node when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        # Select and then reload the image in the texture node.
        if texture_node.image:
            context.scene.tool_settings.image_paint.canvas = texture_node.image
            bpy.ops.image.reload()
            debug_logging.log_status("Reloaded {0}.".format(texture_node.image.name), self, type='INFO')
        return {'FINISHED'}

class MATLAYER_OT_delete_texture_node_image(Operator):
    bl_idname = "matlayer.delete_texture_node_image"
    bl_label = "Delete Texture Node Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the texture image stored in the texture node from blenders data, and it's saved file on disk if one exists"

    node_tree_name: StringProperty(default="")
    node_name: StringProperty(default="")

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status("Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        if self.node_name == "":
            debug_logging.log_status("Provided texture node name is blank when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if not texture_node:
            debug_logging.log_status("Can't find the specified texture node when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        # Delete the image in the texture node from the blend data if one exists.
        if texture_node.image:
            image_name = texture_node.image.name
            bpy.data.images.remove(texture_node.image)
            debug_logging.log_status("Deleted " + image_name, self, type='INFO')
        else:
            debug_logging.log_status("No image to delete.", self, type='INFO')

        return {'FINISHED'}