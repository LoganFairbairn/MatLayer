import bpy
from bpy.types import PropertyGroup, Operator
from ..nodes import layer_nodes
from ...texture_handling import image_file_handling
from ..nodes import material_channel_nodes

class COATER_layer_filter_stack(PropertyGroup):
    '''Properties for layer filters.'''
    selected_filter_index: bpy.props.IntProperty(default=-1)

class COATER_UL_layer_filter_stack(bpy.types.UIList):
    '''Draws the mask stack for the selected layer.'''
    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text="Filter")

class COATER_layer_filters(PropertyGroup):
    name: bpy.props.StringProperty(name="", description="The name of the layer filter", default="Layer Filter Naming Error")


class COATER_OT_add_layer_filter_menu(Operator):
    '''Opens a menu of layer filters that can be added to the selected layer.'''
    bl_label = ""
    bl_idname = "coater.add_layer_filter_menu"
    bl_description = "Opens a menu of layer filters that can be added to the selected layer"

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

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
        col.operator("coater.add_layer_filter_invert")
        col.operator("coater.add_layer_filter_levels")
        col.operator("coater.add_layer_filter_hsv")
        col.operator("coater.add_layer_filter_rgb_curves")


class COATER_OT_add_layer_filter_invert(Operator):
    '''Adds an invert filter to the selected layer.'''
    bl_idname = "coater.add_layer_filter_invert"
    bl_label = "Add Invert Adjustment"
    bl_description = "Adds an invert filter to the selected layer"

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
            return{'FINISHED'}

class COATER_OT_add_layer_filter_levels(Operator):
    '''Adds level adjustment to the selected layer.'''
    bl_idname = "coater.add_layer_filter_levels"
    bl_label = "Add Levels Adjustment"
    bl_description = "Adds a level adjustment to the selected layer"

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
            return{'FINISHED'}

class COATER_OT_add_layer_filter_hsv(Operator):
    '''Adds a hue, saturation, value adjustment to the selected layer.'''
    bl_idname = "coater.add_layer_filter_hsv"
    bl_label = "Add HSV Adjustment"
    bl_description = "Adds a HSV adjustment to the selected layer"

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
            return{'FINISHED'}

class COATER_OT_add_layer_filter_rgb_curves(Operator):
    '''Adds level adjustment to the selected layer.'''
    bl_idname = "coater.add_layer_filter_rgb_curves"
    bl_label = "Add RGB Curves Adjustment"
    bl_description = "Adds a RGB curves adjustment to the selected layer"

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
            return{'FINISHED'}

class COATER_OT_delete_layer_filter(Operator):
    '''Deletes the selected layer filter.'''
    bl_idname = "coater.add_layer_filter_rgb_curves"
    bl_label = "Delete Layer Filter"
    bl_description = "Deletes the selected layer filter."

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
            return{'FINISHED'}