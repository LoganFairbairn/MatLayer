# Copyright (c) 2021-2023 Logan Fairbairn
# logan-fairbairn@outlook.com
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# This file imports and registers all required modules for this add-on.

import bpy
import bpy.utils.previews       # Imported for loading layer texture previews as icons.
from bpy.props import PointerProperty, CollectionProperty, EnumProperty, StringProperty
from bpy.app.handlers import persistent

# Preferences
from .preferences import MATLAYER_pack_textures, MATLAYER_RGBA_pack_channels, MATLAYER_texture_export_settings, AddonPreferences

# Texture Set Settings
from .core.texture_set_settings import MATLAYER_texture_set_settings, MATLAYER_OT_toggle_texture_set_material_channel

# Material Layers
from .core.material_layers import MATLAYER_layer_stack, MATLAYER_layers, MATLAYER_OT_add_material_layer, MATLAYER_OT_add_paint_material_layer, MATLAYER_OT_add_decal_material_layer, MATLAYER_OT_delete_layer, MATLAYER_OT_duplicate_layer, MATLAYER_OT_move_material_layer_up, MATLAYER_OT_move_material_layer_down, MATLAYER_OT_toggle_material_channel_preview, MATLAYER_OT_toggle_layer_blur, MATLAYER_OT_toggle_material_channel_blur, MATLAYER_OT_toggle_hide_layer, MATLAYER_OT_set_layer_projection_uv, MATLAYER_OT_set_layer_projection_triplanar, MATLAYER_OT_change_material_channel_value_node, MATLAYER_OT_toggle_triplanar_flip_correction, MATLAYER_OT_isolate_material_channel, refresh_layer_stack

# Layer Masks
from .core.layer_masks import MATLAYER_mask_stack, MATLAYER_masks, MATLAYER_UL_mask_list, MATLAYER_OT_move_layer_mask_up, MATLAYER_OT_move_layer_mask_down, MATLAYER_OT_duplicate_layer_mask, MATLAYER_OT_delete_layer_mask, MATLAYER_OT_add_empty_layer_mask, MATLAYER_OT_add_black_layer_mask, MATLAYER_OT_add_white_layer_mask, MATLAYER_OT_add_edge_wear_mask, MATLAYER_OT_set_mask_projection_uv, MATLAYER_OT_set_mask_projection_triplanar, MATLAYER_OT_set_mask_output_channel, MATLAYER_OT_toggle_mask_blur, MATLAYER_OT_isolate_mask

# Baking
from .core.baking import MATLAYER_baking_settings, MATLAYER_OT_bake_mesh_map, MATLAYER_OT_batch_bake, MATLAYER_OT_open_bake_folder, MATLAYER_OT_delete_ao_map, MATLAYER_OT_delete_curvature_map, MATLAYER_OT_delete_thickness_map, MATLAYER_OT_delete_normal_map, MATLAYER_OT_delete_world_space_normals_map, update_meshmap_names

# Exporting
from .core.exporting import MATLAYER_exporting_settings, MATLAYER_OT_export, MATLAYER_OT_open_export_folder, MATLAYER_OT_set_export_template, MATLAYER_OT_save_export_template, MATLAYER_OT_add_export_texture, MATLAYER_OT_remove_export_texture, ExportTemplateMenu, set_export_template

# Utilities
from .core.image_utilities import MATLAYER_OT_add_texture_node_image, MATLAYER_OT_import_texture_node_image, MATLAYER_OT_edit_texture_node_image_externally, MATLAY_OT_export_uvs, MATLAYER_OT_reload_texture_node_image, MATLAYER_OT_delete_texture_node_image, MATLAY_OT_image_edit_uvs
from .core.layer_utilities import MATLAYER_OT_import_texture_set, MATLAYER_OT_merge_materials
from .core.utility_operations import MATLAYER_OT_set_decal_layer_snapping, MATLAYER_OT_append_workspace, MATLAYER_OT_append_basic_brushes

# User Interface
from .ui.ui_section_tabs import UtilitySubMenu
from .ui.ui_layer_section import MATLAYER_OT_add_material_layer_menu, MATLAYER_OT_add_layer_mask_menu, MATLAYER_OT_add_material_filter_menu, ImageUtilitySubMenu, LayerProjectionModeSubMenu, MaskProjectionModeSubMenu, MaterialChannelValueNodeSubMenu, LayerUtilitySubMenu, LayerTriplanarProjectionSubMenu, MaskChannelSubMenu, MATERIAL_LAYER_PROPERTY_TABS
from .ui.ui_main import *
from .ui.ui_layer_stack import MATLAYER_UL_layer_list

# Subscription Update Handler
from .core.subscription_update_handler import on_active_object_changed, on_active_object_name_changed, on_active_material_index_changed, on_active_material_name_changed

bl_info = {
    "name": "MatLayer",
    "author": "Logan Fairbairn (Ryver)",
    "version": (2, 0, 0),
    "blender": (3, 6, 1),
    "location": "View3D > Sidebar > MatLayer",
    "description": "Replaces node based texturing workflow with a layer stack workflow through a custom user interface.",
    "warning": "",
    "doc_url": "",
    "category": "Material Editing",
}

# List of classes to be registered.
classes = (
    # Preferences
    MATLAYER_pack_textures, 
    MATLAYER_RGBA_pack_channels,
    MATLAYER_texture_export_settings,
    AddonPreferences,

    # Baking
    MATLAYER_baking_settings,
    MATLAYER_OT_bake_mesh_map,
    MATLAYER_OT_batch_bake,
    MATLAYER_OT_open_bake_folder,
    MATLAYER_OT_delete_ao_map,
    MATLAYER_OT_delete_curvature_map,
    MATLAYER_OT_delete_thickness_map,
    MATLAYER_OT_delete_normal_map,
    MATLAYER_OT_delete_world_space_normals_map,

    # Exporting
    MATLAYER_exporting_settings,
    MATLAYER_OT_export,
    MATLAYER_OT_open_export_folder,
    MATLAYER_OT_set_export_template,
    MATLAYER_OT_save_export_template,
    MATLAYER_OT_add_export_texture,
    MATLAYER_OT_remove_export_texture,
    ExportTemplateMenu,

    # Material Layers
    MATLAYER_layer_stack,
    MATLAYER_layers,
    MATLAYER_OT_add_material_layer, 
    MATLAYER_OT_add_paint_material_layer,
    MATLAYER_OT_add_decal_material_layer,
    MATLAYER_OT_delete_layer,
    MATLAYER_OT_duplicate_layer, 
    MATLAYER_OT_move_material_layer_up,
    MATLAYER_OT_move_material_layer_down,
    MATLAYER_OT_toggle_material_channel_preview,
    MATLAYER_OT_toggle_layer_blur,
    MATLAYER_OT_toggle_material_channel_blur,
    MATLAYER_OT_toggle_hide_layer,
    MATLAYER_OT_set_layer_projection_uv,
    MATLAYER_OT_set_layer_projection_triplanar,
    MATLAYER_OT_change_material_channel_value_node,
    MATLAYER_OT_toggle_triplanar_flip_correction,
    MATLAYER_OT_isolate_material_channel,

    # Layer Masks
    MATLAYER_mask_stack, 
    MATLAYER_masks,
    MATLAYER_UL_mask_list,
    MATLAYER_OT_move_layer_mask_up, 
    MATLAYER_OT_move_layer_mask_down,
    MATLAYER_OT_duplicate_layer_mask,
    MATLAYER_OT_delete_layer_mask,
    MATLAYER_OT_add_empty_layer_mask,
    MATLAYER_OT_add_black_layer_mask,
    MATLAYER_OT_add_white_layer_mask,
    MATLAYER_OT_add_edge_wear_mask,
    MATLAYER_OT_set_mask_projection_uv,
    MATLAYER_OT_set_mask_projection_triplanar,
    MATLAYER_OT_set_mask_output_channel,
    MATLAYER_OT_toggle_mask_blur,
    MATLAYER_OT_isolate_mask,

    # Image Utilities
    MATLAYER_OT_add_texture_node_image, 
    MATLAYER_OT_import_texture_node_image, 
    MATLAYER_OT_edit_texture_node_image_externally,
    MATLAY_OT_export_uvs,
    MATLAYER_OT_reload_texture_node_image, 
    MATLAYER_OT_delete_texture_node_image,
    MATLAY_OT_image_edit_uvs,

    # Layer Utilities
    MATLAYER_OT_import_texture_set,
    MATLAYER_OT_merge_materials,

    # Texture Set Settings
    MATLAYER_texture_set_settings,
    MATLAYER_OT_toggle_texture_set_material_channel,

    # Utility Operators
    MATLAYER_OT_set_decal_layer_snapping,
    MATLAYER_OT_append_workspace,
    MATLAYER_OT_append_basic_brushes,

    # User Interface
    MATLAYER_UL_layer_list,
    UtilitySubMenu,
    MATLAYER_OT_add_material_layer_menu,
    MATLAYER_OT_add_layer_mask_menu,
    MATLAYER_OT_add_material_filter_menu,
    ImageUtilitySubMenu,
    LayerProjectionModeSubMenu,
    MaskProjectionModeSubMenu,
    MaterialChannelValueNodeSubMenu,
    LayerUtilitySubMenu,
    LayerTriplanarProjectionSubMenu,
    MaskChannelSubMenu,
    MATLAYER_panel_properties,
    MATLAYER_PT_Panel
)

# Mark load handlers as persistent so they are not freed when loading a new blend file.
@persistent
def load_handler(dummy):
    bpy.types.Scene.previous_active_material_name = bpy.context.view_layer.objects.active.active_material.name

    # Subscribe to the active object.
    subscribe_to = bpy.types.LayerObjects, "active"
    bpy.types.Scene.matlayer_object_selection_updater = object()
    bpy.msgbus.subscribe_rna(key=subscribe_to, owner=bpy.types.Scene.matlayer_object_selection_updater, args=(), notify=on_active_object_changed)

    # Subscribe to the active objects name.
    active_object = bpy.context.view_layer.objects.active
    bpy.types.Scene.previous_object_name = active_object.name
    bpy.types.Scene.active_object_name_owner = object()
    bpy.msgbus.clear_by_owner(bpy.types.Scene.active_object_name_owner)
    if active_object:
        if active_object.type == 'MESH':
            bpy.msgbus.subscribe_rna(key=active_object.path_resolve("name", False), owner=bpy.types.Scene.active_object_name_owner, notify=on_active_object_name_changed, args=())

            if active_object.active_material:

                # Subscribe to the active material index.
                bpy.types.Scene.active_material_index_owner = object()
                bpy.msgbus.clear_by_owner(bpy.types.Scene.active_material_index_owner)
                bpy.msgbus.subscribe_rna(key=active_object.path_resolve("active_material_index", False), owner=bpy.types.Scene.active_material_index_owner,notify=on_active_material_index_changed, args=())

                # Subscribe to the active material name.
                bpy.types.Scene.previous_active_material_name = active_object.active_material.name
                bpy.types.Scene.active_material_name_owner = object()
                bpy.msgbus.clear_by_owner(bpy.types.Scene.active_material_name_owner)
                bpy.msgbus.subscribe_rna(key=active_object.active_material.path_resolve("name", False), owner=bpy.types.Scene.active_material_index_owner,notify=on_active_material_name_changed, args=())

                refresh_layer_stack()   # Refresh layer stack on blender file load.

# Run startup functions when a new blend file is loaded.
bpy.app.handlers.load_post.append(load_handler)

def register():
    # Register properties, operators and pannels.
    for cls in classes:
        bpy.utils.register_class(cls)

    # User Interface Properties
    bpy.types.Scene.matlayer_panel_properties = PointerProperty(type=MATLAYER_panel_properties)
    bpy.types.Scene.matlayer_material_property_tabs = EnumProperty(items=MATERIAL_LAYER_PROPERTY_TABS)
    bpy.types.Scene.matlayer_merge_material = PointerProperty(type=bpy.types.Material)

    # Material Layer Properties
    bpy.types.Scene.matlayer_layer_stack = PointerProperty(type=MATLAYER_layer_stack)
    bpy.types.Scene.matlayer_layers = CollectionProperty(type=MATLAYER_layers)

    # Layer Mask Properties
    bpy.types.Scene.matlayer_mask_stack = PointerProperty(type=MATLAYER_mask_stack)
    bpy.types.Scene.matlayer_masks = CollectionProperty(type=MATLAYER_masks)

    # Settings
    bpy.types.Scene.matlayer_texture_set_settings = PointerProperty(type=MATLAYER_texture_set_settings)
    bpy.types.Scene.matlayer_baking_settings = PointerProperty(type=MATLAYER_baking_settings)
    bpy.types.Scene.matlayer_export_settings = PointerProperty(type=MATLAYER_exporting_settings)

    # Subscription Update Handling Properties
    bpy.types.Scene.previous_active_material_name = StringProperty(default="")

    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    export_textures = addon_preferences.export_textures
    if len(export_textures) <= 0:
        set_export_template('Unreal Engine 4')

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
