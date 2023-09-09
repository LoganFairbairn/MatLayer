import bpy
from bpy.types import Operator
from bpy.props import PointerProperty, StringProperty
from bpy_extras.io_utils import ImportHelper        # For importing images.
from ..core import debug_logging                    # For printing / displaying debugging related messages.
from ..core import image_utilities                  # For access to image related helper functions.
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
                image_utilities.set_image_colorspace_by_material_channel(imported_image, material_channel_name)

                # Print information about using DirectX normal maps for users if it's detected they are using one.
                if image_utilities.check_for_directx(file.name):
                    self.report({'INFO'}, "You may have imported a DirectX normal map which will cause your imported normal map to appear inverted. You should use an OpenGL normal map instead or fix the textures name if it's already an OpenGL normal map.")
        return {'FINISHED'}
    
class MATLAYER_OT_merge_materials(Operator):
    bl_idname = "matlayer.merge_materials"
    bl_label = "Merge Materials"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Merges the layers from the selected material into the active material. Any mesh map textures in the merged material will be replaced by the mesh maps on the active object if they are baked"

    bpy.types.Scene.matlayer_merge_material = PointerProperty(type=bpy.types.Material)
    material_name: StringProperty(default="")

    def execute(self, context):
        return {'FINISHED'}