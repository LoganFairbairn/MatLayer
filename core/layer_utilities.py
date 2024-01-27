import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper        # For importing images.
from ..core import debug_logging                    # For printing / displaying debugging related messages.
from ..core import image_utilities                  # For access to image related helper functions.
from ..core import material_layers                  # For accessing material layer nodes.
from ..core import layer_masks                      # For editing layer masks.
from ..core import blender_addon_utils              # For extra helpful Blender utilities.
from ..core import texture_set_settings as tss      # For access to texture set settings.
from ..core import export_textures                  # For access to the invert image function.
import os                                           # For saving layer images.
import re                                           # For splitting strings to identify material channels.

# Dictionary of words / tags that may be in image texture names that could be used to identify material channels from image file names.
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
    "bump": 'HEIGHT',
    "opacity": 'ALPHA',
    "opaque": 'ALPHA',
    "alpha": 'ALPHA',

    # RGB channel packing...
    "orm": 'CHANNEL_PACKED',
    "rmo": 'CHANNEL_PACKED',

    # RGBA channel packing, 'X' is used to identify when nothing is packed into a channel.
    "moxs": 'CHANNEL_PACKED',

    # Naming conventions such as 'MyTextureName_RoughnessMetallic' can't be imported automatically
    # because it's ambiguous for which RGBA channel the values are intended to go into.
}

# https://docs.unrealengine.com/4.27/en-US/ProductionPipelines/AssetNaming/
# With an identifiable material channel format, such as the one used commonly in game engines (T_MyTexture_C_1),
# we can identify material channels using only the first few letters.
MATERIAL_CHANNEL_ABBREVIATIONS = {
    "c": 'COLOR',
    "m": 'METALLIC',
    "r": 'ROUGHNESS',
    "n": 'NORMAL',
    "ngl": 'NORMAL',
    "ndx": 'NORMAL',
    "h": 'HEIGHT',
    "b": 'HEIGHT',
    "s": 'SPECULAR',
    "ss": 'SUBSURFACE',
    "a": 'ALPHA',
    "cc": 'COAT',
    "e": 'EMISSION',
    #"O": "OCCLUSION",
}

class MATLAYER_OT_import_texture_set(Operator, ImportHelper):
    bl_idname = "matlayer.import_texture_set"
    bl_label = "Import Texture Set"
    bl_description = "Imports multiple selected textures into material channels by parsing selected file names. Images with naming conventions that don't accurately identify the material channel they belong to will not import properly"
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
            split_components = filename.split(' ')
            components = []
            for c in split_components:
                if c != '':
                    components.append(c.lower())

            return components

        def get_rgba_channel_from_index(index):
            '''Returns the RGBA channel name for the provided index (i.e 0 = R, 1 = G...).'''
            match index:
                case -1:
                    return 'COLOR'
                case 0:
                    return 'RED'
                case 1:
                    return 'GREEN'
                case 2:
                    return 'BLUE'
                case 3:
                    return 'ALPHA'
                case _:
                    return 'ERROR'

        # Compile a list of all unique tags found accross all user selected image file names.
        material_channel_occurance = {}
        for file in self.files:
            tags = split_filename_by_components(file.name)
            for tag in tags:
                if tag not in material_channel_occurance and tag in MATERIAL_CHANNEL_TAGS:
                    material_channel = MATERIAL_CHANNEL_TAGS[tag]
                    material_channel_occurance[material_channel] = 0

        # Calculate how many times a unique channel tag appears accross all user selected image files.
        for file in self.files:
            tags = split_filename_by_components(file.name)
            for tag in tags:
                if tag in MATERIAL_CHANNEL_TAGS:
                    material_channel = MATERIAL_CHANNEL_TAGS[tag]
                    if material_channel in material_channel_occurance:
                        material_channel_occurance[material_channel] += 1

        # Cycle through all selected image files and try to identify the correct material channel to import them into.
        selected_image_file = False
        for file in self.files:
            detected_material_channel = 'NONE'
            
            # If the image file starts with a 'T_' assume it's using a commonly used Unreal Engine / game engine naming convention.
            if file.name.startswith('T_'):
                remove_file_extension = file.name.split('.')[0]
                channel_abbreviation = remove_file_extension.split('_')[2].lower()
                if channel_abbreviation in MATERIAL_CHANNEL_ABBREVIATIONS:
                    detected_material_channel = MATERIAL_CHANNEL_ABBREVIATIONS[channel_abbreviation]

            # For image files that don't start with 'T_' guess the material channel by parsing for tags in the file name that would ID it.
            else:

                # Create a list of tags used in this files name.
                tags = split_filename_by_components(file.name)
                channel_tags_in_filename = []
                for tag in tags:
                    if tag in MATERIAL_CHANNEL_TAGS:
                        channel_tags_in_filename.append(MATERIAL_CHANNEL_TAGS[tag])

                # Don't import files that have no material channel tag detected in it's file name.
                if len(channel_tags_in_filename) > 0:

                    # Start by assuming the correct material channel is the one that appears the least in the file name.
                    # I.E: Selected files: RoughMetal_002_2k_Color, RoughMetal_002_2k_Normal, RoughMetal_002_2k_Metallic, RoughMetal_002_2k_Rough
                    # For the first file in the above example, the correct material channel would be color,
                    # because 'metallic' appears more than once accross all user selected image files.
                    detected_material_channel = channel_tags_in_filename[0]
                    material_channel_occurances_equal = True
                    for material_channel_name in channel_tags_in_filename:
                        if material_channel_occurance[material_channel_name] < material_channel_occurance[detected_material_channel]:
                            detected_material_channel = material_channel_name
                            material_channel_occurances_equal = False
                    
                    # If all material channels identified in the files name occur equally throughout all selected filenames,
                    # use the material channel that occurs the most in the files name.
                    # I.E: Selected files: RoughMetal_002_2k_Color, RoughMetal_002_2k_Normal, RoughMetal_002_2k_Metallic, RoughMetal_002_2k_Rough
                    # For the third file in the above example, the correct material channel is 'metallic' because that tag appears twice in the name.
                    if material_channel_occurances_equal:
                        for material_channel_name in channel_tags_in_filename:
                            if material_channel_occurance[material_channel_name] > material_channel_occurance[detected_material_channel]:
                                detected_material_channel = material_channel_name

            # Import the image only if the material channel was detected.
            if detected_material_channel != 'NONE':
                folder_directory = os.path.split(self.filepath)
                image_path = os.path.join(folder_directory[0], file.name)
                bpy.ops.image.open(filepath=image_path)
                imported_image = bpy.data.images[file.name]

                # Create a list of all material channels that are packed into this image.
                # For images not using channel packing, this list will have a length of 1.
                packed_channels = []
                channel_packed_format = ""
                if detected_material_channel == 'CHANNEL_PACKED':
                    for tag in tags:
                        if tag in MATERIAL_CHANNEL_TAGS:
                            channel_packed_format = tag
                            for i in range(0, len(channel_packed_format)):
                                if channel_packed_format[i] in MATERIAL_CHANNEL_ABBREVIATIONS:
                                    packed_channel = MATERIAL_CHANNEL_ABBREVIATIONS[channel_packed_format[i]]

                                    # If the active material isn't using the specular material channel, the material channel abbreviated with 'S'
                                    # is more likely 'Smoothness', instead of 'Specular'. Swap the packed channel to Roughness and invert the filter
                                    # to convert the smoothness into roughness.
                                    if packed_channel == 'SPECULAR' and tss.get_material_channel_active('SPECULAR') == False:
                                        packed_channel = 'ROUGHNESS'

                                        invert_r = False
                                        invert_g = False
                                        invert_b = False
                                        invert_a = False
                                        match i:
                                            case 0:
                                                invert_r = True
                                            case 1:
                                                invert_g = True
                                            case 2:
                                                invert_b = True
                                            case 3:
                                                invert_a = True

                                        export_textures.invert_image(imported_image, invert_r, invert_g, invert_b, invert_a)
                                        debug_logging.log_status("Channel packed smoothness was detected and inverted into roughness.", self, type='INFO')

                                    packed_channels.append([packed_channel, get_rgba_channel_from_index(i)])
                else:
                    packed_channels.append([detected_material_channel, -1])

                # Change all material channels to use texture nodes (if they aren't already).
                for packed_channel in packed_channels:
                    channel = packed_channel[0]
                    selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
                    value_node = material_layers.get_material_layer_node('VALUE', selected_layer_index, channel)
                    if value_node.bl_static_type != 'TEX_IMAGE':
                        material_layers.replace_material_channel_node(channel, 'TEXTURE')

                    # Place the image into a material nodes based on texture projection and inferred material channel name.
                    projection_node = material_layers.get_material_layer_node('PROJECTION', selected_layer_index)
                    match projection_node.node_tree.name:
                        case 'ML_UVProjection':
                            value_node = material_layers.get_material_layer_node('VALUE', selected_layer_index, channel)
                            if value_node.bl_static_type == 'TEX_IMAGE':
                                value_node.image = imported_image

                        case 'ML_TriplanarProjection':
                            for i in range(0, 3):
                                value_node = material_layers.get_material_layer_node('VALUE', selected_layer_index, channel, node_number=i + 1)
                                if value_node.bl_static_type == 'TEX_IMAGE':
                                    value_node.image = imported_image

                # If the image is detected to be using channel packing, adjust the output of the material channel.
                if detected_material_channel == 'CHANNEL_PACKED':
                    for i in range(0, len(packed_channels)):
                        channel = packed_channels[i][0]
                        output_channel = packed_channels[i][1]
                        material_layers.set_material_channel_output_channel(channel, output_channel, selected_layer_index)

                # Select the first image file in the canvas painting window.
                if selected_image_file == False:
                    context.scene.tool_settings.image_paint.canvas = imported_image
                    selected_image_file = True

                # Update the imported images colorspace based on it's specified material channel.
                image_utilities.set_image_colorspace_by_material_channel(imported_image, detected_material_channel)

                # Print a warning about using DirectX normal maps for users if it's detected they are using one.
                if detected_material_channel == 'NORMAL':
                    if image_utilities.check_for_directx(file.name):
                        self.report({'INFO'}, "DirectX normal map import detected, normals may be inverted. You should use an OpenGL normal map instead.")

                # Copy the imported image to a folder next to the blend file for file management purposes.
                # This happens only if 'save imported textures' is on in the add-on preferences.
                image_utilities.save_raw_image(image_path, imported_image.name)

            else :
                debug_logging.log("No material channel detected for file: {0}".format(file.name))

        return {'FINISHED'}
    
class MATLAYER_OT_merge_materials(Operator):
    bl_idname = "matlayer.merge_materials"
    bl_label = "Merge Materials"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Merges all layers from the selected material into the active material. Any mesh map textures in the merged material will be replaced by the mesh maps on the active object"

    def execute(self, context):
        if blender_addon_utils.verify_material_operation_context(self) == False:
            return {'FINISHED'}

        merge_material = bpy.context.scene.matlayer_merge_material
        if merge_material:
            layer_count = material_layers.count_layers(merge_material)
            if (layer_count) <= 0:
                debug_logging.log_status("No layers to merge in the merge material.", self, type='ERROR')
                return {'FINISHED'}

            else:
                active_material = bpy.context.active_object.active_material
                for i in range(0, layer_count):
                    
                    # Duplicate the layer node tree and add a new layer group node to the tree.
                    merge_layer_node = merge_material.node_tree.nodes.get(str(i))
                    if merge_layer_node:
                        if merge_layer_node.node_tree:
                            duplicated_node_tree = blender_addon_utils.duplicate_node_group(merge_layer_node.node_tree.name)
                            if duplicated_node_tree:
                                new_layer_slot_index = material_layers.add_material_layer_slot()

                                duplicated_node_tree.name = "{0}_{1}".format(active_material.name, str(new_layer_slot_index))
                                new_layer_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
                                new_layer_group_node.node_tree = duplicated_node_tree
                                new_layer_group_node.name = str(new_layer_slot_index) + "~"
                                new_layer_group_node.label = merge_layer_node.label
                                
                                material_layers.reindex_layer_nodes(change_made='ADDED_LAYER', affected_layer_index=new_layer_slot_index)
                                material_layers.organize_layer_group_nodes()
                                material_layers.link_layer_group_nodes(self)
                                layer_masks.organize_mask_nodes()

                        # Clear the mask stack from the new layer.
                        masks = bpy.context.scene.matlayer_masks
                        masks.clear()

                        # Duplicate all masks associated with that layer.
                        mask_count = layer_masks.count_masks(i)
                        for c in range(0, mask_count):
                            original_mask_node = layer_masks.get_mask_node('MASK', i, c)
                            if original_mask_node:
                                duplicated_node_tree = blender_addon_utils.duplicate_node_group(original_mask_node.node_tree.name)
                                if duplicated_node_tree:
                                    new_mask_slot_index = layer_masks.add_mask_slot()
                                    duplicated_mask_name = layer_masks.format_mask_name(bpy.context.active_object.active_material.name, new_layer_slot_index, new_mask_slot_index) + "~"
                                    duplicated_node_tree.name = duplicated_mask_name
                                    new_mask_group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
                                    new_mask_group_node.node_tree = duplicated_node_tree
                                    new_mask_group_node.name = duplicated_mask_name
                                    new_mask_group_node.label = original_mask_node.label

                                    layer_masks.reindex_masks('ADDED_MASK', new_layer_slot_index, affected_mask_index=i)

                        layer_masks.link_mask_nodes(new_layer_slot_index)
                        layer_masks.organize_mask_nodes()

            bpy.context.scene.matlayer_merge_material = None
            debug_logging.log_status("Merged materials.", self, type='INFO')

        else:
            debug_logging.log_status("Merge material specified is empty, or invalid.", self, type='ERROR')
            return {'FINISHED'}
        return {'FINISHED'}