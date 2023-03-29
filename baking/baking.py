# This file contains baking operators and settings for common mesh map bake types.

import os
import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty, IntProperty, StringProperty, PointerProperty, EnumProperty
from ..texture_set_settings.texture_set_settings import TEXTURE_SET_RESOLUTIONS

def verify_bake_object(self, context):
    '''Verifies the active object is a mesh and has an active UV map.'''
    active_object = bpy.context.active_object

    # Make sure the active object is a Mesh.
    if active_object.type != 'MESH':
        self.report({'INFO'}, "Active object must be a mesh")
        return False

    # Make sure the active object has a UV map.
    if active_object.data.uv_layers.active == None:
        self.report({'INFO'}, "Active object has no active UV layer")
        return False

    return True

def set_bake_size(context):
    '''Sets the size of the bake image based on baking settings.'''
    baking_settings = context.scene.matlay_baking_settings

    if baking_settings.output_width == 'FIVE_TWELVE':
        output_width = 512

    if baking_settings.output_width == 'ONEK':
        output_width = 1024

    if baking_settings.output_width == 'TWOK':
        output_width = 2048
        
    if baking_settings.output_width == 'FOURK':
        output_width = 4096

    if baking_settings.output_height == 'FIVE_TWELVE':
        output_height = 512

    if baking_settings.output_height == 'ONEK':
        output_height = 1024
        
    if baking_settings.output_height == 'TWOK':
        output_height = 2048

    if baking_settings.output_height == 'FOURK':
        output_height = 4096

    output_size = [output_width, output_height]

    return output_size

def create_bake_image(context, bake_type):
    '''Creates a new bake image.'''
    output_size = set_bake_size(context)

    active_object = context.active_object
    bake_image_name = active_object.name + "_" + bake_type

    # Delete existing bake image if it exists.
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

    # Save the new image.
    bake_path = bpy.path.abspath("//") + 'Bakes'
    if os.path.exists(bake_path) == False:
        os.mkdir(bake_path)

    bake_image = bpy.data.images[bake_image_name]
    bake_image.filepath = bake_path + "/" + bake_image_name + ".png"
    bake_image.file_format = 'PNG'
    bake_image.colorspace_settings.name = 'Non-Color'

    return bake_image_name

def empty_material_slots(context):
    # Store the original material.
    original_material = context.active_object.active_material

    # Remove existing material slots from the object.
    for x in context.object.material_slots:
        context.object.active_material_index = 0
        bpy.ops.object.material_slot_remove()

    return original_material

def add_new_bake_material(context, material_name):
    '''Adds a new material for baking.'''

    # Create a material for baking.
    bake_material = bpy.data.materials.get(material_name)

    if bake_material != None:
        bpy.data.materials.remove(bake_material)

    bake_material = bpy.data.materials.new(name=material_name)
    bake_material.use_nodes = True

    # Add the bake material to the active object's material slots.
    context.active_object.data.materials.append(bake_material)

    return bake_material

def set_output_quality():
    '''Sets the quality based on baking settings.'''
    baking_settings = bpy.context.scene.matlay_baking_settings

    if baking_settings.output_quality == 'LOW_QUALITY':
        bpy.data.scenes["Scene"].cycles.samples = 1

    if baking_settings.output_quality == 'RECOMMENDED_QUALITY':
        bpy.data.scenes["Scene"].cycles.samples = 64

    if baking_settings.output_quality == 'HIGH_QUALITY':
        bpy.data.scenes["Scene"].cycles.samples = 128

def start_bake():
    '''Sets bake settings and initializes a bake.'''
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.bake_type = 'EMIT'
    bpy.ops.object.bake(type='EMIT')

def end_bake(bake_material, original_material):
    '''Resets settings and deletes bake materials.'''
    bpy.data.materials.remove(bake_material)
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'

    # Re-apply the original material.
    bpy.context.active_object.active_material = original_material

def save_bake(bake_image_name):
    '''Saves the bake image.'''
    bake_image = bpy.data.images[bake_image_name]
    if bake_image != None:
        if bake_image.is_dirty:
            bake_image.save()

def add_ambient_occlusion_nodes(context, material, image_name):
    # Add nodes.
    nodes = material.node_tree.nodes

    bsdf_node = nodes.get("Principled BSDF")
    if bsdf_node != None:
        nodes.remove(bsdf_node)

    material_output_node = nodes.get("Material Output")
    image_node = nodes.new(type='ShaderNodeTexImage')
    emission_node = nodes.new(type='ShaderNodeEmission')
    ao_node = nodes.new(type='ShaderNodeAmbientOcclusion')
    color_ramp_node = nodes.new(type='ShaderNodeValToRGB')

    # Set node values.
    baking_settings = context.scene.matlay_baking_settings
    if image_name != "":
        image_node.image = bpy.data.images[image_name]
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

def add_curvature_nodes(context, material, image_name):
    nodes = material.node_tree.nodes

    bsdf_node = nodes.get("Principled BSDF")
    if bsdf_node != None:
        nodes.remove(bsdf_node)

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
    baking_settings = context.scene.matlay_baking_settings

    if image_name != "":
        image_node.image = bpy.data.images[image_name]

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

#----------------------------- BAKING SETTINGS -----------------------------#

SELECTED_BAKE_TYPE = [
    ("AMBIENT_OCCLUSION", "Ambient Occlusion", ""), 
    ("CURVATURE", "Curvature", ""),
    ("THICKNESS", "Thickness", ""),
    ("NORMAL", "Normal", "")
    ]

QUALITY_SETTINGS = [
    ("LOW_QUALITY", "Low Quality", ""), 
    ("RECOMMENDED_QUALITY", "Recommended Quality", ""),
    ("HIGH_QUALITY", "High Quality", "")
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
    output_quality: EnumProperty(items=QUALITY_SETTINGS, name="Output Quality", description="Output quality of the bake.", default='RECOMMENDED_QUALITY')
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
    high_poly_mesh: PointerProperty(type=bpy.types.Mesh, name="High Poly Mesh", description="The high poly mesh from which mesh detail will be baked to texture maps. The high poly mesh should generally be overlapped by your low poly mesh before starting baking. You do not need to provide a high poly mesh for baking")

#----------------------------- BAKING OPERATORS -----------------------------#

class MATLAY_OT_bake(Operator):
    '''Bakes all selected texture maps.'''
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
        return {'FINISHED'}

class MATLAY_OT_bake_ambient_occlusion(Operator):
    '''Bakes ambient occlusion from the selected object to a texture. If a high poly object is defined the ambient occlusion will be baked from the high poly mesh to the low poly mesh UVs'''
    bl_idname = "matlay.bake_ambient_occlusion"
    bl_label = "Bake Ambient Occlusion"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bake_type = "AO"
        if verify_bake_object(self, context):
            bake_image_name = create_bake_image(context, bake_type)
            original_material = empty_material_slots(context)
            bake_material = add_new_bake_material(context, "MatLay_AmbientOcclusion")
            add_ambient_occlusion_nodes(context, bake_material, bake_image_name)
            start_bake()
            set_output_quality()
            end_bake(bake_material, original_material)
            save_bake(bake_image_name)
            return {'FINISHED'}

class MATLAY_OT_bake_curvature(Operator):
    '''Bakes curvature from the selected object to a texture. If a high poly object is defined the curvature will be baked from the high poly mesh to the low poly mesh UVs'''
    bl_idname = "matlay.bake_curvature"
    bl_label = "Bake Curvature"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bake_type = "Curvature"
        if verify_bake_object(self, context):
            bake_image_name = create_bake_image(context, bake_type)
            original_material = empty_material_slots(context)
            bake_material = add_new_bake_material(context, "MatLay_Curvature")
            add_curvature_nodes(context, bake_material, bake_image_name)
            start_bake()
            set_output_quality()
            end_bake(bake_material, original_material)
            save_bake(bake_image_name)
            return {'FINISHED'}

class MATLAY_OT_bake_thickness(Operator):
    '''Bakes thickness from the selected object to a texture. If a high poly object is defined the thickness will be baked from the high poly mesh to the low poly mesh UVs'''
    bl_idname = "matlay.bake_thickness"
    bl_label = "Bake Thickness"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}
    
class MATLAY_OT_bake_normals(Operator):
    '''Bakes a normals from the selected object to a texture. If a high poly object is defined the normals will be baked from the high poly mesh to the low poly mesh UVs'''
    bl_idname = "matlay.bake_normals"
    bl_label = "Bake Normals"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}
    
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