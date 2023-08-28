import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import BoolProperty, IntProperty, EnumProperty, StringProperty, PointerProperty

def add_material_filter(type):
    '''Adds a material fitler of the specified type to the selected material layer.'''
    print("Placeholder...")

class MATLAYER_material_filter_stack(PropertyGroup):
    '''Properties for the layer stack.'''
    selected_index: IntProperty(default=-1, description="Selected material filter index")

class MATLAYER_material_filters(PropertyGroup):
    hidden: BoolProperty(name="Hidden", description="Show if the layer is hidden")

class MATLAYER_UL_material_filter_list(bpy.types.UIList):
    '''Draws the material filter stack.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)

class MATLAYER_OT_add_material_filter_hsv(Operator):
    bl_label = "Add Material Filter HSV"
    bl_idname = "matlayer.add_material_filter_hsv"
    bl_description = "Adds a hue / saturation / value filter to the selected material layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}
    
class MATLAYER_OT_add_material_filter_color_ramp(Operator):
    bl_label = "Add Material Filter Color Ramp"
    bl_idname = "matlayer.add_material_filter_color_ramp"
    bl_description = "Adds a color ramp filter to the selected material layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}
    
class MATLAYER_OT_add_material_filter_invert(Operator):
    bl_label = "Add Material Filter Invert"
    bl_idname = "matlayer.add_material_filter_invert"
    bl_description = "Adds an invert filter to the selected material layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}
    
class MATLAYER_OT_move_material_filter_up(Operator):
    bl_label = "Move Material Filter Up"
    bl_idname = "matlayer.move_material_filter_up"
    bl_description = "Moves the selected material filter up on the layer stack"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

class MATLAYER_OT_move_material_filter_down(Operator):
    bl_label = "Move Material Filter Down"
    bl_idname = "matlayer.move_material_filter_down"
    bl_description = "Moves the selected material filter down on the layer stack"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

class MATLAYER_OT_duplicate_material_filter(Operator):
    bl_label = "Duplicate Material Filter"
    bl_idname = "matlayer.duplicate_material_filter"
    bl_description = "Duplicates the selected material filter"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

class MATLAYER_OT_delete_material_filter(Operator):
    bl_label = "Delete Material Filter"
    bl_idname = "matlayer.delete_material_filter"
    bl_description = "Delete the selected material filter"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}