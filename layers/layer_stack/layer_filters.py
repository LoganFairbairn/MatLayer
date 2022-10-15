import bpy
from bpy.types import PropertyGroup
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


# TODO: Add delete filter operator here.