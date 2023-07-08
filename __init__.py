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
from bpy.props import PointerProperty, CollectionProperty
from bpy.app.handlers import persistent

# Import add-on preference settings.
from .preferences import MATLAYER_pack_textures, MATLAYER_RGBA_pack_channels, MATLAYER_texture_export_settings, AddonPreferences

# Import texture set modules.
from .core.texture_set_settings import MATLAYER_texture_set_settings, GlobalMaterialChannelToggles

# Import layer related modules.
from .core.material_layers import *

# Import material channel modules.
from .core.material_channels import MATLAYER_OT_toggle_material_channel_preview, update_material_channel_node_names

# Import layer masking modules.
from .core.layer_masks import MaskProjectionSettings, MATLAYER_mask_stack, MATLAYER_masks, MATLAYER_UL_mask_stack, MATLAYER_OT_add_mask_menu, MATLAYER_OT_add_black_layer_mask, MATLAYER_OT_add_white_layer_mask, MATLAYER_OT_add_empty_layer_mask, MATLAYER_OT_add_group_node_layer_mask, MATLAYER_OT_add_noise_layer_mask, MATLAYER_OT_add_voronoi_layer_mask, MATLAYER_OT_add_musgrave_layer_mask, MATLAYER_OT_open_layer_mask_menu, MATLAYER_OT_delete_layer_mask,MATLAYER_OT_move_layer_mask_up, MATLAYER_OT_move_layer_mask_down, MATLAYER_OT_add_mask_image, MATLAYER_OT_delete_mask_image, MATLAYER_OT_import_mask_image, MATLAYER_mask_filter_stack, MATLAYER_mask_filters, MATLAYER_UL_mask_filter_stack, MATLAYER_OT_add_mask_filter_invert, MATLAYER_OT_add_mask_filter_val_to_rgb, MATLAYER_OT_add_layer_mask_filter_menu, MATLAYER_OT_delete_mask_filter, MATLAYER_OT_move_layer_mask_filter

# Import layer operations.
from .core.layer_operations import *

# Import material filter modules.
from .core.material_filters import FiltersMaterialChannelToggles, MATLAYER_material_filter_stack, MATLAYER_UL_layer_filter_stack, MATLAYER_material_filters, MATLAYER_OT_add_layer_filter_menu, MATLAYER_OT_add_layer_filter_rgb_curves, MATLAYER_OT_add_layer_filter_hsv, MATLAYER_OT_add_layer_filter_invert, MATLAYER_OT_add_layer_filter_val_to_rgb, MATLAYER_OT_add_layer_filter_bright_contrast, MATLAYER_OT_add_material_filter_normal_intensity, MATLAYER_OT_delete_layer_filter, MATLAYER_OT_move_layer_filter_up, MATLAYER_OT_move_layer_filter_down

# Import baking modules.
from .core.baking import MATLAYER_baking_settings, MATLAYER_OT_bake, MATLAYER_OT_open_bake_folder, MATLAYER_OT_delete_ao_map, MATLAYER_OT_delete_curvature_map, MATLAYER_OT_delete_thickness_map, MATLAYER_OT_delete_normal_map, MATLAYER_OT_delete_bevel_normal_map, update_meshmap_names

# Import exporting modules.
from .core.exporting import MATLAYER_exporting_settings, MATLAYER_OT_export, MATLAYER_OT_open_export_folder, MATLAYER_OT_set_export_template, MATLAYER_OT_save_export_template, MATLAYER_OT_add_export_texture, MATLAYER_OT_remove_export_texture, ExportTemplateMenu, set_export_template

# Import tool / utility modules.
from .utilities.image_file_handling import MATLAYER_OT_add_layer_image, MATLAYER_OT_delete_layer_image, MATLAYER_OT_import_texture, MATLAYER_OT_import_texture_set

# Import settings.
from .utilities.utility_operations import MATLAYER_OT_set_decal_layer_snapping, MATLAYER_OT_append_workspace, MATLAYER_OT_append_basic_brushes, MATLAYER_OT_delete_unused_external_images

# Import logging.
from .utilities.logging import MatlayerSettings

# Import user interface modules.
from .ui.ui_main import *
from .ui.ui_layer_stack import *

bl_info = {
    "name": "MatLayer",
    "author": "Logan Fairbairn (Ryver)",
    "version": (1, 0, 6),
    "blender": (3, 5, 0),
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
    MATLAYER_OT_bake,
    MATLAYER_OT_open_bake_folder,
    MATLAYER_OT_delete_ao_map,
    MATLAYER_OT_delete_curvature_map,
    MATLAYER_OT_delete_thickness_map,
    MATLAYER_OT_delete_normal_map,
    MATLAYER_OT_delete_bevel_normal_map,

    # Exporting
    MATLAYER_exporting_settings,
    MATLAYER_OT_export,
    MATLAYER_OT_open_export_folder,
    MATLAYER_OT_set_export_template,
    MATLAYER_OT_save_export_template,
    MATLAYER_OT_add_export_texture,
    MATLAYER_OT_remove_export_texture,
    ExportTemplateMenu,

    # Material Channels
    MATLAYER_OT_toggle_material_channel_preview,

    # Layers
    MaterialChannelToggles,
    MaterialChannelNodeType,
    ProjectionSettings,
    MaterialChannelTextures,
    MaterialChannelColors,
    MaterialChannelUniformValues,
    MaterialChannelGroupNodes,
    MaterialChannelBlurring,
    MATLAYER_OT_open_material_layer_settings,
    MATLAYER_layer_stack,
    MATLAYER_layers,

    # Masks
    MaskProjectionSettings,
    MATLAYER_mask_stack,
    MATLAYER_masks,
    MATLAYER_UL_mask_stack,
    MATLAYER_OT_add_black_layer_mask, 
    MATLAYER_OT_add_white_layer_mask,
    MATLAYER_OT_add_empty_layer_mask,
    MATLAYER_OT_add_group_node_layer_mask,
    MATLAYER_OT_add_noise_layer_mask,
    MATLAYER_OT_add_voronoi_layer_mask,
    MATLAYER_OT_add_musgrave_layer_mask,
    MATLAYER_OT_open_layer_mask_menu,
    MATLAYER_OT_delete_layer_mask,
    MATLAYER_OT_move_layer_mask_up,
    MATLAYER_OT_move_layer_mask_down,
    MATLAYER_OT_add_mask_image, 
    MATLAYER_OT_delete_mask_image, 
    MATLAYER_OT_import_mask_image,

    # Mask Filters
    MATLAYER_mask_filter_stack,
    MATLAYER_mask_filters,
    MATLAYER_UL_mask_filter_stack,
    MATLAYER_OT_add_mask_filter_invert,
    MATLAYER_OT_add_mask_filter_val_to_rgb,
    MATLAYER_OT_add_layer_mask_filter_menu,
    MATLAYER_OT_delete_mask_filter,
    MATLAYER_OT_move_layer_mask_filter,

    # Filters
    FiltersMaterialChannelToggles,
    MATLAYER_material_filter_stack, 
    MATLAYER_UL_layer_filter_stack,
    MATLAYER_material_filters,
    MATLAYER_OT_add_layer_filter_rgb_curves,
    MATLAYER_OT_add_layer_filter_hsv,
    MATLAYER_OT_add_layer_filter_invert,
    MATLAYER_OT_add_layer_filter_val_to_rgb,
    MATLAYER_OT_add_layer_filter_bright_contrast,
    MATLAYER_OT_add_material_filter_normal_intensity,
    MATLAYER_OT_delete_layer_filter,
    MATLAYER_OT_move_layer_filter_up,
    MATLAYER_OT_move_layer_filter_down,
    MATLAYER_OT_add_mask_menu,
    MATLAYER_OT_add_layer_filter_menu,

    # Layer Operations
    MATLAYER_UL_layer_list,
    MATLAYER_OT_add_decal_layer,
    MATLAYER_OT_add_material_layer,
    MATLAYER_OT_add_paint_layer,
    MATLAYER_OT_add_layer_menu,
    MATLAYER_OT_delete_layer,
    MATLAYER_OT_duplicate_layer,
    MATLAYER_OT_move_material_layer,
    MATLAYER_OT_import_texture,
    MATLAYER_OT_import_texture_set,
    MATLAYER_OT_read_layer_nodes,
    MATLAYER_OT_add_layer_image,
    MATLAYER_OT_delete_layer_image,
    MATLAYER_OT_edit_uvs_externally,
    MATLAYER_OT_edit_image_externally,
    MATLAYER_OT_reload_image,

    # Texture Set Settings
    GlobalMaterialChannelToggles,
    MATLAYER_texture_set_settings,

    # Utility Operators
    MATLAYER_OT_set_decal_layer_snapping,
    MATLAYER_OT_append_workspace,
    MATLAYER_OT_append_basic_brushes,
    MATLAYER_OT_delete_unused_external_images,

    # Logging
    MatlayerSettings,

    # Main Panel
    MATLAYER_panel_properties,
    MATLAYER_PT_Panel
)

def on_active_material_index_changed():
    '''Reads material nodes into the user interface when the active material index is changed.'''
    bpy.context.scene.matlayer_layer_stack.layer_index = 0
    bpy.ops.matlayer.read_layer_nodes(auto_called=True)
    bpy.types.Scene.previous_active_material_name = bpy.context.view_layer.objects.active.active_material.name

def on_active_material_name_changed():
    '''Updates material channel nodes when the active material name is changed.'''
    update_material_channel_node_names(bpy.types.Scene.previous_active_material_name)
    bpy.types.Scene.previous_active_material_name = bpy.context.view_layer.objects.active.active_material.name

def on_active_object_name_changed():
    '''Updates mesh maps when the object name is changed.'''
    update_meshmap_names(bpy.types.Scene.previous_object_name)
    bpy.types.Scene.previous_object_name = bpy.context.view_layer.objects.active.name

def on_active_object_changed():
    '''Triggers a layer stack refresh when the selected object changes.'''
    bpy.ops.matlayer.read_layer_nodes(auto_called=True)
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


# Mark load handlers as persistent so they are not freed when loading a new blend file.
@persistent
def load_handler(dummy):

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

                # Read active material settings when the blender file loads.
                bpy.ops.matlayer.read_layer_nodes(auto_called=True)

# Run startup functions when a new blend file is loaded.
bpy.app.handlers.load_post.append(load_handler)

def register():
    # Register properties, operators and pannels.
    for cls in classes:
        bpy.utils.register_class(cls)
        
    # Settings
    bpy.types.Scene.matlayer_settings = PointerProperty(type=MatlayerSettings)

    # Panel Properties
    bpy.types.Scene.matlayer_panel_properties = PointerProperty(type=MATLAYER_panel_properties)

    # Layer Properties
    bpy.types.Scene.matlayer_layer_stack = PointerProperty(type=MATLAYER_layer_stack)
    bpy.types.Scene.matlayer_layers = CollectionProperty(type=MATLAYER_layers)

    # Material Filter Properties
    bpy.types.Scene.matlayer_material_filter_stack = PointerProperty(type=MATLAYER_material_filter_stack)
    bpy.types.Scene.matlayer_material_filters = CollectionProperty(type=MATLAYER_material_filters)

    # Layer Mask Properites
    bpy.types.Scene.matlayer_mask_stack = PointerProperty(type=MATLAYER_mask_stack)
    bpy.types.Scene.matlayer_masks = CollectionProperty(type=MATLAYER_masks)
    bpy.types.Scene.matlayer_mask_filter_stack = PointerProperty(type=MATLAYER_mask_filter_stack)
    bpy.types.Scene.matlayer_mask_filters = CollectionProperty(type=MATLAYER_mask_filters)

    # Settings
    bpy.types.Scene.matlayer_texture_set_settings = PointerProperty(type=MATLAYER_texture_set_settings)
    bpy.types.Scene.matlayer_baking_settings = PointerProperty(type=MATLAYER_baking_settings)
    bpy.types.Scene.matlayer_export_settings = PointerProperty(type=MATLAYER_exporting_settings)

    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    export_textures = addon_preferences.export_textures
    if len(export_textures) <= 0:
        set_export_template('Unreal Engine 4')

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
