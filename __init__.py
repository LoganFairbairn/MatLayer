# Copyright (c) 2021 Logan Fairbairn
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

# This file imports and registers all required modules.

import bpy
from bpy.app.handlers import persistent

# Import add-on preferences.
from .preferences.coater_preferences import *

# Import layer functionality.
from .layers.layers import *
from .layers.layer_stack import *
from .layers.layer_settings import COATER_layer_settings
from .layers.add_image_layer import COATER_OT_add_image_layer, COATER_OT_add_empty_image_layer
from .layers.add_color_layer import COATER_OT_add_color_layer
from .layers.add_group_layer import COATER_OT_add_group_layer
from .layers.layer_masking import COATER_OT_add_image_mask, COATER_OT_delete_layer_mask
from .layers.refresh_layers import COATER_OT_refresh_layers
from .layers.merge_layers import COATER_OT_merge_layer
from .layers.duplicate_layers import COATER_OT_duplicate_layer
from .layers.import_layer_image import COATER_OT_import_color_image, COATER_OT_import_mask_image
from .layers.select_layer import COATER_OT_select_layer_image, COATER_OT_select_layer_mask
from .layers.move_layer import COATER_OT_move_layer_up, COATER_OT_move_layer_down
from .layers.toggle_channel_preview import COATER_OT_toggle_channel_preview
from .layers.delete_layer import COATER_OT_delete_layer
from .layers.bake_layer import COATER_OT_bake_layer

# Import baking functionality.
from .baking.baking_settings import COATER_baking_settings
from .baking.bake_ambient_occlusion import COATER_OT_bake_ambient_occlusion, COATER_OT_toggle_ambient_occlusion_preview
from .baking.bake_curvature import COATER_OT_bake_curvature, COATER_OT_toggle_curvature_preview
from .baking.bake_functions import *

# Import exporting functioality.
from .exporting.coater_export import *
from .exporting.export_to_image_editor import *
from .exporting.exporting_settings import COATER_exporting_settings

# Import tool functionality.
from .swap_tool_color import *

# Import user interface functionality.
from .ui.coater_ui import *
from .ui.popup_add_layer import *
from .ui.popup_add_mask import *
from .ui.ui_layer_stack import *

# Improt extra features.
from .extra_features.toggle_texture_paint_mode import *
from .extra_features.apply_color_grid import COATER_OT_apply_color_grid

bl_info = {
    "name": "Coater",
    "author": "Logan Fairbairn",
    "version": (0, 7),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Coater",
    "description": "Replaces node based texturing workflow with a layer stack workflow.",
    "warning": "",
    "doc_url": "",
    "category": "Material Editing",
}

# List of classes to be registered.
classes = (
    #Addon Preferences
    COATER_AddonPreferences,
    
    # Baking
    COATER_baking_settings,
    COATER_OT_bake,
    COATER_OT_toggle_ambient_occlusion_preview,
    COATER_OT_bake_ambient_occlusion,
    COATER_OT_toggle_curvature_preview,
    COATER_OT_bake_curvature,

    # Exporting
    COATER_exporting_settings,
    COATER_OT_export,
    COATER_OT_export_base_color,
    COATER_OT_export_roughness,
    COATER_OT_export_metallic,
    COATER_OT_export_normals,
    COATER_OT_export_emission,

    # Layers
    COATER_layer_stack,
    COATER_layers,

    # Layer Menus
    COATER_OT_add_layer_menu,
    COATER_OT_add_mask_menu,

    # Layer Operations
    COATER_UL_layer_list,
    COATER_layer_settings,
    COATER_OT_add_color_layer,
    COATER_OT_add_image_layer,
    COATER_OT_add_group_layer,
    COATER_OT_add_image_mask,
    COATER_OT_delete_layer_mask,
    COATER_OT_import_mask_image,
    COATER_OT_add_empty_image_layer,
    COATER_OT_delete_layer,
    COATER_OT_move_layer_up,
    COATER_OT_move_layer_down,
    COATER_OT_merge_layer,
    COATER_OT_duplicate_layer,
    COATER_OT_toggle_channel_preview,
    COATER_OT_import_color_image,
    COATER_OT_refresh_layers,
    COATER_OT_select_layer_image,
    COATER_OT_select_layer_mask,
    COATER_OT_bake_layer,

    # Main Panel & General Settings
    COATER_panel_properties,
    COATER_PT_Panel,

    # Color Swap
    COATER_OT_swap_primary_color,
    
    # Misc functions
    COATER_OT_image_editor_export,
    COATER_OT_toggle_texture_paint_mode,
    COATER_OT_apply_color_grid,
)

def obj_selected_callback():
    '''Updates coater layers when a the active object selection changes.'''
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

    # Layer Stack Properties
    bpy.types.Scene.coater_layer_stack = bpy.props.PointerProperty(type=COATER_layer_stack)
    bpy.types.Scene.coater_layers = bpy.props.CollectionProperty(type=COATER_layers)
    bpy.types.Scene.coater_layer_settings = bpy.props.PointerProperty(type=COATER_layer_settings)

    # Baking Settings
    bpy.types.Scene.coater_baking_settings = bpy.props.PointerProperty(type=COATER_baking_settings)
    
    # Exporting Settings
    bpy.types.Scene.coater_export_settings = bpy.props.PointerProperty(type=COATER_exporting_settings)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # TODO: Unregister pointers??

if __name__ == "__main__":
    register()

        
