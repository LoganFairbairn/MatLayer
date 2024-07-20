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
from .core.texture_set_settings import MATLAYER_texture_set_settings, MATLAYER_OT_toggle_texture_set_material_channel, MATLAYER_OT_set_raw_texture_folder, MATLAYER_OT_open_raw_texture_folder

# Shaders
from .core import shaders

# Material Layers
from .core import material_layers

# Layer Masks
from .core.layer_masks import MATLAYER_mask_stack, MATLAYER_masks, MATLAYER_UL_mask_list, MATLAYER_OT_move_layer_mask_up, MATLAYER_OT_move_layer_mask_down, MATLAYER_OT_duplicate_layer_mask, MATLAYER_OT_delete_layer_mask, MATLAYER_OT_add_empty_layer_mask, MATLAYER_OT_add_black_layer_mask, MATLAYER_OT_add_white_layer_mask, MATLAYER_OT_add_linear_gradient_mask, MATLAYER_OT_add_decal_mask, MATLAYER_OT_add_ambient_occlusion_mask, MATLAYER_OT_add_curvature_mask, MATLAYER_OT_add_thickness_mask, MATLAYER_OT_add_world_space_normals_mask,  MATLAYER_OT_add_grunge_mask, MATLAYER_OT_add_edge_wear_mask, MATLAYER_OT_add_decal_mask, MATLAYER_OT_set_mask_projection_uv, MATLAYER_OT_set_mask_projection_triplanar, MATLAYER_OT_set_mask_output_channel, MATLAYER_OT_isolate_mask, MATLAYER_OT_toggle_mask_blur

# Material Slots
from .core.material_slots import MATLAYER_OT_add_material_slot, MATLAYER_OT_remove_material_slot, MATLAYER_OT_move_material_slot_up, MATLAYER_OT_move_material_slot_down

# Baking
from .core.mesh_map_baking import MATLAYER_mesh_map_anti_aliasing, MATLAYER_baking_settings, MATLAYER_OT_batch_bake, MATLAYER_OT_set_mesh_map_folder, MATLAYER_OT_open_mesh_map_folder, MATLAYER_OT_preview_mesh_map, MATLAYER_OT_disable_mesh_map_preview, MATLAYER_OT_delete_mesh_map, MATLAYER_OT_create_baking_cage, MATLAYER_OT_delete_baking_cage

# Exporting
from .core.export_textures import MATLAYER_pack_textures, MATLAYER_RGBA_pack_channels, MATLAYER_texture_export_settings, MATLAYER_texture_export_settings, MATLAYER_texture_set_export_settings, MATLAYER_OT_export, MATLAYER_OT_set_export_folder, MATLAYER_OT_open_export_folder, MATLAYER_OT_set_export_template, MATLAYER_OT_save_export_template, MATLAYER_OT_refresh_export_template_list, MATLAYER_OT_delete_export_template, MATLAYER_OT_add_export_texture, MATLAYER_OT_remove_export_texture, MATLAYER_export_template_names, ExportTemplateMenu, read_export_template_names, set_export_template

# Utilities
from .core.image_utilities import MATLAYER_OT_add_texture_node_image, MATLAYER_OT_import_texture_node_image, MATLAYER_OT_edit_texture_node_image_externally, MATLAY_OT_export_uvs, MATLAYER_OT_reload_texture_node_image, MATLAYER_OT_delete_texture_node_image, MATLAY_OT_image_edit_uvs, auto_save_images
from .core.layer_utilities import MATLAYER_OT_import_texture_set, MATLAYER_OT_merge_materials
from .core.utility_operations import MATLAYER_OT_set_decal_layer_snapping, MATLAYER_OT_append_workspace, MATLAYER_OT_append_basic_brushes, MATLAYER_OT_append_hdri_world, MATLAYER_OT_remove_unused_raw_textures

# User Interface
from .ui.ui_section_tabs import UtilitySubMenu
from .ui.ui_layer_section import MATLAYER_OT_add_material_layer_menu, MATLAYER_OT_add_layer_mask_menu, MATLAYER_OT_add_material_filter_menu, MaterialChannelSubMenu, ImageUtilitySubMenu, LayerProjectionModeSubMenu, MaskProjectionModeSubMenu, MaterialChannelValueNodeSubMenu, MaskChannelSubMenu, MaterialChannelOutputSubMenu, MATERIAL_LAYER_PROPERTY_TABS
from .ui.ui_shaders_section import ShaderSubMenu, MATLAYER_UL_shader_channel_list, MATLAYER_UL_global_shader_property_list
from .ui.ui_main import *
from .ui.ui_layer_stack import MATLAYER_UL_layer_list, LayerBlendingModeSubMenu

# Subscription Update Handler
from .core.subscription_update_handler import on_active_material_changed, on_active_object_changed, on_active_object_name_changed, on_active_material_index_changed, on_active_material_name_changed

bl_info = {
    "name": "MatLayer",
    "author": "Logan Fairbairn (Ryver)",
    "version": (3, 0, 0),
    "blender": (4, 0, 2),
    "location": "View3D > Sidebar > MatLayer",
    "description": "Provides a layer based wrapper user interface and utility functions for editing complex materials in Blender",
    "warning": "",
    "doc_url": "",
    "category": "Material Editing",
}

# List of classes to be registered.
classes = (
    # Preferences
    AddonPreferences,

    # Mesh Map Baking
    MATLAYER_mesh_map_anti_aliasing,
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
    MATLAYER_pack_textures,
    MATLAYER_RGBA_pack_channels,
    MATLAYER_texture_export_settings,
    MATLAYER_texture_set_export_settings,
    MATLAYER_export_template_names,
    MATLAYER_OT_export,
    MATLAYER_OT_set_export_template,
    MATLAYER_OT_save_export_template,
    MATLAYER_OT_refresh_export_template_list,
    MATLAYER_OT_delete_export_template,
    MATLAYER_OT_add_export_texture,
    MATLAYER_OT_remove_export_texture,
    MATLAYER_OT_set_export_folder,
    MATLAYER_OT_open_export_folder,
    ExportTemplateMenu,

    # Shaders
    shaders.MATLAYER_shader_name,
    shaders.MATLAYER_shader_material_channel,
    shaders.MATLAYER_shader_global_property,
    shaders.MATLAYER_shader_info,
    shaders.MATLAYER_OT_set_shader,
    shaders.MATLAYER_OT_new_shader,
    shaders.MATLAYER_OT_save_shader,
    shaders.MATLAYER_OT_delete_shader,
    shaders.MATLAYER_OT_add_shader_channel,
    shaders.MATLAYER_OT_delete_shader_channel,
    shaders.MATLAYER_OT_add_global_shader_property,
    shaders.MATLAYER_OT_delete_global_shader_property,
    shaders.MATLAYER_OT_create_shader_from_nodetree,

    # Material Layers
    material_layers.MATLAYER_layer_stack,
    material_layers.MATLAYER_layers,
    material_layers.MATLAYER_OT_add_material_layer,
    material_layers.MATLAYER_OT_add_decal_material_layer,
    material_layers.MATLAYER_OT_add_image_layer,
    material_layers.MATLAYER_OT_delete_layer,
    material_layers.MATLAYER_OT_duplicate_layer, 
    material_layers.MATLAYER_OT_move_material_layer_up,
    material_layers.MATLAYER_OT_move_material_layer_down,
    material_layers.MATLAYER_OT_toggle_material_channel_preview,
    material_layers.MATLAYER_OT_toggle_hide_layer,
    material_layers.MATLAYER_OT_set_layer_projection_uv,
    material_layers.MATLAYER_OT_set_layer_projection_triplanar,
    material_layers.MATLAYER_OT_change_material_channel_value_node,
    material_layers.MATLAYER_OT_toggle_triplanar_flip_correction,
    material_layers.MATLAYER_OT_isolate_material_channel,
    material_layers.MATLAYER_OT_toggle_image_alpha_blending,
    material_layers.MATLAYER_OT_toggle_material_channel_filter,
    material_layers.MATLAYER_OT_set_material_channel,
    material_layers.MATLAYER_OT_set_matchannel_crgba_output,
    material_layers.MATLAYER_OT_set_layer_blending_mode,
    material_layers.MATLAYER_OT_merge_layers,

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
    ShaderSubMenu,
    MATLAYER_UL_shader_channel_list,
    MATLAYER_UL_global_shader_property_list,
    MATLAYER_UL_layer_list,
    LayerBlendingModeSubMenu,
    UtilitySubMenu,
    MATLAYER_OT_add_material_layer_menu,
    MATLAYER_OT_add_layer_mask_menu,
    MATLAYER_OT_add_material_filter_menu,
    MaterialChannelSubMenu,
    ImageUtilitySubMenu,
    LayerProjectionModeSubMenu,
    MaskProjectionModeSubMenu,
    MaterialChannelValueNodeSubMenu,
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

        # Update properties when there is a shader nodetree change...
        if update.id.name == "Shader Nodetree":

            # When a texture property is updated, sync all texture samples for the layer if it's using triplanar projection.
            material_layers.sync_triplanar_settings()

            # Group nodes for material channels can become unlinked when a user applies a custom group node.
            # Search for an relink any unlinked material channels that occur as a result of this change.
            shader_info = bpy.context.scene.matlayer_shader_info
            for channel in shader_info.material_channels:
                selected_layer_index = bpy.context.scene.matlayer_layer_stack.selected_layer_index
                value_node = material_layers.get_material_layer_node('VALUE', selected_layer_index, channel.name)
                if value_node:
                    if len(value_node.outputs) > 0:
                        if len(value_node.outputs[0].links) == 0:
                            output_channel = material_layers.get_material_channel_crgba_output(channel.name)
                            material_layers.relink_material_channel(
                                relink_material_channel_name=channel.name, 
                                original_output_channel=output_channel, 
                                unlink_projection=True
                            )

            # TODO: Look into optimizing this further, this causes lots of lag.
            # Re-link layer group nodes together (so changes in layer opacity will trigger relinking).
            #material_layers.link_layer_group_nodes(self=None)

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

        material_layers.refresh_layer_stack()

    # TODO: Temporary fix for updating the shader list.
    shaders.update_shader_list()

# Run startup functions when a new blend file is loaded.
bpy.app.handlers.load_post.append(load_handler)

def register():
    # Register properties, operators and pannels.
    for cls in classes:
        bpy.utils.register_class(cls)

    # Scene Properties
    bpy.types.Scene.matlayer_panel_properties = PointerProperty(type=MATLAYER_panel_properties)
    bpy.types.Scene.matlayer_material_property_tabs = EnumProperty(items=MATERIAL_LAYER_PROPERTY_TABS)
    bpy.types.Scene.matlayer_merge_material = PointerProperty(type=bpy.types.Material)

    # Shader Properties
    bpy.types.Scene.matlayer_shader_list = CollectionProperty(type=shaders.MATLAYER_shader_name)
    bpy.types.Scene.matlayer_shader_info = PointerProperty(type=shaders.MATLAYER_shader_info)
    bpy.types.Scene.matlayer_selected_shader_index = IntProperty()
    bpy.types.Scene.matlayer_selected_global_shader_property_index = IntProperty()

    # Layer & Mask Properties
    bpy.types.Scene.matlayer_layer_stack = PointerProperty(type=material_layers.MATLAYER_layer_stack)
    bpy.types.Scene.matlayer_layers = CollectionProperty(type=material_layers.MATLAYER_layers)
    bpy.types.Scene.matlayer_mask_stack = PointerProperty(type=MATLAYER_mask_stack)
    bpy.types.Scene.matlayer_masks = CollectionProperty(type=MATLAYER_masks)

    # Other Properties
    bpy.types.Scene.matlayer_texture_set_settings = PointerProperty(type=MATLAYER_texture_set_settings)
    bpy.types.Scene.matlayer_baking_settings = PointerProperty(type=MATLAYER_baking_settings)
    bpy.types.Scene.matlayer_export_templates = CollectionProperty(type=MATLAYER_export_template_names)
    bpy.types.Scene.pause_auto_updates = BoolProperty(default=False)
    bpy.types.Scene.previous_active_material_name = StringProperty(default="")
    bpy.types.Scene.previous_object_name = StringProperty(default="")

    # Exporting Properties
    bpy.types.Scene.matlayer_texture_export_settings = PointerProperty(type=MATLAYER_texture_set_export_settings)
    
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
