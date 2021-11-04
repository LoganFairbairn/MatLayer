import bpy

class COATER_UL_layer_list(bpy.types.UIList):
    '''Draws the layer stack.'''

    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False

        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

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
                row.prop(layers[layer_index], "layer_type", icon="IMAGE_DATA", icon_only=True, emboss=False, index=0)

            elif item.layer_type == 'COLOR_LAYER':
                row.prop(layers[layer_index], "layer_type", icon="COLOR", icon_only=True, emboss=False, index=1)

            # Draw the layer's name.
            row.prop(item, "layer_name", text="", emboss=False, icon_value=icon)

            # TODO: Draw if the layer is masked.