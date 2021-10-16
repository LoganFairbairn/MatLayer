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

# Import layer functionality.
from . layers import *
from . add_layer_menu import *
from . add_mask_menu import *
from . layer_properties import *

# Import baking functionality.
from . baking import *

# Import UI.
from . coater_panel import *
from . coater_tools import *

# Import additional functions.
from . export_to_image_editor import *
from . toggle_texture_paint_mode import *


bl_info = {
    "name": "Coater",
    "author": "Logan Fairbairn",
    "version": (0, 1),
    "blender": (2, 93, 5),
    "location": "View3D > Sidebar > Coater",
    "description": "Replaces node based texturing workflow with a layer stack workflow.",
    "warning": "",
    "doc_url": "",
    "category": "Material Editing",
}


# List of classes to be registered.
classes = (
    COATER_properties,
    COATER_OT_apply_color_grid,
    COATER_OT_bake_common_maps,
    COATER_OT_bake_ambient_occlusion,
    COATER_OT_bake_curvature,
    COATER_OT_bake_edges,

    # Layer Stack
    COATER_layer_stack,
    COATER_layers,
    COATER_OT_add_layer_menu,
    COATER_OT_add_mask_menu,
    COATER_OT_edit_layer_properties,
    COATER_UL_layer_list,
    COATER_OT_add_layer,
    COATER_OT_add_mask,
    COATER_OT_delete_layer,
    COATER_OT_move_layer,
    COATER_OT_merge_layer,
    COATER_OT_duplicate_layer,
    COATER_OT_toggle_channel_preview,

    # Main Panel & General Settings
    COATER_PT_Panel,

    # Tool Settings
    COATER_OT_swap_primary_color,
    
    # Misc functions
    COATER_OT_image_editor_export,
    COATER_OT_toggle_texture_paint_mode
)

def register():
    # Register properties, operators and pannels.
    for cls in classes:
        bpy.utils.register_class(cls)

    # Coater Properties
    bpy.types.Scene.coater_properties = bpy.props.PointerProperty(type=COATER_properties)

    # Layer Stack Properties
    bpy.types.Scene.coater_layer_stack = bpy.props.PointerProperty(type=COATER_layer_stack)
    bpy.types.Scene.coater_layers = bpy.props.CollectionProperty(type=COATER_layers)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.coater_properties


if __name__ == "__main__":
    register()
