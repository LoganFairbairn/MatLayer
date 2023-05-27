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
from bpy.props import PointerProperty, CollectionProperty
import bpy.utils.previews       # Imported for loading texture previews as icons.
from bpy.app.handlers import persistent

# Import add-on preference settings.
from .preferences import AddonPreferences

# Import texture set modules.
from .core.texture_set_settings import MATLAY_texture_set_settings, GlobalMaterialChannelToggles

# Import layer related modules.
from .core.material_layers import *

# Import material channel modules.
from .core.material_channels import MATLAY_OT_toggle_material_channel_preview

# Import layer masking modules.
from .core.layer_masks import MaskProjectionSettings, MATLAY_mask_stack, MATLAY_masks, MATLAY_UL_mask_stack, MATLAY_OT_add_black_layer_mask, MATLAY_OT_add_white_layer_mask, MATLAY_OT_add_empty_layer_mask, MATLAY_OT_add_group_node_layer_mask, MATLAY_OT_add_noise_layer_mask, MATLAY_OT_add_voronoi_layer_mask, MATLAY_OT_add_musgrave_layer_mask, MATLAY_OT_open_layer_mask_menu, MATLAY_OT_delete_layer_mask,MATLAY_OT_move_layer_mask_up, MATLAY_OT_move_layer_mask_down, MATLAY_OT_add_mask_image, MATLAY_OT_delete_mask_image, MATLAY_OT_import_mask_image, MATLAY_mask_filter_stack, MATLAY_mask_filters, MATLAY_UL_mask_filter_stack, MATLAY_OT_add_mask_filter_invert, MATLAY_OT_add_mask_filter_val_to_rgb, MATLAY_OT_add_layer_mask_filter_menu, MATLAY_OT_delete_mask_filter, MATLAY_OT_move_layer_mask_filter

# Import layer operations.
from .core.layer_operations import *

# Import material filter modules.
from .core.material_filters import FiltersMaterialChannelToggles, MATLAY_material_filter_stack, MATLAY_UL_layer_filter_stack, MATLAY_material_filters, MATLAY_OT_add_layer_filter_menu, MATLAY_OT_add_layer_filter_rgb_curves, MATLAY_OT_add_layer_filter_hsv, MATLAY_OT_add_layer_filter_invert, MATLAY_OT_add_layer_filter_val_to_rgb, MATLAY_OT_add_layer_filter_bright_contrast, MATLAY_OT_delete_layer_filter, MATLAY_OT_move_layer_filter_up, MATLAY_OT_move_layer_filter_down

# Import baking modules.
from .core.baking import MATLAY_baking_settings, MATLAY_OT_bake, MATLAY_OT_bake_ambient_occlusion, MATLAY_OT_bake_curvature, MATLAY_OT_bake_thickness, MATLAY_OT_bake_normals, MATLAY_OT_delete_ao_map, MATLAY_OT_delete_curvature_map, MATLAY_OT_delete_thickness_map, MATLAY_OT_delete_normal_map

# Import exporting modules.
from .core.exporting import MATLAY_exporting_settings, MATLAY_OT_export, MATLAY_OT_export_base_color, MATLAY_OT_export_subsurface, MATLAY_OT_export_subsurface_color, MATLAY_OT_export_metallic, MATLAY_OT_export_specular, MATLAY_OT_export_roughness, MATLAY_OT_export_normals, MATLAY_OT_export_height, MATLAY_OT_export_emission

# Import tool / utility modules.
from .utilities.image_file_handling import MATLAY_OT_add_layer_image, MATLAY_OT_delete_layer_image, MATLAY_OT_import_texture, MATLAY_OT_import_texture_set

# Import settings.
from .utilities.matlay_utils import MatlaySettings, MATLAY_OT_set_decal_layer_snapping, MATLAY_OT_append_workspace, MATLAY_OT_append_basic_brushes, MATLAY_OT_delete_unused_external_images

# Import user interface modules.
from .ui.matlay_ui import *
from .ui.popup_add_mask import *
from .ui.ui_layer_stack import *

bl_info = {
    "name": "MatLay",
    "author": "Logan Fairbairn (Ryver)",
    "version": (1, 0, 2),
    "blender": (3, 4, 1),
    "location": "View3D > Sidebar > MatLay",
    "description": "Replaces node based texturing workflow with a layer stack workflow.",
    "warning": "",
    "doc_url": "",
    "category": "Material Editing",
}

# List of classes to be registered.
classes = (
    # Preferences
    AddonPreferences,

    # Baking
    MATLAY_baking_settings,
    MATLAY_OT_bake,
    MATLAY_OT_bake_ambient_occlusion,
    MATLAY_OT_bake_curvature,
    MATLAY_OT_bake_thickness,
    MATLAY_OT_bake_normals,
    MATLAY_OT_delete_ao_map,
    MATLAY_OT_delete_curvature_map,
    MATLAY_OT_delete_thickness_map,
    MATLAY_OT_delete_normal_map,

    # Exporting
    MATLAY_exporting_settings,
    MATLAY_OT_export,
    MATLAY_OT_export_base_color,
    MATLAY_OT_export_subsurface,
    MATLAY_OT_export_subsurface_color,
    MATLAY_OT_export_metallic,
    MATLAY_OT_export_specular,
    MATLAY_OT_export_roughness,
    MATLAY_OT_export_normals,
    MATLAY_OT_export_height,
    MATLAY_OT_export_emission,

    # Material Channels
    MATLAY_OT_toggle_material_channel_preview,

    # Layers
    MaterialChannelToggles,
    MaterialChannelNodeType,
    ProjectionSettings,
    MaterialChannelTextures,
    MaterialChannelColors,
    MaterialChannelUniformValues,
    MaterialChannelGroupNodes,
    MaterialChannelBlurring,
    MATLAY_OT_open_material_layer_settings,
    MATLAY_layer_stack,
    MATLAY_layers,

    # Masks
    MaskProjectionSettings,
    MATLAY_mask_stack,
    MATLAY_masks,
    MATLAY_UL_mask_stack,
    MATLAY_OT_add_black_layer_mask, 
    MATLAY_OT_add_white_layer_mask,
    MATLAY_OT_add_empty_layer_mask,
    MATLAY_OT_add_group_node_layer_mask,
    MATLAY_OT_add_noise_layer_mask,
    MATLAY_OT_add_voronoi_layer_mask,
    MATLAY_OT_add_musgrave_layer_mask,
    MATLAY_OT_open_layer_mask_menu,
    MATLAY_OT_delete_layer_mask,
    MATLAY_OT_move_layer_mask_up,
    MATLAY_OT_move_layer_mask_down,
    MATLAY_OT_add_mask_image, 
    MATLAY_OT_delete_mask_image, 
    MATLAY_OT_import_mask_image,

    # Mask Filters
    MATLAY_mask_filter_stack,
    MATLAY_mask_filters,
    MATLAY_UL_mask_filter_stack,
    MATLAY_OT_add_mask_filter_invert,
    MATLAY_OT_add_mask_filter_val_to_rgb,
    MATLAY_OT_add_layer_mask_filter_menu,
    MATLAY_OT_delete_mask_filter,
    MATLAY_OT_move_layer_mask_filter,

    # Filters
    FiltersMaterialChannelToggles,
    MATLAY_material_filter_stack, 
    MATLAY_UL_layer_filter_stack,
    MATLAY_material_filters,
    MATLAY_OT_add_layer_filter_rgb_curves,
    MATLAY_OT_add_layer_filter_hsv,
    MATLAY_OT_add_layer_filter_invert,
    MATLAY_OT_add_layer_filter_val_to_rgb,
    MATLAY_OT_add_layer_filter_bright_contrast,
    MATLAY_OT_delete_layer_filter,
    MATLAY_OT_move_layer_filter_up,
    MATLAY_OT_move_layer_filter_down,
    MATLAY_OT_add_mask_menu,
    MATLAY_OT_add_layer_filter_menu,

    # Layer Operations
    MATLAY_UL_layer_list,
    MATLAY_OT_add_decal_layer,
    MATLAY_OT_add_material_layer,
    MATLAY_OT_add_paint_layer,
    MATLAY_OT_add_layer_menu,
    MATLAY_OT_delete_layer,
    MATLAY_OT_duplicate_layer,
    MATLAY_OT_move_material_layer,
    MATLAY_OT_import_texture,
    MATLAY_OT_import_texture_set,
    MATLAY_OT_read_layer_nodes,
    MATLAY_OT_add_layer_image,
    MATLAY_OT_delete_layer_image,
    MATLAY_OT_edit_uvs_externally,
    MATLAY_OT_edit_image_externally,
    MATLAY_OT_reload_image,

    # Texture Set Settings
    GlobalMaterialChannelToggles,
    MATLAY_texture_set_settings,

    # Utilities
    MatlaySettings,
    MATLAY_OT_set_decal_layer_snapping,
    MATLAY_OT_append_workspace,
    MATLAY_OT_append_basic_brushes,
    MATLAY_OT_delete_unused_external_images,

    # Main Panel
    MATLAY_panel_properties,
    MATLAY_PT_Panel
)

# Read material nodes when the active material index is updated.
def on_active_material_index_changed():
    bpy.context.scene.matlay_layer_stack.layer_index = 0
    bpy.ops.matlay.read_layer_nodes(auto_called=True)

# Read material nodes for the active material when a different object is selected.
def on_active_object_changed():
    '''Triggers a layer stack refresh when the selected object changes.'''
    bpy.ops.matlay.read_layer_nodes(auto_called=True)
    bpy.msgbus.clear_by_owner(bpy.types.Scene.active_material_index_owner)
    active = bpy.context.view_layer.objects.active
    if active:
        bpy.msgbus.subscribe_rna(
            key=active.path_resolve("active_material_index", False),
            owner=bpy.types.Scene.active_material_index_owner,
            notify=on_active_material_index_changed,
            args=()
        )

# Mark load handlers as persistent so they are not freed when loading a new blend file.
@persistent
def load_handler(dummy):
    subscribe_to = bpy.types.LayerObjects, "active"
    bpy.types.Scene.matlay_object_selection_updater = object()
    bpy.msgbus.subscribe_rna(key=subscribe_to, owner=bpy.types.Scene.matlay_object_selection_updater, args=(), notify=on_active_object_changed)

    # Active Material Index
    bpy.types.Scene.active_material_index_owner = object()
    bpy.msgbus.clear_by_owner(bpy.types.Scene.active_material_index_owner)
    active = bpy.context.view_layer.objects.active
    if active:
        bpy.msgbus.subscribe_rna(
            key=active.path_resolve("active_material_index", False),
            owner=bpy.types.Scene.active_material_index_owner,
            notify=on_active_material_index_changed,
            args=()
        )

# Run function on loading a new blend file.
bpy.app.handlers.load_post.append(load_handler)

def register():
    # Register properties, operators and pannels.
    for cls in classes:
        bpy.utils.register_class(cls)
        
    # Settings
    bpy.types.Scene.matlay_settings = PointerProperty(type=MatlaySettings)

    # Panel Properties
    bpy.types.Scene.matlay_panel_properties = PointerProperty(type=MATLAY_panel_properties)

    # Layer Properties
    bpy.types.Scene.matlay_layer_stack = PointerProperty(type=MATLAY_layer_stack)
    bpy.types.Scene.matlay_layers = CollectionProperty(type=MATLAY_layers)

    # Material Filter Properties
    bpy.types.Scene.matlay_material_filter_stack = PointerProperty(type=MATLAY_material_filter_stack)
    bpy.types.Scene.matlay_material_filters = CollectionProperty(type=MATLAY_material_filters)

    # Layer Mask Properites
    bpy.types.Scene.matlay_mask_stack = PointerProperty(type=MATLAY_mask_stack)
    bpy.types.Scene.matlay_masks = CollectionProperty(type=MATLAY_masks)
    bpy.types.Scene.matlay_mask_filter_stack = PointerProperty(type=MATLAY_mask_filter_stack)
    bpy.types.Scene.matlay_mask_filters = CollectionProperty(type=MATLAY_mask_filters)

    # Settings
    bpy.types.Scene.matlay_texture_set_settings = PointerProperty(type=MATLAY_texture_set_settings)
    bpy.types.Scene.matlay_baking_settings = PointerProperty(type=MATLAY_baking_settings)
    bpy.types.Scene.matlay_export_settings = PointerProperty(type=MATLAY_exporting_settings)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
