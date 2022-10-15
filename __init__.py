# Copyright (c) 2021-2022 Logan Fairbairn
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

# This file imports and registers all required modules for Coater (Blender add-on).

import bpy
from bpy.app.handlers import persistent

# Import texture set modules.
from .texture_set_settings.texture_set_settings import COATER_texture_set_settings

# Import layer related modules.
from .layers.layer_stack.layers import *
from .layers.layer_stack.layer_stack import *
from .layers.layer_stack.layer_settings import COATER_layer_settings
from .layers.nodes.read_layer_nodes import COATER_OT_read_layer_nodes
from .layers.layer_stack.select_layer import COATER_OT_select_layer_image, COATER_OT_select_layer_mask
from .layers.layer_operations.toggle_channel_preview import COATER_OT_toggle_channel_preview

# Import layer masking modules.
from .layers.layer_operations.layer_masking import COATER_mask_stack, COATER_UL_mask_stack, COATER_masks, COATER_OT_add_empty_mask, COATER_OT_delete_layer_mask, COATER_OT_delete_layer_image_mask, COATER_OT_add_black_mask, COATER_OT_add_white_mask

# Import filter modules.
from .layers.layer_stack.layer_filters import COATER_layer_filter_stack, COATER_UL_layer_filter_stack, COATER_layer_filters

# Import layer operation modules.
from .layers.layer_operations.add_layer import COATER_OT_add_layer
from .layers.layer_operations.delete_layer import COATER_OT_delete_layer
from .layers.layer_operations.bake_layer import COATER_OT_bake_layer
from .layers.layer_operations.move_layer import COATER_OT_move_layer_up, COATER_OT_move_layer_down
from .layers.layer_operations.merge_layers import COATER_OT_merge_layer
from .layers.layer_operations.duplicate_layers import COATER_OT_duplicate_layer
from .layers.layer_operations.merge_layers import COATER_OT_merge_layer
from .layers.layer_operations.duplicate_layers import COATER_OT_duplicate_layer
from .layers.layer_operations.merge_layers import COATER_OT_merge_layer
from .layers.layer_operations.duplicate_layers import COATER_OT_duplicate_layer

# Import baking modules.
from .baking.baking_settings import COATER_baking_settings
from .baking.bake_ambient_occlusion import COATER_OT_bake_ambient_occlusion
from .baking.bake_curvature import COATER_OT_bake_curvature
from .baking.bake_thickness import COATER_OT_bake_thickness
from .baking.bake_functions import *

# Import exporting modules.
from .exporting.coater_export import *
from .exporting.export_to_image_editor import *
from .exporting.exporting_settings import COATER_exporting_settings

# Import tool / utility modules.
from .texture_handling.image_file_handling import COATER_OT_add_layer_image, COATER_OT_delete_layer_image
from .texture_handling.import_layer_image import COATER_OT_import_color_image, COATER_OT_import_mask_image, COATER_OT_unlink_layer_image
from .swap_tool_color import *

# Import user interface modules.
from .ui.coater_ui import *
from .ui.popup_add_mask import *
from .ui.ui_layer_stack import *

# Import extra feature modules.
from .extra_features.apply_color_grid import COATER_OT_apply_color_grid

bl_info = {
    "name": "Coater",
    "author": "Logan Fairbairn",
    "version": (0, 8),
    "blender": (3, 1, 2),
    "location": "View3D > Sidebar > Coater",
    "description": "Replaces node based texturing workflow with a layer stack workflow.",
    "warning": "",
    "doc_url": "",
    "category": "Material Editing",
}

# List of classes to be registered.
classes = (
    # Texture Set Settings
    COATER_texture_set_settings,
    
    # Baking
    COATER_baking_settings,
    COATER_OT_bake,
    COATER_OT_bake_ambient_occlusion,
    COATER_OT_bake_curvature,
    COATER_OT_bake_thickness,

    # Exporting
    COATER_exporting_settings,
    COATER_OT_export,
    COATER_OT_export_base_color,
    COATER_OT_export_metallic,
    COATER_OT_export_roughness,
    COATER_OT_export_normals,
    COATER_OT_export_height,
    COATER_OT_export_emission,
    COATER_OT_export_scattering,

    # Layers
    COATER_layer_stack,
    COATER_layers,

    # Masks
    COATER_mask_stack,
    COATER_UL_mask_stack,
    COATER_masks,

    # Filters
    COATER_layer_filter_stack, 
    COATER_UL_layer_filter_stack, 
    COATER_layer_filters,

    # Layer Menus
    COATER_OT_add_mask_menu,

    # Layer Operations
    COATER_UL_layer_list,
    COATER_layer_settings,
    COATER_OT_add_layer,
    COATER_OT_add_empty_mask,
    COATER_OT_delete_layer_mask,
    COATER_OT_add_black_mask,
    COATER_OT_add_white_mask,
    COATER_OT_delete_layer_image_mask,
    COATER_OT_import_mask_image,
    COATER_OT_delete_layer,
    COATER_OT_move_layer_up,
    COATER_OT_move_layer_down,
    COATER_OT_merge_layer,
    COATER_OT_duplicate_layer,
    COATER_OT_toggle_channel_preview,
    COATER_OT_import_color_image,
    COATER_OT_unlink_layer_image,
    COATER_OT_read_layer_nodes,
    COATER_OT_select_layer_image,
    COATER_OT_select_layer_mask,
    COATER_OT_bake_layer,
    COATER_OT_add_layer_image,
    COATER_OT_delete_layer_image,

    # Main Panel & General Settings
    COATER_panel_properties,
    COATER_PT_Panel,

    # Color Swap
    COATER_OT_swap_primary_color,
    
    # Misc functions
    COATER_OT_image_editor_export,
    COATER_OT_apply_color_grid,
)

def obj_selected_callback():
    '''Triggers a layer refresh when the selected object changes.'''
    bpy.ops.coater.refresh_layers()

@persistent
def load_handler(dummy):
    subscribe_to = bpy.types.LayerObjects, "active"
    bpy.types.Scene.coater_object_selection_updater = object()
    bpy.msgbus.subscribe_rna(key=subscribe_to, owner=bpy.types.Scene.coater_object_selection_updater, args=(), notify=obj_selected_callback)

bpy.app.handlers.load_post.append(load_handler)

def register():
    # Register properties, operators and pannels.
    for cls in classes:
        bpy.utils.register_class(cls)

    # Panel Properties
    bpy.types.Scene.coater_panel_properties = bpy.props.PointerProperty(type=COATER_panel_properties)

    # Layer Properties
    bpy.types.Scene.coater_layer_stack = bpy.props.PointerProperty(type=COATER_layer_stack)
    bpy.types.Scene.coater_layers = bpy.props.CollectionProperty(type=COATER_layers)

    # Layer Mask Properites
    bpy.types.Scene.coater_mask_stack = bpy.props.PointerProperty(type=COATER_mask_stack)
    bpy.types.Scene.coater_masks = bpy.props.CollectionProperty(type=COATER_masks)

    # Layer Filter Properties
    bpy.types.Scene.coater_layer_filter_stack = bpy.props.PointerProperty(type=COATER_layer_filter_stack)
    bpy.types.Scene.coater_layer_filters = bpy.props.CollectionProperty(type=COATER_layer_filters)

    # Settings
    bpy.types.Scene.coater_texture_set_settings = bpy.props.PointerProperty(type=COATER_texture_set_settings)
    bpy.types.Scene.coater_layer_settings = bpy.props.PointerProperty(type=COATER_layer_settings)
    bpy.types.Scene.coater_baking_settings = bpy.props.PointerProperty(type=COATER_baking_settings)
    bpy.types.Scene.coater_export_settings = bpy.props.PointerProperty(type=COATER_exporting_settings)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # TODO: Unregister pointers????????

if __name__ == "__main__":
    register()

        
