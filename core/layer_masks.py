import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import BoolProperty, IntProperty, EnumProperty, StringProperty, PointerProperty

def add_layer_mask(type):
    '''Adds a mask of the specified type to the selected material layer.'''
    print("Placeholder...")

class MATLAYER_mask_stack(PropertyGroup):
    '''Properties for the layer stack.'''
    selected_index: IntProperty(default=-1, description="Selected material filter index")

class MATLAYER_masks(PropertyGroup):
    hidden: BoolProperty(name="Hidden", description="Show if the layer is hidden")

class MATLAYER_UL_mask_list(bpy.types.UIList):
    '''Draws the mask stack.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)

class MATLAYER_OT_move_layer_mask_up(Operator):
    bl_label = "Move Layer Mask Up"
    bl_idname = "matlayer.move_layer_mask_up"
    bl_description = "Moves the selected layer mask up on the mask stack"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

class MATLAYER_OT_move_layer_mask_down(Operator):
    bl_label = "Move Layer Mask Down"
    bl_idname = "matlayer.move_layer_mask_down"
    bl_description = "Moves the selected layer mask down on the mask stack"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

class MATLAYER_OT_duplicate_layer_mask(Operator):
    bl_label = "Duplicate Layer Mask"
    bl_idname = "matlayer.duplicate_layer_mask"
    bl_description = "Duplicates the selected mask"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

class MATLAYER_OT_delete_layer_mask(Operator):
    bl_label = "Delete Layer Mask"
    bl_idname = "matlayer.delete_layer_mask"
    bl_description = "Deletes the selected mask from the selected material layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

class MATLAYER_OT_add_empty_layer_mask(Operator):
    bl_label = "Add Empty Layer Mask"
    bl_idname = "matlayer.add_empty_layer_mask"
    bl_description = "Adds an default image based node group mask to the selected material layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}
    
class MATLAYER_OT_add_black_layer_mask(Operator):
    bl_label = "Add Black Layer Mask"
    bl_idname = "matlayer.add_black_layer_mask"
    bl_description = "Adds an default image based node group mask with to the selected material layer and fills the image slot with a black image"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}
    
class MATLAYER_OT_add_white_layer_mask(Operator):
    bl_label = "Add White Layer Mask"
    bl_idname = "matlayer.add_white_layer_mask"
    bl_description = "Adds an default image based node group mask with to the selected material layer and fills the image slot with a white image"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}
