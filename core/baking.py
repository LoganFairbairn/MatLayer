# This file contains baking operators and settings for common mesh map bake types.

import os
import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty, IntProperty, StringProperty, PointerProperty, EnumProperty
from .texture_set_settings import TEXTURE_SET_RESOLUTIONS
from ..utilities import logging

#----------------------------- BAKING SETTINGS -----------------------------#

SELECTED_BAKE_TYPE = [
    ("AMBIENT_OCCLUSION", "Ambient Occlusion", ""), 
    ("CURVATURE", "Curvature", ""),
    ("THICKNESS", "Thickness", ""),
    ("NORMAL", "Normals", "")
    ]

QUALITY_SETTINGS = [
    ("LOW_QUALITY", "Low Quality (for testing)", "Extremly low quality baking, generally used only for testing baking functionality or previewing a really rough version of baked textures. Using this quality will significantly reduce time it takes to bake mesh maps."), 
    ("RECOMMENDED_QUALITY", "Recommended Quality", "The suggested quality for baking texture maps."),
    ("HIGH_QUALITY", "High Quality", "A higher than average baking quality. This should be used for when fine, accurate detail is required in mesh map textures. Using this quality will significantly slow down baking speeds.")
    ]

def get_meshmap_image_name(meshmap_type):
    '''Returns the name appended to the end of mesh map image files.'''
    match meshmap_type:
        case 'AMBIENT_OCCLUSION':
            return 'AO'

        case 'CURVATURE':
            return'Curvature'

        case 'THICKNESS':
            return'Thickness'

        case 'NORMAL':
            return 'Normals'

def get_meshmap_name(meshmap_type):
    '''Returns the image name for the mesh map of the selected / active object.'''
    meshmap_image_name = get_meshmap_image_name(meshmap_type)
    return "{0}_{1}".format(bpy.context.active_object.name, meshmap_image_name)

def update_match_bake_resolution(self, context):
    '''Match the height to the width.'''
    baking_settings = context.scene.matlayer_baking_settings
    if baking_settings.match_bake_resolution:
        baking_settings.output_height = baking_settings.output_width

def update_bake_width(self, context):
    '''Match the height to the width of the bake output'''
    baking_settings = context.scene.matlayer_baking_settings
    if baking_settings.match_bake_resolution:
        if baking_settings.output_height != baking_settings.output_width:
            baking_settings.output_height = baking_settings.output_width

class MATLAYER_baking_settings(bpy.types.PropertyGroup):
    bake_type: EnumProperty(items=SELECTED_BAKE_TYPE, name="Bake Types", description="Bake type currently selected", default='AMBIENT_OCCLUSION')
    output_quality: EnumProperty(items=QUALITY_SETTINGS, name="Output Quality", description="Output quality of the baked mesh maps", default='RECOMMENDED_QUALITY')
    output_width: EnumProperty(items=TEXTURE_SET_RESOLUTIONS,name="Output Height",description="Image size for the baked texure map result(s)", default='TWOK', update=update_bake_width)
    output_height: EnumProperty(items=TEXTURE_SET_RESOLUTIONS, name="Output Height", description="Image size for the baked texure map result(s)", default='TWOK')
    match_bake_resolution: BoolProperty(name="Match Bake Resoltion", description="When toggled on, the bake resolution's width and height will be synced", default=True, update=update_match_bake_resolution)
    bake_ambient_occlusion: BoolProperty(name="Bake Ambient Occlusion", description="Toggle for baking ambient occlusion as part of the batch baking operator", default=True)
    ambient_occlusion_image_name: StringProperty(name="", description="The baking AO image", default="")
    ambient_occlusion_intensity: FloatProperty(name="Ambient Occlusion Intensity", description="", min=0.1, max=0.99, default=0.15)
    ambient_occlusion_samples: IntProperty(name="Ambient Occlusion Samples", description="The amount of samples for ambient occlusion taken", min=1, max=128, default=64)
    ambient_occlusion_local: BoolProperty(name="Local AO", description="Ambient occlusion will not bake shadow cast by other objects", default=True)
    ambient_occlusion_inside: BoolProperty(name="Inside AO", description="Ambient occlusion will trace rays towards the inside of the object", default=False)
    bake_curvature: BoolProperty(name="Bake Curvature", description="Toggle for baking curvature as part of the batch baking process", default=True)
    curvature_image_name: StringProperty(name="", description="The baked curvature for object", default="")
    curvature_edge_intensity: FloatProperty(name="Edge Intensity", description="Brightens edges", min=0.0, max=10.0, default=3.0)
    curvature_edge_radius: FloatProperty(name="Edge Radius", description="Edge radius", min=0.001, max=0.1, default=0.01)
    curvature_ao_masking: FloatProperty(name="AO Masking", description="Mask the curvature edges using ambient occlusion", min=0.0, max=1.0, default=1.0)
    bake_thickness: BoolProperty(name="Bake Thickness", description="Toggle for baking thickness as part of the batch baking operator", default=True)
    thickness_samples: IntProperty(name="Thickness Samples", description="The amount of samples for thickness baking. Increasing this value will increase the quality of the output thickness maps", min=1, max=128, default=64)
    bake_normals: BoolProperty(name="Bake Normal", description="Toggle for baking normal maps for baking as part of the batch baking operator", default=True)
    cage_extrusion: FloatProperty(name="Cage Extrusion", description="Infaltes the active object by the specified amount for baking. This helps matching to points nearer to the outside of the selected object meshes", default=0.111, min=0.0, max=1.0)
    high_poly_object: PointerProperty(type=bpy.types.Object, name="High Poly Object", description="The high poly object (must be a mesh) from which mesh detail will be baked to texture maps. The high poly mesh should generally be overlapped by your low poly mesh before starting baking. You do not need to provide a high poly mesh for baking texture maps")


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
    baking_settings = bpy.context.scene.matlayer_baking_settings
    image_node.image = bake_image
    ao_node.samples = baking_settings.ambient_occlusion_samples
    ao_node.only_local = baking_settings.ambient_occlusion_local
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
    baking_settings = bpy.context.scene.matlayer_baking_settings

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
    ao_node = nodes.new(type='ShaderNodeAmbientOcclusion')
    invert_node = nodes.new(type='ShaderNodeInvert')

    # Set node values.
    baking_settings = bpy.context.scene.matlayer_baking_settings
    image_node.image = bake_image
    ao_node.samples = baking_settings.thickness_samples
    ao_node.only_local = True
    ao_node.inside = True

    # Link Nodes
    links = material.node_tree.links
    links.new(ao_node.outputs[1], invert_node.inputs[1])
    links.new(ao_node.outputs[0], material_output_node.inputs[0])

def add_normal_baking_nodes(material, bake_image):
    nodes = material.node_tree.nodes

    # Add nodes.
    image_node = nodes.new(type='ShaderNodeTexImage')

    # Set node values.
    image_node.image = bake_image

#----------------------------- BAKING FUNCTIONS -----------------------------#

def verify_bake_object(self):
    '''Verifies the selected object can be baked to.'''
    active_object = bpy.context.active_object
    
    # Verify there is a selected object.
    if len(bpy.context.selected_objects) <= 0:
        self.report({'ERROR'}, "No valid selected objects. Select an object before baking / exporting.")
        return False

    # Verify the active object exists.
    if active_object == None:
        self.report({'ERROR'}, "No valid active object. Select an object before baking / exporting.")
        return False

    # Make sure the active object is a Mesh.
    if active_object.type != 'MESH':
        self.report({'ERROR'}, "Selected object must be a mesh for baking / exporting.")
        return False

    # Make sure the active object has a UV map.
    if active_object.data.uv_layers.active == None:
        self.report({'ERROR'}, "Selected object has no active UV layer / map. Add a UV layer / map to your object and unwrap it.")
        return False
    
    # Check to see if the (low poly) selected active object is hidden.
    if active_object.hide_get():
        self.report({'ERROR'}, "Selected object is hidden. Unhide the selected object.")
        return False
    return True

def create_bake_image(bake_type):
    '''Creates a new bake image in Blender's data and define it's save location'''

    # Define the baking size based on settings.
    baking_settings = bpy.context.scene.matlayer_baking_settings
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
    bake_image_name = bpy.context.active_object.name
    match bake_type:
        case 'AMBIENT_OCCLUSION':
            bake_image_name += "_AO"

        case 'CURVATURE':
            bake_image_name += "_Curvature"

        case 'THICKNESS':
            bake_image_name += "_Thickness"

        case 'NORMALS':
            bake_image_name += "_Normals"

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
    matlayer_image_path = os.path.join(bpy.path.abspath("//"), "Matlayer")
    if os.path.exists(matlayer_image_path) == False:
        os.mkdir(matlayer_image_path)

    bake_path = os.path.join(matlayer_image_path, "MeshMaps")
    if os.path.exists(bake_path) == False:
        os.mkdir(bake_path)

    bake_image = bpy.data.images[bake_image_name]
    bake_image.filepath = bake_path + "/" + bake_image_name + ".png"
    bake_image.file_format = 'PNG'

    if bake_type == 'NORMALS':
        bake_image.colorspace_settings.name = 'Non-Color'

    else:
        bake_image.colorspace_settings.name = 'sRGB'
    

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
        case 'NORMAL':
            temp_material_name = "MatLay_Normal"

    bake_material = bpy.data.materials.get(temp_material_name)
    if bake_material != None:
        bpy.data.materials.remove(bake_material)

    bake_material = bpy.data.materials.new(name=temp_material_name)
    bake_material.use_nodes = True

    # Remove the Principled BSDF node from the material, it's not used in node setups for baking.
    nodes = bake_material.node_tree.nodes
    bsdf_node = nodes.get("MatLayer BSDF")
    if bsdf_node != None:
        nodes.remove(bsdf_node)

    return bake_material

def bake_mesh_map(bake_type, self):
    # Verify that there is a valid object to bake mesh maps for.
    if verify_bake_object(self) == False:
        return

    # The (low poly) selected active object should be unhiden, selectable and visible.
    active_object = bpy.context.active_object
    active_object.hide_set(False)
    active_object.hide_render = False
    active_object.hide_select = False

    # The high poly mesh must be unhidden, selectable and visible.
    high_poly_object = bpy.context.scene.matlayer_baking_settings.high_poly_object
    if high_poly_object:
        high_poly_object.hide_set(False)
        high_poly_object.hide_render = False
        high_poly_object.hide_select = False

    bake_image = create_bake_image(bake_type)
    temp_bake_material = create_temp_bake_material(bake_type)

    # Cache original materials applied to the active object so the materials can be re-applied after baking and apply the temporary bake material to all material slots.
    original_materials = []
    if len(bpy.context.object.material_slots) > 0:
        for x in bpy.context.object.material_slots:
            original_materials.append(x.material)
            x.material = temp_bake_material

    # Add a new material slot.
    else:
        bpy.context.object.data.materials.append(temp_bake_material)

    # Add a node setup based on the bake type.
    match bake_type:
        case 'AMBIENT_OCCLUSION':
            add_ambient_occlusion_baking_nodes(temp_bake_material, bake_image)

        case 'CURVATURE':
            add_curvature_baking_nodes(temp_bake_material, bake_image)

        case 'THICKNESS':
            add_thickness_baking_nodes(temp_bake_material, bake_image)

        case 'NORMALS':
            add_normal_baking_nodes(temp_bake_material, bake_image)

    # Apply bake settings and bake the material to a texture.
    baking_settings = bpy.context.scene.matlayer_baking_settings
    match baking_settings.output_quality:
        case 'LOW_QUALITY':
            bpy.data.scenes["Scene"].cycles.samples = 1

        case 'RECOMMENDED_QUALITY':
            bpy.data.scenes["Scene"].cycles.samples = 64

        case 'HIGH_QUALITY':
            bpy.data.scenes["Scene"].cycles.samples = 128

    # Cache the render engine so we can reset it after baking.
    original_render_engine = bpy.context.scene.render.engine

    bpy.context.scene.render.engine = 'CYCLES'
    match bake_type:
        case 'NORMALS':
            if baking_settings.high_poly_object != None:
                bpy.context.scene.render.bake.use_selected_to_active = True
                bpy.context.scene.render.bake.cage_extrusion = baking_settings.cage_extrusion
                
                # Select the low poly and high poly objects.
                active_object = bpy.context.active_object
                bpy.ops.object.select_all(action='DESELECT')
                baking_settings.high_poly_object.select_set(True)
                active_object.select_set(True)
                bpy.context.scene.render.bake.use_selected_to_active = True
            else:
                bpy.context.scene.render.bake.use_selected_to_active = False
            bpy.ops.object.bake(type='NORMAL')

        case _:
            bpy.context.scene.render.bake.use_selected_to_active = False
            bpy.ops.object.bake(type='EMIT')

    # Reset the render engine.
    bpy.context.scene.render.engine = original_render_engine

    # High the high poly object, there's no need for it to be visible anymore.
    high_poly_object = bpy.context.scene.matlayer_baking_settings.high_poly_object
    if high_poly_object:
        high_poly_object.hide_set(True)

    # Save the baked image.
    if bake_image:
        if bake_image.is_dirty:
            bake_image.save()
        else:
            logging.popup_message_box("Baked image pixel data wasn't updated during baking.", "MatLay baking error.", 'ERROR')

    # Re-apply the materials that were originally on the object and 
    if len(original_materials) <= 0:
        bpy.ops.object.material_slot_remove(0)
    else:
        for i in range(0, len(original_materials)):
            bpy.context.object.material_slots[i].material = original_materials[i]
        
    # Delete the temporary bake material.
    bpy.data.materials.remove(temp_bake_material)

    # Reset the render engine.
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'

    # Display a finished message.
    matlayer_image_path = os.path.join(bpy.path.abspath("//"), "Matlayer")
    bake_path = os.path.join(matlayer_image_path, "MeshMaps")
    self.report({'INFO'}, "Baking mesh maps complete. You can find all bake mesh maps here: {0}".format(bake_path))

class MATLAYER_OT_bake(Operator):
    '''Bakes all checked mesh texture maps in succession. Note that this function (especially on slower computers, or when using a CPU for rendering) can take a few minutes.'''
    bl_idname = "matlayer.bake"
    bl_label = "Batch Bake"
    bl_description = "Bakes all checked mesh texture maps in succession. Note that this function can take a few minutes, especially on slower computers, or when using CPU for rendering"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        baking_settings = context.scene.matlayer_baking_settings

        if baking_settings.bake_ambient_occlusion:
            bake_mesh_map('AMBIENT_OCCLUSION', self)

        if baking_settings.bake_curvature:
            bake_mesh_map('CURVATURE', self)

        if baking_settings.bake_thickness:
            bake_mesh_map('THICKNESS', self)

        if baking_settings.bake_normals:
            bake_mesh_map('NORMALS', self)

        return {'FINISHED'}

class MATLAYER_OT_bake_ambient_occlusion(Operator):
    '''Bakes ambient occlusion from the selected object to a texture. If a high poly object is defined the ambient occlusion will be baked from the high poly mesh to the low poly mesh UVs'''
    bl_idname = "matlayer.bake_ambient_occlusion"
    bl_label = "Bake Ambient Occlusion"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bake_mesh_map('AMBIENT_OCCLUSION', self)
        return {'FINISHED'}

class MATLAYER_OT_bake_curvature(Operator):
    '''Bakes curvature from the selected object to a texture. If a high poly object is defined the curvature will be baked from the high poly mesh to the low poly mesh UVs'''
    bl_idname = "matlayer.bake_curvature"
    bl_label = "Bake Curvature"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bake_mesh_map('CURVATURE', self)
        return {'FINISHED'}

class MATLAYER_OT_bake_thickness(Operator):
    '''Bakes thickness from the selected object to a texture. If a high poly object is defined the thickness will be baked from the high poly mesh to the low poly mesh UVs'''
    bl_idname = "matlayer.bake_thickness"
    bl_label = "Bake Thickness"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bake_mesh_map('THICKNESS', self)
        return {'FINISHED'}
    
class MATLAYER_OT_bake_normals(Operator):
    '''Bakes a normals from the selected object to a texture. If a high poly object is defined the normals will be baked from the high poly mesh to the low poly mesh UVs'''
    bl_idname = "matlayer.bake_normals"
    bl_label = "Bake Normals"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bake_mesh_map('NORMALS', self)
        return {'FINISHED'}


#----------------------------- DELETING MESH MAP FUNCTIONS -----------------------------#

def delete_meshmap(meshmap_type, self):
    '''Deletes the meshmap of the provided type for the selected / active object if it exists from the blend files data.'''
    meshmap_name = get_meshmap_name(meshmap_type)
    if bpy.context.active_object:
        meshmap_image = bpy.data.images.get(meshmap_name)
        if meshmap_image:
            bpy.data.images.remove(meshmap_image)
            self.report({'INFO'}, "{0} mesh map was deleted.".format(meshmap_name))
        else:
            self.report({'INFO'}, "{0} mesh map doesn't exist.".format(meshmap_name))
    else:
        self.report({'INFO'}, "No active object to delete mesh maps for, re-select the object you wish to delete mesh maps for.")

class MATLAYER_OT_delete_ao_map(Operator):
    bl_idname = "matlayer.delete_ao_map"
    bl_label = "Delete Ambient Occlusion Map"
    bl_description = "Deletes the baked ambient occlusion map for the active object if one exists"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        delete_meshmap('AMBIENT_OCCLUSION', self)
        return {'FINISHED'}
    
class MATLAYER_OT_delete_curvature_map(Operator):
    bl_idname = "matlayer.delete_curvature_map"
    bl_label = "Delete Curvature Map"
    bl_description = "Deletes the baked curvature map for the active object if one exists"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        delete_meshmap('CURVATURE', self)
        return {'FINISHED'}
    
class MATLAYER_OT_delete_thickness_map(Operator):
    bl_idname = "matlayer.delete_thickness_map"
    bl_label = "Delete Thickness Map"
    bl_description = "Deletes the baked thickness map for the active object if one exists"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        delete_meshmap('THICKNESS', self)
        return {'FINISHED'}
    
class MATLAYER_OT_delete_normal_map(Operator):
    bl_idname = "matlayer.delete_normal_map"
    bl_label = "Delete Normal Map"
    bl_description = "Deletes the baked normal map for the active object if one exists"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        delete_meshmap('NORMAL', self)
        return {'FINISHED'}