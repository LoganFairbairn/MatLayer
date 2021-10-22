import bpy

class COATER_UL_layer_list(bpy.types.UIList):
    '''Draws the layer stack.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index
        self.use_filter_show = False

        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            # Draw the layer hide icon.
            row = layout.row()
            if item.layer_hidden == True:
                row.prop(item, "layer_hidden", text="", emboss=False, icon='HIDE_ON')

            elif item.layer_hidden == False:
                row.prop(item, "layer_hidden", text="", emboss=False, icon='HIDE_OFF')

            # Draw the layer's type.
            row = layout.row(align=True)
            if item.layer_type == 'IMAGE_LAYER':
                row.operator("coater.edit_layer_properties", emboss=False, icon="IMAGE_DATA")

            elif item.layer_type == 'COLOR_LAYER':
                row.operator("coater.edit_layer_properties", emboss=False, icon="COLOR")

            # Draw the layer's name.
            row.prop(item, "layer_name", text="", emboss=False, icon_value=icon)

            # Draw the layer's blending mode and opacity.
            row = layout.row()
            split = layout.split()
            col = split.column(align=True)
            col.prop(item, "blend_mode")
            col.prop(item, "layer_opacity", icon_only=True)
            col.scale_y = 0.5
            col.ui_units_x = 8