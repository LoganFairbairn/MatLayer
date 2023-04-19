import bpy
from bpy.types import PropertyGroup, Operator, UIList
from bpy.props import BoolProperty, IntProperty, StringProperty, PointerProperty
from . import material_channels
from . import layer_nodes
from ..utilities import info_messages
from ..utilities import matlay_utils


# All MATERIAL filter nodes will use this name.
FILTER_NODE_NAME = 'FILTER'

# A list of filter node types available in this add-on.
FILTER_NODE_TYPES = ("INVERT", "VALTORGB", "HUE_SAT", "CURVE_RGB")

# The maximum number of filters a single layer can use. Realistically users should never need more filters on a single layer than this.
MAX_LAYER_FILTER_COUNT = 5

#----------------------------- FILTER PROPERTY AUTO UPDATING FUNCTIONS -----------------------------#

def filter_material_channel_toggle(channel_toggle, material_channel_name, context):
    # Mute / unmute filter nodes for the selected layer and filter.
    selected_layer_stack_index = context.scene.matlay_layer_stack.layer_index
    selected_filter_index = context.scene.matlay_material_filter_stack.selected_filter_index
    filter_node = get_material_filter_node(material_channel_name, selected_layer_stack_index, selected_filter_index)

    # Unmute
    if channel_toggle:
        filter_node.mute = False

    # Mute
    else:
        filter_node.mute = True
    
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
            filter_node_name = format_filter_node_name(material_layer_index, i)
            if get_edited:
                filter_node_name += '~'
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

def update_material_filter_node_indicies(material_channel_name):
    '''Renames all filter nodes with correct indicies by checking the node tree for newly added, edited (signified by a tilda at the end of their name), or deleted filter nodes'''
    material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
    selected_layer_index = bpy.context.scene.matlay_layer_stack.layer_index
    filters = bpy.context.scene.matlay_material_filters

    changed_filter_index = -1
    filter_added = False
    filter_deleted = False

    # 1. Update layer stack indicies first.
    number_of_layers = len(filters)
    for i in range(0, number_of_layers):
        filters[i].stack_index = i

    # 2. Check for a newly added filter (signified by a tilda at the end of the node's name).
    for i in range(0, len(filters)):
        temp_filter_node_name = format_filter_node_name(selected_layer_index, i) + "~"
        temp_filter_node = material_channel_node.node_tree.nodes.get(temp_filter_node_name)
        if temp_filter_node:
            filter_added = True
            changed_filter_index = i
            break

    # 3. Check for a deleted filter.
    if not filter_added:
        for i in range(0, len(filters)):
            temp_filter_node_name = format_filter_node_name(selected_layer_index, i)
            temp_filter_node = material_channel_node.node_tree.nodes.get(temp_filter_node_name)
            if not temp_filter_node:
                filter_deleted = True
                changed_filter_index = i
                break

    # 4. Rename filter nodes above the newly added material filter on the filter stack if any exist (in reverse order to avoid naming conflicts).
    if filter_added:
        for i in range(len(filters), changed_filter_index + 1, -1):
            index = i - 1
            filter_node_name = filters[index].name + "_" + str(selected_layer_index) + "_" + str(index - 1)
            filter_node = material_channel_node.node_tree.nodes.get(filter_node_name)

            if filter_node:
                filter_node.name = format_filter_node_name(selected_layer_index, index)
                filter_node.label = filter_node.name
                filters[index].stack_index = index

        # Remove the tilda from the newly added filter.
        new_filter_node_name = format_filter_node_name(selected_layer_index, changed_filter_index) + "~"
        new_filter_node = material_channel_node.node_tree.nodes.get(new_filter_node_name)
        if new_filter_node:
            new_filter_node.name = new_filter_node_name.replace('~', '')
            new_filter_node.label = new_filter_node.name
            filters[changed_filter_index].stack_index = changed_filter_index

    # 5. Rename filter layer nodes above the deleted filter layer if any exist.
    if filter_deleted and len(filters) > 0:
        for i in range(changed_filter_index + 1, len(filters), 1):
            old_filter_node_name = format_filter_node_name(selected_layer_index, i)
            filter_node = material_channel_node.node_tree.nodes.get(old_filter_node_name)

            if filter_node:
                filter_node.name = format_filter_node_name(selected_layer_index, i - 1)
                filter_node.label = filter_node.name
                filters[i].stack_index = i - 1

def relink_material_filter_nodes(material_channel_name):
    '''Re-links all material filter nodes in the given material channel.'''
    selected_material_layer_index = bpy.context.scene.matlay_layer_stack.layer_index
    filter_nodes = get_all_material_filter_nodes(material_channel_name, selected_material_layer_index, get_edited=False)
    material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)

    for i in range(0, len(filter_nodes)):
        filter_node = filter_nodes[i]

        next_filter_node = None
        if len(filter_nodes) - 1 > i:

            # Unlink all mask filter nodes.
            node_links = material_channel_node.node_tree.links
            for l in node_links:
                if l.from_node.name == filter_node.name:
                    node_links.remove(l)

            # Link to the next filter node in the layer stack if it exists.
            next_filter_node = filter_nodes[i + 1]
            if next_filter_node:
                match next_filter_node.bl_static_type:
                    case 'INVERT':
                        material_channel_node.node_tree.links.new(filter_node.outputs[0], next_filter_node.inputs[1])
                    case 'VALTORGB':
                        material_channel_node.node_tree.links.new(filter_node.outputs[0], next_filter_node.inputs[0])
                    case 'HUE_SAT':
                        material_channel_node.node_tree.links.new(filter_node.outputs[0], next_filter_node.inputs[4])
                    case 'CURVE_RGB':
                        material_channel_node.node_tree.links.new(filter_node.outputs[0], next_filter_node.inputs[1])
    
    # If there are no filter nodes, re-connect the color texture to the mix layer node.
    if len(filter_nodes) <= 0:
        layer_texture_node = layer_nodes.get_layer_node('TEXTURE', material_channel_name, selected_material_layer_index, bpy.context, False)
        layer_mix_node = layer_nodes.get_layer_node('MIXLAYER', material_channel_name, selected_material_layer_index, bpy.context, False)
        if layer_texture_node:
            material_channel_node.node_tree.links.new(layer_texture_node.outputs[0], layer_mix_node.inputs[2])

# TODO: Remove this wrapper function, use relink / reindex individually.
def update_material_filter_nodes(context):
    '''Updates the index stored in filter node names, and re-links material filters. This should generally called after adding or removing filter nodes.'''
    # If there are no material layers there shouldn't be any material filters, don't update the material filter nodes.
    number_of_material_layers = len(context.scene.matlay_layers)
    if number_of_material_layers > 0:
        material_channel_names = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_names:
            update_material_filter_node_indicies(material_channel_name)
            relink_material_filter_nodes(material_channel_name)

def refresh_material_filter_stack(context):
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
    if len(filters) > 0 and previously_selected_filter_index < len(filters) - 1 and previously_selected_filter_index >= 0:
        filter_stack.selected_filter_index = previously_selected_filter_index
    else:
        filter_stack.selected_filter_index = 0

    # Read muted material channels for the selected fitler index.
    for material_channel_name in material_channels.get_material_channel_list():
        for i in range(0, len(layer_filter_nodes)):
            filter_node = get_material_filter_node(material_channel_name, selected_layer_index, x)
            if filter_node.mute:
                setattr(filters[i].material_channel_toggles, material_channel_name.lower() + "_channel_toggle", False)
            else:
                setattr(filters[i].material_channel_toggles, material_channel_name.lower() + "_channel_toggle", True)

    # Allow auto updating for filter properties again. 
    context.scene.matlay_material_filter_stack.update_filter_properties = True

def add_material_layer_filter(filter_type, context):
    '''Creates a new material layer filter slot and node.'''
    filters = context.scene.matlay_material_filters
    filter_stack = context.scene.matlay_material_filter_stack
    selected_layer_filter_index = context.scene.matlay_material_filter_stack.selected_filter_index
    selected_layer_index = context.scene.matlay_layer_stack.layer_index

    # Stop users from adding too many material filters.
    if len(filters) >= MAX_LAYER_FILTER_COUNT:
        info_messages.popup_message_box("You can't have more than {0} filters on a single layer. This is a safeguard to stop users from adding an unnecessary amount of filters, which will impact performance.".format(MAX_LAYER_FILTER_COUNT), 'User Error', 'ERROR')
        return
    
    # Add a new layer filter slot, name and select it.
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

    new_filter_index = 0
    if len(filters) == 0:
        new_filter_index = 0
    else:
        new_filter_index = selected_layer_filter_index

    # Add a shader node for the layer filter (in all material channels).
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
        if material_channel_node:
                
                # Create new filter node, with tilda to indicate it's a newly added node.
                filter_node = material_channel_node.node_tree.nodes.new(filter_type)
                filter_node.name = format_filter_node_name(selected_layer_index, new_filter_index) + "~"
                filter_node.label = filter_node.name

                # Add the new node to the layer frame.
                frame = layer_nodes.get_layer_frame(material_channel_name, selected_layer_index, context)
                if frame:
                    filter_node.parent = frame

    # Re-organize and re-link material layer nodes so mix nodes will automatically connect with filter nodes.
    layer_nodes.update_layer_nodes(context)

    # Toggle the material filter off for all material channels excluding color, because users will generally want the material filter to only apply for one material channel anyways. This makes it slightly faster for users to toggle on the material channel they want the material filter to apply to.
    for material_channel_name in material_channel_list:
        if material_channel_name != 'COLOR':
            setattr(filters[new_filter_index].material_channel_toggles, material_channel_name.lower() + "_channel_toggle", False)
            filter_material_channel_toggle(False, material_channel_name, context)

def move_filter_layer(direction, context):
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

    # 1. Add a tilda to the end of all the filter nodes to signify they are being edited (and to avoid naming conflicts).
    material_channel_list = material_channels.get_material_channel_list()
    for material_channel_name in material_channel_list:
        node = get_material_filter_node(material_channel_name, selected_material_layer_index, selected_filter_index, False)
        if node:
            node.name = node.name + "~"
            node.label = node.name

    # 2. Update the filter node names for the layer below or above the selected index.
    for material_channel_name in material_channel_list:
        node = get_material_filter_node(material_channel_name, selected_material_layer_index, moving_to_index, False)
        if node:
            node.name = format_filter_node_name(selected_material_layer_index, selected_filter_index)
            node.label = node.name

    # 3. Remove the tilda from the end of the filter node names that were edited and re-index them.
    for material_channel_name in material_channel_list:
        node = get_material_filter_node(material_channel_name, selected_material_layer_index, selected_filter_index, True)
        if node:
            node.name = format_filter_node_name(selected_material_layer_index, moving_to_index)
            node.label = node.name

    # 4. Move the selected filter on the ui stack.
    if direction == 'UP':
        index_to_move_to = max(min(selected_filter_index + 1, len(filters) - 1), 0)
    else:
        index_to_move_to = max(min(selected_filter_index - 1, len(filters) - 1), 0)
    filters.move(selected_filter_index, index_to_move_to)
    context.scene.matlay_material_filter_stack.selected_filter_index = index_to_move_to

    # 5. Re-link and organize filter nodes.
    layer_nodes.update_layer_nodes(context)

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
                node_info = filter_node.name.split('_')
                row.label(text=str(item.stack_index + 1) + ". " + node_info[0])

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
        add_material_layer_filter('ShaderNodeInvert', context)
        matlay_utils.set_valid_material_shading_mode(context)
        return{'FINISHED'}

class MATLAY_OT_add_layer_filter_levels(Operator):
    '''Adds level adjustment to the selected layer.'''
    bl_idname = "matlay.add_layer_filter_levels"
    bl_label = "Add Levels"
    bl_description = "Adds a level adjustment (color ramp) to the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        matlay_utils.set_valid_mode()
        add_material_layer_filter('ShaderNodeValToRGB', context)
        matlay_utils.set_valid_material_shading_mode(context)
        return{'FINISHED'}

class MATLAY_OT_add_layer_filter_hsv(Operator):
    '''Adds a hue, saturation, value adjustment to the selected layer.'''
    bl_idname = "matlay.add_layer_filter_hsv"
    bl_label = "Add HSV"
    bl_description = "Adds a HSV adjustment to the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        matlay_utils.set_valid_mode()
        add_material_layer_filter('ShaderNodeHueSaturation', context)
        matlay_utils.set_valid_material_shading_mode(context)
        return{'FINISHED'}

class MATLAY_OT_add_layer_filter_rgb_curves(Operator):
    '''Adds level adjustment to the selected layer.'''
    bl_idname = "matlay.add_layer_filter_rgb_curves"
    bl_label = "Add RGB Curves"
    bl_description = "Adds a RGB curves adjustment to the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.matlay_layers

    def execute(self, context):
        matlay_utils.set_valid_mode()
        add_material_layer_filter('ShaderNodeRGBCurve', context)
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
        col.operator("matlay.add_layer_filter_levels", text="Levels")
        col.operator("matlay.add_layer_filter_hsv", text="HSV")
        col.operator("matlay.add_layer_filter_rgb_curves", text="RGB Curves")

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
        filters = context.scene.matlay_material_filters
        selected_layer_index = context.scene.matlay_layer_stack.layer_index
        selected_filter_index = context.scene.matlay_material_filter_stack.selected_filter_index

        matlay_utils.set_valid_mode()

        # Delete the material filter nodes.
        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
            filter_node = get_material_filter_node(material_channel_name, selected_layer_index, selected_filter_index)
            if filter_node:
                material_channel_node.node_tree.nodes.remove(filter_node)

        # Re-index and re-link material filter nodes.
        number_of_filter_nodes = len(get_all_material_filter_nodes("COLOR", selected_layer_index))
        if number_of_filter_nodes > 0:
            update_material_filter_nodes(context)

        # Remove the filter stack slot.
        filters.remove(selected_filter_index)
        
        # Reset the selected filter index.
        context.scene.matlay_material_filter_stack.selected_filter_index = max(min(selected_filter_index - 1, len(filters) - 1), 0)

        # Re-link and re-organize layers.
        layer_nodes.update_layer_nodes(context)

        matlay_utils.set_valid_material_shading_mode(context)

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