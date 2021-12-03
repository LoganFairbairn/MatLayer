import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty

class COATER_AddonPreferences(AddonPreferences):
    bl_idname = "Coater"

    image_size_presets: bpy.props.EnumProperty(
        items=[('LR', "512x512", "Low resolution"),
               ('ONE_K', "1024x1024", "1k image size"),
               ('TWO_K', "2048x2048", "2K image size"),
               ('FOUR_K', "4096x4096", "4k image size")],
        name="Image Size Presets",
        description="Preset Sizes for images",
    )

    # Interface Settings
    show_color_picker: bpy.props.BoolProperty(default=False, name="Show Color Picker")
    show_color_palette: bpy.props.BoolProperty(default=False, name="Show Color Palette")
    show_brush_settings: bpy.props.BoolProperty(default=True, name="Show Brush Settings")

    # Layer Settings
    layer_folder: bpy.props.StringProperty(default="", name="Layers")

    # Bake Settings
    bake_folder: bpy.props.StringProperty(default="", name="Bakes")
    bake_ao: bpy.props.BoolProperty(default=True, name="Bake Ambient Occlusion")
    bake_curvature: bpy.props.BoolProperty(default=True, name="Bake Curvature")
    bake_edges: bpy.props.BoolProperty(default=False, name="Bake Edges")
    bake_normals: bpy.props.BoolProperty(default=False, name="Bake Normals")

    # Export Settings
    export_textures_folder: bpy.props.StringProperty(default="", name="Exports")
    export_base_color: bpy.props.BoolProperty(default=True, name="Export Base Color")
    export_roughness: bpy.props.BoolProperty(default=False, name="Export Roughness")
    export_metallic: bpy.props.BoolProperty(default=False, name="Export Metallic")
    export_normals: bpy.props.BoolProperty(default=False, name="Export Normals")
    export_emission: bpy.props.BoolProperty(default=False, name="Export Emission")
    export_ao: bpy.props.BoolProperty(default=False, name="Export Ambient Occlusion")