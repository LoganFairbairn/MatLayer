import bpy

class COATER_exporting_settings(bpy.types.PropertyGroup):
    bake_ambient_occlusion: bpy.props.BoolProperty(name="Bake Ambient Occlusion", description="Bake ambient occlusion", default=True)
    export_base_color: bpy.props.BoolProperty(default=True, name="Export Base Color")
    export_roughness: bpy.props.BoolProperty(default=False, name="Export Roughness")
    export_metallic: bpy.props.BoolProperty(default=False, name="Export Metallic")
    export_normals: bpy.props.BoolProperty(default=False, name="Export Normals")
    export_emission: bpy.props.BoolProperty(default=False, name="Export Emission")