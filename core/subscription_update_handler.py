import bpy
from ..core import material_layers
from ..core import layer_masks
from ..core import debug_logging

def update_meshmap_names():
    '''Renames meshmap names when an object is renamed to ensure the mesh maps are still identifiable as being linked to the renamed object.'''
    print("Placeholder...")

def on_active_material_index_changed():
    '''Reads material nodes into the user interface when the active material index is changed.'''
    bpy.context.scene.matlayer_layer_stack.selected_layer_index = 0
    material_layers.refresh_layer_stack()
    bpy.types.Scene.previous_active_material_name = bpy.context.view_layer.objects.active.active_material.name

def on_active_material_name_changed():
    '''Updates layer and mask group node names associated with materials created with this add-on when the active material is renamed.'''
    previous_material_name = bpy.types.Scene.previous_active_material_name
    active_material = bpy.context.active_object.active_material
    layer_count = material_layers.count_layers(active_material)

    # Rename all layer group nodes related to the renamed material.
    for i in range(0, layer_count):
        layer_node_tree = bpy.data.node_groups.get("{0}_{1}".format(previous_material_name, i))
        if layer_node_tree:
            layer_node_tree.name = "{0}_{1}".format(active_material.name, i)

        # Rename all mask group nodes related to the renamed material.
        mask_count = layer_masks.count_masks(i)
        for c in range(0, mask_count):
            mask_node_tree = bpy.data.node_groups.get("{0}_{1}_{2}".format(previous_material_name, i, c))
            if mask_node_tree:
                mask_node_tree.name = "{0}_{1}_{2}".format(active_material.name, i, c)

    bpy.types.Scene.previous_active_material_name = active_material.name
    debug_logging.log("Updated group node names for all group nodes related to the renamed material.")

def on_active_object_name_changed():
    '''Updates mesh maps when the object name is changed.'''
    update_meshmap_names(bpy.types.Scene.previous_object_name)
    bpy.types.Scene.previous_object_name = bpy.context.view_layer.objects.active.name

def on_active_object_changed():
    '''Triggers a layer stack refresh when the selected object changes.'''

    material_layers.refresh_layer_stack()
    active_object = bpy.context.view_layer.objects.active

    # Re-subscribe to the active objects name.
    bpy.types.Scene.previous_object_name = active_object.name
    bpy.msgbus.clear_by_owner(bpy.types.Scene.active_object_name_owner)
    if active_object:
        if active_object.type == 'MESH':
            bpy.msgbus.subscribe_rna(key=active_object.path_resolve("name", False), owner=bpy.types.Scene.active_object_name_owner, notify=on_active_object_name_changed, args=())

            if active_object.active_material:

                # Re-subscribe to the active material index
                bpy.msgbus.clear_by_owner(bpy.types.Scene.active_material_index_owner)
                bpy.msgbus.subscribe_rna(key=active_object.path_resolve("active_material_index", False), owner=bpy.types.Scene.active_material_index_owner, notify=on_active_material_index_changed, args=())

                # Re-subscribe to the active materials name.
                bpy.types.Scene.previous_active_material_name = active_object.active_material.name
                bpy.types.Scene.active_material_name_owner = object()
                bpy.msgbus.clear_by_owner(bpy.types.Scene.active_material_name_owner)
                if active_object.type == 'MESH' and active_object.active_material:
                    bpy.msgbus.subscribe_rna(key=active_object.active_material.path_resolve("name", False), owner=bpy.types.Scene.active_material_index_owner,notify=on_active_material_name_changed, args=())