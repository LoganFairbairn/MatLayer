import bpy

def update_match_bake_resolution(self, context):
    baking_settings = context.scene.coater_baking_settings

    if baking_settings.match_bake_resolution:
        baking_settings.output_height = baking_settings.output_width

def update_bake_width(self, context):
    baking_settings = context.scene.coater_baking_settings

    if baking_settings.match_bake_resolution:
        if baking_settings.output_height != baking_settings.output_width:
            baking_settings.output_height = baking_settings.output_width

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
        default='TWOK',
        update=update_bake_width
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

    match_bake_resolution: bpy.props.BoolProperty(name="Match Bake Resoltion", description="When toggled on, the bake resolution's width and height will be synced", default=True, update=update_match_bake_resolution)

    bake_ambient_occlusion: bpy.props.BoolProperty(name="Bake Ambient Occlusion", description="Bake ambient occlusion", default=True)
    ambient_occlusion_image_name: bpy.props.StringProperty(name="", description="The baking AO image", default="")
    ambient_occlusion_intensity: bpy.props.FloatProperty(name="Ambient Occlusion Intensity", description="", min=0.1, max=0.99, default=0.5)
    ambient_occlusion_samples: bpy.props.FloatProperty(name="Ambient Occlusion Samples", description="The amount of samples for ambient occlusion taken", min=1.0, max=128.0, default=64.0)
    ambient_occlusion_local: bpy.props.BoolProperty(name="Local AO", description="Ambient occlusion will not bake shadow cast by other objects", default=True)
    ambient_occlusion_inside: bpy.props.BoolProperty(name="Inside AO", description="Ambient occlusion will trace rays towards the inside of the object", default=False)

    bake_curvature: bpy.props.BoolProperty(name="Bake Curvature", description="Bake Curvature", default=True)
    curvature_image_name: bpy.props.StringProperty(name="", description="The baked curvature for object", default="")
    curvature_edge_intensity: bpy.props.FloatProperty(name="Edge Intensity", description="Brightens edges", min=0.0, max=10.0, default=3.0)
    curvature_edge_radius: bpy.props.FloatProperty(name="Edge Thickness", description="Edge thickness", min=0.001, max=0.1, default=0.01)
    curvature_ao_masking: bpy.props.FloatProperty(name="AO Masking", description="Mask the curvature edges using ambient occlusion.", min=0.0, max=1.0, default=1.0)