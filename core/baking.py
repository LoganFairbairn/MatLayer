# This file contains baking operators and settings for common mesh map bake types.

import os
import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty, IntProperty, StringProperty, PointerProperty, EnumProperty
from .texture_set_settings import TEXTURE_SET_RESOLUTIONS
from . import blender_addon_utils
from . import debug_logging

MESH_MAP_TYPES = ("AMBIENT_OCCLUSION", "CURVATURE", "THICKNESS", "NORMALS", "WORLD_SPACE_NORMALS")

SELECTED_BAKE_TYPE = [
    ("AMBIENT_OCCLUSION", "Ambient Occlusion", ""), 
    ("CURVATURE", "Curvature", ""),
    ("THICKNESS", "Thickness", ""),
    ("NORMAL", "Normals", ""),
    ("WORLD_SPACE_NORMALS", "World Space Normals", "")
]

QUALITY_SETTINGS = [
    ("LOW_QUALITY", "Low Quality (for testing)", "Extremly low quality baking, generally used only for testing baking functionality or previewing a really rough version of baked textures. Using this quality will significantly reduce time it takes to bake mesh maps"), 
    ("RECOMMENDED_QUALITY", "Recommended Quality", "The suggested quality for baking texture maps"),
    ("HIGH_QUALITY", "High Quality", "A higher than average baking quality. This should be used for when fine, accurate detail is required in mesh map textures. Using this quality will significantly slow down baking speeds")
]

#----------------------------- UPDATING FUNCTIONS -----------------------------#

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

def update_meshmap_names(previous_name):
    '''Updates the meshmap names using old names to the name of the active object (called after an object name change).'''
    print("Placeholder...")
    '''
    for meshmap_type in BAKE_TYPES:
        meshmap_name = format_meshmap_name(previous_name, meshmap_type)
        meshmap_image = bpy.data.images.get(meshmap_name)
        if meshmap_image:
            meshmap_image.name = format_meshmap_name(bpy.context.active_object.name, meshmap_type)
    '''

#----------------------------- HELPER FUNCTIONS -----------------------------#

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

def verify_bake_object(self):
    '''Verifies the active object can have mesh maps or textures baked for it.'''
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

def create_bake_image(mesh_map_type):
    '''Creates a new image in Blender's data to bake to.'''

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
    mesh_map_name = get_meshmap_name(bpy.context.active_object.name, mesh_map_type)

    # Create a new image in Blender's data, delete existing bake image if it exists.
    image = bpy.data.images.get(mesh_map_name)
    if image != None:
        bpy.data.images.remove(image)
    image = bpy.ops.image.new(name=mesh_map_name,
                              width=output_size[0],
                              height=output_size[1],
                              color=(0.0, 0.0, 0.0, 1.0),
                              alpha=False,
                              generated_type='BLANK',
                              float=False,
                              use_stereo_3d=False,
                              tiled=False)

    mesh_map_image = bpy.data.images[mesh_map_name]
    mesh_map_image.colorspace_settings.name = 'Non-Color'

    return mesh_map_image

def apply_baking_quality_settings():
    '''Applies baking quality settings.'''
    baking_settings = bpy.context.scene.matlayer_baking_settings
    match baking_settings.output_quality:
        case 'LOW_QUALITY':
            bpy.data.scenes["Scene"].cycles.samples = 1

        case 'RECOMMENDED_QUALITY':
            bpy.data.scenes["Scene"].cycles.samples = 64

        case 'HIGH_QUALITY':
            bpy.data.scenes["Scene"].cycles.samples = 128

def bake_mesh_map(mesh_map_type, self):
    '''Applies a premade baking material to the active object and starts baking. Returns true if baking was successful.'''

    baking_settings = bpy.context.scene.matlayer_baking_settings
    if mesh_map_type == 'NORMALS' and baking_settings.high_poly_object == None:
        debug_logging.log("Skipping normal map baking, no high poly object is specified.")
        return True

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

    # Create and assign an image to bake the mesh map to.
    new_bake_image = create_bake_image(mesh_map_type)
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

    # Apply the bake material to the object.
    if len(bpy.context.object.material_slots) > 0:
        for x in bpy.context.object.material_slots:
            x.material = temp_bake_material
    else:
        bpy.context.object.data.materials.append(temp_bake_material)

    # Set render engine settings and trigger the baking process.
    bpy.context.scene.render.engine = 'CYCLES'
    match mesh_map_type:
        case 'NORMALS':
            bpy.context.scene.render.bake.use_selected_to_active = True
            bpy.context.scene.render.bake.cage_extrusion = baking_settings.cage_extrusion
            
            # Select the low poly and high poly objects.
            active_object = bpy.context.active_object
            bpy.ops.object.select_all(action='DESELECT')
            baking_settings.high_poly_object.select_set(True)
            active_object.select_set(True)
            bpy.context.scene.render.bake.use_selected_to_active = True
            bpy.ops.object.bake('INVOKE_DEFAULT', type='NORMAL')

        case _:
            bpy.context.scene.render.bake.use_selected_to_active = False
            bpy.ops.object.bake('INVOKE_DEFAULT', type='EMIT')
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

#----------------------------- OPERATORS AND PROPERTIES -----------------------------#

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
    bake_bevel_normals: BoolProperty(name="Bake Bevel Normal", description="Toggle for baking a bevel normal map for baking as part of the batch baking operator", default=False)
    bake_world_space_normals: BoolProperty(name="Bake World Space Normals", description="Toggle for baking world space normals as part of the batch baking operator", default=True)

class MATLAYER_OT_bake_mesh_map(Operator):
    bl_idname = "matlayer.bake_mesh_map"
    bl_label = "Bake Mesh Map"
    bl_description = "Bakes the specified mesh map for the active (selected) object"

    mesh_map_type: StringProperty(default='AMBIENT_OCCLUSION')

    _timer = None
    _temp_bake_material = None
    _mesh_map_image = None
    _mesh_map_group_node = None
    _original_materials = []
    _original_render_engine = None

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
            if self._mesh_map_image.is_dirty:
                self._mesh_map_image.pack()
                self.finish(context)
                return {'FINISHED'}
        
        return {'PASS_THROUGH'}

    def execute(self, context):
        if verify_bake_object(self) == False:
            return {'FINISHED'}

        # Make the low poly selected active object unhiden, selectable and visible.
        active_object = bpy.context.active_object
        active_object.hide_set(False)
        active_object.hide_render = False
        active_object.hide_select = False

        # Make the high poly mesh unhidden, selectable and visible.
        high_poly_object = bpy.context.scene.matlayer_baking_settings.high_poly_object
        if high_poly_object:
            high_poly_object.hide_set(False)
            high_poly_object.hide_render = False
            high_poly_object.hide_select = False
    
        # Append a premade material setup for baking the specified mesh map type.
        match self.mesh_map_type:
            case 'AMBIENT_OCCLUSION':
                self._temp_bake_material = blender_addon_utils.append_material('BakeAmbientOcclusion')
                self._mesh_map_group_node = bpy.data.node_groups.get("ML_AmbientOcclusion")

            case 'CURVATURE':
                self._temp_bake_material = blender_addon_utils.append_material('BakeCurvature')
                self._mesh_map_group_node = bpy.data.node_groups.get("ML_Curvature")

            case 'THICKNESS':
                self._temp_bake_material = blender_addon_utils.append_material('BakeThickness')
                self._mesh_map_group_node = bpy.data.node_groups.get("ML_Thickness")

            case 'NORMALS':
                self._temp_bake_material = blender_addon_utils.append_material('BakeNormals')

            case 'WORLD_SPACE_NORMALS':
                self._temp_bake_material = blender_addon_utils.append_material('BakeWorldSpaceNormals')
                self._mesh_map_group_node = bpy.data.node_groups.get("ML_WorldSpaceNormals")

        # Cache original materials applied to the active object so the materials can be re-applied after baking.
        self._original_materials.clear()
        active_object_material_slots = bpy.context.active_object.material_slots
        if len(active_object_material_slots) > 0:
            for x in active_object_material_slots:
                self._original_materials.append(x.material)
                x.material = self._temp_bake_material
        else:
            bpy.context.object.data.materials.append(self._temp_bake_material)

        # Create and assign an image to bake the mesh map to.
        self._mesh_map_image = create_bake_image(self.mesh_map_type)
        bake_image_node = self._temp_bake_material.node_tree.nodes.get("BAKE_IMAGE")
        if bake_image_node:
            bake_image_node.image = self._mesh_map_image
            for node in self._temp_bake_material.node_tree.nodes:
                node.select = False
            bake_image_node.select = True
            self._temp_bake_material.node_tree.nodes.active = bake_image_node
            context.scene.tool_settings.image_paint.canvas = self._mesh_map_image
        else:
            self.report({'ERROR'}, "Error: Image node not found in premade mesh map baking material setup.")
            return {'FINISHED'}

        # Apply bake settings and bake the material to a texture.
        baking_settings = bpy.context.scene.matlayer_baking_settings
        match baking_settings.output_quality:
            case 'LOW_QUALITY':
                bpy.data.scenes["Scene"].cycles.samples = 1

            case 'RECOMMENDED_QUALITY':
                bpy.data.scenes["Scene"].cycles.samples = 64

            case 'HIGH_QUALITY':
                bpy.data.scenes["Scene"].cycles.samples = 128

        # Remember the render engine so we can reset it after baking.
        self._original_render_engine = bpy.context.scene.render.engine

        # Start baking the mesh map.
        self.report({'INFO'}, "Starting mesh map baking, press escape (ESC) to cancel.")
        bpy.context.scene.render.engine = 'CYCLES'
        match self.mesh_map_type:
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
                bpy.ops.object.bake('INVOKE_DEFAULT', type='NORMAL')

            case _:
                bpy.context.scene.render.bake.use_selected_to_active = False
                bpy.ops.object.bake('INVOKE_DEFAULT', type='EMIT')

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

        # Re-apply the materials that were originally on the object and delete the temporary bake material.
        for i in range(0, len(bpy.context.object.material_slots)):
            bpy.context.object.material_slots[i].material = self._original_materials[i]

        # Remove the temporary baking material and the mesh map group node.
        bpy.data.materials.remove(self._temp_bake_material)
        if self._mesh_map_group_node:
            bpy.data.node_groups.remove(self._mesh_map_group_node)

        # Reset the render engine.
        bpy.context.scene.render.engine = self._original_render_engine

        self.report({'INFO'}, "Baking mesh map was manually cancelled.")

    def finish(self, context):
        # Remove the timer.
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

        # High the high poly object, there's no need for it to be visible anymore.
        high_poly_object = bpy.context.scene.matlayer_baking_settings.high_poly_object
        if high_poly_object:
            high_poly_object.hide_set(True)

        # Re-apply the materials that were originally on the object.
        if len(self._original_materials) > 0:
            for i in range(0, len(self._original_materials)):
                bpy.context.object.material_slots[i].material = self._original_materials[i]

        # Remove the temporary baking material and the mesh map group node.
        bpy.data.materials.remove(self._temp_bake_material)
        if self._mesh_map_group_node:
            bpy.data.node_groups.remove(self._mesh_map_group_node)

        # Reset the render engine.
        bpy.context.scene.render.engine = self._original_render_engine

        self.report({'INFO'}, "Baking mesh map completed.")

class MATLAYER_OT_batch_bake(Operator):
    bl_idname = "matlayer.batch_bake"
    bl_label = "Batch Bake"
    bl_description = "Bakes all checked mesh texture maps in succession. Note that this function can take a few minutes, especially on slower computers, or when using CPU for rendering"

    _timer = None
    _temp_bake_material_name = ""
    _mesh_map_image_index = 0
    _mesh_map_group_node_name = ""
    _mesh_maps_to_bake = []
    _baked_mesh_map_count = 0
    _original_material_names = []
    _original_render_engine = None

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
            # Check if the object is still baking.
            if not bpy.app.is_job_running('OBJECT_BAKE'):
                debug_logging.log("Finished baking {0}.".format(self._mesh_maps_to_bake[self._baked_mesh_map_count]))
                self._baked_mesh_map_count += 1

                temp_bake_material = bpy.data.materials.get(self._temp_bake_material_name)
                if temp_bake_material:
                    bpy.data.materials.remove(temp_bake_material)

                bake_node_group = bpy.data.node_groups.get(self._mesh_map_group_node_name)
                if bake_node_group:
                    bpy.data.node_groups.remove(bake_node_group)

                # Bake the next mesh map.
                if self._baked_mesh_map_count < len(self._mesh_maps_to_bake):
                    baked_successfully = bake_mesh_map(self._mesh_maps_to_bake[self._baked_mesh_map_count], self)
                    if baked_successfully == False:
                        self.finish(context)
                        return {'FINISHED'}

                # Finish the batch baking process if all mesh maps are baked.
                else:
                    self.finish(context)
                    return {'FINISHED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        if verify_bake_object(self) == False:
            return {'FINISHED'}
        
        self._mesh_maps_to_bake.clear()
        self._mesh_maps_to_bake = get_batch_bake_mesh_maps()    # Get a list of mesh maps to bake.

        # Make the low poly selected active object unhiden, selectable and visible.
        active_object = bpy.context.active_object
        active_object.hide_set(False)
        active_object.hide_render = False
        active_object.hide_select = False

        # Make the high poly mesh unhidden, selectable and visible.
        high_poly_object = bpy.context.scene.matlayer_baking_settings.high_poly_object
        if high_poly_object:
            high_poly_object.hide_set(False)
            high_poly_object.hide_render = False
            high_poly_object.hide_select = False

        # Cache original materials applied to the active object so the materials can be re-applied after baking.
        self._original_material_names.clear()
        active_object_material_slots = bpy.context.active_object.material_slots
        if len(active_object_material_slots) > 0:
            for x in active_object_material_slots:
                if x.material:
                    self._original_material_names.append(x.material.name)
                else:
                    self._original_material_names.append("")
        
        apply_baking_quality_settings()                                         # Apply bake settings and bake the material to a texture.
        self._original_render_engine = bpy.context.scene.render.engine          # Remember the render engine so we can reset it after baking.        
        baked_successfully = bake_mesh_map(self._mesh_maps_to_bake[0], self)    # Start baking the mesh map.
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

        # Re-apply the materials that were originally on the object and delete the temporary bake material.
        for i in range(0, len(self._original_material_names)):
            material = bpy.data.materials.get(self._original_material_names[i])
            if material:
                bpy.context.object.material_slots[i].material = material

        # Reset the render engine.
        bpy.context.scene.render.engine = self._original_render_engine

        debug_logging.log_status("Baking mesh map was manually cancelled.", self, 'INFO')

    def finish(self, context):
        # Remove the timer.
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

        # High the high poly object, there's no need for it to be visible anymore.
        high_poly_object = bpy.context.scene.matlayer_baking_settings.high_poly_object
        if high_poly_object:
            high_poly_object.hide_set(True)

        # Re-apply the materials that were originally on the object.
        for i in range(0, len(self._original_material_names)):
            material = bpy.data.materials.get(self._original_material_names[i])
            if material:
                bpy.context.object.material_slots[i].material = material

        # Reset the render engine.
        bpy.context.scene.render.engine = self._original_render_engine

        debug_logging.log_status("Baking mesh map completed.", self, 'INFO')

class MATLAYER_OT_open_bake_folder(Operator):
    bl_idname = "matlayer.open_bake_folder"
    bl_label = "Open Bake Folder"
    bl_description = "Opens the bake folder in your systems file explorer"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        matlayer_image_path = os.path.join(bpy.path.abspath("//"), "Assets")
        bake_path = os.path.join(matlayer_image_path, "MeshMaps")
        if os.path.exists(bake_path):
            os.startfile(bake_path)
        else:
            self.report({'ERROR'}, "Bake folder doesn't exist, bake mesh maps and the bake folder will be automatically created for you.")
        return {'FINISHED'}

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
        delete_meshmap('NORMALS', self)
        return {'FINISHED'}

class MATLAYER_OT_delete_world_space_normals_map(Operator):
    bl_idname = "matlayer.delete_world_space_normals_map"
    bl_label = "Delete World Space Normals Map"
    bl_description = "Deletes the baked world space normals map for the active object if one exists"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        delete_meshmap('WORLD_SPACE_NORMALS', self)
        return {'FINISHED'}