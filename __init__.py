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

# This file imports and registers all required modules for MatLay (Blender add-on).

import bpy
from bpy.props import PointerProperty, CollectionProperty
import bpy.utils.previews       # Imported for loading texture previews as icons.
from bpy.app.handlers import persistent

# Import texture set modules.
from .core.texture_set_settings import MATLAY_texture_set_settings, GlobalMaterialChannelToggles

# Import layer related modules.
from .core.layers import *
from .core.layer_stack import *

# Import material channel modules.
from .core.material_channels import MATLAY_OT_toggle_material_channel_preview

# Import layer masking modules.
from .core.layer_masks import MATLAY_mask_stack, MATLAY_UL_mask_stack, MATLAY_masks, MATLAY_OT_open_mask_settings, MATLAY_OT_add_mask, MATLAY_OT_delete_layer_mask, MATLAY_OT_move_layer_mask_up, MATLAY_OT_move_layer_mask_down, MATLAY_OT_add_layer_mask_filter_menu, MATLAY_OT_add_mask_filter_invert, MATLAY_OT_add_mask_filter_levels

# Import filter modules.
from .core.layer_filters import FiltersMaterialChannelToggles, MATLAY_material_filter_stack, MATLAY_UL_layer_filter_stack, MATLAY_material_filters, MATLAY_OT_add_layer_filter_menu, MATLAY_OT_add_layer_filter_rgb_curves, MATLAY_OT_add_layer_filter_hsv, MATLAY_OT_add_layer_filter_invert, MATLAY_OT_add_layer_filter_levels, MATLAY_OT_delete_layer_filter, MATLAY_OT_move_layer_filter_up, MATLAY_OT_move_layer_filter_down

# Import layer operations.
from .core.layer_operations import *

# Import baking modules.
from .core.baking import MATLAY_baking_settings, MATLAY_OT_bake, MATLAY_OT_bake_ambient_occlusion, MATLAY_OT_bake_curvature, MATLAY_OT_bake_thickness, MATLAY_OT_bake_normals, MATLAY_OT_delete_ao_map, MATLAY_OT_delete_curvature_map, MATLAY_OT_delete_thickness_map, MATLAY_OT_delete_normal_map

# Import exporting modules.
from .core.exporting import MATLAY_exporting_settings, MATLAY_OT_export, MATLAY_OT_export_base_color, MATLAY_OT_export_subsurface, MATLAY_OT_export_subsurface_color, MATLAY_OT_export_metallic, MATLAY_OT_export_specular, MATLAY_OT_export_roughness, MATLAY_OT_export_normals, MATLAY_OT_export_height, MATLAY_OT_export_emission

# Import tool / utility modules.
from .utilities.image_file_handling import MATLAY_OT_add_layer_image, MATLAY_OT_delete_layer_image, MATLAY_OT_import_texture, MATLAY_OT_import_mask_image

# Import user interface modules.
from .ui.matlay_ui import *
from .ui.popup_add_mask import *
from .ui.ui_layer_stack import *

bl_info = {
    "name": "MatLay",
    "author": "Logan Fairbairn (Ryver)",
    "version": (0, 87),
    "blender": (3, 4, 1),
    "location": "View3D > Sidebar > MatLay",
    "description": "Replaces node based texturing workflow with a layer stack workflow.",
    "warning": "",
    "doc_url": "",
    "category": "Material Editing",
}

# List of classes to be registered.
classes = (
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
    MaterialChannelColors,
    MaterialChannelUniformValues,
    MATLAY_OT_open_material_layer_settings,
    MATLAY_layer_stack,
    MATLAY_layers,

    # Masks
    MATLAY_mask_stack,
    MATLAY_UL_mask_stack,
    MATLAY_masks,
    MATLAY_OT_open_mask_settings,
    MATLAY_OT_add_mask,
    MATLAY_OT_delete_layer_mask,
    MATLAY_OT_move_layer_mask_up, 
    MATLAY_OT_move_layer_mask_down,
    MATLAY_OT_import_mask_image,
    MATLAY_OT_add_layer_mask_filter_menu,
    MATLAY_OT_add_mask_filter_invert,
    MATLAY_OT_add_mask_filter_levels,

    # Filters
    FiltersMaterialChannelToggles,
    MATLAY_material_filter_stack, 
    MATLAY_UL_layer_filter_stack,
    MATLAY_material_filters,
    MATLAY_OT_add_layer_filter_rgb_curves,
    MATLAY_OT_add_layer_filter_hsv,
    MATLAY_OT_add_layer_filter_invert,
    MATLAY_OT_add_layer_filter_levels,
    MATLAY_OT_delete_layer_filter,
    MATLAY_OT_move_layer_filter_up,
    MATLAY_OT_move_layer_filter_down,
    MATLAY_OT_add_mask_menu,
    MATLAY_OT_add_layer_filter_menu,

    # Layer Operations
    MATLAY_UL_layer_list,
    MATLAY_OT_add_layer,
    MATLAY_OT_delete_layer,
    MATLAY_OT_duplicate_layer,
    MATLAY_OT_move_material_layer,
    MATLAY_OT_import_texture,
    MATLAY_OT_refresh_layer_nodes,
    MATLAY_OT_add_layer_image,
    MATLAY_OT_delete_layer_image,

    # Texture Set Settings
    GlobalMaterialChannelToggles,
    MATLAY_texture_set_settings,

    # Main Panel & General Settings
    MATLAY_panel_properties,
    MATLAY_PT_Panel,
    
    # Misc functions
    MATLAY_OT_image_editor_export
)

# Refreshes the layer stack when a different object is selected.
def obj_selected_callback():
    '''Triggers a layer stack refresh when the selected object changes.'''
    bpy.ops.matlay.refresh_layer_nodes(auto_called=True)

@persistent
def load_handler(dummy):
    subscribe_to = bpy.types.LayerObjects, "active"
    bpy.types.Scene.matlay_object_selection_updater = object()
    bpy.msgbus.subscribe_rna(key=subscribe_to, owner=bpy.types.Scene.matlay_object_selection_updater, args=(), notify=obj_selected_callback)

bpy.app.handlers.load_post.append(load_handler)

# Global variable for icons used as layer previews.
#preview_collections = {}

def register():
    # Register properties, operators and pannels.
    for cls in classes:
        bpy.utils.register_class(cls)

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

    # Settings
    bpy.types.Scene.matlay_texture_set_settings = PointerProperty(type=MATLAY_texture_set_settings)
    bpy.types.Scene.matlay_baking_settings = PointerProperty(type=MATLAY_baking_settings)
    bpy.types.Scene.matlay_export_settings = PointerProperty(type=MATLAY_exporting_settings)

    # Icons (for layer previews)
    #bpy.types.Scene.preview_icons = bpy.utils.previews.new()
    #preview_collections["main"] = bpy.types.Scene.preview_icons

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # Clear preview collections.
    #for bpy.types.Scene.preview_icons in preview_collections.values():
    #    bpy.utils.previews.remove(bpy.types.Scene.preview_icons)
    #preview_collections.clear()

    # TODO: Unregister pointers????????
    bpy.types.Scene.matlay_panel_properties = None

    bpy.types.Scene.matlay_layer_stack = None
    bpy.types.Scene.matlay_layers = None

    # Material Filter Properties
    bpy.types.Scene.matlay_material_filter_stack = None
    bpy.types.Scene.matlay_material_filters = None

    # Layer Mask Properites
    bpy.types.Scene.matlay_mask_stack = None
    bpy.types.Scene.matlay_masks = None

    # Settings
    bpy.types.Scene.matlay_texture_set_settings = None
    bpy.types.Scene.matlay_baking_settings = None
    bpy.types.Scene.matlay_export_settings = None

if __name__ == "__main__":
    register()

        
