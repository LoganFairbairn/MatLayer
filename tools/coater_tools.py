import bpy

def create_default_palette():
    coater_palette = bpy.data.palettes.get("Coater_Palette")
    if coater_palette is None:
        return bpy.data.palettes.new("Coater_Palette")

    else:
        return coater_palette

