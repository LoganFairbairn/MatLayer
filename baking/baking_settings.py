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

def update_match_output_resolution(self, context):
    baking_properties = context.scene.coater_baking_properties

    if baking_properties.match_output_resolution:
        baking_properties.output_height = baking_properties.output_width

def update_output_width(self, context):
    baking_properties = context.scene.coater_baking_properties

    if baking_properties.match_output_resolution:
        if baking_properties.output_height != baking_properties.output_width:
            baking_properties.output_height = baking_properties.output_width

# Baking settings.
class COATER_baking_settings(bpy.types.PropertyGroup):
    bake_type: bpy.props.EnumProperty(
        items=[('AMBIENT_OCCLUSION', "Ambient Occlusion", ""),
               ('CURVATURE', "Curvature", ""),
               ('EDGES', 'Edges', "")],
        name="Bake Types",
        description="Projection type of the image attached to the selected layer",
        default='AMBIENT_OCCLUSION'
    )

    output_quality: bpy.props.EnumProperty(
        items=[('LOW_QUALITY', "Low Quality", ""),
               ('RECOMMENDED_QUALITY', "Recommended Quality", ""),
               ('HIGH_QUALITY', 'High Quality', "")],
        name="Output Quality",
        description="Output quality of the bake.",
        default='RECOMMENDED_QUALITY'
    )

    output_width: bpy.props.EnumProperty(
        items=[('FIVE_TWELVE', "512", ""),
               ('ONEK', "1024", ""),
               ('TWOK', "2048", ""),
               ('FOURK', "4096", "")],
        name="Output Height",
        description="Image size for the baked texure map result(s).",
        default='FIVE_TWELVE',
        update=update_output_width
    )

    output_height: bpy.props.EnumProperty(
        items=[('FIVE_TWELVE', "512", ""),
               ('ONEK', "1024", ""),
               ('TWOK', "2048", ""),
               ('FOURK', "4096", "")],
        name="Output Height",
        description="Image size for the baked texure map result(s).",
        default='FIVE_TWELVE'
    )

    match_output_resolution: bpy.props.BoolProperty(name="Match Output Resoltion", description="Match the output resoltion", default=True, update=update_match_output_resolution)

    bake_ambient_occlusion: bpy.props.BoolProperty(name="Bake Ambient Occlusion", description="Bake ambient occlusion", default=True)
    ambient_occlusion_image_name: bpy.props.StringProperty(name="", description="The baking AO image", default="")
    ambient_occlusion_intensity: bpy.props.FloatProperty(name="Ambient Occlusion Intensity", description="", min=0.0, max=1.0, default=0.5)
    ambient_occlusion_samples: bpy.props.FloatProperty(name="Ambient Occlusion Samples", description="The amount of samples for ambient occlusion taken", min=1.0, max=128.0, default=64.0)
    ambient_occlusion_local: bpy.props.BoolProperty(name="Local AO", description="Ambient occlusion will not bake shadow cast by other objects", default=True)
    ambient_occlusion_inside: bpy.props.BoolProperty(name="Inside AO", description="Ambient occlusion will trace rays towards the inside of the object", default=False)

    bake_curvature: bpy.props.BoolProperty(name="Bake Curvature", description="Bake Curvature", default=True)
    curvature_image_name: bpy.props.StringProperty(name="", description="The baked curvature for object", default="")
    curvature_edge_intensity: bpy.props.FloatProperty(name="Edge Intensity", description="Brightens edges", min=0.0, max=10.0, default=3.0)
    curvature_edge_radius: bpy.props.FloatProperty(name="Edge Thickness", description="Edge thickness", min=0.001, max=0.1, default=0.01)
    curvature_ao_masking: bpy.props.FloatProperty(name="AO Masking", description="Mask the curvature edges using ambient occlusion.", min=0.0, max=1.0, default=1.0)