# This file contains baking operators and settings for common mesh map bake types.

import os
import bpy
from bpy.types import Operator
from bpy.props import StringProperty, PointerProperty
from ..core import material_layers
from ..core import blender_addon_utils
from ..core import debug_logging
from ..core import texture_set_settings as tss
from .. import preferences

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

MESH_MAP_TYPES = ("NORMALS", "AMBIENT_OCCLUSION", "CURVATURE", "THICKNESS", "WORLD_SPACE_NORMALS")


#----------------------------- UPDATING FUNCTIONS -----------------------------#


def update_occlusion_samples(self, context):
    '''Updates the occlusion samples setting in the active material'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    node = get_meshmap_node('AMBIENT_OCCLUSION')
    if node:
        node.samples = addon_preferences.occlusion_samples

def update_occlusion_distance(self, context):
    '''Updates the occlusion distance setting in the active material'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    node = get_meshmap_node('AMBIENT_OCCLUSION')
    if node:
        node.inputs.get('Distance').default_value = addon_preferences.occlusion_distance

def update_occlusion_intensity(self, context):
    '''Updates the occlusion contrast setting in the active material.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    node = get_meshmap_node('AMBIENT_OCCLUSION_INTENSITY')
    if node:
        node.inputs[1].default_value = addon_preferences.occlusion_intensity

def update_local_occlusion(self, context):
    '''Updates the local occlusion setting in the active material.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    node = get_meshmap_node('AMBIENT_OCCLUSION')
    if node:
        node.only_local = addon_preferences.local_occlusion

def update_bevel_radius(self, context):
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    node = get_meshmap_node('BEVEL')
    if node:
        active_object = bpy.context.active_object
        if addon_preferences.relative_to_bounding_box:
            bounding_box_multiplier = (active_object.dimensions[0] + active_object.dimensions[1] + active_object.dimensions[2]) / 3
            node.inputs[0].default_value = addon_preferences.bevel_radius * bounding_box_multiplier
        else:
            node.inputs[0].default_value = addon_preferences.bevel_radius

def update_bevel_samples(self, context):
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    node = get_meshmap_node('BEVEL')
    if node:
        node.samples = addon_preferences.bevel_samples


#----------------------------- HELPER FUNCTIONS -----------------------------#


def get_meshmap_node(node_type):
    '''Returns a node found within a mesh map material setup if it exists.'''
    active_object = bpy.context.active_object
    if active_object:
        if active_object.active_material:
            ao_node = active_object.active_material.node_tree.nodes.get('MESH_MAP')
            if ao_node:
                return ao_node.node_tree.nodes.get(node_type)
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

def create_bake_image(mesh_map_type, object_name):
    '''Creates a new image in Blender's data to bake to.'''

    # Use the object's name and bake type to define the bake image name.
    mesh_map_name = get_meshmap_name(object_name, mesh_map_type)

    # Specific mesh maps require higher image color bit depth to be able to store optimal amounts of mesh information.
    if mesh_map_type == 'NORMALS' or mesh_map_type == 'CURVATURE':
        high_bit_depth = True
    else:
        high_bit_depth = False

    # For anti-aliasing, mesh maps are baked at a higher resolution and then scaled down (which effectively applies anti-aliasing).
    # Define the anti-aliasing multiplier based on mesh map settings.
    anti_aliasing_multiplier = 1
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    match getattr(addon_preferences.mesh_map_anti_aliasing, mesh_map_type.lower() + "_anti_aliasing", '1X'):
        case '1X':
            anti_aliasing_multiplier = 1
        case '2X':
            anti_aliasing_multiplier = 2
        case '4X':
            anti_aliasing_multiplier = 4

    # Set an image pixel resolution multiplier for mesh map upscaling.
    match addon_preferences.mesh_map_upscaling_multiplier:
        case 'NO_UPSCALE':
            upscale_multiplier = 1.0
        case '2X':
            upscale_multiplier = 0.5
        case '4X':
            upscale_multiplier = 0.25
        case '8X':
            upscale_multiplier = 0.125

    # Create a new image in Blender's data, delete existing bake image if it exists.
    new_image_width = int(tss.get_texture_width() * anti_aliasing_multiplier * upscale_multiplier)
    new_image_height = int(tss.get_texture_height() * anti_aliasing_multiplier * upscale_multiplier)
    mesh_map_image = blender_addon_utils.create_image(
        new_image_name=mesh_map_name,
        image_width=new_image_width,
        image_height=new_image_height,
        base_color=(0.0, 0.0, 0.0, 1.0),
        alpha_channel=False,
        thirty_two_bit=high_bit_depth,
        add_unique_id=False,
        delete_existing=True
    )

    mesh_map_image.colorspace_settings.name = 'Non-Color'
    mesh_map_image.use_fake_user = True
    return mesh_map_image

def apply_baking_settings():
    '''Applies baking settings to existing node setups before baking.'''
    update_occlusion_samples(None, None)
    update_occlusion_distance(None, None)
    update_occlusion_intensity(None, None)
    update_local_occlusion(None, None)
    update_bevel_radius(None, None)
    update_bevel_samples(None, None)

def apply_mesh_map_quality():
    '''Applies mesh map quality settings.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    match addon_preferences.mesh_map_quality:
        case 'TEST_QUALITY':
            bpy.context.scene.cycles.samples = 1

        case 'EXTREMELY_LOW_QUALITY':
            bpy.context.scene.cycles.samples = 8

        case 'VERY_LOW_QUALITY':
            bpy.context.scene.cycles.samples = 16

        case 'LOW_QUALITY':
            bpy.context.scene.cycles.samples = 32

        case 'RECOMMENDED_QUALITY':
            bpy.context.scene.cycles.samples = 64

        case 'HIGH_QUALITY':
            bpy.context.scene.cycles.samples = 128

        case 'INSANE_QUALITY':
            bpy.context.scene.cycles.samples = 256

def bake_mesh_map(mesh_map_type, object_name, self):
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

    # Apply baking settings to the baking material setup.
    apply_baking_settings()

    # Create and assign an image to bake the mesh map to.
    new_bake_image = create_bake_image(mesh_map_type, object_name)
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
        #bpy.context.scene.render.bake.cage_extrusion = addon_preferences.cage_extrusion

    else:
        bpy.context.scene.render.bake.use_selected_to_active = False

    # Apply mesh map quality settings.
    apply_mesh_map_quality()

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

def remove_mesh_map_baking_assets():
    '''Removes all mesh map baking materials and nodes if they exist.'''
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

def remove_triangulate_modifiers():
    '''Removes the triangulate modifiess from the low and high poly objects.'''
    active_object = bpy.context.active_object
    if active_object:
        triangulate_modifier = active_object.modifiers.get('BAKE_TRIANGULATE')
        if triangulate_modifier:
            active_object.modifiers.remove(triangulate_modifier)

    high_poly_object = bpy.context.scene.matlayer_baking_settings.high_poly_object
    if high_poly_object:
        triangulate_modifier = high_poly_object.modifiers.get('BAKE_TRIANGULATE')
        if triangulate_modifier:
            high_poly_object.modifiers.remove(triangulate_modifier)

def delete_auto_cage_object():
    '''Deletes the auto cage object created for mesh map baking if one exists.'''
    low_poly_object = bpy.context.active_object
    if low_poly_object:
        cage_object = bpy.data.objects.get(low_poly_object.name + "_Cage")
        if cage_object:
            bpy.data.objects.remove(cage_object)


#----------------------------- OPERATORS AND PROPERTIES -----------------------------#


class MATLAYER_baking_settings(bpy.types.PropertyGroup):
    high_poly_object: PointerProperty(type=bpy.types.Object, name="High Poly Object", description="The high poly object (must be a mesh) from which mesh detail will be baked to texture maps. The high poly mesh should generally be overlapped by your low poly mesh before starting baking. You do not need to provide a high poly mesh for baking texture maps")

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

                # Pack baked mesh map images.
                mesh_map_type = self._mesh_maps_to_bake[self._baked_mesh_map_count]
                mesh_map_name = get_meshmap_name(bpy.context.active_object.name, mesh_map_type)
                mesh_map_image = bpy.data.images.get(mesh_map_name)
                if mesh_map_image:
                    mesh_map_image.pack()

                    # Scale baked textures down to apply anti-aliasing.
                    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
                    match getattr(addon_preferences.mesh_map_anti_aliasing, mesh_map_type.lower() + "_anti_aliasing", '1X'):
                        case '2X':
                            mesh_map_image.scale(int(mesh_map_image.size[0] * 0.5), int(mesh_map_image.size[1] * 0.5))
                        case '4X':                            
                            mesh_map_image.scale(int(mesh_map_image.size[0] * 0.25), int(mesh_map_image.size[1] * 0.25))

                    # Scale baked textures up to match the texture set resolution size.
                    match addon_preferences.mesh_map_upscaling_multiplier:
                        case '2X':
                            mesh_map_image.scale(int(mesh_map_image.size[0] * 2), int(mesh_map_image.size[1] * 2))
                        case '4X':
                            mesh_map_image.scale(int(mesh_map_image.size[0] * 4), int(mesh_map_image.size[1] * 4))
                        case '8X':
                            mesh_map_image.scale(int(mesh_map_image.size[0] * 8), int(mesh_map_image.size[1] * 8))

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
        # Remove lingering mesh map assets if they exist.
        remove_mesh_map_baking_assets()

        # Verify the active object can be baked to.
        if blender_addon_utils.verify_bake_object(self) == False:
            return {'FINISHED'}

        # To avoid errors don't start baking if there is already a bake job running.
        if bpy.app.is_job_running('OBJECT_BAKE') == True:
            debug_logging.log_status("Bake job already in process, cancel or wait until the bake is finished before starting another.", self)
            return {'FINISHED'}
        
        addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
        bpy.context.scene.pause_auto_updates = True
        debug_logging.log("Starting mesh map baking...", sub_process=False)

        # Ensure we start this operation in object mode.
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        # Get a list of mesh maps to bake.
        self._mesh_maps_to_bake.clear()
        self._mesh_maps_to_bake = get_batch_bake_mesh_maps()
        if len(self._mesh_maps_to_bake) <= 0:
            debug_logging.log_status("No mesh maps checked for baking.", self, type='INFO')
            return {'FINISHED'}

        # Adjust settings based on the defined cage mode.
        low_poly_object = bpy.context.active_object
        match addon_preferences.cage_mode:

            # No cage object will be used.
            case 'NO_CAGE':
                bpy.context.scene.render.bake.use_cage = False

            # A cage object will be automatically created for baking by duplicating the low poly object and scaling it's normals using a complex solidify modifier.
            case 'AUTO_CAGE':
                auto_cage_object = None
                if bpy.context.scene.render.bake.cage_object == None:
                    auto_cage_object = low_poly_object.copy()
                    auto_cage_object.data = low_poly_object.data.copy()
                    auto_cage_object.name = low_poly_object.name + "_Cage"
                    bpy.context.collection.objects.link(auto_cage_object)
                    bpy.context.scene.render.bake.cage_object = auto_cage_object

                    blender_addon_utils.select_only(auto_cage_object)
                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.transform.shrink_fatten(
                        value=addon_preferences.cage_upscale,
                        use_even_offset=False, 
                        mirror=True, 
                        use_proportional_edit=False,
                        proportional_edit_falloff='SMOOTH', 
                        proportional_size=1, 
                        use_proportional_connected=False, 
                        use_proportional_projected=False, 
                        snap=False
                    )

                    # Triangulate the automatically created cage object.
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                    if addon_preferences.triangulate:
                        blender_addon_utils.add_modifier(auto_cage_object, new_modifier_type='TRIANGULATE', modifier_name='BAKE_TRIANGULATE', only_one=True)
                        bpy.ops.object.modifier_apply(modifier="BAKE_TRIANGULATE", report=True)

                    # Hide the auto cage object, it doesn't need to be visible for baking.
                    auto_cage_object.hide_set(True)
                    auto_cage_object.hide_render = True
                    blender_addon_utils.select_only(low_poly_object)

            # The cage is manually defined by the user, check one was provided.
            case 'MANUAL_CAGE':
                bpy.context.scene.render.bake.use_cage = True
                if bpy.context.scene.render.bake.cage_object == None:
                    debug_logging.log_status("No cage object was provided. Please use no cage, auto cage mode, or define a cage object before baking", self, type='INFO')
                    return {'FINISHED'}
                
                else:
                    # Triangulate the manually created cage object.
                    if addon_preferences.triangulate:
                        cage_object = bpy.context.scene.render.bake.cage_object
                        blender_addon_utils.add_modifier(cage_object, new_modifier_type='TRIANGULATE', modifier_name='BAKE_TRIANGULATE', only_one=True)
                        blender_addon_utils.select_only(cage_object)
                        bpy.ops.object.modifier_apply(modifier="BAKE_TRIANGULATE", report=False)
                        blender_addon_utils.select_only(low_poly_object)

        # Ensure the low poly selected active object unhiden, selectable and visible.
        low_poly_object.hide_set(False)
        low_poly_object.hide_render = False

        # Make the high poly mesh unhidden, selectable and visible.
        high_poly_object = bpy.context.scene.matlayer_baking_settings.high_poly_object
        if high_poly_object:
            high_poly_object.hide_set(False)
            high_poly_object.hide_render = False

        # Triangulate the high, and low poly objects based on baking settings.
        if addon_preferences.triangulate:
            blender_addon_utils.add_modifier(low_poly_object, new_modifier_type='TRIANGULATE', modifier_name='BAKE_TRIANGULATE', only_one=True)

            if high_poly_object:
                blender_addon_utils.add_modifier(high_poly_object, new_modifier_type='TRIANGULATE', modifier_name='BAKE_TRIANGULATE', only_one=True)

            debug_logging.log("Applied triangulation to all bake objects.", sub_process=True)

        # Cache original materials applied to the active object so the materials can be re-applied after baking.
        self._original_material_names.clear()
        low_poly_obj_material_slots = bpy.context.active_object.material_slots
        if len(low_poly_obj_material_slots) > 0:
            for x in low_poly_obj_material_slots:
                if x.material:
                    self._original_material_names.append(x.material.name)
                else:
                    self._original_material_names.append("")

        # Remember the render engine so we can reset it after baking.
        self._original_render_engine = bpy.context.scene.render.engine

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

        # Re-apply the materials that were originally on the object and delete the temporary bake material.
        for i in range(0, len(self._original_material_names)):
            material = bpy.data.materials.get(self._original_material_names[i])
            if material:
                bpy.context.object.material_slots[i].material = material

        remove_triangulate_modifiers()
        delete_auto_cage_object()

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

        # High the high poly object, there's no need for it to be visible anymore.
        high_poly_object = bpy.context.scene.matlayer_baking_settings.high_poly_object
        if high_poly_object:
            high_poly_object.hide_set(True)
            high_poly_object.hide_render = True

        # Re-apply the materials that were originally on the object.
        for i in range(0, len(self._original_material_names)):
            material = bpy.data.materials.get(self._original_material_names[i])
            if material:
                bpy.context.object.material_slots[i].material = material

        remove_triangulate_modifiers()
        delete_auto_cage_object()

        # Select only the low poly object.
        low_poly_object = bpy.context.active_object
        if low_poly_object:
            blender_addon_utils.select_only(low_poly_object)

        # Reset the render engine.
        bpy.context.scene.render.engine = self._original_render_engine
        debug_logging.log_status("Baking mesh map(s) completed.", self, 'INFO')

        # Apply mesh maps to the existing material.
        material_layers.apply_mesh_maps()

        # Unpause auto updates, mark baking mesh maps as complete.
        bpy.context.scene.pause_auto_updates = False

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

        # Make sure there are no lingering existing mesh map assets.
        remove_mesh_map_baking_assets()

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
    bl_description = "Sets the render engine back to EEVEE, and removes all mesh map preview materials on active objects (if any exist)"

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        remove_mesh_map_baking_assets()
        bpy.context.space_data.shading.type = 'MATERIAL'
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
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
