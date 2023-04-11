import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import BoolProperty, IntProperty, StringProperty, PointerProperty
from . import material_channels
from . import layer_nodes
from ..utilities import info_messages

# A list of filter node types available in this add-on.
FILTER_NODE_TYPES = ("INVERT", "VALTORGB", "HUE_SAT", "CURVE_RGB")

# The maximum number of filters a single layer can use. Realistically users should never need more filters on a single layer than this.
MAX_LAYER_FILTER_COUNT = 5

#----------------------------- AUTO UPDATING FUNCTIONS FOR FILTER PROPERTIES -----------------------------#

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

def get_filter_name(filter_type):
    '''Returns the given name of a filter based on it's type.'''
    match filter_type:
        case 'ShaderNodeInvert':
            return 'INVERT'
        case 'ShaderNodeValToRGB':
            return 'VALTORGB'
        case 'ShaderNodeHueSaturation':
            return 'HUESAT'
        case 'ShaderNodeRGBCurve':
            return 'CURVERGB'

def format_filter_node_name(filter_node_type, material_layer_index, filter_index):
    '''All nodes made with this add-on must have properly formatted names, this function will return a properly formatted name for a material filter node.'''
    return  "{0}_{1}_{2}".format(filter_node_type, str(material_layer_index), str(filter_index))

def get_material_filter_node(material_channel_name, material_layer_stack_index, filter_index):
    '''Returns the filter node for the given material layer index at the filter index by reading through existing node within the specified material channel'''
    material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
    if material_channel_node:
        for node in material_channel_node.node_tree.nodes:
            if node.bl_static_type in FILTER_NODE_TYPES:
                node_name = node.name
                filter_node_info = node_name.split('_')
                filter_node_material_layer_index = filter_node_info[1]
                filter_node_index = filter_node_info[2]
                if int(filter_node_material_layer_index) == material_layer_stack_index and int(filter_node_index) == filter_index:
                    return node
    return None

def get_material_filter_nodes(material_layer_stack_index, material_channel_name, get_edited=False):
    '''Returns all the filter nodes in the given material layer and within the given material channel. If get edited is passed as true, all nodes part of the given material layer marked as being edited (signified by a tilda at the end of their name) will be returned.'''
    filter_nodes = []
    material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
    if material_channel_node:
        for node in material_channel_node.node_tree.nodes:
            if node.bl_static_type in FILTER_NODE_TYPES:
                node_name = node.name
                filter_node_info = node_name.split('_')
                filter_node_material_layer_index = filter_node_info[1]

                # TODO: Check for a tilda at the end of the node's name (which indicates the node is being changed).

                if int(filter_node_material_layer_index) == material_layer_stack_index:
                    filter_nodes.append(node)
    return filter_nodes

def get_filter_nodes_count(material_layer_stack_index):
    '''Returns the total number of filter nodes in the given layer by reading the material nodes.'''
    number_of_filter_nodes = 0
    for i in range(0, MAX_LAYER_FILTER_COUNT):
        filter_node = get_material_filter_node('COLOR', material_layer_stack_index, i)
        if filter_node:
            number_of_filter_nodes += 1
    return number_of_filter_nodes

def update_material_filter_node_indicies(material_channel_name):
    '''Renames all filter nodes with correct indicies by checking the node tree for newly added, edited (signified by a tilda at the end of their name), or deleted filter nodes'''
    material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
    changed_filter_index = -1
    selected_layer_index = bpy.context.scene.matlay_layer_stack.layer_index
    filters = bpy.context.scene.matlay_material_filters
    filter_added = False
    filter_deleted = False

    # 1. Check for a newly added filter (signified by a tilda at the end of the node's name).
    for i in range(0, len(filters)):
        temp_filter_node_name = format_filter_node_name(filters[i].name, selected_layer_index, i) + "~"
        temp_filter_node = material_channel_node.node_tree.nodes.get(temp_filter_node_name)
        if temp_filter_node:
            filter_added = True
            changed_filter_index = i
            break

    # 2. Check for a deleted filter.
    if not filter_added:
        for i in range(0, len(filters)):
            temp_filter_node_name = format_filter_node_name(filters[i].name, selected_layer_index, i)
            temp_filter_node = material_channel_node.node_tree.nodes.get(temp_filter_node_name)
            if not  temp_filter_node:
                filter_deleted = True
                changed_filter_index = i
                break

    # 3. Rename the all layer nodes starting with the changed layer and remove the tilda from the newly added layer.
    if filter_added:
        for i in range(len(filters), changed_filter_index + 1, -1):
            filter_node = material_channel_node.node_tree.nodes.get(filters[i - 1].name + "_" + str(selected_layer_index) + "_" + str(i - 1))
            if filter_node:
                filter_node.name = format_filter_node_name(filters[i].name, selected_layer_index, i)
                filter_node.label = filter_node.name
                filters[i].stack_index = i

        # Remove the tilda from the newly added filter.
        new_filter_node_name = format_filter_node_name(filters[i].name, selected_layer_index, i) + "~"
        new_filter_node = material_channel_node.node_tree.nodes.get(new_filter_node_name)
        if new_filter_node:
            new_filter_node.name = format_filter_node_name(filters[changed_filter_index].name, selected_layer_index, changed_filter_index)
            new_filter_node.label = new_filter_node.name
            filters[changed_filter_index].stack_index = i

    # 4. Rename filter layer nodes above the deleted filter layer if any exist.
    if filter_deleted and len(filters) > 0:
        for i in range(changed_filter_index + 1, len(filters), 1):
            old_filter_node_name = format_filter_node_name(filters[i].name, selected_layer_index, i)
            filter_node = material_channel_node.node_tree.nodes.get(old_filter_node_name)

            if filter_node:
                filter_node.name = format_filter_node_name(filters[i].name, selected_layer_index, i - 1)
                filter_node.label = filter_node.name
                filters[i].stack_index = i - 1

def re_link_material_filter_nodes(material_channel_name):
    '''Re-links all material filter nodes in the given material channel.'''
    selected_material_layer_index = bpy.context.scene.matlay_layer_stack.layer_index
    filter_nodes = get_material_filter_nodes(selected_material_layer_index, material_channel_name)

    material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
    for i in range(0, len(filter_nodes)):
        filter_node = filter_nodes[i]

        next_filter_node = None
        if len(filter_nodes) - 1 > i:
            next_filter_node = filter_nodes[i + 1]

            # Clear the output links
            node_links = material_channel_node.node_tree.links
            for l in node_links:
                if l.from_node.name == filter_node.name:
                    node_links.remove(l)

            # Link to the next filter node in the layer stack if it exists.
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

# TODO: Remove this in favor of calling re-link or re-index functions individually as required.  
def update_material_filter_nodes(context):
    '''Updates the index stored in filter node names, and re-links material filters. This should generally called after adding or removing filter nodes.'''
    # If there are no material layers there shouldn't be any material filters, don't update the material filter nodes.
    number_of_material_layers = len(context.scene.matlay_layers)
    if number_of_material_layers > 0:
        material_channel_names = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_names:
            update_material_filter_node_indicies(material_channel_name)
            re_link_material_filter_nodes(material_channel_name)

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
    layer_filter_nodes = get_material_filter_nodes(selected_layer_index, selected_material_channel)
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

    if len(filters) >= MAX_LAYER_FILTER_COUNT:
        info_messages.popup_message_box("You can't have more than {0} filters on a single layer. This is a safeguard to stop users from adding an unnecessary amount of filters, which will drastically effect performance.".format(MAX_LAYER_FILTER_COUNT), 'User Error', 'ERROR')
        return

    # Define a node name based on the provided filter type.
    match filter_type:
        case 'ShaderNodeInvert':
            node_name = 'INVERT'
        case 'ShaderNodeValToRGB':
            node_name = 'VALTORGB'
        case 'ShaderNodeHueSaturation':
            node_name = 'HUESAT'
        case 'ShaderNodeRGBCurve':
            node_name = 'CURVERGB'
    
    # Add a new layer filter slot, name and select it.
    filters.add()
    filters[len(filters) - 1].name = node_name
    filters[len(filters) - 1].cached_name = node_name

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
                filter_node.name = format_filter_node_name(filters[new_filter_index].name, selected_layer_index, new_filter_index) + "~"
                filter_node.label = filter_node.name

                # Add the new node to the layer frame.
                frame = layer_nodes.get_layer_frame(material_channel_name, selected_layer_index, context)
                if frame:
                    filter_node.parent = frame

    # TODO: Do I need this?
    # Update and re-link and organize filter nodes.
    #update_material_filter_nodes(context)

    # Re-organize and re-link material layer nodes so mix nodes will automatically connect with filter nodes.
    layer_nodes.update_layer_nodes(context)

def move_filter_layer(direction, context):
    filters = context.scene.matlay_material_filters
    selected_filter_index = context.scene.matlay_material_filter_stack.selected_filter_index
    selected_layer_index = context.scene.matlay_layer_stack.layer_index
    material_channel_list = material_channels.get_material_channel_list()

    if direction == "DOWN":
        # Get the filter layer index under the selected layer filter. 
        under_filter_layer_index = max(min(selected_filter_index - 1, len(filters) - 1), 0)
        if selected_filter_index - 1 < 0:
            return

        # Add a tilda to the end of the filter node's name for the filter node that will be moved down on the layer stack.
        for material_channel_name in material_channel_list:
            filter_node = get_material_filter_node(material_channel_name, selected_layer_index, selected_filter_index)
            filter_node.name = filter_node.name + "~"
            filter_node.label = filter_node.name
        
        # Update the name of the material filter node below this one of the filter stack.
        for material_channel_name in material_channel_list:
            filter_node = get_material_filter_node(material_channel_name, under_filter_layer_index, selected_filter_index)
            filter_node.name = format_filter_node_name(filters[selected_filter_index].name, selected_layer_index, selected_filter_index)
            filter_node.label = filter_node.name

        # Remove the tilda from the end of the layer filter node and decrease it's index to move it down on the filter stack.
        for material_channel_name in material_channel_list:
            material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
            filter_node = material_channel_node.node_tree.nodes.get(filters[under_filter_layer_index] + str(selected_layer_index) + "_" + str(selected_filter_index) + "~")
            filter_node.name = format_filter_node_name(filters[selected_filter_index].name, selected_layer_index, selected_filter_index - 1)
            filter_node.label = filter_node.name

        # Update the filter stack index.
        filters[selected_filter_index].stack_index -= 1
        filters[under_filter_layer_index].stack_index += 1

        # Move the layer stack slot.
        index_to_move_to = max(min(selected_filter_index - 1, len(filters) -1), 0)
        filters.move(selected_filter_index, index_to_move_to)
        context.scene.matlay_layer_filter_stack.selected_filter_index = index_to_move_to

    if direction == "UP":
        # Get the filter layer index above the selected later filter.
        over_layer_index = max(min(selected_filter_index + 1, len(filters) - 1), 0)
        if selected_filter_index + 1 > len(filters) - 1:
            return
        
        # Add a tilda to the end of the layer frame and the layer nodes names for the selected layer.
        for material_channel_name in material_channel_list:
            filter_node = get_material_filter_node(material_channel_name, selected_layer_index, selected_filter_index)
            filter_node.name = filter_node.name + "~"
            filter_node.label = filter_node.name
        
        # Update the layer nodes for the layer below to have the selected layer index.
        for material_channel_name in material_channel_list:
            material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
            filter_node_name = format_filter_node_name(filters[over_layer_index].name, selected_layer_index, over_layer_index)
            filter_node = material_channel_node.node_tree.nodes.get(filter_node_name)
            filter_node.name = format_filter_node_name(filters[selected_filter_index].name, selected_layer_index, selected_filter_index)
            filter_node.label = filter_node.name

        # Remove the tilda from the end of the filter node and increase it's index.
        for material_channel_name in material_channel_list:
            material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
            filter_node_name = format_filter_node_name(filters[selected_filter_index].name, selected_layer_index, selected_filter_index) + "~"
            filter_node = material_channel_node.node_tree.nodes.get(filter_node_name)
            filter_node.name = format_filter_node_name(filters[selected_filter_index + 1].name, selected_layer_index, selected_filter_index + 1)
            filter_node.label = filter_node.name
        
        # Update the filter stack index.
        filters[selected_filter_index].stack_index += 1
        filters[over_layer_index].stack_index -= 1

        index_to_move_to = max(min(selected_filter_index + 1, len(filters) - 1), 0)
        filters.move(selected_filter_index, index_to_move_to)
        context.scene.matlay_layer_filter_stack.selected_filter_index = index_to_move_to

    # Re-link layer filter nodes.
    for material_channel_name in material_channel_list:
        re_link_material_filter_nodes(material_channel_name, context)

    # Re-organize the nodes.
    for material_channel_name in material_channel_list:
        material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
        layer_nodes.organize_layer_nodes_in_material_channel(material_channel_name, context)


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
    name: StringProperty(name="Filter Name", description="The name of the material filter.", default="Invalid Name")
    stack_index: IntProperty(name="Stack Index", description = "The (array) stack index for this filter used to define the order in which filters should be applied to the material", default=-999)
    material_channel_toggles: PointerProperty(type=FiltersMaterialChannelToggles, name="Material Channel Toggles")

class MATLAY_material_filter_stack(PropertyGroup):
    '''Properties for layer filters.'''
    selected_filter_index: IntProperty(default=-1)
    auto_update_filter_properties: BoolProperty(name="Update Filter Properties", description="When true, changing filter properties will trigger automatic updates.", default=True)

class MATLAY_UL_layer_filter_stack(bpy.types.UIList):
    '''Draws the material filter stack.'''
    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.label(text=context.scene.matlay_material_filters[item.stack_index].name)
            #row.prop(item, "stack_index")

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
        add_material_layer_filter('ShaderNodeInvert', context)
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
        add_material_layer_filter('ShaderNodeValToRGB', context)
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
        add_material_layer_filter('ShaderNodeHueSaturation', context)
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
        add_material_layer_filter('ShaderNodeRGBCurve', context)
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

        # Delete the material filter nodes.
        material_channel_list = material_channels.get_material_channel_list()
        for material_channel_name in material_channel_list:
            material_channel_node = material_channels.get_material_channel_node(context, material_channel_name)
            filter_node = get_material_filter_node(material_channel_name, selected_layer_index, selected_filter_index)
            if filter_node:
                material_channel_node.node_tree.nodes.remove(filter_node)

        # Re-index and re-link material filter nodes.
        number_of_filter_nodes = len(get_material_filter_nodes(selected_layer_index, "COLOR"))
        if number_of_filter_nodes > 0:
            update_material_filter_nodes(context)

        # Remove the filter stack slot.
        filters.remove(selected_filter_index)
        
        # Reset the selected filter index.
        context.scene.matlay_material_filter_stack.selected_filter_index = max(min(selected_filter_index - 1, len(filters) - 1), 0)

        # Re-link layers.
        for material_channel_name in material_channel_list:
            layer_nodes.relink_layers(material_channel_name, context)

            # TODO: Organize nodes.

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
        move_filter_layer("UP", context)
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
        move_filter_layer("DOWN", context)
        return{'FINISHED'}
