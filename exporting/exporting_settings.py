import bpy

class COATER_exporting_settings(bpy.types.PropertyGroup):
    export_folder: bpy.props.StringProperty(default="", description="Path to folder location where baked texture are saved.", name="Export Folder Path")

    export_base_color: bpy.props.BoolProperty(default=True, name="Export Base Color")
    export_metallic: bpy.props.BoolProperty(default=True, name="Export Metallic")
    export_roughness: bpy.props.BoolProperty(default=True, name="Export Roughness")
    export_normals: bpy.props.BoolProperty(default=True, name="Export Normals")
    export_height: bpy.props.BoolProperty(default=True, name="Export Height")
    export_emission: bpy.props.BoolProperty(default=True, name="Export Emission")
    export_scattering: bpy.props.BoolProperty(default=True, name="Export Scattering")