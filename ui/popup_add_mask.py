import bpy
from bpy.types import Operator

class MATLAY_OT_add_mask_menu(Operator):
    '''Opens a menu of mask types that can be added to the selected layer.'''
    bl_label = ""
    bl_idname = "matlay.add_mask_menu"
    bl_description = "Opens a menu of mask types that can be added to the selected layer"

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

    # Opens the popup when the add layer button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=150)

    # Draws the properties in the popup.
    def draw(self, context):
        layout = self.layout
        split = layout.split()
        col = split.column(align=True)
        col.scale_y = 1.4
        col.operator("matlay.add_empty_mask")
        col.operator("matlay.add_black_mask")
        col.operator("matlay.add_white_mask")
