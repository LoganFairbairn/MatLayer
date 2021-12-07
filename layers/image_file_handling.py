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

# This file provides easy ways to correctly edit and save images made with Coater.

import bpy

def get_image_name(layer_name):
    '''Returns the image name'''
    bpy.context.scene.coater_layers
    layer_index = bpy.context.scene.coater_layer_stack.layer_index

def save_layer_image(image_name):
    '''Saves the given layer image to the designated layer folder.'''
    print("")

def rename_layer_image(image_name, new_name):
    '''Renames the given layer image to the new name.'''
    print("")