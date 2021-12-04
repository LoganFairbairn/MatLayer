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

# Exporting settings.
class COATER_exporting_settings(bpy.types.PropertyGroup):
    bake_ambient_occlusion: bpy.props.BoolProperty(name="Bake Ambient Occlusion", description="Bake ambient occlusion", default=True)
    export_base_color: bpy.props.BoolProperty(default=True, name="Export Base Color")
    export_roughness: bpy.props.BoolProperty(default=False, name="Export Roughness")
    export_metallic: bpy.props.BoolProperty(default=False, name="Export Metallic")
    export_normals: bpy.props.BoolProperty(default=False, name="Export Normals")
    export_emission: bpy.props.BoolProperty(default=False, name="Export Emission")