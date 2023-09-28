# This module contains functions for registering changes of properties and context within Blender to trigger updates of properties in this add-on.

import bpy
from ..core import material_layers
from ..core import layer_masks
from ..core import mesh_map_baking
from ..core import debug_logging


#----------------------------- SUBSCRIPTIONS -----------------------------#


def sub_to_active_object_name(active_object):
    '''Re-subscribes to the active object's name.'''
    debug_logging.log("Re-subscribing to the active object's name...", sub_process=True)
    bpy.types.Scene.previous_object_name = active_object.name
    bpy.msgbus.clear_by_owner(bpy.types.Scene.active_object_name_sub_owner)
    bpy.msgbus.subscribe_rna(key=active_object.path_resolve("name", False), owner=bpy.types.Scene.active_object_name_sub_owner, notify=on_active_object_name_changed, args=())
    debug_logging.log("Re-subscribed to the active objects name.")

def sub_to_active_material_name(active_object):
    '''Re-subscribes to the active materials name.'''
    debug_logging.log("Re-subscribing to the active material name...", sub_process=True)
    if active_object.active_material:
        bpy.types.Scene.previous_active_material_name = active_object.active_material.name
        bpy.msgbus.clear_by_owner(bpy.types.Scene.active_material_name_sub_owner)
        bpy.msgbus.subscribe_rna(key=active_object.active_material.path_resolve("name", False), owner=bpy.types.Scene.active_material_name_sub_owner, notify=on_active_material_name_changed, args=())
    debug_logging.log("Re-subscribed to the active material name.", sub_process=True)

def sub_to_active_material_index(active_object):
    '''Re-subscribe to the active material index.'''
    debug_logging.log("Re-subscribing to the active material index...", sub_process=True)
    if active_object.active_material:
        bpy.msgbus.clear_by_owner(bpy.types.Scene.active_material_index_sub_owner)
        bpy.msgbus.subscribe_rna(key=active_object.path_resolve("active_material_index", False), owner=bpy.types.Scene.active_material_index_sub_owner, notify=on_active_material_index_changed, args=())
    debug_logging.log("Re-subscribed to the active material index.", sub_process=True)


#----------------------------- SUBSCRIPTION CALLBACK FUNCTIONS -----------------------------#


def on_active_material_changed(scene):
    '''Update properties when the active material is changed.'''

    # Avoid running auto updates during operations that require them to be paused (i.e mesh map baking, exporting textures).
    if bpy.context.scene.pause_auto_updates == False:

        # Ensure the active object attribute exists within this context (causes exception crashes otherwise).
        active_object_attibute = getattr(bpy.context.view_layer.objects, "active", None)
        if active_object_attibute:
            active_object = bpy.context.view_layer.objects.active
            if active_object:

                # Only trigger the active material callback if the active material is different from the previous material.
                if bpy.context.scene.previous_active_material_name != active_object.name:
                    debug_logging.log("Active material change detected, updating properties...", sub_process=True)
                    sub_to_active_material_index(active_object)
                    sub_to_active_material_name(active_object)
                    material_layers.refresh_layer_stack(reason="Active material changed.", scene=scene)

def on_active_material_index_changed():
    '''Reads material nodes into the user interface when the active material index is changed.'''
    if bpy.context.scene.pause_auto_updates == False:
        debug_logging.log("Active material index was changed...", sub_process=True)
        active_object = bpy.context.view_layer.objects.active
        if active_object:
            if active_object.type == 'MESH':
                if active_object.active_material:
                    bpy.types.Scene.previous_active_material_name = active_object.active_material.name
                    bpy.context.scene.matlayer_layer_stack.selected_layer_index = 0
                    material_layers.refresh_layer_stack()
                    sub_to_active_material_index(active_object)
                    sub_to_active_material_name(active_object)
                else:
                    bpy.types.Scene.previous_active_material_name = ""

def on_active_material_name_changed():
    '''Updates layer and mask group node names associated with materials created with this add-on when the active material is renamed.'''
    if bpy.context.scene.pause_auto_updates == False:
        debug_logging.log("Active material name was changed...", sub_process=True)

        previous_material_name = bpy.types.Scene.previous_active_material_name
        active_material = bpy.context.active_object.active_material
        layer_count = material_layers.count_layers(active_material)

        # Rename all layer group nodes related to the renamed material.
        for i in range(0, layer_count):
            layer_node_tree = bpy.data.node_groups.get("{0}_{1}".format(previous_material_name, i))
            if layer_node_tree:
                layer_node_tree.name = material_layers.format_layer_group_node_name(active_material.name, i)

            # Rename all mask group nodes related to the renamed material.
            mask_count = layer_masks.count_masks(i)
            for c in range(0, mask_count):
                mask_node_tree = bpy.data.node_groups.get("{0}_{1}_{2}".format(previous_material_name, i, c))
                if mask_node_tree:
                    mask_node_tree.name = layer_masks.format_mask_name(i, c, active_material.name)

        bpy.types.Scene.previous_active_material_name = active_material.name
        debug_logging.log("Updated group node names for all group nodes related to the renamed material.")

def on_active_object_name_changed():
    '''Updates properties when the object name is changed.'''
    if bpy.context.scene.pause_auto_updates == False:
        debug_logging.log("Active object name was changed...", sub_process=True)
        
        # Update names for any mesh maps related to the renamed object.
        previous_object_name = bpy.types.Scene.previous_object_name
        active_object = bpy.context.active_object

        for mesh_map_type in mesh_map_baking.MESH_MAP_TYPES:
            mesh_map_name = mesh_map_baking.get_meshmap_name(previous_object_name, mesh_map_type)
            mesh_map_image = bpy.data.images.get(mesh_map_name)
            if mesh_map_image:
                mesh_map_image.name = mesh_map_baking.get_meshmap_name(active_object.name, mesh_map_type)

        bpy.types.Scene.previous_object_name = bpy.context.view_layer.objects.active.name
        debug_logging.log("Updated mesh map names after active object was renamed.")

def on_active_object_changed():
    '''Triggers a layer stack refresh when the selected object changes.'''
    if bpy.context.scene.pause_auto_updates == False:
        debug_logging.log("Active object changed...", sub_process=True)
        active_object = bpy.context.view_layer.objects.active
        if active_object:
            if active_object.type == 'MESH':
                sub_to_active_object_name(active_object)
                sub_to_active_material_index(active_object)
                sub_to_active_material_name(active_object)
                material_layers.refresh_layer_stack("Active object changed.")