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
from bpy.props import PointerProperty, CollectionProperty, EnumProperty, StringProperty, BoolProperty
from bpy.app.handlers import persistent

# Preferences
from .preferences import MATLAYER_pack_textures, MATLAYER_RGBA_pack_channels, MATLAYER_texture_export_settings, MATLAYER_mesh_map_anti_aliasing, AddonPreferences

# Texture Set Settings
from .core.texture_set_settings import MATLAYER_texture_set_settings, MATLAYER_OT_toggle_texture_set_material_channel, MATLAYER_OT_set_raw_texture_folder, MATLAYER_OT_open_raw_texture_folder

# Material Layers
from .core.material_layers import MATLAYER_layer_stack, MATLAYER_layers, MATLAYER_OT_add_material_layer, MATLAYER_OT_add_paint_material_layer, MATLAYER_OT_add_decal_material_layer, MATLAYER_OT_delete_layer, MATLAYER_OT_duplicate_layer, MATLAYER_OT_move_material_layer_up, MATLAYER_OT_move_material_layer_down, MATLAYER_OT_toggle_material_channel_preview, MATLAYER_OT_toggle_layer_blur, MATLAYER_OT_toggle_material_channel_blur, MATLAYER_OT_toggle_hide_layer, MATLAYER_OT_set_layer_projection_uv, MATLAYER_OT_set_layer_projection_triplanar, MATLAYER_OT_change_material_channel_value_node, MATLAYER_OT_toggle_triplanar_flip_correction, MATLAYER_OT_isolate_material_channel, MATLAYER_OT_toggle_image_alpha_blending, MATLAYER_OT_toggle_material_channel_filter, MATLAYER_OT_set_material_channel_output_channel, MATLAYER_OT_set_layer_blending_mode, refresh_layer_stack, sync_triplanar_settings

# Layer Masks
from .core.layer_masks import MATLAYER_mask_stack, MATLAYER_masks, MATLAYER_UL_mask_list, MATLAYER_OT_move_layer_mask_up, MATLAYER_OT_move_layer_mask_down, MATLAYER_OT_duplicate_layer_mask, MATLAYER_OT_delete_layer_mask, MATLAYER_OT_add_empty_layer_mask, MATLAYER_OT_add_black_layer_mask, MATLAYER_OT_add_white_layer_mask, MATLAYER_OT_add_linear_gradient_mask, MATLAYER_OT_add_decal_mask, MATLAYER_OT_add_ambient_occlusion_mask, MATLAYER_OT_add_curvature_mask, MATLAYER_OT_add_thickness_mask, MATLAYER_OT_add_world_space_normals_mask,  MATLAYER_OT_add_grunge_mask, MATLAYER_OT_add_edge_wear_mask, MATLAYER_OT_add_decal_mask, MATLAYER_OT_set_mask_projection_uv, MATLAYER_OT_set_mask_projection_triplanar, MATLAYER_OT_set_mask_output_channel, MATLAYER_OT_isolate_mask, MATLAYER_OT_toggle_mask_blur

# Material Slots
from .core.material_slots import MATLAYER_OT_add_material_slot, MATLAYER_OT_remove_material_slot, MATLAYER_OT_move_material_slot_up, MATLAYER_OT_move_material_slot_down

# Baking
from .core.mesh_map_baking import MATLAYER_baking_settings, MATLAYER_OT_batch_bake, MATLAYER_OT_set_mesh_map_folder, MATLAYER_OT_open_mesh_map_folder, MATLAYER_OT_preview_mesh_map, MATLAYER_OT_disable_mesh_map_preview, MATLAYER_OT_delete_mesh_map, MATLAYER_OT_create_baking_cage, MATLAYER_OT_delete_baking_cage

# Exporting
from .core.export_textures import MATLAYER_OT_export, MATLAYER_OT_set_export_folder, MATLAYER_OT_open_export_folder, MATLAYER_OT_set_export_template, MATLAYER_OT_save_export_template, MATLAYER_OT_refresh_export_template_list, MATLAYER_OT_delete_export_template, MATLAYER_OT_add_export_texture, MATLAYER_OT_remove_export_texture, MATLAYER_export_template_name, ExportTemplateMenu, read_export_template_names, set_export_template

# Utilities
from .core.image_utilities import MATLAYER_OT_add_texture_node_image, MATLAYER_OT_import_texture_node_image, MATLAYER_OT_edit_texture_node_image_externally, MATLAY_OT_export_uvs, MATLAYER_OT_reload_texture_node_image, MATLAYER_OT_delete_texture_node_image, MATLAY_OT_image_edit_uvs, auto_save_images
from .core.layer_utilities import MATLAYER_OT_import_texture_set, MATLAYER_OT_merge_materials
from .core.utility_operations import MATLAYER_OT_set_decal_layer_snapping, MATLAYER_OT_append_workspace, MATLAYER_OT_append_basic_brushes, MATLAYER_OT_append_hdri_world, MATLAYER_OT_remove_unused_raw_textures

# User Interface
from .ui.ui_section_tabs import UtilitySubMenu
from .ui.ui_layer_section import MATLAYER_OT_add_material_layer_menu, MATLAYER_OT_add_layer_mask_menu, MATLAYER_OT_add_material_filter_menu, ImageUtilitySubMenu, LayerProjectionModeSubMenu, MaskProjectionModeSubMenu, MaterialChannelValueNodeSubMenu, LayerUtilitySubMenu, MaskChannelSubMenu, MaterialChannelOutputSubMenu, MATERIAL_LAYER_PROPERTY_TABS
from .ui.ui_main import *
from .ui.ui_layer_stack import MATLAYER_UL_layer_list, LayerBlendingModeSubMenu

# Subscription Update Handler
from .core.subscription_update_handler import on_active_material_changed, on_active_object_changed, on_active_object_name_changed, on_active_material_index_changed, on_active_material_name_changed

bl_info = {
    "name": "MatLayer",
    "author": "Logan Fairbairn (Ryver)",
    "version": (2, 0, 3),
    "blender": (4, 0, 0),
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
    MATLAYER_mesh_map_anti_aliasing,
    AddonPreferences,

    # Mesh Map Baking
    MATLAYER_baking_settings,
    MATLAYER_OT_batch_bake,
    MATLAYER_OT_set_mesh_map_folder,
    MATLAYER_OT_open_mesh_map_folder,
    MATLAYER_OT_preview_mesh_map,
    MATLAYER_OT_disable_mesh_map_preview,
    MATLAYER_OT_delete_mesh_map,
    MATLAYER_OT_create_baking_cage,
    MATLAYER_OT_delete_baking_cage,

    # Exporting
    MATLAYER_OT_export,
    MATLAYER_OT_set_export_template,
    MATLAYER_OT_save_export_template,
    MATLAYER_OT_refresh_export_template_list,
    MATLAYER_OT_delete_export_template,
    MATLAYER_OT_add_export_texture,
    MATLAYER_OT_remove_export_texture,
    MATLAYER_export_template_name,
    MATLAYER_OT_set_export_folder,
    MATLAYER_OT_open_export_folder,
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
    MATLAYER_OT_toggle_image_alpha_blending,
    MATLAYER_OT_toggle_material_channel_filter,
    MATLAYER_OT_set_material_channel_output_channel,
    MATLAYER_OT_set_layer_blending_mode,

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
    MATLAYER_OT_add_linear_gradient_mask,
    MATLAYER_OT_add_grunge_mask,
    MATLAYER_OT_add_edge_wear_mask,
    MATLAYER_OT_add_decal_mask,
    MATLAYER_OT_add_ambient_occlusion_mask, 
    MATLAYER_OT_add_curvature_mask, 
    MATLAYER_OT_add_thickness_mask, 
    MATLAYER_OT_add_world_space_normals_mask,
    MATLAYER_OT_set_mask_projection_uv,
    MATLAYER_OT_set_mask_projection_triplanar,
    MATLAYER_OT_set_mask_output_channel,
    MATLAYER_OT_isolate_mask,
    MATLAYER_OT_toggle_mask_blur,

    # Material Slots
    MATLAYER_OT_add_material_slot, 
    MATLAYER_OT_remove_material_slot,
    MATLAYER_OT_move_material_slot_up, 
    MATLAYER_OT_move_material_slot_down,

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
    MATLAYER_OT_set_raw_texture_folder,
    MATLAYER_OT_open_raw_texture_folder,

    # Utility Operators
    MATLAYER_OT_set_decal_layer_snapping,
    MATLAYER_OT_append_workspace,
    MATLAYER_OT_append_basic_brushes,
    MATLAYER_OT_append_hdri_world,
    MATLAYER_OT_remove_unused_raw_textures,

    # User Interface
    MATLAYER_UL_layer_list,
    LayerBlendingModeSubMenu,
    UtilitySubMenu,
    MATLAYER_OT_add_material_layer_menu,
    MATLAYER_OT_add_layer_mask_menu,
    MATLAYER_OT_add_material_filter_menu,
    ImageUtilitySubMenu,
    LayerProjectionModeSubMenu,
    MaskProjectionModeSubMenu,
    MaterialChannelValueNodeSubMenu,
    LayerUtilitySubMenu,
    MaskChannelSubMenu,
    MaterialChannelOutputSubMenu,
    MATLAYER_panel_properties,
    MATLAYER_PT_Panel
)

@persistent
def depsgraph_change_handler(scene, depsgraph):

    # Variable to ensure the active material callback is only called once per depsgraph update.
    triggered_active_material_callback = False
    for update in depsgraph.updates:

        # Refresh the layer stack when the active object is updated.
        if triggered_active_material_callback == False:
            active_object_attibute = getattr(bpy.context.view_layer.objects, "active", None)
            if active_object_attibute:
                active_object = bpy.context.view_layer.objects.active
                if active_object:
                    if update.id.name == active_object.name:
                        on_active_material_changed(scene)
                        triggered_active_material_callback = True

        # If there is a shader nodetree change, and triplanar projection is being used for the selected layer, sync all texture samples.
        if update.id.name == "Shader Nodetree":
            sync_triplanar_settings()

# Mark load handlers as persistent so they are not freed when loading a new blend file.
@persistent
def load_handler(dummy):

    # Add an app handler to run updates for add-on properties when properties on the active object are changed.
    bpy.app.handlers.depsgraph_update_post.clear()
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_change_handler)

    # Create objects to manage subscription updating.
    bpy.types.Scene.matlayer_object_selection_updater = object()
    bpy.types.Scene.active_object_name_sub_owner = object()
    bpy.types.Scene.active_material_index_sub_owner = object()
    bpy.types.Scene.active_material_name_sub_owner = object()

    # Subscribe to the active object to get notifications when it's changed.
    subscribe_to = bpy.types.LayerObjects, "active"
    bpy.msgbus.subscribe_rna(key=subscribe_to, owner=bpy.types.Scene.matlayer_object_selection_updater, args=(), notify=on_active_object_changed)

    # Update the reference to the active material name, so it can be used to identify when properties need to be updated later.
    active_object = bpy.context.view_layer.objects.active
    if active_object:
        if active_object.active_material != None:
            bpy.types.Scene.previous_active_material_name = active_object.active_material.name
        else:
            bpy.types.Scene.previous_active_material_name = ""

        # Subscribe to the active objects name to get notifications when it's changed.
        bpy.types.Scene.previous_object_name = active_object.name
        bpy.msgbus.clear_by_owner(bpy.types.Scene.active_object_name_sub_owner)
        bpy.msgbus.subscribe_rna(key=active_object.path_resolve("name", False), owner=bpy.types.Scene.active_object_name_sub_owner, notify=on_active_object_name_changed, args=())

        # If the active object has material slots, subscribe to the material index to get notifications when it's changed.
        if len(active_object.material_slots) > 0:
            bpy.msgbus.clear_by_owner(bpy.types.Scene.active_material_index_sub_owner)
            bpy.msgbus.subscribe_rna(key=active_object.path_resolve("active_material_index", False), owner=bpy.types.Scene.active_material_index_sub_owner, notify=on_active_material_index_changed, args=())

            # If there is an active material, subscribe to it's name to get notifications when it's changed.
            if active_object.active_material:
                bpy.types.Scene.previous_active_material_name = active_object.active_material.name
                bpy.msgbus.clear_by_owner(bpy.types.Scene.active_material_name_sub_owner)
                bpy.msgbus.subscribe_rna(key=active_object.active_material.path_resolve("name", False), owner=bpy.types.Scene.active_material_name_sub_owner, notify=on_active_material_name_changed, args=())

        refresh_layer_stack()

    # Read existing export templates into Blender memory, and apply the user set export template if one exists.
    read_export_template_names()
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    set_export_template(addon_preferences.export_template_name)

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
    bpy.types.Scene.matlayer_export_templates = CollectionProperty(type=MATLAYER_export_template_name)

    # Subscription Update Handling Properties
    bpy.types.Scene.pause_auto_updates = BoolProperty(default=False)
    bpy.types.Scene.previous_active_material_name = StringProperty(default="")
    bpy.types.Scene.previous_object_name = StringProperty(default="")

    # Output Folder Properties
    bpy.types.Scene.matlayer_raw_textures_folder = StringProperty(
        name="Raw Texture Folder",
        description="Folder where textures used in materials are saved. If a folder isn't defined, or is invalid, exported textures will save to a 'Raw Textures' folder next to the saved blend file",
        default="Default",
    )

    bpy.types.Scene.matlayer_mesh_map_folder = StringProperty(
        name="Mesh Map Folder",
        description="Folder where baked mesh maps are externally saved. If a folder isn't defined, or is invalid, the mesh maps will save to a 'Mesh Map' folder next to the saved blend file",
        default="Default",
    )

    bpy.types.Scene.matlayer_export_folder = StringProperty(
        name="Export Folder",
        description="Folder where completed textures are exported to. If a folder isn't defined, or is invalid, exported textures will save to a 'Textures' folder next to the saved blend file",
        default="Default",
    )

    # Apply a default export template.
    set_export_template("PBR Metallic Roughness")

    # Register auto-saving for all images.
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    bpy.app.timers.register(auto_save_images, first_interval=addon_preferences.image_auto_save_interval)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # Empty objects that manage subscription updating.
    bpy.types.Scene.matlayer_object_selection_updater = None
    bpy.types.Scene.active_object_name_sub_owner = None
    bpy.types.Scene.active_material_index_sub_owner = None
    bpy.types.Scene.active_material_name_sub_owner = None

    # Unregister image auto saving.
    if bpy.app.timers.is_registered(auto_save_images):
        bpy.app.timers.unregister(auto_save_images)

if __name__ == "__main__":
    register()
