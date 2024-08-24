# This file contains operators for adding, editing and removing filters for material channels.

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, StringProperty
from ..core import debug_logging

def add_material_filter(filter_type, material_channel):
    '''Adds a filter of the specified type to the specified material channel'''

    # TODO: Stop users from adding more than one of the same filter type.

    # TODO: Add the filter node of the specified type to the node tree.

    debug_logging.log("Added {0} filter to {1}".format(filter_type, material_channel))

def delete_material_filter(filter_index):
    '''Deletes the material filter node with the specified index.'''
    debug_logging.log("Deleted filter at index {0}".format(filter_index))

class MATLAYER_OT_add_material_filter(Operator):
    bl_label = "Add Material Filter"
    bl_idname = "matlayer.add_material_filter"
    bl_description = "Adds a filter of the specified type to the specified material channel"
    bl_options = {'REGISTER', 'UNDO'}

    filter_type: StringProperty()
    material_channel: StringProperty()

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        add_material_filter(self.filter_type, self.material_channel)
        return {'FINISHED'}
    
class MATLAYER_OT_delete_material_filter(Operator):
    bl_label = "Delete Material Filter"
    bl_idname = "matlayer.delete_material_filter"
    bl_description = "Deletes the specified material filter"
    bl_options = {'REGISTER', 'UNDO'}

    filter_index: IntProperty()

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        delete_material_filter(self.filter_index)
        return {'FINISHED'}