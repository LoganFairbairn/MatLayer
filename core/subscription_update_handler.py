import bpy
from ..core import material_layers
from ..core import layer_masks
from ..core import baking
from ..core import debug_logging

def on_active_material_index_changed():
    '''Reads material nodes into the user interface when the active material index is changed.'''
    debug_logging.log("Active material index changed.")
    bpy.context.scene.matlayer_layer_stack.selected_layer_index = 0
    material_layers.refresh_layer_stack()

    active_object = bpy.context.view_layer.objects.active
    if active_object:
        if active_object.active_material:
            bpy.types.Scene.previous_active_material_name = active_object.active_material.name
        else:
            bpy.types.Scene.previous_active_material_name = ""

def on_active_material_name_changed():
    '''Updates layer and mask group node names associated with materials created with this add-on when the active material is renamed.'''
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
    
    # Update names for any mesh maps related to the renamed object.
    previous_object_name = bpy.types.Scene.previous_object_name
    active_object = bpy.context.active_object

    for mesh_map_type in baking.MESH_MAP_TYPES:
        mesh_map_name = baking.get_meshmap_name(previous_object_name, mesh_map_type)
        mesh_map_image = bpy.data.images.get(mesh_map_name)
        if mesh_map_image:
            mesh_map_image.name = baking.get_meshmap_name(active_object.name, mesh_map_type)

    bpy.types.Scene.previous_object_name = bpy.context.view_layer.objects.active.name
    #bpy.context.scene.previous_object_name = active_object.name

def on_active_object_changed():
    '''Triggers a layer stack refresh when the selected object changes.'''

    material_layers.refresh_layer_stack()
    active_object = bpy.context.view_layer.objects.active
    
    if active_object:
        if active_object.type == 'MESH':

            debug_logging.log("Changed active object.")

            # Re-subscribe to the active objects name.
            bpy.types.Scene.previous_object_name = active_object.name
            bpy.msgbus.clear_by_owner(bpy.types.Scene.active_object_name_owner)
            bpy.msgbus.subscribe_rna(key=active_object.path_resolve("name", False), owner=bpy.types.Scene.active_object_name_owner, notify=on_active_object_name_changed, args=())

            if active_object.active_material:

                # Re-subscribe to the active material index.
                bpy.msgbus.clear_by_owner(bpy.types.Scene.active_material_index_owner)
                bpy.msgbus.subscribe_rna(key=active_object.path_resolve("active_material_index", False), owner=bpy.types.Scene.active_material_index_owner, notify=on_active_material_index_changed, args=())

                # Re-subscribe to the active materials name.
                bpy.types.Scene.previous_active_material_name = active_object.active_material.name
                bpy.types.Scene.active_material_name_owner = object()
                bpy.msgbus.clear_by_owner(bpy.types.Scene.active_material_name_owner)
                bpy.msgbus.subscribe_rna(key=active_object.active_material.path_resolve("name", False), owner=bpy.types.Scene.active_material_name_owner, notify=on_active_material_name_changed, args=())