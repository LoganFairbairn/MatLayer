# This module contains overrides for material slot editing operators.
# Overriding these operators allows the layer stack to refresh after a change is made.

import bpy
from bpy.types import Operator
from ..core import material_layers

class MATLAYER_OT_add_material_slot(Operator):
    bl_idname = "matlayer.add_material_slot"
    bl_label = "Add Material Slot"
    bl_description = "Adds a new material slot, and updates the layer stack user interface"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bpy.ops.object.material_slot_add()
        material_layers.refresh_layer_stack()
        return {'FINISHED'}
    
class MATLAYER_OT_remove_material_slot(Operator):
    bl_idname = "matlayer.remove_material_slot"
    bl_label = "Remove Material Slot"
    bl_description = "Removes the selected material slot, and updates the layer stack user interface"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bpy.ops.object.material_slot_remove()
        material_layers.refresh_layer_stack()
        return {'FINISHED'}
    
class MATLAYER_OT_move_material_slot_up(Operator):
    bl_idname = "matlayer.move_material_slot_up"
    bl_label = "Move Material Slot Up"
    bl_description = "Moves the selected material slot up, and updates the layer stack user interface"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bpy.ops.object.material_slot_move(direction='UP')
        material_layers.refresh_layer_stack()
        return {'FINISHED'}
    
class MATLAYER_OT_move_material_slot_down(Operator):
    bl_idname = "matlayer.move_material_slot_down"
    bl_label = "Move Material Slot Down"
    bl_description = "Moves the selected material slot down, and updates the layer stack user interface"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bpy.ops.object.material_slot_move(direction='DOWN')
        material_layers.refresh_layer_stack()
        return {'FINISHED'}