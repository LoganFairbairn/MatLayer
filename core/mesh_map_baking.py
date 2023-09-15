# This file contains baking operators and settings for common mesh map bake types.

import os
import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty, PointerProperty
from ..core import material_layers
from ..core import blender_addon_utils
from ..core import debug_logging
from .. import preferences
import re

MESH_MAP_MATERIAL_NAMES = (
    "BakeNormals",
    "BakeAmbientOcclusion",
    "BakeCurvature",
    "BakeThickness",
    "BakeWorldSpaceNormals"
)

MESH_MAP_TYPES = ("NORMALS", "AMBIENT_OCCLUSION", "CURVATURE", "THICKNESS", "WORLD_SPACE_NORMALS")

#----------------------------- UPDATING FUNCTIONS -----------------------------#

def update_match_bake_resolution(self, context):
    '''Match the height to the width.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    baking_settings = context.scene.matlayer_baking_settings
    if baking_settings.match_bake_resolution:
        addon_preferences.output_height = addon_preferences.output_width

def update_bake_width(self, context):
    '''Match the height to the width of the bake output'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    baking_settings = context.scene.matlayer_baking_settings
    if baking_settings.match_bake_resolution:
        if addon_preferences.output_height != addon_preferences.output_width:
            addon_preferences.output_height = addon_preferences.output_width

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
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    match addon_preferences.output_width:
        case 'FIVE_TWELVE':
            output_width = 512
        case 'ONEK':
            output_width = 1024
        case 'TWOK':
            output_width = 2048
        case 'FOURK':
            output_width = 4096

    match addon_preferences.output_height:
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
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    match addon_preferences.output_quality:
        case 'LOW_QUALITY':
            bpy.data.scenes["Scene"].cycles.samples = 1

        case 'RECOMMENDED_QUALITY':
            bpy.data.scenes["Scene"].cycles.samples = 64

        case 'HIGH_QUALITY':
            bpy.data.scenes["Scene"].cycles.samples = 128

def bake_mesh_map(mesh_map_type, self):
    '''Applies a premade baking material to the active object and starts baking. Returns true if baking was successful.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    baking_settings = bpy.context.scene.matlayer_baking_settings

    bpy.context.scene.render.engine = 'CYCLES'      # Set render engine to Cycles (required for baking).

    # Skip normal map baking if there is no high poly object defined, no normal information can be baked without a high poly object.
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

    # Apply the bake material to the low poly object.
    active_object = bpy.context.active_object
    if len(bpy.context.object.material_slots) > 0:
        for material_slot in bpy.context.object.material_slots:
            material_slot.material = temp_bake_material
    else:
        active_object.materials.append(temp_bake_material)

    # If a high poly object is specified...
    high_poly_object = baking_settings.high_poly_object
    if high_poly_object != None:
        # Apply the bake material to the high poly object (high poly details for curvature, ambient occlusion will not be transfered otherwise).
        if len(high_poly_object.material_slots) > 0:
            for material_slot in high_poly_object.material_slots:
                material_slot.material = temp_bake_material
        else:
            high_poly_object.materials.append(temp_bake_material)

        # Select the low poly and high poly objects in the correct order.
        bpy.ops.object.select_all(action='DESELECT')
        high_poly_object.select_set(True)
        active_object.select_set(True)

        # Apply high to low poly render settings
        bpy.context.scene.render.bake.use_selected_to_active = True
        bpy.context.scene.render.bake.cage_extrusion = addon_preferences.cage_extrusion

    else:
        bpy.context.scene.render.bake.use_selected_to_active = False

    # Trigger the baking process.
    match mesh_map_type:
        case 'NORMALS':
            bpy.ops.object.bake('INVOKE_DEFAULT', type='NORMAL')
        case _:
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
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    mesh_maps_to_bake = []

    if addon_preferences.bake_ambient_occlusion:
        mesh_maps_to_bake.append('AMBIENT_OCCLUSION')

    if addon_preferences.bake_curvature:
        mesh_maps_to_bake.append('CURVATURE')

    if addon_preferences.bake_thickness:
        mesh_maps_to_bake.append('THICKNESS')

    if addon_preferences.bake_normals:
        mesh_maps_to_bake.append('NORMALS')

    if addon_preferences.bake_world_space_normals:
        mesh_maps_to_bake.append('WORLD_SPACE_NORMALS')

    return mesh_maps_to_bake

#----------------------------- OPERATORS AND PROPERTIES -----------------------------#

class MATLAYER_baking_settings(bpy.types.PropertyGroup):
    match_bake_resolution: BoolProperty(name="Match Bake Resoltion", description="When toggled on, the bake resolution's width and height will be synced", default=True, update=update_match_bake_resolution)
    high_poly_object: PointerProperty(type=bpy.types.Object, name="High Poly Object", description="The high poly object (must be a mesh) from which mesh detail will be baked to texture maps. The high poly mesh should generally be overlapped by your low poly mesh before starting baking. You do not need to provide a high poly mesh for baking texture maps")

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

        material_layers.apply_mesh_maps()

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
        material_layers.apply_mesh_maps()

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
            active_object.materials.append(mesh_map_material)

        # If the object has material slots, assign the new color grid material to all material slots for all selected objects.
        else:
            active_object.active_material_index = 0
            for i in range(len(active_object.material_slots)):
                active_object.material_slots[i].material = mesh_map_material

        # Apply viewport and render engine settings to allow the user to see the mesh map preview.
        bpy.context.space_data.shading.type = 'RENDERED'
        bpy.context.scene.render.engine = 'CYCLES'

        return {'FINISHED'}

class MATLAYER_OT_disable_mesh_map_preview(Operator):
    bl_idname = "matlayer.disable_mesh_map_preview"
    bl_label = "Disable Mesh Map Preview"
    bl_description = "Sets the render engine back to EEVEE, and removes all mesh map preview materials on active objects (if any exist)"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):

        for mesh_map_type in MESH_MAP_TYPES:
            mesh_map_material_name = mesh_map_type.replace('_', ' ')
            mesh_map_material_name = "Bake" + re.sub(r'\b[a-z]', lambda m: m.group().upper(), mesh_map_material_name.capitalize())
            
            mesh_map_material = bpy.data.materials.get(mesh_map_material_name)
            if mesh_map_material:
                bpy.data.materials.remove(mesh_map_material)

        bpy.context.space_data.shading.type = 'MATERIAL'
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
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
