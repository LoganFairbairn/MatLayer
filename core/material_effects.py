# This module contains automations for setting up specific, commonly used effects for materials such as Edge Wear, Dirt, Grunge, Dust, and more.

import bpy
from bpy.types import Operator

class MATLAYER_OT_add_edge_wear(Operator):
    bl_label = "Add Edge Wear"
    bl_idname = "matlayer.add_edge_wear"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}
    
class MATLAYER_OT_add_grunge(Operator):
    bl_label = "Add Grunge"
    bl_idname = "matlayer.add_grunge"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}
    
class MATLAYER_OT_add_dust(Operator):
    bl_label = "Add Dust"
    bl_idname = "matlayer.add_dust"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}
    
class MATLAYER_OT_add_drips(Operator):
    bl_label = "Add Drips"
    bl_idname = "matlayer.add_drips"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}