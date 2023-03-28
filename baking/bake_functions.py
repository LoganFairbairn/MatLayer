# This file contains operators that quickly bake common texture maps.

import os # For file handling.
import bpy
from bpy.types import Operator

# Bakes all selected texture maps.
class MATLAY_OT_bake(Operator):
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