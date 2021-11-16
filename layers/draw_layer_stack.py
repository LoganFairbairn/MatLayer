import bpy
from ..import layer_functions

class COATER_UL_layer_list(bpy.types.UIList):
    '''Draws the layer stack.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False

        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            # Draw the layer hide icon.
            row = layout.row()
            if item.hidden == True:
                row.prop(item, "hidden", text="", emboss=False, icon='HIDE_ON')

            elif item.hidden == False:
                row.prop(item, "hidden", text="", emboss=False, icon='HIDE_OFF')

            # Draw the layer's type.
            row = layout.row(align=True)
            if item.layer_type == 'IMAGE_LAYER':
                row.operator("coater.select_layer_image", text="", emboss=False, icon='IMAGE_DATA')

            elif item.layer_type == 'COLOR_LAYER':
                row.label(text="", icon="COLOR")

            # Draw if the layer is masked.
            row = layout.row()
            if item.mask_node_name != "":
                layer_index = context.scene.coater_layer_stack.layer_index
                mask_node = layer_functions.get_node(context, 'MASK', layer_index)
                if mask_node != None:
                    if context.scene.tool_settings.image_paint.canvas == mask_node.image:
                        row.operator("coater.select_layer_mask", text="", emboss=True, depress=True, icon='MOD_MASK')

                    else:
                        row.operator("coater.select_layer_mask", text="", emboss=True, icon='MOD_MASK')

                else:
                    row.operator("coater.select_layer_mask", text="", emboss=True, icon='MOD_MASK')

            # Draw the layer's name.
            row.prop(item, "layer_name", text="", emboss=False)

