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

import bpy
from . layers import *
from . baking import *
from . display import *
from . coater_panel import *
from . export_to_image_editor import *


bl_info = {
    "name": "Coater",
    "author": "Logan Fairbairn",
    "version": (0, 1),
    "blender": (2, 91, 2),
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
    COATER_OT_bake_ambient_occlusion,
    COATER_OT_set_hand_painted,

    # Layer Stack
    LayerProperties,
    COATER_UL_layer_list,
    COATER_OT_add_layer,
    COATER_OT_add_color_layer,
    COATER_OT_delete_layer,
    COATER_OT_move_layer,
    COATER_OT_merge_layer,
    COATER_OT_duplicate_layer,

    # Main Panel & General Settings
    COATER_PT_Panel,

    # Additional functions.
    COATER_OT_image_editor_export
)


def register():
    # Register properties, operators and pannels.
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.coater_properties = bpy.props.PointerProperty(
        type=COATER_properties)

    bpy.types.Scene.my_list = bpy.props.CollectionProperty(
        type=LayerProperties, name="layers 4123")

    bpy.types.Scene.layer_index = bpy.props.IntProperty(name="Index for my_list",
                                                        default=0)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.coater_properties


if __name__ == "__main__":
    register()
