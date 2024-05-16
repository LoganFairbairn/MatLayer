# This module contains functions for registering changes of properties and context within Blender to trigger updates of properties in this add-on.

import bpy
import os
from ..core import material_layers
from ..core import layer_masks
from ..core import mesh_map_baking
from ..core import debug_logging
from ..core import blender_addon_utils
from ..core import shaders


#----------------------------- SUBSCRIPTIONS -----------------------------#


def sub_to_active_object_name(active_object):
    '''Re-subscribes to the active object's name.'''
    bpy.types.Scene.previous_object_name = active_object.name
    bpy.msgbus.clear_by_owner(bpy.types.Scene.active_object_name_sub_owner)
    bpy.msgbus.subscribe_rna(key=active_object.path_resolve("name", False), owner=bpy.types.Scene.active_object_name_sub_owner, notify=on_active_object_name_changed, args=())
    debug_logging.log("Re-subscribed to the active objects name.", sub_process=True)

def sub_to_active_material_name(active_object):
    '''Re-subscribes to the active materials name.'''
    if active_object.active_material:
        bpy.types.Scene.previous_active_material_name = active_object.active_material.name
        bpy.msgbus.clear_by_owner(bpy.types.Scene.active_material_name_sub_owner)
        bpy.msgbus.subscribe_rna(key=active_object.active_material.path_resolve("name", False), owner=bpy.types.Scene.active_material_name_sub_owner, notify=on_active_material_name_changed, args=())
    debug_logging.log("Re-subscribed to the active material name.", sub_process=True)

def sub_to_active_material_index(active_object):
    '''Re-subscribe to the active material index.'''
    if active_object.active_material:
        bpy.msgbus.clear_by_owner(bpy.types.Scene.active_material_index_sub_owner)
        bpy.msgbus.subscribe_rna(key=active_object.path_resolve("active_material_index", False), owner=bpy.types.Scene.active_material_index_sub_owner, notify=on_active_material_index_changed, args=())
    debug_logging.log("Re-subscribed to the active material index.", sub_process=True)


#----------------------------- SUBSCRIPTION CALLBACK FUNCTIONS -----------------------------#


def on_active_material_changed(scene):
    '''Updates properties when the active material is changed.'''

    # Avoid running auto updates during operations that require them to be paused (i.e mesh map baking, exporting textures).
    if bpy.context.scene.pause_auto_updates == False:
        active_object = bpy.context.view_layer.objects.active
        if active_object:
            if active_object.active_material:
                if bpy.types.Scene.previous_active_material_name != active_object.active_material.name:
                    sub_to_active_material_index(active_object)
                    sub_to_active_material_name(active_object)
                    material_layers.refresh_layer_stack(reason="Active material changed.", scene=scene)
                    bpy.types.Scene.previous_active_material_name = active_object.active_material.name
                    shaders.read_shader(active_object.active_material)

            else:
                if bpy.types.Scene.previous_active_material_name != "":
                    sub_to_active_material_index(active_object)
                    sub_to_active_material_name(active_object)
                    material_layers.refresh_layer_stack(reason="Active material changed.", scene=scene)
                    bpy.types.Scene.previous_active_material_name = ""

def on_active_material_index_changed():
    '''Reads material nodes into the user interface when the active material index is changed.'''

    # Avoid running auto updates during operations that require them to be paused (i.e mesh map baking, exporting textures).
    if bpy.context.scene.pause_auto_updates == False:

        active_object = bpy.context.view_layer.objects.active
        if active_object:
            debug_logging.log("Active material index change detected, updating properties...", sub_process=True)

            if active_object.active_material:
                if active_object.active_material.name != bpy.types.Scene.previous_active_material_name:
                    bpy.context.scene.matlayer_layer_stack.selected_layer_index = 0
                    material_layers.refresh_layer_stack()
                    sub_to_active_material_index(active_object)
                    sub_to_active_material_name(active_object)
                    bpy.types.Scene.previous_active_material_name = active_object.active_material.name
                    shaders.read_shader(active_object.active_material)
    
            else:
                if bpy.types.Scene.previous_active_material_name != "":
                    bpy.context.scene.matlayer_layer_stack.selected_layer_index = 0
                    material_layers.refresh_layer_stack()
                    sub_to_active_material_index(active_object)
                    sub_to_active_material_name(active_object)
                    bpy.types.Scene.previous_active_material_name = ""

def on_active_material_name_changed():
    '''Updates layer and mask group node names associated with materials created with this add-on when the active material is renamed.'''
    if bpy.context.scene.pause_auto_updates == False:
        debug_logging.log("Active material name was changed.", sub_process=True)

        previous_material_name = bpy.types.Scene.previous_active_material_name
        active_material = bpy.context.active_object.active_material
        layer_count = material_layers.count_layers(active_material)

        # Rename all layer group nodes related to the renamed material.
        for i in range(0, layer_count):
            layer_node_tree = bpy.data.node_groups.get("{0}_{1}".format(previous_material_name, i))
            if layer_node_tree:
                layer_node_tree.name = material_layers.format_layer_group_node_name(active_material.name, i)

            # Rename all mask group nodes related to the renamed material.
            mask_count = layer_masks.count_masks(i, material_name=previous_material_name)
            for c in range(0, mask_count):
                mask_node_name = layer_masks.format_mask_name(i, c, previous_material_name)
                mask_node = active_material.node_tree.nodes.get(mask_node_name)
                if mask_node:
                    mask_node.name = layer_masks.format_mask_name(i, c, active_material.name)
                    mask_node.node_tree.name = mask_node.name

        bpy.types.Scene.previous_active_material_name = active_material.name
        debug_logging.log("Updated group node names for all group nodes related to the renamed material.")

def on_active_object_name_changed():
    '''Updates mesh maps names related to the active object when the active object's name is changed.'''
    if bpy.context.scene.pause_auto_updates == False:
        debug_logging.log("Active object name was changed...", sub_process=True)
        
        # Update names for any mesh maps related to the renamed object.
        previous_object_name = bpy.types.Scene.previous_object_name
        active_object = bpy.context.active_object

        for mesh_map_type in mesh_map_baking.MESH_MAP_TYPES:
            previous_mesh_map_name = mesh_map_baking.get_meshmap_name(previous_object_name, mesh_map_type)
            new_mesh_map_name = mesh_map_baking.get_meshmap_name(active_object.name, mesh_map_type)

            # Rename the images stored in the blend data.
            mesh_map_image = bpy.data.images.get(previous_mesh_map_name)
            if mesh_map_image:
                mesh_map_image.name = new_mesh_map_name

            # Rename the images stored in the raw textures folder.
            mesh_map_folder = blender_addon_utils.get_texture_folder_path(folder='MESH_MAPS')
            previous_mesh_map_filepath = os.path.join(mesh_map_folder, previous_mesh_map_name + ".png")
            if os.path.exists(previous_mesh_map_filepath):
                new_mesh_map_filepath = os.path.join(mesh_map_folder, new_mesh_map_name + ".png")
                os.rename(previous_mesh_map_filepath, new_mesh_map_filepath)

        bpy.types.Scene.previous_object_name = bpy.context.view_layer.objects.active.name
        debug_logging.log("Updated mesh map names for renamed object.")

def on_active_object_changed():
    '''Triggers a layer stack refresh when the selected object changes.'''
    if bpy.context.scene.pause_auto_updates == False:
        debug_logging.log("Active object changed...", sub_process=True)
        active_object = bpy.context.view_layer.objects.active
        if active_object:
            sub_to_active_object_name(active_object)
            sub_to_active_material_index(active_object)
            sub_to_active_material_name(active_object)

            # Read the shader from the active material if one exists.
            if active_object.active_material:
                shaders.read_shader(active_object.active_material)

            # Refresh the number of layers in the layer stack.
            material_layers.refresh_layer_stack("Active object changed.")