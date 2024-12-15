# This file contains baking operators and settings for common mesh map bake types.

import os
import time
import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import StringProperty, PointerProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty
from ..core import material_layers
from ..core import blender_addon_utils
from ..core import debug_logging
from ..core import texture_set_settings as tss

MESH_MAP_MATERIAL_NAMES = (
    "BakeNormals",
    "BakeAmbientOcclusion",
    "BakeCurvature",
    "BakeThickness",
    "BakeWorldSpaceNormals"
)

MESH_MAP_GROUP_NAMES = (
    "ML_AmbientOcclusion",
    "ML_Curvature",
    "ML_Thickness",
    "ML_WorldSpaceNormals"
)

MESH_MAP_TYPES = (
    "NORMALS", 
    "AMBIENT_OCCLUSION",
    "CURVATURE", 
    "THICKNESS", 
    "WORLD_SPACE_NORMALS"
)

MESH_MAP_ANTI_ALIASING = [
    ("NO_AA", "No AA", "No anti aliasing will be applied to output mesh map textures"),
    ("2X", "2xAA", "Mesh maps will be rendered at 2x scale and then scaled down to effectively apply anti-aliasing"),
    ("4X", "4xAA", "Mesh maps will be rendered at 4x scale and then scaled down to effectively apply anti-aliasing")
]

MESH_MAP_UPSCALE_MULTIPLIER = [
    ("NO_UPSCALE", "No Upscale", "All mesh maps will be baked at the pixel resolution defined in this materials texture set"),
    ("1_75X", "1.75x Upscale", "All mesh maps will be baked at 0.75 of the pixel resolution defined in this materials texture set and then upscaled to match the texture set resolution"),
    ("2X", "2x Upscale", "All mesh maps will be baked at half of the pixel resolution defined in this materials texture set and then upscaled to match the texture set resolution")
]

MESH_MAP_BAKING_QUALITY = [
    ("TEST_QUALITY", "Test Quality", "Test quality sampling, ideal for quickly testing the output of mesh map bakes. Not recommended for use in production (1 sample)"),
    ("EXTREMELY_LOW_QUALITY", "Extremely Low Quality", "Extremely low baking quality (8 samples), generally the result is too low quality for use in production"),
    ("LOW_QUALITY", "Low Quality", "Low baking quality, useful for when you want somewhat accurate mesh map data produced quickly (16 samples)"),
    ("RECOMMENDED_QUALITY", "Recommended Quality", "Recommended baking quality, ideal for most use cases (32 samples)"),
    ("HIGH_QUALITY", "High Quality", "High baking quality, useful for when you want slightly more accurate mesh map data (64 samples)"),
    ("VERY_HIGH_QUALITY", "Very High Quality", "Very high quality sampling, for significantly more accurate mesh map data, not recommended for standard use, baking times will be long (128 samples)"),
    ("INSANE_QUALITY", "Insane Quality", "Very high sampling, for hyper accurate mesh map data output, not recommended for standard use. Render times are very long (256 samples)")
]

MESH_MAP_CAGE_MODE = [
    ("NO_CAGE", "No Cage", "No cage will be used when baking mesh maps. This can in rare cases produce better results than using a cage"),
    ("MANUAL_CAGE", "Manual Cage", "Insert a manually created cage to be used when baking mesh maps. Baking using a cage can cause some skewing of the baked data if the cage extends too much, or missing normal data in areas where the geometry is not covered by the cage. For some objects that have small crevaces where cage mesh normals would intersect if extruded defining a manual cage object will produce the best results")
]


#----------------------------- UPDATING FUNCTIONS -----------------------------#


def update_occlusion_samples(self, context):
    '''Updates the occlusion samples setting in the active material'''
    baking_settings = bpy.context.scene.matlayer_baking_settings
    node = get_meshmap_node('AMBIENT_OCCLUSION')
    if node:
        node.samples = baking_settings.occlusion_samples

def update_occlusion_distance(self, context):
    '''Updates the occlusion distance setting in the active material'''
    baking_settings = bpy.context.scene.matlayer_baking_settings
    node = get_meshmap_node('AMBIENT_OCCLUSION')
    if node:
        node.inputs.get('Distance').default_value = baking_settings.occlusion_distance

def update_occlusion_intensity(self, context):
    '''Updates the occlusion contrast setting in the active material.'''
    baking_settings = bpy.context.scene.matlayer_baking_settings
    node = get_meshmap_node('AMBIENT_OCCLUSION_INTENSITY')
    if node:
        node.inputs[1].default_value = baking_settings.occlusion_intensity

def update_local_occlusion(self, context):
    '''Updates the local occlusion setting in the active material.'''
    baking_settings = bpy.context.scene.matlayer_baking_settings
    node = get_meshmap_node('AMBIENT_OCCLUSION')
    if node:
        node.only_local = baking_settings.local_occlusion

def update_bevel_radius(self, context):
    baking_settings = bpy.context.scene.matlayer_baking_settings
    node = get_meshmap_node('BEVEL')
    if node:
        if baking_settings.relative_to_bounding_box:
            bounding_box_multiplier = get_bounding_box_multiplier()
            node.inputs[0].default_value = baking_settings.bevel_radius * bounding_box_multiplier
        else:
            node.inputs[0].default_value = baking_settings.bevel_radius

def update_bevel_samples(self, context):
    baking_settings = bpy.context.scene.matlayer_baking_settings
    node = get_meshmap_node('BEVEL')
    if node:
        node.samples = baking_settings.bevel_samples

def update_thickness_distance(self, context):
    baking_settings = bpy.context.scene.matlayer_baking_settings
    node = get_meshmap_node('THICKNESS')
    if node:
        node.inputs[1].default_value = baking_settings.thickness_distance

def update_local_thickness(self, context):
    baking_settings = bpy.context.scene.matlayer_baking_settings
    node = get_meshmap_node('THICKNESS')
    if node:
        node.only_local = baking_settings.local_thickness

def update_thickness_samples(self, context):
    baking_settings = bpy.context.scene.matlayer_baking_settings
    node = get_meshmap_node('THICKNESS')
    if node:
        node.samples = baking_settings.thickness_samples


#----------------------------- HELPER FUNCTIONS -----------------------------#


def get_bounding_box_multiplier():
    '''Returns the average of the active mesh dimensions to multiply into distance based baking properties.'''
    active_object = bpy.context.active_object
    bounding_box_multiplier = (active_object.dimensions[0] + active_object.dimensions[1] + active_object.dimensions[2]) / 3
    return bounding_box_multiplier

def get_meshmap_node(node_name):
    '''Returns a node found within a mesh map material setup if it exists.'''
    active_object = bpy.context.active_object
    if active_object:
        if active_object.active_material:
            node = active_object.active_material.node_tree.nodes.get('MESH_MAP')
            if node:
                return node.node_tree.nodes.get(node_name)
            else:
                debug_logging.log("Mesh map group node does not exist.")

def get_meshmap_name(mesh_name, mesh_map_type):
    '''Returns the image file name for the mesh map of the specified type. The mesh name can be an objects name if the object is a mesh type.'''
    match mesh_map_type:
        case 'AMBIENT_OCCLUSION':
            return "{0}_AO".format(mesh_name)

        case 'CURVATURE':
            return "{0}_Curvature".format(mesh_name)

        case 'THICKNESS':
            return "{0}_Thickness".format(mesh_name)

        case 'NORMALS':
            return "{0}_Normals".format(mesh_name)
        
        case 'WORLD_SPACE_NORMALS':
            return "{0}_WorldSpaceNormals".format(mesh_name)

def get_meshmap_image(mesh_name, mesh_map_type):
    '''Returns a mesh map image if it exists. The mesh name can be an objects name if the object is a mesh type.'''
    mesh_map_name = get_meshmap_name(mesh_name, mesh_map_type)
    return bpy.data.images.get(mesh_map_name)

def create_bake_image(mesh_map_type, object_name, baking_settings):
    '''Creates a new image in Blender's data to bake to.'''

    # Use the object's name and bake type to define the bake image name.
    mesh_map_name = get_meshmap_name(object_name, mesh_map_type)

    # For anti-aliasing, mesh maps are baked at a higher resolution and then scaled down (which effectively applies anti-aliasing).
    # Define the anti-aliasing multiplier based on mesh map settings.
    anti_aliasing_multiplier = 1
    match getattr(baking_settings.mesh_map_anti_aliasing, mesh_map_type.lower() + "_anti_aliasing", '1X'):
        case '1X':
            anti_aliasing_multiplier = 1
        case '2X':
            anti_aliasing_multiplier = 2
        case '4X':
            anti_aliasing_multiplier = 4

    # Set an image pixel resolution multiplier for mesh map upscaling.
    match baking_settings.mesh_map_upscaling_multiplier:
        case 'NO_UPSCALE':
            upscale_multiplier = 1.0
        case '1_75X':
            upscale_multiplier = 0.75
        case '2X':
            upscale_multiplier = 0.5

    # Create a new image in Blender's data, delete existing bake image if it exists.
    new_image_width = int(round(tss.get_texture_width() * anti_aliasing_multiplier * upscale_multiplier))
    new_image_height = int(round(tss.get_texture_height() * anti_aliasing_multiplier * upscale_multiplier))
    mesh_map_image = blender_addon_utils.create_image(
        new_image_name=mesh_map_name,
        image_width=new_image_width,
        image_height=new_image_height,
        base_color=(0.0, 0.0, 0.0, 1.0),
        alpha_channel=False,
        thirty_two_bit=True,
        add_unique_id=False,
        delete_existing=True
    )

    matlayer_mesh_map_folder = blender_addon_utils.get_texture_folder_path(folder='MESH_MAPS')
    mesh_map_image.filepath = "{0}/{1}.{2}".format(matlayer_mesh_map_folder, mesh_map_image.name, 'png')
    mesh_map_image.file_format = 'PNG'
    mesh_map_image.colorspace_settings.name = 'Non-Color'
    mesh_map_image.use_fake_user = True
    return mesh_map_image

def apply_baking_settings():
    '''Applies baking settings to existing node setups before baking.'''

    # Apply occlusion settings.
    update_occlusion_samples(None, None)
    update_occlusion_distance(None, None)
    update_occlusion_intensity(None, None)
    update_local_occlusion(None, None)

    # Apply curvature settings.
    update_bevel_radius(None, None)
    update_bevel_samples(None, None)

    # Apply thickness settings.
    update_thickness_samples(None, None)
    update_thickness_distance(None, None)
    update_local_thickness(None, None)

def apply_mesh_map_quality(baking_settings):
    '''Applies mesh map quality settings.'''
    match baking_settings.mesh_map_quality:
        case 'TEST_QUALITY':
            bpy.context.scene.cycles.samples = 1

        case 'EXTREMELY_LOW_QUALITY':
            bpy.context.scene.cycles.samples = 8

        case 'LOW_QUALITY':
            bpy.context.scene.cycles.samples = 16

        case 'RECOMMENDED_QUALITY':
            bpy.context.scene.cycles.samples = 32

        case 'HIGH_QUALITY':
            bpy.context.scene.cycles.samples = 64

        case 'VERY_HIGH_QUALITY':
            bpy.context.scene.cycles.samples = 128

        case 'INSANE_QUALITY':
            bpy.context.scene.cycles.samples = 256

def bake_mesh_map(mesh_map_type, object_name, self):
    '''Applies a premade baking material to the active object and starts baking. Returns true if baking was successful.'''
    baking_settings = bpy.context.scene.matlayer_baking_settings

    # Append a premade material for baking the specified mesh map type.
    match mesh_map_type:
        case 'AMBIENT_OCCLUSION':
            temp_bake_material = blender_addon_utils.append_material('BakeAmbientOcclusion')
            self._mesh_map_group_node_name = "ML_AmbientOcclusion"

        case 'CURVATURE':
            temp_bake_material = blender_addon_utils.append_material('BakeCurvature')
            self._mesh_map_group_node_name = "ML_Curvature"

        case 'THICKNESS':
            temp_bake_material = blender_addon_utils.append_material('BakeThickness')
            self._mesh_map_group_node_name = "ML_Thickness"

        case 'NORMALS':
            temp_bake_material = blender_addon_utils.append_material('BakeNormals')

        case 'WORLD_SPACE_NORMALS':
            temp_bake_material = blender_addon_utils.append_material('BakeWorldSpaceNormals')
            self._mesh_map_group_node_name = "ML_WorldSpaceNormals"

    self._temp_bake_material_name = temp_bake_material.name

    # Skip normal map baking if there is no high poly object defined, no normal information can be baked without a high poly object.
    if mesh_map_type == 'NORMALS' and baking_settings.high_poly_object == None:
        debug_logging.log("Skipping normal map baking, no high poly object is specified.")
        return True

    # Create and assign an image to bake the mesh map to.
    new_bake_image = create_bake_image(mesh_map_type, object_name, baking_settings)
    self._mesh_map_image_index = bpy.data.images.find(new_bake_image.name)
    bake_image_node = temp_bake_material.node_tree.nodes.get("BAKE_IMAGE")
    if bake_image_node:
        bake_image_node.image = new_bake_image
        for node in temp_bake_material.node_tree.nodes:
            node.select = False
        bake_image_node.select = True
        temp_bake_material.node_tree.nodes.active = bake_image_node
        bpy.context.scene.tool_settings.image_paint.canvas = new_bake_image
    else:
        debug_logging.log_status("Error: Image node not found in premade mesh map baking material setup.", self, type='ERROR')
        return False

    # Apply the bake material to the low poly object.
    active_object = bpy.context.active_object
    if len(bpy.context.object.material_slots) > 0:
        for material_slot in bpy.context.object.material_slots:
            material_slot.material = temp_bake_material
    else:
        active_object.data.materials.append(temp_bake_material)

    # If a high poly object is specified...
    high_poly_object = baking_settings.high_poly_object
    if high_poly_object != None:
        # Apply the bake material to the high poly object (high poly details for curvature, ambient occlusion will not be transfered otherwise).
        if len(high_poly_object.material_slots) > 0:
            for material_slot in high_poly_object.material_slots:
                material_slot.material = temp_bake_material
        else:
            high_poly_object.data.materials.append(temp_bake_material)

        # Select the low poly and high poly objects in the correct order.
        bpy.ops.object.select_all(action='DESELECT')
        high_poly_object.select_set(True)
        active_object.select_set(True)

        # Apply high to low poly render settings
        bpy.context.scene.render.bake.use_selected_to_active = True

    else:
        bpy.context.scene.render.bake.use_selected_to_active = False

    # Apply mesh map quality and baking settings.
    apply_baking_settings()
    apply_mesh_map_quality(baking_settings)
    bpy.context.scene.render.bake.margin = baking_settings.uv_padding

    # Trigger the baking process.
    match mesh_map_type:
        case 'NORMALS':
            bpy.ops.object.bake('INVOKE_DEFAULT', type='NORMAL')
        case _:
            bpy.ops.object.bake('INVOKE_DEFAULT', type='EMIT')

    # Print debug info...
    mesh_map_type = mesh_map_type.replace('_', ' ')
    mesh_map_type = blender_addon_utils.capitalize_by_space(mesh_map_type)
    debug_logging.log("Starting baking: {0}".format(mesh_map_type))

    return True

def delete_meshmap(meshmap_type, self):
    '''Deletes the meshmap of the specified type for the active object if it exists from the blend files data.'''
    meshmap_name = get_meshmap_name(bpy.context.active_object.name, meshmap_type)
    if bpy.context.active_object:
        meshmap_image = bpy.data.images.get(meshmap_name)
        if meshmap_image:
            bpy.data.images.remove(meshmap_image)
            self.report({'INFO'}, "{0} mesh map was deleted.".format(meshmap_name))
        else:
            self.report({'INFO'}, "{0} mesh map doesn't exist.".format(meshmap_name))
    else:
        self.report({'INFO'}, "No active object to delete mesh maps for, re-select the object you wish to delete mesh maps for.")

def get_batch_bake_mesh_maps():
    '''Returns a list of mesh maps checked for inclusion in the batch baking process.'''
    baking_settings = bpy.context.scene.matlayer_baking_settings
    mesh_maps_to_bake = []

    if baking_settings.bake_ambient_occlusion:
        mesh_maps_to_bake.append('AMBIENT_OCCLUSION')

    if baking_settings.bake_curvature:
        mesh_maps_to_bake.append('CURVATURE')

    if baking_settings.bake_thickness:
        mesh_maps_to_bake.append('THICKNESS')

    if baking_settings.bake_normals:
        mesh_maps_to_bake.append('NORMALS')

    if baking_settings.bake_world_space_normals:
        mesh_maps_to_bake.append('WORLD_SPACE_NORMALS')

    return mesh_maps_to_bake

def clean_mesh_map_assets():
    '''Removes all mesh map baking materials and group nodes if they exist.'''
    # Remove all mesh map materials.
    for mesh_map_material_name in MESH_MAP_MATERIAL_NAMES:
        mesh_map_material = bpy.data.materials.get(mesh_map_material_name)
        if mesh_map_material:
            bpy.data.materials.remove(mesh_map_material)

    # Remove all mesh map group nodes.
    for group_node_name in MESH_MAP_GROUP_NAMES:
        mesh_map_group_node = bpy.data.node_groups.get(group_node_name)
        if mesh_map_group_node:
            bpy.data.node_groups.remove(mesh_map_group_node)

def create_baking_cage(self):
    '''Creates a duplicate of the selected object, scaled slightly up to act as a cage object for baking high to low poly mesh map textures.'''

    # This function requires a selected (active object), abort if there is not active object.
    active_object = bpy.context.active_object
    if not active_object:
        return
    
    # If the active object being selected is a cage object, don't make a new cage.
    selecting_cage = active_object.name.endswith("_Cage")
    if selecting_cage:
        debug_logging.log_status("Selected object is a bake cage.", self, type='INFO')
        return
    
    # Make a scaled up duplicate of the object to act as the base mesh.
    cage_object = active_object.copy()
    cage_mesh = active_object.data.copy()
    cage_object.data = cage_mesh
    cage_object.name = active_object.name + "_Cage"
    bpy.context.collection.objects.link(cage_object)
    bpy.context.scene.render.bake.cage_object = cage_object
    blender_addon_utils.select_only(cage_object)
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.shrink_fatten(
        value=0.01,
        use_even_offset=False,
        mirror=True,
        use_proportional_edit=False,
        proportional_edit_falloff='SMOOTH', 
        proportional_size=1,
        use_proportional_connected=False, 
        use_proportional_projected=False, 
        snap=False
    )

    # Change viewport shading so users can see the applied cage material.
    bpy.context.space_data.shading.color_type = 'MATERIAL'
    bpy.context.space_data.shading.type = 'SOLID'

    # Create a new material for the cage object.
    # This material will be slightly transparent to allow the user to see through the cage object.
    # The material will display slightly see-through even when in 'shaded' viewport display mode.
    cage_material_name = 'Cage Material'
    cage_material = bpy.data.materials.get(cage_material_name)
    if not cage_material:
        cage_material = bpy.data.materials.new(name=cage_material_name)
        cage_material.diffuse_color = [1.0, 0.3, 0.0, 0.3]
        cage_material.metallic = 0.0
        cage_material.roughness = 1.0

    # Must be in object mode to make changes to the material.
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    # Remove all material slots on the cage object.
    cage_object.data.materials.clear()
    cage_object.data.materials.append(cage_material)

    # Show a message for users.
    debug_logging.log_status("Created new bake cage object.", self, type='INFO')

def delete_baking_cage(self):
    '''Deletes the selected baking cage, or the bake cage for the selected object if one exists.'''

    # This function requires a selected (active object), abort if there is not active object.
    active_object = bpy.context.active_object
    if not active_object:
        return
    
    # If the active object being selected is a bake cage, delete it.
    selecting_cage = active_object.name.endswith("_Cage")
    if selecting_cage:
        bpy.data.objects.remove(active_object)
        debug_logging.log_status("Removed selected bake cage object.", self, type='INFO')

    # Delete the bake cage if one exists for the selected object.
    else:
        cage_object = bpy.data.objects.get(active_object.name + "_Cage")
        if cage_object:
            bpy.data.objects.remove(cage_object)
            debug_logging.log_status("Removed bake cage for selected object.", self, type='INFO')


#----------------------------- OPERATORS AND PROPERTIES -----------------------------#


class MATLAYER_mesh_map_anti_aliasing(PropertyGroup):
    normals_anti_aliasing: EnumProperty(items=MESH_MAP_ANTI_ALIASING, name="Normal Map Anti Aliasing", description="Anti aliasing for output normal maps. Higher values creates softer, less pixelated edges around geometry data from the high poly mesh that's baked into the texture. This value multiplies the initial bake resolution before being scaled down to the target resolution effectively applying anti-aliasing, but also increasing bake time", default='NO_AA')
    ambient_occlusion_anti_aliasing: EnumProperty(items=MESH_MAP_ANTI_ALIASING, name="Ambient Occlusion Anti Aliasing", description="Anti aliasing for output ambient occlusion maps. Higher values creates softer, less pixelated edges around geometry data from the high poly mesh that's baked into the texture. This value multiplies the initial bake resolution before being scaled down to the target resolution effectively applying anti-aliasing, but also increasing bake time", default='NO_AA')
    curvature_anti_aliasing: EnumProperty(items=MESH_MAP_ANTI_ALIASING, name="Curvature Anti Aliasing", description="Anti aliasing for output curvature maps. Higher values creates softer, less pixelated edges around geometry data from the high poly mesh that's baked into the texture. This value multiplies the initial bake resolution before being scaled down to the target resolution effectively applying anti-aliasing, but also increasing bake time", default='NO_AA')
    thickness_anti_aliasing: EnumProperty(items=MESH_MAP_ANTI_ALIASING, name="Thickness Anti Aliasing", description="Anti aliasing for output thickness maps. Higher values creates softer, less pixelated edges around geometry data from the high poly mesh that's baked into the texture. This value multiplies the initial bake resolution before being scaled down to the target resolution effectively applying anti-aliasing, but also increasing bake time", default='NO_AA')
    world_space_normals_anti_aliasing: EnumProperty(items=MESH_MAP_ANTI_ALIASING, name="World Space Normals Anti Aliasing", description="Anti aliasing for output world space normal maps. Higher values creates softer, less pixelated edges around geometry data from the high poly mesh that's baked into the texture. This value multiplies the initial bake resolution before being scaled down to the target resolution effectively applying anti-aliasing, but also increasing bake time", default='NO_AA')

class MATLAYER_baking_settings(bpy.types.PropertyGroup):
    high_poly_object: PointerProperty(
        type=bpy.types.Object, 
        name="High Poly Object", 
        description="The high poly object (must be a mesh) from which mesh detail will be baked to texture maps. The high poly mesh should generally be overlapped by your low poly mesh before starting baking. You do not need to provide a high poly mesh for baking texture maps"
    )

    mesh_map_anti_aliasing: PointerProperty(
        type=MATLAYER_mesh_map_anti_aliasing, 
        name="Mesh Map Anti Aliasing"
    )

    mesh_map_upscaling_multiplier: EnumProperty(
        items=MESH_MAP_UPSCALE_MULTIPLIER,
        name="Mesh Map Upscale Multiplier",
        description="Bakes the mesh map at a smaller resolution, then upscales the mesh map image to match the texture set resolution. Baking at a lower resolution and upscaling allows mesh maps to bake much faster, but with lower quality and accuracy. A small amount of blurring caused by upscaling mesh map images slightly can result in more useful mesh maps",
        default='1_75X'
    )

    mesh_map_quality: EnumProperty(
        items=MESH_MAP_BAKING_QUALITY, 
        name="Mesh Map Quality", 
        description="Bake quality",
        default='RECOMMENDED_QUALITY'
    )

    cage_mode: EnumProperty(
        items=MESH_MAP_CAGE_MODE,
        name="Cage Mode",
        description="Mode to define if a cage is used for mesh map baking",
        default='MANUAL_CAGE'
    )

    cage_upscale: FloatProperty(
        name="Cage Upscale",
        description="Upscales a duplicate of the low poly mesh by the specified amount to use as a cage for mesh map baking", 
        default=0.01,
        min=0.0,
        soft_max=0.1,
        step=0.1,
        precision=4
    )

    uv_padding: IntProperty(
        name="UV Padding",
        description="Amount of padding in pixels to extend the baked data out of UV islands. This ensures there is no visible seams between UV splits",
        default=14,
        min=4,
        max=64
    )

    bake_normals: BoolProperty(
        name="Bake Normal", 
        description="Toggle for baking normal maps for baking as part of the batch baking operator", 
        default=True
    )

    bake_ambient_occlusion: BoolProperty(
        name="Bake Ambient Occlusion", 
        description="Toggle for baking ambient occlusion as part of the batch baking operator", 
        default=True
    )

    bake_curvature: BoolProperty(
        name="Bake Curvature", 
        description="Toggle for baking curvature as part of the batch baking operator", 
        default=True
    )

    bake_thickness: BoolProperty(
        name="Bake Thickness", 
        description="Toggle for baking thickness as part of the batch baking operator", 
        default=True
    )

    bake_world_space_normals: BoolProperty(
        name="Bake World Space Normals", 
        description="Toggle for baking world space normals as part of the batch baking operator", 
        default=True
    )

    # Ambient Occlusion Settings
    occlusion_samples: IntProperty(
        name="Occlusion Samples", 
        description="Number of rays to trace for the occlusion shader evaluation. Higher values slightly increase occlusion quality at the cost of increased bake time. In most cases the default value is ideal", 
        default=16, 
        min=1,
        max=128,
        update=update_occlusion_samples
    )
    
    occlusion_distance: FloatProperty(
        name="Occlusion Distance", 
        description="Occlusion distance between polygons. Lower values results in less occlusion. In most cases the default value is ideal",
        default=1.0,
        min=0.1,
        max=1.0,
        update=update_occlusion_distance
    )

    occlusion_intensity: FloatProperty(
        name="Occlusion Intensity",
        description="Intensity of the ambient occlusion, higher values result in more intense occlusion shadows",
        default=1.5,
        min=0.1,
        max=10.0,
        update=update_occlusion_intensity
    )

    local_occlusion: BoolProperty(
        name="Local Occlusion",
        description="When off, other objects within the scene will contribute to the baked ambient occlusion",
        default=True,
        update=update_local_occlusion
    )

    # Curvature Settings
    bevel_radius: FloatProperty(
        name="Bevel Radius",
        description="Radius of the sharp edges baked into the curvature map",
        default=0.0025,
        soft_min=0.001,
        soft_max=0.01,
        step=0.1,
        precision=4,
        update=update_bevel_radius
    )

    bevel_samples: IntProperty(
        name="Bevel Samples",
        description="Number of rays to trace per shader evaluation for curvature bevel (sharp edges) samples. Higher samples results in sharper edges",
        default=2,
        min=2,
        max=16,
        update=update_bevel_samples
    )

    relative_to_bounding_box: BoolProperty(
        name="Relative to Bounding Box",
        description="If true, the sampling radius used in curvature mesh map baking will be multiplied by the averaged size of the active objects bounding box. This allows the sampling radius to stay roughly correct among varying sizes of objects without the need to manually adjust the property",
        default=True
    )

    # Thickness Settings
    thickness_samples: IntProperty(
        name="Thickness Samples", 
        description="Number of rays to trace for the thickness shader evaluation. Higher values slightly increase thickness quality at the cost of increased bake time. In most cases the default value is ideal", 
        default=16, 
        min=1,
        max=128,
        update=update_thickness_samples
    )

    thickness_distance: FloatProperty(
        name="Thickness Distance",
        description="Distance for thickness rays.",
        default=0.1,
        min=0.0,
        max=1.0,
        update=update_thickness_distance
    )

    local_thickness: BoolProperty(
        name="Local Thickness",
        description="When off, other objects within the scene will contribute to the baked thickness",
        default=True,
        update=update_local_thickness
    )

class MATLAYER_OT_batch_bake(Operator):
    bl_idname = "matlayer.batch_bake"
    bl_label = "Batch Bake"
    bl_description = "Bakes all checked mesh texture maps in succession. Note that this function can take a few minutes, especially on slower computers, or when using CPU for rendering. Textures are created at the defined texture set resolution"

    _timer = None
    _temp_bake_material_name = ""
    _mesh_map_image_index = 0
    _mesh_map_group_node_name = ""
    _mesh_maps_to_bake = []
    _baked_mesh_map_count = 0
    _original_material_names = []
    _original_render_engine = None
    _start_bake_time = 0
    _exclude_layer_collections = []

    # Users must have an object selected to call this operator.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def modal(self, context, event):
        # If a user presses escape, mesh map baking will cancel.
        if event.type in {'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}
        
        if event.type == 'TIMER':
            # If a mesh map isn't actively baking, move to the next mesh map, or end the function.
            if not bpy.app.is_job_running('OBJECT_BAKE'):
                mesh_map_type = self._mesh_maps_to_bake[self._baked_mesh_map_count]
                mesh_map_name = get_meshmap_name(bpy.context.active_object.name, mesh_map_type)
                mesh_map_image = bpy.data.images.get(mesh_map_name)
                if mesh_map_image:
                    # Scale baked textures down to apply anti-aliasing.
                    baking_settings = bpy.context.scene.matlayer_baking_settings
                    match getattr(baking_settings.mesh_map_anti_aliasing, mesh_map_type.lower() + "_anti_aliasing", '1X'):
                        case '2X':
                            mesh_map_image.scale(int(mesh_map_image.size[0] * 0.5), int(mesh_map_image.size[1] * 0.5))
                        case '4X':                            
                            mesh_map_image.scale(int(mesh_map_image.size[0] * 0.25), int(mesh_map_image.size[1] * 0.25))

                    # Scale baked textures up to match the texture set resolution size.
                    match baking_settings.mesh_map_upscaling_multiplier:
                        case '1_75X':
                            mesh_map_image.scale(int(round(mesh_map_image.size[0] * 1.333333)), int(round(mesh_map_image.size[1] * 1.333333)))
                        case '2X':
                            mesh_map_image.scale(int(mesh_map_image.size[0] * 2), int(mesh_map_image.size[1] * 2))

                    # Save the mesh map to disk.
                    mesh_map_image.save(quality=0)

                # Log mesh map baking completion.
                mesh_map_type = mesh_map_type.replace('_', ' ')
                mesh_map_type = blender_addon_utils.capitalize_by_space(mesh_map_type)
                debug_logging.log("Finished baking: {0}".format(mesh_map_type))
                self._baked_mesh_map_count += 1

                # Remove temporary bake materials and node groups.
                temp_bake_material = bpy.data.materials.get(self._temp_bake_material_name)
                if temp_bake_material:
                    bpy.data.materials.remove(temp_bake_material)

                bake_node_group = bpy.data.node_groups.get(self._mesh_map_group_node_name)
                if bake_node_group:
                    bpy.data.node_groups.remove(bake_node_group)

                # Bake the next mesh map.
                if self._baked_mesh_map_count < len(self._mesh_maps_to_bake):
                    mesh_map_type = self._mesh_maps_to_bake[self._baked_mesh_map_count]
                    baked_successfully = bake_mesh_map(mesh_map_type, bpy.context.active_object.name, self)

                    # If there is an error with baking a mesh map, finish the operation.
                    if baked_successfully == False:
                        debug_logging.log("Baking error.")
                        self.finish(context)
                        return {'FINISHED'}

                # Finish the batch baking process if all mesh maps are baked.
                else:
                    self.finish(context)
                    return {'FINISHED'}
                
        return {'PASS_THROUGH'}

    def execute(self, context):

        # Verify the mesh map baking folder is valid.
        mesh_map_folder = blender_addon_utils.get_texture_folder_path(folder='MESH_MAPS')
        folder_valid = blender_addon_utils.verify_folder(mesh_map_folder)
        if not folder_valid:
            debug_logging.log_status("Define a valid mesh map folder before baking, or reset the folder path to 'Default'.", self, type='ERROR')
            return {'FINISHED'}

        # Save the blend file to help users avoid losing work if Blender crashes while baking.
        bpy.ops.wm.save_mainfile()

        # Remove lingering mesh map assets if they exist.
        clean_mesh_map_assets()

        # Set the viewport shading mode to 'Material' (helps bake materials slightly faster while still being able to preview material changes).
        bpy.context.space_data.shading.type = 'MATERIAL'

        # Verify the active object can be baked to.
        if blender_addon_utils.verify_bake_object(self) == False:
            return {'FINISHED'}

        # To avoid errors don't start baking if there is already a bake job running.
        if bpy.app.is_job_running('OBJECT_BAKE') == True:
            debug_logging.log_status("Bake job already in process, cancel or wait until the bake is finished before starting another.", self)
            return {'FINISHED'}
        
        # Pause auto-updates for this add-on while baking.
        bpy.context.scene.pause_auto_updates = True
        debug_logging.log("Starting mesh map baking...", sub_process=False)

        # Record the starting time before baking.
        self._start_bake_time = time.time()

        # Ensure we start this operation in object mode.
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        # Get a list of mesh maps to bake.
        self._mesh_maps_to_bake.clear()
        self._mesh_maps_to_bake = get_batch_bake_mesh_maps()
        if len(self._mesh_maps_to_bake) <= 0:
            debug_logging.log_status("No mesh maps checked for baking.", self, type='INFO')
            return {'FINISHED'}

        baking_settings = bpy.context.scene.matlayer_baking_settings
        low_poly_object = bpy.context.active_object
        high_poly_object = baking_settings.high_poly_object

        # If a high poly object is specified...
        if high_poly_object:

            # Having a high poly object in an excluded layer collection causes baking errors. Make sure all layer collections a high poly object is in is not excluded from the view layer.
            self._exclude_layer_collections.clear()
            view_layer_collections = bpy.context.view_layer.layer_collection.children
            user_collections = high_poly_object.users_collection
            for collection in user_collections:
                layer_collection = view_layer_collections.get(collection.name)
                self._exclude_layer_collections.append(layer_collection.exclude)
                layer_collection.exclude = False

            # Adjust settings based on the selected cage mode.
            match baking_settings.cage_mode:
                case 'NO_CAGE':
                    bpy.context.scene.render.bake.use_cage = False

                case 'MANUAL_CAGE':
                    bpy.context.scene.render.bake.use_cage = True

                    # If a cage object isn't defined, ask the user to define one.
                    cage_object = bpy.context.scene.render.bake.cage_object
                    if cage_object == None:
                        debug_logging.log_status("No cage object, please define a cage object.", self, type='INFO')
                        return {'FINISHED'}
                        
                    # Abort if both a cage and high poly object is defined, 
                    # but the vertex count between the low poly and cage objects don't match.
                    if cage_object and high_poly_object:
                        cage_object_vertex_count = len(cage_object.data.vertices)
                        low_poly_object_vertex_count = len(high_poly_object.data.vertices)
                        debug_logging.log("Cage object vertex count: {0}".format(cage_object_vertex_count))
                        debug_logging.log("High poly object vertex count: {0}".format(low_poly_object_vertex_count))
                        if len(cage_object.data.vertices) != len(low_poly_object.data.vertices):
                            debug_logging.log_status("Vertex count for low poly and cage object must match.", self, type='ERROR')
                            return {'FINISHED'}

            # Ensure the high poly object is visible for rendering.
            high_poly_object.hide_set(False)
            high_poly_object.hide_render = False
        
        # Ensure the low poly object is visible for rendering.
        low_poly_object.hide_set(False)
        low_poly_object.hide_render = False

        # Cache original materials applied to the active object so the materials can be re-applied after baking.
        self._original_material_names.clear()
        low_poly_obj_material_slots = bpy.context.active_object.material_slots
        if len(low_poly_obj_material_slots) > 0:
            for x in low_poly_obj_material_slots:
                if x.material:
                    self._original_material_names.append(x.material.name)
                else:
                    self._original_material_names.append("")

        # Set render engine to Cycles (required for baking) and remember the original render engine so we can reset it after baking.
        self._original_render_engine = bpy.context.scene.render.engine
        bpy.context.scene.render.engine = 'CYCLES'

        # Start baking the mesh map.
        baked_successfully = bake_mesh_map(self._mesh_maps_to_bake[0], low_poly_object.name, self)    
        if baked_successfully == False:
            self.finish(context)
            return {'FINISHED'}

        # Add a timer to provide periodic timer events.
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        # Remove the timer if it exists, it's no longer needed.
        if self._timer:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)

        # High the high poly object, and re-exclude layer collections the high poly object belongs to.
        high_poly_object = bpy.context.scene.matlayer_baking_settings.high_poly_object
        if high_poly_object:
            high_poly_object.hide_set(True)
            high_poly_object.hide_render = True
            
            view_layer_collections = bpy.context.view_layer.layer_collection.children
            user_collections = high_poly_object.users_collection
            for i, collection in enumerate(user_collections):
                layer_collection = view_layer_collections.get(collection.name)
                layer_collection.exclude = self._exclude_layer_collections[i]

        # Re-apply the materials that were originally on the object and delete the temporary bake material.
        for i in range(0, len(self._original_material_names)):
            material = bpy.data.materials.get(self._original_material_names[i])
            if material:
                bpy.context.object.material_slots[i].material = material

        # Reset the render engine.
        bpy.context.scene.render.engine = self._original_render_engine

        # Unpause auto updates, unmark baking mesh maps toggle.
        bpy.context.scene.pause_auto_updates = False

        debug_logging.log_status("Baking mesh map was manually cancelled.", self, 'INFO')

    def finish(self, context):
        # Remove the timer.
        if self._timer:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)

        # High the high poly object, and re-exclude layer collections the high poly object belongs to.
        high_poly_object = bpy.context.scene.matlayer_baking_settings.high_poly_object
        if high_poly_object:
            high_poly_object.hide_set(True)
            high_poly_object.hide_render = True

            view_layer_collections = bpy.context.view_layer.layer_collection.children
            user_collections = high_poly_object.users_collection
            for i, collection in enumerate(user_collections):
                layer_collection = view_layer_collections.get(collection.name)
                layer_collection.exclude = self._exclude_layer_collections[i]

        # Re-apply the materials that were originally on the object.
        for i in range(0, len(self._original_material_names)):
            material = bpy.data.materials.get(self._original_material_names[i])
            if material:
                bpy.context.object.material_slots[i].material = material

        # Select only the low poly object.
        low_poly_object = bpy.context.active_object
        if low_poly_object:
            blender_addon_utils.select_only(low_poly_object)

        # Reset the render engine.
        bpy.context.scene.render.engine = self._original_render_engine

        # Apply mesh maps to the existing material.
        material_layers.apply_mesh_maps()

        # Unpause auto updates, mark baking mesh maps as complete.
        bpy.context.scene.pause_auto_updates = False

        # Log the completion of baking mesh maps.
        end_bake_time = time.time()
        total_bake_time = end_bake_time - self._start_bake_time
        debug_logging.log_status("Baking mesh map(s) completed, total bake time: {0} seconds.".format(round(total_bake_time), 1), self, 'INFO')

class MATLAYER_OT_set_mesh_map_folder(Operator):
    bl_idname = "matlayer.set_mesh_map_folder"
    bl_label = "Set Mesh Maps Folder"
    bl_description = "Opens a file explorer to select the folder where baked mesh maps are externally saved"
    bl_options = {'REGISTER'}

    directory: StringProperty()

    # Filters for only folders.
    filter_folder: BoolProperty(
        default=True,
        options={"HIDDEN"}
    )

    def execute(self, context):
        if not os.path.isdir(self.directory):
            debug_logging.log_status("Invalid directory.", self, type='INFO')
        else:
            context.scene.matlayer_mesh_map_folder = self.directory
            debug_logging.log_status("Export folder set to: {0}".format(self.directory), self, type='INFO')
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MATLAYER_OT_open_mesh_map_folder(Operator):
    bl_idname = "matlayer.open_mesh_map_folder"
    bl_label = "Open Mesh Map Folder"
    bl_description = "Opens the folder in your systems file explorer where mesh map images will be saved after baking"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        matlayer_mesh_map_folder_path = blender_addon_utils.get_texture_folder_path(folder='MESH_MAPS')
        blender_addon_utils.open_folder(matlayer_mesh_map_folder_path, self)
        return {'FINISHED'}

class MATLAYER_OT_preview_mesh_map(Operator):
    bl_idname = "matlayer.preview_mesh_map"
    bl_label = "Preview Mesh Map"
    bl_description = "Replaces all material slots on the selected (active) object with a material used for baking the specified mesh map, then applies viewport and render settings to make the preview visible"

    mesh_map_type: StringProperty(default='AMBIENT_OCCLUSION')

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        if blender_addon_utils.verify_material_operation_context(self, check_active_material=False) == False:
            return {'FINISHED'}

        # Make sure there are no lingering existing mesh map assets.
        clean_mesh_map_assets()

        # Cache the render engine and material mode...
        # This allows them to be re-applied when the mesh map preview is disabled.
        bpy.context.scene["original_render_engine"] = bpy.context.scene.render.engine
        bpy.context.scene["original_viewport_shading_mode"] = bpy.context.space_data.shading.type

        # Cache materials that are applied to the active object inside of the object...
        # this allows the materials to be re-applied when the mesh map preview is disabled.
        active_object = bpy.context.active_object

        for k in active_object.keys():
            if k.startswith('original_material_name_'):
                del k

        if len(active_object.material_slots) > 0:
            for x, slot in enumerate(active_object.material_slots):
                if slot.material:
                    active_object["original_material_name_{0}".format(x)] = slot.material.name
                else:
                    active_object["original_material_name_{0}".format(x)] = ""

        # Append a material that will be used to preview the mesh map.
        match self.mesh_map_type:
            case 'AMBIENT_OCCLUSION':
                mesh_map_material = blender_addon_utils.append_material('BakeAmbientOcclusion')

            case 'CURVATURE':
                mesh_map_material = blender_addon_utils.append_material('BakeCurvature')

            case 'THICKNESS':
                mesh_map_material = blender_addon_utils.append_material('BakeThickness')

            case 'NORMALS':
                mesh_map_material = blender_addon_utils.append_material('BakeNormals')

            case 'WORLD_SPACE_NORMALS':
                mesh_map_material = blender_addon_utils.append_material('BakeWorldSpaceNormals')

        active_object = bpy.context.active_object

        # If there is no material slots on the selected object, add one.
        if len(active_object.material_slots) <= 0:
            active_object.data.materials.append(mesh_map_material)

        # If the object has material slots, assign the new color grid material to all material slots for all selected objects.
        else:
            active_object.active_material_index = 0
            for i in range(len(active_object.material_slots)):
                active_object.material_slots[i].material = mesh_map_material

        # Apply viewport and render engine settings to allow the user to see the mesh map preview.
        bpy.context.space_data.shading.type = 'RENDERED'
        bpy.context.scene.render.engine = 'CYCLES'

        # Apply baking settings to the new material.
        apply_baking_settings()

        return {'FINISHED'}

class MATLAYER_OT_disable_mesh_map_preview(Operator):
    bl_idname = "matlayer.disable_mesh_map_preview"
    bl_label = "Disable Mesh Map Preview"
    bl_description = "Reapplies the previously selected render engine and all of the active objects materials that were in use before the mesh map preview was toggled on"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        clean_mesh_map_assets()

        # Re-apply materials and other settings used before the mesh map preview was toggled on...
        active_object = bpy.context.active_object
        material_index = 0
        for key in active_object.keys():

            # Re-apply materials.
            if key.startswith('original_material_name_'):
                original_material_name = active_object[key]
                original_material = bpy.data.materials.get(original_material_name)
                if original_material:
                    if material_index < len(active_object.material_slots):
                        active_object.material_slots[material_index].material = original_material
                        material_index += 1
                    else:
                        break
                else:
                    debug_logging.log("Material applied before previewing mesh maps no longer exists: {0}".format(original_material_name))

        # Delete custom properties for storing the original material names from the object, they are no longer needed.
        for k in active_object.keys():
            if k.startswith('original_material_name_'):
                del k

        # Re-apply the render engine and the viewport shading mode.
        scene = bpy.context.scene
        scene_keys = scene.keys()
        if 'original_render_engine' in scene_keys:
            bpy.context.scene.render.engine = scene['original_render_engine']
            del scene['original_render_engine']

        if 'original_viewport_shading_mode' in scene_keys:
            bpy.context.space_data.shading.type = scene['original_viewport_shading_mode']
            del scene['original_viewport_shading_mode']

        debug_logging.log_status("Disabled mesh map preview.", self, type='INFO')
        return {'FINISHED'}

class MATLAYER_OT_delete_mesh_map(Operator):
    bl_idname = "matlayer.delete_mesh_map"
    bl_label = "Delete Mesh Map"
    bl_description = "Deletes the specified mesh map from the blend files data for the active object if one exists"

    mesh_map_name: StringProperty(default='AMBIENT_OCCLUSION')

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        delete_meshmap(self.mesh_map_name, self)
        return {'FINISHED'}

class MATLAYER_OT_create_baking_cage(Operator):
    bl_idname = "matlayer.create_baking_cage"
    bl_label = "Create Baking Cage"
    bl_description = "Creates a duplicate of the selected object, scaled slightly up to act as a cage object for baking high to low poly mesh map textures"

    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        create_baking_cage(self)
        return {'FINISHED'}
    
class MATLAYER_OT_delete_baking_cage(Operator):
    bl_idname = "matlayer.delete_baking_cage"
    bl_label = "Delete Baking Cage"
    bl_description = "Deletes the selected baking cage, or the bake cage for the selected object if one exists"

    @ classmethod
    def poll(cls, context):
        return context.active_object
    
    def execute(self, context):
        delete_baking_cage(self)
        return {'FINISHED'}