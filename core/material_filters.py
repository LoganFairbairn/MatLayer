import bpy
from bpy.types import PropertyGroup, Operator, UIList
from bpy.props import BoolProperty, IntProperty, StringProperty, PointerProperty
from . import material_channels
from . import layer_nodes
from ..utilities import logging
from ..utilities import matlay_utils


# All MATERIAL filter nodes will use this name.
FILTER_NODE_NAME = 'FILTER'

# The maximum number of filters a single layer can use. Realistically users should never need more filters on a single layer than this.
MAX_LAYER_FILTER_COUNT = 5

#----------------------------- FILTER PROPERTY AUTO UPDATING FUNCTIONS -----------------------------#

def filter_material_channel_toggle(channel_toggle, material_channel_name, context):
    # Mute / unmute filter nodes for the selected layer and filter.
    selected_layer_stack_index = context.scene.matlay_layer_stack.layer_index
    selected_filter_index = context.scene.matlay_material_filter_stack.selected_filter_index
    filter_node = get_material_filter_node(material_channel_name, selected_layer_stack_index, selected_filter_index)
    layer_nodes.set_node_active(filter_node, channel_toggle)
    layer_nodes.relink_material_nodes(selected_layer_stack_index)
    layer_nodes.relink_mix_layer_nodes()
    matlay_utils.set_valid_material_shading_mode(context)

def update_filter_color_channel_toggle(self, context):
    filter_material_channel_toggle(self.color_channel_toggle, 'COLOR', context)

def update_filter_subsurface_channel_toggle(self, context):
    filter_material_channel_toggle(self.subsurface_channel_toggle, 'SUBSURFACE', context)

def update_filter_subsurface_color_channel_toggle(self, context):
    filter_material_channel_toggle(self.subsurface_color_channel_toggle, 'SUBSURFACE_COLOR', context)

def update_filter_metallic_channel_toggle(self, context):
    filter_material_channel_toggle(self.metallic_channel_toggle, 'METALLIC', context)

def update_filter_specular_channel_toggle(self, context):
    filter_material_channel_toggle(self.specular_channel_toggle, 'SPECULAR', context)

def update_filter_roughness_channel_toggle(self, context):
    filter_material_channel_toggle(self.roughness_channel_toggle, 'ROUGHNESS', context)

def updated_filter_emission_channel_toggle(self, context):
    filter_material_channel_toggle(self.emission_channel_toggle, 'EMISSION', context)

def updated_filter_normal_channel_toggle(self, context):
    filter_material_channel_toggle(self.normal_channel_toggle, 'NORMAL', context)

def update_filter_height_channel_toggle(self, context):
    filter_material_channel_toggle(self.height_channel_toggle, 'HEIGHT', context)

#----------------------------- CORE MATERIAL FILTER FUNCTIONS -----------------------------#

def validate_filter_selected_index():
    '''Validates that the selected material filter index is within a valid range. This should be used as a safety check to avoid running operators that require a valid index.'''

    material_filters = bpy.context.scene.matlay_material_filters
    selected_material_filter_index = bpy.context.scene.matlay_material_filter_stack.selected_filter_index

    if selected_material_filter_index > (len(material_filters) - 1) or selected_material_filter_index < 0:
        if len(material_filters) > 0:
            bpy.context.scene.matlay_material_filter_stack.selected_filter_index = 0
            return True
        else:
            bpy.context.scene.matlay_material_filter_stack.selected_filter_index = -1
            return False
    return True

def format_filter_node_name(material_layer_index, material_filter_index, get_edited=False):
    '''All nodes made with this add-on must have properly formated names, this function will return a properly formated name for a material filter node.'''
    name = "{0}_{1}_{2}".format(FILTER_NODE_NAME, str(material_layer_index), str(material_filter_index))
    if get_edited:
        name += '~'
    return  name

def get_material_filter_node(material_channel_name, material_layer_index, material_filter_index, get_edited=False):
    '''Returns the filter node for the given material layer index at the filter index by reading through existing nodes within the specified material channel'''
    material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
    if material_channel_node:
        node_name = format_filter_node_name(material_layer_index, material_filter_index, get_edited)
        return material_channel_node.node_tree.nodes.get(node_name)

def get_all_material_filter_nodes(material_channel_name, material_layer_index, get_edited=False):
    '''Returns ALL filter nodes in the given material layer material channel. If get edited is passed as true, all nodes part of the given material layer marked as being edited (signified by a tilda at the end of their name) will be returned.'''
    nodes = []
    material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
    if material_channel_node:
        for i in range(0, MAX_LAYER_FILTER_COUNT):
            filter_node_name = format_filter_node_name(material_layer_index, i, get_edited)
            node = material_channel_node.node_tree.nodes.get(filter_node_name)
            if node:
                nodes.append(node)
    return nodes

def get_filter_nodes_count(material_layer_index):
    '''Returns the total number of filter nodes in the given layer by reading the material nodes.'''
    number_of_filter_nodes = 0
    for i in range(0, MAX_LAYER_FILTER_COUNT):
        filter_node = get_material_filter_node('COLOR', material_layer_index, i)
        if filter_node:
            number_of_filter_nodes += 1
    return number_of_filter_nodes

def reindex_material_filter_nodes(change_made, changed_material_filter_index=0):
    '''Reindexes material filter nodes based off the provided change and index. Valid arguments include: 'ADDED', 'DELETED' '''
    
    # Do not reindex material filter nodes if there are no layers.
    number_of_material_layers = len(bpy.context.scene.matlay_layers)
    if number_of_material_layers <= 0:
        return

    # Do no reindex material filter nodes if there are no material filters.
    filters = bpy.context.scene.matlay_material_filters
    if len(filters) <= 0:
        return

    # Update layer stack indicies first.
    number_of_layers = len(filters)
    for i in range(0, number_of_layers):
        filters[i].stack_index = i

    selected_layer_index = bpy.context.scene.matlay_layer_stack.layer_index

    match change_made:
        case 'ADDED':
            for material_channel_name in material_channels.get_material_channel_list():
                material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)

                for i in range(len(filters), changed_material_filter_index + 1, -1):
                    index = i - 1
                    filter_node_name = filters[index].name + "_" + str(selected_layer_index) + "_" + str(index - 1)
                    filter_node = material_channel_node.node_tree.nodes.get(filter_node_name)

                    if filter_node:
                        filter_node.name = format_filter_node_name(selected_layer_index, index)
                        filter_node.label = filter_node.name
                        filters[index].stack_index = index

                # Remove the tilda from the newly added filter.
                new_filter_node_name = format_filter_node_name(selected_layer_index, changed_material_filter_index, True)
                new_filter_node = material_channel_node.node_tree.nodes.get(new_filter_node_name)
                if new_filter_node:
                    new_filter_node.name = new_filter_node_name.replace('~', '')
                    new_filter_node.label = new_filter_node.name
                    filters[changed_material_filter_index].stack_index = changed_material_filter_index

        case 'DELETED':
            for material_channel_name in material_channels.get_material_channel_list():
                material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
                for i in range(changed_material_filter_index + 1, len(filters), 1):
                    old_filter_node_name = format_filter_node_name(selected_layer_index, i)
                    filter_node = material_channel_node.node_tree.nodes.get(old_filter_node_name)

                    if filter_node:
                        filter_node.name = format_filter_node_name(selected_layer_index, i - 1)
                        filter_node.label = filter_node.name
                        filters[i].stack_index = i - 1

def relink_material_filter_nodes(material_layer_index):
    '''Relinks material filter nodes with other material filter nodes.'''
    number_of_material_layers = len(bpy.context.scene.matlay_layers)
    if number_of_material_layers <= 0:
        return
    
    for material_channel_name in material_channels.get_material_channel_list():
        material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
        filter_nodes = get_all_material_filter_nodes(material_channel_name, material_layer_index, get_edited=False)

        for i in range(0, len(filter_nodes)):
            filter_node = get_material_filter_node(material_channel_name, material_layer_index, i)
            
            # Unlink the filter node.
            node_links = material_channel_node.node_tree.links
            for l in node_links:
                if l.from_node.name == filter_node.name:
                    node_links.remove(l)

            # If the current material filter is disabled, skip connecting it.
            if layer_nodes.get_node_active(filter_node) == False:
                continue

            # Link to the next ACTIVE filter node in the layer stack if it exists.
            next_active_filter_index = i + 1
            next_active_filter_node = get_material_filter_node(material_channel_name, material_layer_index, next_active_filter_index)
            if next_active_filter_node:
                while layer_nodes.get_node_active(next_active_filter_node) == False:
                    next_active_filter_index += 1
                    next_active_filter_node = get_material_filter_node(material_channel_name, material_layer_index, next_active_filter_index)
                    if not next_active_filter_node:
                        break

            if next_active_filter_node:
                match next_active_filter_node.bl_static_type:
                    case 'INVERT':
                        material_channel_node.node_tree.links.new(filter_node.outputs[0], next_active_filter_node.inputs[1])
                    case 'VALTORGB':
                        material_channel_node.node_tree.links.new(filter_node.outputs[0], next_active_filter_node.inputs[0])
                    case 'HUE_SAT':
                        material_channel_node.node_tree.links.new(filter_node.outputs[0], next_active_filter_node.inputs[4])
                    case 'CURVE_RGB':
                        material_channel_node.node_tree.links.new(filter_node.outputs[0], next_active_filter_node.inputs[1])
                    case 'BRIGHTCONTRAST':
                        material_channel_node.node_tree.links.new(filter_node.outputs[0], next_active_filter_node.inputs[0])

def read_material_filter_nodes(context):
    '''Reads layer nodes to re-construct the filter layer stack.'''
    filters = context.scene.matlay_material_filters
    filter_stack = context.scene.matlay_material_filter_stack
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    selected_material_channel = context.scene.matlay_layer_stack.selected_material_channel

    # When reading from the material node tree, we don't want material filter properties to auto-update as doing so will cause errors.
    context.scene.matlay_material_filter_stack.auto_update_filter_properties = False

    # Cache the selected filter index, we'll reset the selected filter index to the closest index after refreshing.
    previously_selected_filter_index = filter_stack.selected_filter_index

    # Clear all layer filters.
    filters.clear()

    # Read the material nodes and re-add layer filters to the layer stack.
    layer_filter_nodes = get_all_material_filter_nodes(selected_material_channel, selected_layer_index)
    for x in range(0, len(layer_filter_nodes)):
        filters.add()
        node_name = layer_filter_nodes[x].name.split("_")
        filters[x].name = node_name[0]
        filters[x].stack_index = x

    # Reset the selected filter.
    if len(filters) > 0 and previously_selected_filter_index <= len(filters) - 1 and previously_selected_filter_index >= 0:
        filter_stack.selected_filter_index = previously_selected_filter_index
    else:
        filter_stack.selected_filter_index = 0

    # Read inactive material channels for the selected fitler index.
    for i in range(0, len(layer_filter_nodes)):
        for material_channel_name in material_channels.get_material_channel_list():
            filter_node = get_material_filter_node(material_channel_name, selected_layer_index, x)
            filter_node_active = layer_nodes.get_node_active(filter_node)
            setattr(filters[i].material_channel_toggles, material_channel_name.lower() + "_channel_toggle", filter_node_active)

    # Allow auto updating for filter properties again. 
    context.scene.matlay_material_filter_stack.update_filter_properties = True

def add_material_filter_slot():
    '''Adds a new material filter slot.'''
    filters = bpy.context.scene.matlay_material_filters
    filter_stack = bpy.context.scene.matlay_material_filter_stack
    selected_layer_filter_index = bpy.context.scene.matlay_material_filter_stack.selected_filter_index

    filters.add()

    if selected_layer_filter_index < 0:
        move_index = len(filters) - 1
        move_to_index = 0
        filters.move(move_index, move_to_index)
        filter_stack.selected_filter_index = move_to_index
        selected_layer_filter_index = len(filters) - 1
            
    else:
        move_index = len(filters) - 1
        move_to_index = max(0, min(selected_layer_filter_index + 1, len(filters) - 1))
        filters.move(move_index, move_to_index)
        filter_stack.selected_filter_index = move_to_index
        selected_layer_filter_index = max(0, min(selected_layer_filter_index + 1, len(filters) - 1))

    return bpy.context.scene.matlay_material_filter_stack.selected_filter_index

def add_material_filter(filter_type, context):
    '''Creates a new material layer filter slot and node.'''
    validate_filter_selected_index()

    filters = context.scene.matlay_material_filters
    selected_material_layer_index = context.scene.matlay_layer_stack.layer_index

    # Stop users from adding too many material filters.
    if len(filters) >= MAX_LAYER_FILTER_COUNT:
        logging.popup_message_box("You can't have more than {0} filters on a single layer. This is a safeguard to stop users from adding an unnecessary amount of filters, which will impact performance.".format(MAX_LAYER_FILTER_COUNT), 'User Error', 'ERROR')
        return
    
    # Add a new layer filter slot, name and select it.
    new_material_filter_slot_index = add_material_filter_slot()
    new_filter_index = context.scene.matlay_material_filter_stack.selected_filter_index

    # Add a new material filter node to all material channels and parent it to the layers frame.
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
        if material_channel_node:
                filter_node = material_channel_node.node_tree.nodes.new(filter_type)
                filter_node.name = format_filter_node_name(selected_material_layer_index, new_filter_index) + "~"
                filter_node.label = filter_node.name

                frame = layer_nodes.get_layer_frame(material_channel_name, selected_material_layer_index, context)
                if frame:
                    filter_node.parent = frame

    # Re-organize and re-link material layer nodes so mix nodes will automatically connect with filter nodes.
    reindex_material_filter_nodes('ADDED', new_material_filter_slot_index)
    layer_nodes.organize_all_layer_nodes()
    layer_nodes.relink_material_nodes(selected_material_layer_index)
    layer_nodes.relink_mix_layer_nodes()

    # Toggle the material filter off for all material channels excluding color, because users will generally want the material filter to only apply for one material channel anyways. This makes it slightly faster for users to toggle on the material channel they want the material filter to apply to.
    for material_channel_name in material_channel_list:
        if material_channel_name != 'COLOR':
            setattr(filters[new_filter_index].material_channel_toggles, material_channel_name.lower() + "_channel_toggle", False)
            filter_material_channel_toggle(False, material_channel_name, context)

    matlay_utils.update_total_node_and_link_count()

def move_filter_layer(direction, context):
    validate_filter_selected_index()
    
    filters = context.scene.matlay_material_filters
    filter_stack = context.scene.matlay_material_filter_stack
    selected_filter_index = context.scene.matlay_material_filter_stack.selected_filter_index
    selected_material_layer_index = context.scene.matlay_layer_stack.layer_index
    material_channel_list = material_channels.get_material_channel_list()

    filter_stack.auto_update_filter_properties = False

    # Don't move the filter out of range.
    if direction == 'UP' and selected_filter_index + 1 > len(filters) - 1:
        return
    if direction == 'DOWN' and selected_filter_index - 1 < 0:
        return
    
    # Get the layer index over or under the selected layer, depending on the direction the layer is being moved.
    if direction == 'UP':
        moving_to_index = max(min(selected_filter_index + 1, len(filters) - 1), 0)
    else:
        moving_to_index = max(min(selected_filter_index - 1, len(filters) - 1), 0)

    # Add a tilda to the end of all the filter nodes to signify they are being edited (and to avoid naming conflicts).
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        node = get_material_filter_node(material_channel_name, selected_material_layer_index, selected_filter_index, False)
        if node:
            node.name = node.name + "~"
            node.label = node.name

    # Update the filter node names for the layer below or above the selected index.
    for material_channel_name in material_channel_list:
        node = get_material_filter_node(material_channel_name, selected_material_layer_index, moving_to_index, False)
        if node:
            node.name = format_filter_node_name(selected_material_layer_index, selected_filter_index)
            node.label = node.name

    # Remove the tilda from the end of the filter node names that were edited and re-index them.
    for material_channel_name in material_channel_list:
        node = get_material_filter_node(material_channel_name, selected_material_layer_index, selected_filter_index, True)
        if node:
            node.name = format_filter_node_name(selected_material_layer_index, moving_to_index)
            node.label = node.name

    # Move the selected filter on the ui stack.
    if direction == 'UP':
        index_to_move_to = max(min(selected_filter_index + 1, len(filters) - 1), 0)
    else:
        index_to_move_to = max(min(selected_filter_index - 1, len(filters) - 1), 0)
    filters.move(selected_filter_index, index_to_move_to)
    context.scene.matlay_material_filter_stack.selected_filter_index = index_to_move_to

    # Re-link and organize filter nodes.
    reindex_material_filter_nodes('MOVED', selected_filter_index)
    layer_nodes.organize_all_layer_nodes()
    layer_nodes.relink_material_nodes(selected_material_layer_index)
    layer_nodes.relink_mix_layer_nodes()

    filter_stack.auto_update_filter_properties = True

#----------------------------- OPERATORS -----------------------------#

class FiltersMaterialChannelToggles(PropertyGroup):
    '''Boolean toggles for each material channel.'''
    color_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the effect of the selected material filter for the color material channel", update=update_filter_color_channel_toggle)
    subsurface_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the effect of the selected material filter for the subsurface material channel", update=update_filter_subsurface_channel_toggle)
    subsurface_color_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the effect of the selected material filter for the subsurface color material channel", update=update_filter_subsurface_color_channel_toggle)
    metallic_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the effect of the selected material filter for the metallic material channel", update=update_filter_metallic_channel_toggle)
    specular_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the effect of the selected material filter for the specular material channel", update=update_filter_specular_channel_toggle)
    roughness_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the effect of the selected material filter for the roughness material channel", update=update_filter_roughness_channel_toggle)
    emission_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the effect of the selected material filter for the emission material channel", update=updated_filter_emission_channel_toggle)
    normal_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the effect of the selected material filter for the normal material channel", update=updated_filter_normal_channel_toggle)
    height_channel_toggle: BoolProperty(default=True, description="Click to toggle on / off the effect of the selected material filter for the height material channel", update=update_filter_height_channel_toggle)

class MATLAY_material_filters(PropertyGroup):
    stack_index: IntProperty(name="Stack Index", description = "The (array) stack index for this filter used to define the order in which filters should be applied to the material", default=-999)
    material_channel_toggles: PointerProperty(type=FiltersMaterialChannelToggles, name="Material Channel Toggles")

class MATLAY_material_filter_stack(PropertyGroup):
    '''Properties for layer filters.'''
    selected_filter_index: IntProperty(default=-1)
    auto_update_filter_properties: BoolProperty(name="Update Filter Properties", description="When true, changing filter properties will trigger automatic updates.", default=True)

class MATLAY_UL_layer_filter_stack(UIList):
    '''Draws the material filter stack.'''
    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            filter_node = get_material_filter_node('COLOR', bpy.context.scene.matlay_layer_stack.layer_index, item.stack_index, False)
            if filter_node:
                filter_name = ""
                match filter_node.bl_static_type:
                    case 'INVERT':
                        filter_name = "Invert"
                    case 'VALTORGB':
                        filter_name = "Value to RGB"
                    case 'HUE_SAT':
                        filter_name = "Hue Saturation Value"
                    case 'CURVE_RGB':
                        filter_name = "Curve RGB"
                    case 'BRIGHTCONTRAST':
                        filter_name = "Brightness & Contrast"
                row.label(text=str(item.stack_index + 1) + ". " + filter_name)

# TODO: These should be "material" filters instead of layer filters for accuracy.
class MATLAY_OT_add_layer_filter_invert(Operator):
    '''Adds an invert filter to the selected layer.'''
    bl_idname = "matlay.add_layer_filter_invert"
    bl_label = "Add Invert"
    bl_description = "Adds an invert filter to the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        matlay_utils.set_valid_mode()
        add_material_filter('ShaderNodeInvert', context)
        matlay_utils.set_valid_material_shading_mode(context)
        return{'FINISHED'}

class MATLAY_OT_add_layer_filter_val_to_rgb(Operator):
    '''Adds level adjustment to the selected layer.'''
    bl_idname = "matlay.add_layer_filter_val_to_rgb"
    bl_label = "Add Value to RGB"
    bl_description = "Adds a level adjustment (color ramp) to the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        matlay_utils.set_valid_mode()
        add_material_filter('ShaderNodeValToRGB', context)
        matlay_utils.set_valid_material_shading_mode(context)
        return{'FINISHED'}

class MATLAY_OT_add_layer_filter_hsv(Operator):
    '''Adds a hue, saturation, value adjustment to the selected layer.'''
    bl_idname = "matlay.add_layer_filter_hsv"
    bl_label = "Add HSV"
    bl_description = "Adds a hue, saturation, value adjustment to the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        matlay_utils.set_valid_mode()
        add_material_filter('ShaderNodeHueSaturation', context)
        matlay_utils.set_valid_material_shading_mode(context)
        return{'FINISHED'}

class MATLAY_OT_add_layer_filter_rgb_curves(Operator):
    '''Adds a RGB curves adjustment to the selected layer.'''
    bl_idname = "matlay.add_layer_filter_rgb_curves"
    bl_label = "Add RGB Curves"
    bl_description = "Adds a RGB curves adjustment to the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        matlay_utils.set_valid_mode()
        add_material_filter('ShaderNodeRGBCurve', context)
        matlay_utils.set_valid_material_shading_mode(context)
        return{'FINISHED'}

class MATLAY_OT_add_layer_filter_bright_contrast(Operator):
    '''Adds a brightness and contrast filter to the selected layer.'''
    bl_idname = "matlay.add_layer_filter_bright_contrast"
    bl_label = "Add Brightness / Contrast"
    bl_description = "Adds a brightness and contrast filter to the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        matlay_utils.set_valid_mode()
        add_material_filter('ShaderNodeBrightContrast', context)
        matlay_utils.set_valid_material_shading_mode(context)
        return{'FINISHED'}

class MATLAY_OT_add_layer_filter_menu(Operator):
    '''Opens a menu of layer filters that can be added to the selected layer.'''
    bl_label = "Layer Filter Menu"
    bl_idname = "matlay.add_layer_filter_menu"
    bl_description = "Opens a menu of layer filters that can be added to the selected layer"

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

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
        col.operator("matlay.add_layer_filter_invert", text="Invert")
        col.operator("matlay.add_layer_filter_val_to_rgb", text="Value to RGB")
        col.operator("matlay.add_layer_filter_hsv", text="HSV")
        col.operator("matlay.add_layer_filter_rgb_curves", text="RGB Curves")
        col.operator("matlay.add_layer_filter_bright_contrast", text="Brightness / Contrast")

class MATLAY_OT_delete_layer_filter(Operator):
    '''Deletes the selected layer filter.'''
    bl_idname = "matlay.delete_layer_filter"
    bl_label = "Delete Layer Filter"
    bl_description = "Deletes the selected layer filter"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        validate_filter_selected_index()

        filters = context.scene.matlay_material_filters
        selected_material_layer_index = context.scene.matlay_layer_stack.layer_index
        selected_filter_index = context.scene.matlay_material_filter_stack.selected_filter_index

        matlay_utils.set_valid_mode()

        # Delete the material filter nodes.
        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
            filter_node = get_material_filter_node(material_channel_name, selected_material_layer_index, selected_filter_index)
            if filter_node:
                material_channel_node.node_tree.nodes.remove(filter_node)

        # Re-index material filter nodes.
        number_of_filter_nodes = len(get_all_material_filter_nodes("COLOR", selected_material_layer_index))
        if number_of_filter_nodes > 0:
            reindex_material_filter_nodes('DELETED', selected_filter_index)

        # Remove the filter stack slot.
        filters.remove(selected_filter_index)
        
        # Reset the selected filter index.
        context.scene.matlay_material_filter_stack.selected_filter_index = max(min(selected_filter_index - 1, len(filters) - 1), 0)

        # Re-link and re-organize layers.
        layer_nodes.organize_all_layer_nodes()
        layer_nodes.relink_material_nodes(selected_material_layer_index)
        layer_nodes.relink_mix_layer_nodes()
        
        matlay_utils.set_valid_material_shading_mode(context)
        matlay_utils.update_total_node_and_link_count()
        return{'FINISHED'}

class MATLAY_OT_move_layer_filter_up(Operator):
    '''Moves the filter up on the filter layer stack.'''
    bl_idname = "matlay.move_filter_up"
    bl_label = "Move Filter Up"
    bl_description = "Moves the selected layer filter up on the layer stack"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        matlay_utils.set_valid_mode()
        move_filter_layer("UP", context)
        matlay_utils.set_valid_material_shading_mode(context)
        return{'FINISHED'}

class MATLAY_OT_move_layer_filter_down(Operator):
    '''Moves the filter up on the filter layer stack.'''
    bl_idname = "matlay.move_filter_down"
    bl_label = "Move Filter Down"
    bl_description = "Moves the selected layer filter down on the layer stack"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        matlay_utils.set_valid_mode()
        move_filter_layer("DOWN", context)
        matlay_utils.set_valid_material_shading_mode(context)
        return{'FINISHED'}
