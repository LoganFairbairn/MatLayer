# This file contains baking operators and settings for common mesh map bake types.

import os
import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty, IntProperty, StringProperty, PointerProperty, EnumProperty
from ..texture_set_settings.texture_set_settings import TEXTURE_SET_RESOLUTIONS
from ..utilities import print_info_messages

#----------------------------- BAKING SETTINGS -----------------------------#

SELECTED_BAKE_TYPE = [
    ("AMBIENT_OCCLUSION", "Ambient Occlusion", ""), 
    ("CURVATURE", "Curvature", ""),
    ("THICKNESS", "Thickness", ""),
    ("NORMAL", "Normal", "")
    ]

QUALITY_SETTINGS = [
    ("LOW_QUALITY", "Low Quality (for testing)", "Extremly low quality baking, generally used only for testing baking functionality or previewing a really rough version of baked textures. Using this quality will significantly reduce time it takes to bake mesh maps."), 
    ("RECOMMENDED_QUALITY", "Recommended Quality", "The suggested quality for baking texture maps."),
    ("HIGH_QUALITY", "High Quality", "A higher than average baking quality. This should be used for when fine, accurate detail is required in mesh map textures. Using this quality will significantly slow down baking speeds.")
    ]

def update_match_bake_resolution(self, context):
    baking_settings = context.scene.matlay_baking_settings

    if baking_settings.match_bake_resolution:
        baking_settings.output_height = baking_settings.output_width

def update_bake_width(self, context):
    baking_settings = context.scene.matlay_baking_settings

    if baking_settings.match_bake_resolution:
        if baking_settings.output_height != baking_settings.output_width:
            baking_settings.output_height = baking_settings.output_width

class MATLAY_baking_settings(bpy.types.PropertyGroup):
    show_advanced_settings: BoolProperty(name="Show Advanced Settings", description="Click to show / hide advanced baking settings", default=False)
    bake_type: EnumProperty(items=SELECTED_BAKE_TYPE, name="Bake Types", description="Bake type currently selected.", default='AMBIENT_OCCLUSION')
    output_quality: EnumProperty(items=QUALITY_SETTINGS, name="Output Quality", description="Output quality of the baked mesh maps", default='RECOMMENDED_QUALITY')
    output_width: EnumProperty(items=TEXTURE_SET_RESOLUTIONS,name="Output Height",description="Image size for the baked texure map result(s).", default='FIVE_TWELVE', update=update_bake_width)
    output_height: EnumProperty(items=TEXTURE_SET_RESOLUTIONS, name="Output Height", description="Image size for the baked texure map result(s).", default='FIVE_TWELVE')
    match_bake_resolution: BoolProperty(name="Match Bake Resoltion", description="When toggled on, the bake resolution's width and height will be synced", default=True, update=update_match_bake_resolution)
    bake_ambient_occlusion: BoolProperty(name="Bake Ambient Occlusion", description="Toggle for baking ambient occlusion as part of the batch baking operator.", default=True)
    ambient_occlusion_image_name: StringProperty(name="", description="The baking AO image", default="")
    ambient_occlusion_intensity: FloatProperty(name="Ambient Occlusion Intensity", description="", min=0.1, max=0.99, default=0.5)
    ambient_occlusion_samples: IntProperty(name="Ambient Occlusion Samples", description="The amount of samples for ambient occlusion taken", min=1, max=128, default=64)
    ambient_occlusion_local: BoolProperty(name="Local AO", description="Ambient occlusion will not bake shadow cast by other objects", default=True)
    ambient_occlusion_inside: BoolProperty(name="Inside AO", description="Ambient occlusion will trace rays towards the inside of the object", default=False)
    bake_curvature: BoolProperty(name="Bake Curvature", description="Toggle for baking curvature as part of the batch baking process.", default=True)
    curvature_image_name: StringProperty(name="", description="The baked curvature for object", default="")
    curvature_edge_intensity: FloatProperty(name="Edge Intensity", description="Brightens edges", min=0.0, max=10.0, default=3.0)
    curvature_edge_radius: FloatProperty(name="Edge Radius", description="Edge radius", min=0.001, max=0.1, default=0.01)
    curvature_ao_masking: FloatProperty(name="AO Masking", description="Mask the curvature edges using ambient occlusion.", min=0.0, max=1.0, default=1.0)
    bake_thickness: BoolProperty(name="Bake Thickness", description="Bake Thickness", default=True)
    bake_normals: BoolProperty(name="Bake Normal", description="Toggle for baking normal maps for baking as part of the batch baking operator.", default=True)
    high_poly_mesh: PointerProperty(type=bpy.types.Mesh, name="High Poly Mesh", description="The high poly mesh from which mesh detail will be baked to texture maps. The high poly mesh should generally be overlapped by your low poly mesh before starting baking. You do not need to provide a high poly mesh for baking texture maps")


#----------------------------- BAKING NODE SETUPS -----------------------------#

def add_ambient_occlusion_baking_nodes(material, bake_image):
    nodes = material.node_tree.nodes

    # Add nodes.
    material_output_node = nodes.get("Material Output")
    image_node = nodes.new(type='ShaderNodeTexImage')
    emission_node = nodes.new(type='ShaderNodeEmission')
    ao_node = nodes.new(type='ShaderNodeAmbientOcclusion')
    color_ramp_node = nodes.new(type='ShaderNodeValToRGB')

    # Set node values.
    baking_settings = bpy.context.scene.matlay_baking_settings
    image_node.image = bake_image
    ao_node.only_local = baking_settings.ambient_occlusion_local
    ao_node.samples = baking_settings.ambient_occlusion_samples
    ao_node.inside = baking_settings.ambient_occlusion_inside
    color_ramp_node.color_ramp.elements[0].position = baking_settings.ambient_occlusion_intensity
    color_ramp_node.color_ramp.interpolation = 'EASE'

    # Link Nodes
    links = material.node_tree.links
    links.new(ao_node.outputs[0], color_ramp_node.inputs[0])
    links.new(color_ramp_node.outputs[0], emission_node.inputs[0])
    links.new(emission_node.outputs[0], material_output_node.inputs[0])

def add_curvature_baking_nodes(material, bake_image):
    nodes = material.node_tree.nodes

    # Required Nodes
    material_output_node = nodes.get("Material Output")
    image_node = nodes.new(type='ShaderNodeTexImage')
    emission_node = nodes.new(type='ShaderNodeEmission')

    # Ambient Occlusion Mask Nodes
    ao_node = nodes.new(type='ShaderNodeAmbientOcclusion')
    ao_color_ramp_node = nodes.new(type='ShaderNodeValToRGB')
    ao_invert_node = nodes.new(type='ShaderNodeInvert')
    ao_masking_node = nodes.new(type='ShaderNodeMath')

    # Edge Nodes
    edge_bevel_node = nodes.new(type='ShaderNodeBevel')
    edge_geometry_node = nodes.new(type='ShaderNodeNewGeometry')
    edge_vector_math_node = nodes.new(type='ShaderNodeVectorMath')
    edge_invert_node = nodes.new(type='ShaderNodeInvert')
    edge_intensity_node = nodes.new(type='ShaderNodeMath')

    # Ambient Occlusion Masking
    ao_mix_mask_node = nodes.new(type='ShaderNodeMixRGB')

    # Pointiness Nodes
    curvature_geometry_node = nodes.new(type='ShaderNodeNewGeometry')
    curvature_color_ramp_node = nodes.new(type='ShaderNodeValToRGB')

    # Pointiness Edges Mix
    pointiness_mix_node = nodes.new(type='ShaderNodeMixRGB')

    # Set node values.
    baking_settings = bpy.context.scene.matlay_baking_settings

    image_node.image = bake_image

    ao_node.only_local = True
    ao_node.samples = baking_settings.ambient_occlusion_samples
    ao_masking_node.operation = 'MULTIPLY'

    edge_bevel_node.inputs[0].default_value = baking_settings.curvature_edge_radius
    edge_vector_math_node.operation = 'DOT_PRODUCT'
    edge_intensity_node.operation = 'MULTIPLY'
    edge_intensity_node.inputs[1].default_value = baking_settings.curvature_edge_intensity

    ao_masking_node.inputs[1].default_value = baking_settings.curvature_ao_masking
    ao_mix_mask_node.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
    ao_color_ramp_node.color_ramp.elements[0].position = 0.2
    ao_color_ramp_node.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)

    curvature_color_ramp_node.color_ramp.elements[0].position = 0.5
    curvature_color_ramp_node.color_ramp.elements[0].color = (0.25, 0.25, 0.25, 1.0)

    pointiness_mix_node.blend_type = 'SCREEN'
    pointiness_mix_node.inputs[0].default_value = 1

    # Link Nodes
    links = material.node_tree.links

    links.new(material_output_node.inputs[0], emission_node.outputs[0])
    links.new(emission_node.inputs[0], pointiness_mix_node.outputs[0])
        
    links.new(pointiness_mix_node.inputs[1], curvature_color_ramp_node.outputs[0])
    links.new(pointiness_mix_node.inputs[2], ao_mix_mask_node.outputs[0])

    links.new(curvature_color_ramp_node.inputs[0], curvature_geometry_node.outputs[7])

    links.new(ao_mix_mask_node.inputs[0], ao_masking_node.outputs[0])
    links.new(ao_mix_mask_node.inputs[1], edge_intensity_node.outputs[0])

    links.new(ao_masking_node.inputs[0], ao_invert_node.outputs[0])
    links.new(ao_invert_node.inputs[1], ao_color_ramp_node.outputs[0])
    links.new(ao_color_ramp_node.inputs[0], ao_node.outputs[0])

    links.new(edge_intensity_node.inputs[0], edge_invert_node.outputs[0])
    links.new(edge_invert_node.inputs[1], edge_vector_math_node.outputs[1])
    links.new(edge_vector_math_node.inputs[0], edge_bevel_node.outputs[0])
    links.new(edge_vector_math_node.inputs[1], edge_geometry_node.outputs[1])

def add_thickness_baking_nodes(material, bake_image):
    nodes = material.node_tree.nodes

    # Add nodes.
    material_output_node = nodes.get("Material Output")
    image_node = nodes.new(type='ShaderNodeTexImage')
    emission_node = nodes.new(type='ShaderNodeEmission')
    ao_node = nodes.new(type='ShaderNodeAmbientOcclusion')
    color_ramp_node = nodes.new(type='ShaderNodeValToRGB')

    # Set node values.
    baking_settings = bpy.context.scene.matlay_baking_settings
    image_node.image = bake_image
    ao_node.only_local = baking_settings.ambient_occlusion_local
    ao_node.samples = baking_settings.ambient_occlusion_samples
    ao_node.inside = baking_settings.ambient_occlusion_inside
    color_ramp_node.color_ramp.elements[0].position = baking_settings.ambient_occlusion_intensity
    color_ramp_node.color_ramp.interpolation = 'EASE'

    # Link Nodes
    links = material.node_tree.links
    links.new(ao_node.outputs[0], color_ramp_node.inputs[0])
    links.new(color_ramp_node.outputs[0], emission_node.inputs[0])
    links.new(emission_node.outputs[0], material_output_node.inputs[0])


#----------------------------- BAKING FUNCTIONS -----------------------------#

def verify_bake_object():
    '''Verifies the active object is a mesh and has an active UV map.'''
    active_object = bpy.context.active_object

    # Make sure the active object is a Mesh.
    if active_object.type != 'MESH':
        print_info_messages.show_message_box("Active object must be a mesh.", title="MatLay baking error.", icon='ERROR')
        return False

    # Make sure the active object has a UV map.
    if active_object.data.uv_layers.active == None:
        print_info_messages.show_message_box("Active object has no active UV layer.", title="MatLay baking error.", icon='ERROR')
        return False
    
    return True

def create_bake_image(bake_type):
    '''Creates a new bake image in Blender's data and defines it's save location'''

    # Define the baking size based on settings.
    baking_settings = bpy.context.scene.matlay_baking_settings
    match baking_settings.output_width:
        case 'FIVE_TWELVE':
            output_width = 512
        case 'ONEK':
            output_width = 1024
        case 'TWOK':
            output_width = 2048
        case 'FOURK':
            output_width = 4096

    match baking_settings.output_height:
        case 'FIVE_TWELVE':
            output_height = 512
        case 'ONEK':
            output_height = 1024
        case 'TWOK':
            output_height = 2048
        case 'FOURK':
            output_height = 4096

    output_size = [output_width, output_height]

    # Use the object's name and bake type to define the bake image name.
    bake_image_name = bpy.context.active_object.name + "_" + bake_type

    # Create a new image in Blender's data, delete existing bake image if it exists.
    image = bpy.data.images.get(bake_image_name)
    if image != None:
        bpy.data.images.remove(image)
    image = bpy.ops.image.new(name=bake_image_name,
                              width=output_size[0],
                              height=output_size[1],
                              color=(0.0, 0.0, 0.0, 1.0),
                              alpha=False,
                              generated_type='BLANK',
                              float=False,
                              use_stereo_3d=False,
                              tiled=False)

    # Save the new image to a folder for baked images.
    bake_path = bpy.path.abspath("//") + 'Bakes'
    if os.path.exists(bake_path) == False:
        os.mkdir(bake_path)

    bake_image = bpy.data.images[bake_image_name]
    bake_image.filepath = bake_path + "/" + bake_image_name + ".png"
    bake_image.file_format = 'PNG'
    bake_image.colorspace_settings.name = 'Non-Color'

    return bake_image

def create_temp_bake_material(bake_type):
    '''Create a material for baking, remove existing materials if they already exist.'''
    temp_material_name = ""
    match bake_type:
        case 'AMBIENT_OCCLUSION':
            temp_material_name = "MatLay_AO"
        case 'CURVATURE':
            temp_material_name = "MatLay_Curvature"
        case 'THICKNESS':
            temp_material_name = "MatLay_Thickness"

    bake_material = bpy.data.materials.get(temp_material_name)
    if bake_material != None:
        bpy.data.materials.remove(bake_material)

    bake_material = bpy.data.materials.new(name=temp_material_name)
    bake_material.use_nodes = True

    # Remove the Principled BSDF node from the material as it's not used in node setups for baking.
    nodes = bake_material.node_tree.nodes
    bsdf_node = nodes.get("Principled BSDF")
    if bsdf_node != None:
        nodes.remove(bsdf_node)

    return bake_material

def bake_mesh_map(bake_type):
    # Verify that there is a valid object to bake mesh maps for.
    if verify_bake_object() == False:
        return

    bake_image = create_bake_image(bake_type)
    temp_bake_material = create_temp_bake_material(bake_type)

    # Cache original materials applied to the active object so the materials can be re-applied after baking and apply the temporary bake material to all material slots.
    original_materials = []
    for x in bpy.context.object.material_slots:
        original_materials.append(x.material)
        x.material = temp_bake_material

    # Add a node setup based on the bake type.
    match bake_type:
        case 'AO':
            add_ambient_occlusion_baking_nodes(temp_bake_material, bake_image)

        case 'CURVATURE':
            add_curvature_baking_nodes(temp_bake_material, bake_image)

        case 'THICKNESS':
            add_thickness_baking_nodes(temp_bake_material, bake_image)

    # Apply bake settings and bake the material to a texture.
    baking_settings = bpy.context.scene.matlay_baking_settings
    match baking_settings.output_quality:
        case 'LOW_QUALITY':
            bpy.data.scenes["Scene"].cycles.samples = 1

        case 'RECOMMENDED_QUALITY':
            bpy.data.scenes["Scene"].cycles.samples = 64

        case 'HIGH_QUALITY':
            bpy.data.scenes["Scene"].cycles.samples = 128

    if baking_settings.high_poly_mesh != None:
        bpy.context.scene.render.bake.use_selected_to_active = True
    else:
        bpy.context.scene.render.bake.use_selected_to_active = False

    bpy.context.scene.render.engine = 'CYCLES'
    bpy.ops.object.bake(type='EMIT')

    # Save the baked image.
    if bake_image:
        if bake_image.is_dirty:
            bake_image.save()
        else:
            print_info_messages.show_message_box("Baked image pixel data wasn't updated during baking.", "MatLay baking error.", 'ERROR')

    # Re-apply the materials that were originally on the object and delete the temporary material.
    for i in range(0, len(bpy.context.object.material_slots)):
        bpy.context.object.material_slots[i].material = original_materials[i]
    bpy.data.materials.remove(temp_bake_material)

class MATLAY_OT_bake(Operator):
    '''Bakes all checked texture maps in succession'''
    bl_idname = "matlay.bake"
    bl_label = "Bake"
    bl_description = "Bakes all checked texture maps in succession"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        baking_settings = context.scene.matlay_baking_settings

        if baking_settings.bake_ambient_occlusion:
            bpy.ops.matlay.bake_ambient_occlusion()

        if baking_settings.bake_curvature:
            bpy.ops.matlay.bake_curvature()

        if baking_settings.bake_thickness.bake_thickness:
            bpy.ops.matlay.bake_thickness()

        if baking_settings.bake_normals:
            bpy.ops.matlay.bake_normals()

        return {'FINISHED'}

class MATLAY_OT_bake_ambient_occlusion(Operator):
    '''Bakes ambient occlusion from the selected object to a texture. If a high poly object is defined the ambient occlusion will be baked from the high poly mesh to the low poly mesh UVs'''
    bl_idname = "matlay.bake_ambient_occlusion"
    bl_label = "Bake Ambient Occlusion"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bake_mesh_map('AO')
        return {'FINISHED'}

class MATLAY_OT_bake_curvature(Operator):
    '''Bakes curvature from the selected object to a texture. If a high poly object is defined the curvature will be baked from the high poly mesh to the low poly mesh UVs'''
    bl_idname = "matlay.bake_curvature"
    bl_label = "Bake Curvature"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bake_mesh_map('CURVATURE')
        return {'FINISHED'}

class MATLAY_OT_bake_thickness(Operator):
    '''Bakes thickness from the selected object to a texture. If a high poly object is defined the thickness will be baked from the high poly mesh to the low poly mesh UVs'''
    bl_idname = "matlay.bake_thickness"
    bl_label = "Bake Thickness"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bake_mesh_map('THICKNESS')
        return {'FINISHED'}
    
class MATLAY_OT_bake_normals(Operator):
    '''Bakes a normals from the selected object to a texture. If a high poly object is defined the normals will be baked from the high poly mesh to the low poly mesh UVs'''
    bl_idname = "matlay.bake_normals"
    bl_label = "Bake Normals"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bake_mesh_map('NORMALS')
        return {'FINISHED'}


#----------------------------- DELETING MESH MAP FUNCTIONS -----------------------------#

class MATLAY_OT_delete_ao_map(Operator):
    bl_idname = "matlay.delete_ao_map"
    bl_label = "Delete Ambient Occlusion Map"
    bl_description = "Deletes the baked ambient occlusion map for the active object if one exists"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}
    
class MATLAY_OT_delete_curvature_map(Operator):
    bl_idname = "matlay.delete_curvature_map"
    bl_label = "Delete Curvature Map"
    bl_description = "Deletes the baked curvature map for the active object if one exists"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}
    
class MATLAY_OT_delete_thickness_map(Operator):
    bl_idname = "matlay.delete_thickness_map"
    bl_label = "Delete Thickness Map"
    bl_description = "Deletes the baked thickness map for the active object if one exists"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}
    
class MATLAY_OT_delete_normal_map(Operator):
    bl_idname = "matlay.delete_normal_map"
    bl_label = "Delete Normal Map"
    bl_description = "Deletes the baked normal map for the active object if one exists"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}