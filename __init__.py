# Copyright (c) 2021-2024 Logan Fairbairn
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
from bpy.props import PointerProperty, CollectionProperty, EnumProperty, StringProperty, BoolProperty, IntProperty
from bpy.app.handlers import persistent

# Preferences
from .preferences import AddonPreferences

# Texture Set Settings
from .core.texture_set_settings import RYMAT_texture_set_settings, RYMAT_OT_set_raw_texture_folder, RYMAT_OT_open_raw_texture_folder

# Shaders
from .core.shaders import RYMAT_shader_name, RYMAT_shader_material_channel, RYMAT_shader_unlayered_property, RYMAT_shader_info, RYMAT_OT_set_shader, RYMAT_OT_new_shader, RYMAT_OT_save_shader, RYMAT_OT_delete_shader, RYMAT_OT_add_shader_channel, RYMAT_OT_delete_shader_channel, RYMAT_OT_create_shader_from_nodetree, RYMAT_OT_apply_default_shader, update_shader_list, set_shader

# Material Layers
from .core.material_layers import RYMAT_layer_stack, RYMAT_layers, RYMAT_OT_add_material_layer,RYMAT_OT_add_decal_material_layer, RYMAT_OT_add_image_layer, RYMAT_OT_delete_layer, RYMAT_OT_duplicate_layer, RYMAT_OT_move_material_layer_up, RYMAT_OT_move_material_layer_down,RYMAT_OT_toggle_material_channel_preview, RYMAT_OT_toggle_hide_layer, RYMAT_OT_set_layer_projection,RYMAT_OT_change_material_channel_value_node, RYMAT_OT_isolate_material_channel,RYMAT_OT_show_compiled_material, RYMAT_OT_toggle_image_alpha_blending, RYMAT_OT_set_material_channel, RYMAT_OT_set_matchannel_crgba_output, RYMAT_OT_set_layer_blending_mode, RYMAT_OT_merge_with_layer_below, RYMAT_OT_add_material_channel_nodes, RYMAT_OT_delete_material_channel_nodes, refresh_layer_stack, shader_node_tree_update

# Layer Masks
from .core.layer_masks import RYMAT_mask_stack, RYMAT_masks, RYMAT_UL_mask_list, RYMAT_OT_move_layer_mask_up, RYMAT_OT_move_layer_mask_down, RYMAT_OT_duplicate_layer_mask, RYMAT_OT_delete_layer_mask, RYMAT_OT_add_empty_layer_mask, RYMAT_OT_add_black_layer_mask, RYMAT_OT_add_white_layer_mask, RYMAT_OT_add_linear_gradient_mask, RYMAT_OT_add_decal_mask, RYMAT_OT_add_ambient_occlusion_mask, RYMAT_OT_add_curvature_mask, RYMAT_OT_add_thickness_mask, RYMAT_OT_add_world_space_normals_mask,  RYMAT_OT_add_grunge_mask, RYMAT_OT_add_edge_wear_mask, RYMAT_OT_add_decal_mask, RYMAT_OT_set_mask_projection_uv, RYMAT_OT_set_mask_projection_triplanar, RYMAT_OT_set_mask_crgba_channel, RYMAT_OT_isolate_mask

# Material Filters
from .core.material_filters import RYMAT_OT_add_material_filter, RYMAT_OT_delete_material_filter

# Material Slots
from .core.material_slots import RYMAT_OT_add_material_slot, RYMAT_OT_remove_material_slot, RYMAT_OT_move_material_slot_up, RYMAT_OT_move_material_slot_down

# Baking Mesh Maps
from .core.mesh_map_baking import RYMAT_mesh_map_anti_aliasing, RYMAT_baking_settings, RYMAT_OT_batch_bake, RYMAT_OT_set_mesh_map_folder, RYMAT_OT_open_mesh_map_folder, RYMAT_OT_preview_mesh_map, RYMAT_OT_disable_mesh_map_preview, RYMAT_OT_delete_mesh_map, RYMAT_OT_create_baking_cage, RYMAT_OT_delete_baking_cage

# Exporting
from .core.export_textures import RYMAT_pack_textures, RYMAT_RGBA_pack_channels, RYMAT_texture_export_settings, RYMAT_texture_export_settings, RYMAT_texture_set_export_settings, RYMAT_OT_export, RYMAT_OT_set_export_folder, RYMAT_OT_open_export_folder, RYMAT_OT_set_export_template, RYMAT_OT_save_export_template, RYMAT_OT_refresh_export_template_list, RYMAT_OT_delete_export_template, RYMAT_OT_add_export_texture, RYMAT_OT_remove_export_texture, RYMAT_export_template_names, ExportTemplateMenu

# Utilities
from .core.image_utilities import RYMAT_OT_save_all_textures, RYMAT_OT_add_texture_node_image, RYMAT_OT_import_texture_node_image, RYMAT_OT_edit_texture_node_image_externally, RYMAT_OT_rename_texture_node_image, RYMAT_OT_export_uvs, RYMAT_OT_reload_texture_node_image, RYMAT_OT_duplicate_texture_node_image, RYMAT_OT_delete_texture_node_image, RYMAT_OT_image_edit_uvs, auto_save_images
from .core.layer_utilities import RYMAT_OT_import_texture_set, RYMAT_OT_merge_materials
from .core.utility_operations import RYMAT_OT_append_default_workspace, RYMAT_OT_set_decal_layer_snapping, RYMAT_OT_append_hdri_world, RYMAT_OT_remove_unused_raw_textures, RYMAT_OT_append_material_ball, RYMAT_OT_add_black_outlines, RYMAT_OT_remove_outlines

# User Interface
from .ui.ui_edit_layers import RYMAT_OT_add_material_layer_menu, RYMAT_OT_add_layer_mask_menu, AddMaterialChannelSubMenu, MaterialChannelSubMenu, ImageUtilitySubMenu, LayerProjectionModeSubMenu, MaskProjectionModeSubMenu, MaterialChannelValueNodeSubMenu, MaskChannelSubMenu, MaterialChannelOutputSubMenu, MaterialSelectorPanel, LayerStackPanel, MaterialPropertiesPanel, ColorPalettePanel, MATERIAL_LAYER_PROPERTY_TABS, update_material_properties_tab
from .ui.ui_settings import ShaderSubMenu, RYMAT_UL_shader_channel_list, RYMAT_UL_global_shader_property_list
from .ui.ui_layer_stack import RYMAT_UL_layer_list, LayerBlendingModeSubMenu
from .ui.ui_main import FileSubMenu, EditSubMenu, HelpSubMenu, RYMAT_panel_properties, RYMAT_PT_Panel

# Subscription Update Handler
from .core.subscription_update_handler import on_active_material_changed, on_active_object_changed, on_active_object_name_changed, on_active_material_index_changed, on_active_material_name_changed

bl_info = {
    "name": "RyMat",
    "author": "Logan Fairbairn (Ryver)",
    "version": (1, 0, 0),
    "blender": (4, 3, 2),
    "location": "View3D > Sidebar > RyMat",
    "description": "Provides a layer based user interface and utility functions for creating complex materials in Blender",
    "warning": "",
    "doc_url": "https://loganfairbairn.github.io/rymat_documentation.html",
    "category": "Material Editing",
}

# List of classes to be registered.
classes = (
    # Preferences
    AddonPreferences,

    # Mesh Map Baking
    RYMAT_mesh_map_anti_aliasing,
    RYMAT_baking_settings,
    RYMAT_OT_batch_bake,
    RYMAT_OT_set_mesh_map_folder,
    RYMAT_OT_open_mesh_map_folder,
    RYMAT_OT_preview_mesh_map,
    RYMAT_OT_disable_mesh_map_preview,
    RYMAT_OT_delete_mesh_map,
    RYMAT_OT_create_baking_cage,
    RYMAT_OT_delete_baking_cage,

    # Exporting
    RYMAT_pack_textures,
    RYMAT_RGBA_pack_channels,
    RYMAT_texture_export_settings,
    RYMAT_texture_set_export_settings,
    RYMAT_export_template_names,
    RYMAT_OT_export,
    RYMAT_OT_set_export_template,
    RYMAT_OT_save_export_template,
    RYMAT_OT_refresh_export_template_list,
    RYMAT_OT_delete_export_template,
    RYMAT_OT_add_export_texture,
    RYMAT_OT_remove_export_texture,
    RYMAT_OT_set_export_folder,
    RYMAT_OT_open_export_folder,
    ExportTemplateMenu,

    # Shaders
    RYMAT_shader_name,
    RYMAT_shader_material_channel,
    RYMAT_shader_unlayered_property,
    RYMAT_shader_info,
    RYMAT_OT_set_shader,
    RYMAT_OT_new_shader,
    RYMAT_OT_save_shader,
    RYMAT_OT_delete_shader,
    RYMAT_OT_add_shader_channel,
    RYMAT_OT_delete_shader_channel,
    RYMAT_OT_create_shader_from_nodetree,
    RYMAT_OT_apply_default_shader,

    # Material Layers
    RYMAT_layer_stack,
    RYMAT_layers,
    RYMAT_OT_add_material_layer,
    RYMAT_OT_add_decal_material_layer,
    RYMAT_OT_add_image_layer,
    RYMAT_OT_delete_layer,
    RYMAT_OT_duplicate_layer, 
    RYMAT_OT_move_material_layer_up,
    RYMAT_OT_move_material_layer_down,
    RYMAT_OT_toggle_material_channel_preview,
    RYMAT_OT_toggle_hide_layer,
    RYMAT_OT_set_layer_projection,
    RYMAT_OT_change_material_channel_value_node,
    RYMAT_OT_isolate_material_channel,
    RYMAT_OT_show_compiled_material,
    RYMAT_OT_toggle_image_alpha_blending,
    RYMAT_OT_set_material_channel,
    RYMAT_OT_set_matchannel_crgba_output,
    RYMAT_OT_set_layer_blending_mode,
    RYMAT_OT_merge_with_layer_below,
    RYMAT_OT_add_material_channel_nodes,
    RYMAT_OT_delete_material_channel_nodes,

    # Layer Masks
    RYMAT_mask_stack, 
    RYMAT_masks,
    RYMAT_UL_mask_list,
    RYMAT_OT_move_layer_mask_up, 
    RYMAT_OT_move_layer_mask_down,
    RYMAT_OT_duplicate_layer_mask,
    RYMAT_OT_delete_layer_mask,
    RYMAT_OT_add_empty_layer_mask,
    RYMAT_OT_add_black_layer_mask,
    RYMAT_OT_add_white_layer_mask,
    RYMAT_OT_add_linear_gradient_mask,
    RYMAT_OT_add_grunge_mask,
    RYMAT_OT_add_edge_wear_mask,
    RYMAT_OT_add_decal_mask,
    RYMAT_OT_add_ambient_occlusion_mask, 
    RYMAT_OT_add_curvature_mask, 
    RYMAT_OT_add_thickness_mask, 
    RYMAT_OT_add_world_space_normals_mask,
    RYMAT_OT_set_mask_projection_uv,
    RYMAT_OT_set_mask_projection_triplanar,
    RYMAT_OT_set_mask_crgba_channel,
    RYMAT_OT_isolate_mask,

    # Material Filters
    RYMAT_OT_add_material_filter,
    RYMAT_OT_delete_material_filter,

    # Material Slots
    RYMAT_OT_add_material_slot, 
    RYMAT_OT_remove_material_slot,
    RYMAT_OT_move_material_slot_up, 
    RYMAT_OT_move_material_slot_down,

    # Image Utilities
    RYMAT_OT_save_all_textures,
    RYMAT_OT_add_texture_node_image, 
    RYMAT_OT_import_texture_node_image, 
    RYMAT_OT_edit_texture_node_image_externally,
    RYMAT_OT_rename_texture_node_image,
    RYMAT_OT_export_uvs,
    RYMAT_OT_reload_texture_node_image,
    RYMAT_OT_duplicate_texture_node_image,
    RYMAT_OT_delete_texture_node_image,
    RYMAT_OT_image_edit_uvs,

    # Layer Utilities
    RYMAT_OT_import_texture_set,
    RYMAT_OT_merge_materials,

    # Texture Set Settings
    RYMAT_texture_set_settings,
    RYMAT_OT_set_raw_texture_folder,
    RYMAT_OT_open_raw_texture_folder,

    # Utility Operators
    RYMAT_OT_append_default_workspace,
    RYMAT_OT_set_decal_layer_snapping,
    RYMAT_OT_append_hdri_world,
    RYMAT_OT_remove_unused_raw_textures,
    RYMAT_OT_append_material_ball,
    RYMAT_OT_add_black_outlines,
    RYMAT_OT_remove_outlines,

    # User Interface
    FileSubMenu,
    EditSubMenu,
    HelpSubMenu,
    ShaderSubMenu,
    RYMAT_UL_shader_channel_list,
    RYMAT_UL_global_shader_property_list,
    RYMAT_UL_layer_list,
    LayerBlendingModeSubMenu,
    RYMAT_OT_add_material_layer_menu,
    RYMAT_OT_add_layer_mask_menu,
    AddMaterialChannelSubMenu,
    MaterialChannelSubMenu,
    ImageUtilitySubMenu,
    LayerProjectionModeSubMenu,
    MaskProjectionModeSubMenu,
    MaterialChannelValueNodeSubMenu,
    MaskChannelSubMenu,
    MaterialChannelOutputSubMenu,
    RYMAT_panel_properties,
    RYMAT_PT_Panel,
    MaterialSelectorPanel,
    ColorPalettePanel,
    LayerStackPanel,
    MaterialPropertiesPanel
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

        # Run updates when a shader nodetree change is detected.
        if update.id.name == "Shader Nodetree":
            shader_node_tree_update()

# Mark load handlers as persistent so they are not called again when loading a new blend file.
@persistent
def load_handler(dummy):

    # Add an app handler to run updates for add-on properties when properties on the active object are changed.
    bpy.app.handlers.depsgraph_update_post.clear()
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_change_handler)

    # Create objects to manage subscription updating.
    bpy.types.Scene.rymat_object_selection_updater = object()
    bpy.types.Scene.active_object_name_sub_owner = object()
    bpy.types.Scene.active_material_index_sub_owner = object()
    bpy.types.Scene.active_material_name_sub_owner = object()

    # Subscribe to the active object to get notifications when it's changed.
    subscribe_to = bpy.types.LayerObjects, "active"
    bpy.msgbus.subscribe_rna(key=subscribe_to, owner=bpy.types.Scene.rymat_object_selection_updater, args=(), notify=on_active_object_changed)

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
    
    # Apply a default shader setup when a blend file is loaded if there is no shader node defined.
    update_shader_list()
    shader_info = bpy.context.scene.rymat_shader_info
    if shader_info.shader_node_group == None:
        set_shader('MetallicRoughnessPBR')

def register():
    # Register properties, operators and pannels.
    for cls in classes:
        bpy.utils.register_class(cls)

    # Scene Properties
    bpy.types.Scene.rymat_panel_properties = PointerProperty(type=RYMAT_panel_properties)
    bpy.types.Scene.rymat_material_property_tabs = EnumProperty(items=MATERIAL_LAYER_PROPERTY_TABS, update=update_material_properties_tab)
    bpy.types.Scene.rymat_merge_material = PointerProperty(type=bpy.types.Material)

    # Shader Properties
    bpy.types.Scene.rymat_shader_list = CollectionProperty(type=RYMAT_shader_name)
    bpy.types.Scene.rymat_shader_info = PointerProperty(type=RYMAT_shader_info)
    bpy.types.Scene.rymat_shader_channel_index = IntProperty()
    bpy.types.Scene.rymat_selected_global_shader_property_index = IntProperty()

    # Layer & Mask Properties
    bpy.types.Scene.rymat_layer_stack = PointerProperty(type=RYMAT_layer_stack)
    bpy.types.Scene.rymat_layers = CollectionProperty(type=RYMAT_layers)
    bpy.types.Scene.rymat_mask_stack = PointerProperty(type=RYMAT_mask_stack)
    bpy.types.Scene.rymat_masks = CollectionProperty(type=RYMAT_masks)

    # Other Properties
    bpy.types.Scene.rymat_texture_set_settings = PointerProperty(type=RYMAT_texture_set_settings)
    bpy.types.Scene.rymat_baking_settings = PointerProperty(type=RYMAT_baking_settings)
    bpy.types.Scene.rymat_export_templates = CollectionProperty(type=RYMAT_export_template_names)
    bpy.types.Scene.pause_auto_updates = BoolProperty(default=False)
    bpy.types.Scene.previous_active_material_name = StringProperty(default="")
    bpy.types.Scene.previous_object_name = StringProperty(default="")

    # Exporting Properties
    bpy.types.Scene.rymat_texture_export_settings = PointerProperty(type=RYMAT_texture_set_export_settings)
    
    bpy.types.Scene.rymat_raw_textures_folder = StringProperty(
        name="Raw Texture Folder",
        description="Folder where textures used in materials are saved. If a folder isn't defined, or is invalid, exported textures will save to a 'Raw Textures' folder next to the saved blend file",
        default="Default",
    )

    bpy.types.Scene.rymat_mesh_map_folder = StringProperty(
        name="Mesh Map Folder",
        description="Folder where baked mesh maps are externally saved. If a folder isn't defined, or is invalid, the mesh maps will save to a 'Mesh Map' folder next to the saved blend file",
        default="Default",
    )

    bpy.types.Scene.rymat_export_folder = StringProperty(
        name="Export Folder",
        description="Folder where completed textures are exported to. If a folder isn't defined, or is invalid, exported textures will save to a 'Textures' folder next to the saved blend file",
        default="Default",
    )

    # Register auto-saving for all images.
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    bpy.app.timers.register(auto_save_images, first_interval=addon_preferences.image_auto_save_interval)

    # Add a load handler to run functions when a Blender file is loaded.
    bpy.app.handlers.load_post.append(load_handler)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # Empty objects that manage subscription updating.
    bpy.types.Scene.rymat_object_selection_updater = None
    bpy.types.Scene.active_object_name_sub_owner = None
    bpy.types.Scene.active_material_index_sub_owner = None
    bpy.types.Scene.active_material_name_sub_owner = None

    # Unregister image auto saving.
    if bpy.app.timers.is_registered(auto_save_images):
        bpy.app.timers.unregister(auto_save_images)

if __name__ == "__main__":
    register()