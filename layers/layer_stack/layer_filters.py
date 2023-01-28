import bpy
from bpy.types import PropertyGroup, Operator
from ..nodes import material_channel_nodes
from ..nodes import layer_nodes

#----------------------------- LAYER FILTER STACK -----------------------------#

class COATER_layer_filter_stack(PropertyGroup):
    '''Properties for layer filters.'''
    selected_filter_index: bpy.props.IntProperty(default=-1)

class COATER_UL_layer_filter_stack(bpy.types.UIList):
    '''Draws the mask stack for the selected layer.'''
    def draw_item(self, context, layout, data, item, icon, active_data, index):
        self.use_filter_show = False
        self.use_filter_reverse = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.label(text=item.name)
            row.prop(item, "layer_stack_index")

class COATER_layer_filters(PropertyGroup):
    name: bpy.props.StringProperty(name="", description="The name of the layer filter", default="Layer Filter Naming Error")
    layer_stack_index: bpy.props.IntProperty(name="", description = "The layer stack index for this filter", default=-999)

#----------------------------- LAYER FILTER TYPES -----------------------------#

def get_all_layer_filter_nodes(layer_stack_index, material_channel_name, context):
    '''Gets all the filter nodes for a given layer.'''
    filter_nodes = []

    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)
    for i in range(0, 10):
        filter_node = material_channel_node.node_tree.nodes.get("FILTER_" + str(layer_stack_index) + "_" + str(i))
        if filter_node:
            filter_nodes.append(filter_node)
        else:
            break
    return filter_nodes

def get_number_of_filter_nodes(material_channel_name, layer_stack_index, context):
    '''Gets the total number of filter nodes in the given layer by reading the material nodes.'''
    number_of_filter_nodes = 0
    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)
    for i in range(0, 10):
        filter_node = material_channel_node.node_tree.nodes.get("FILTER_" + str(layer_stack_index) + "_" + str(i))
        if filter_node:
            number_of_filter_nodes += 1
        else:
            break
    return number_of_filter_nodes

def update_filter_nodes(context):
    '''Updates filter node indicies. This should be called after adding or removing filter nodes.'''
    material_channel_names = material_channel_nodes.get_material_channel_list()
    for material_channel_name in material_channel_names:
        update_filter_node_indicies(material_channel_name, context)
        re_link_filter_nodes(material_channel_name, context)

def update_filter_node_indicies(material_channel_name, context):
    '''Renames all filter nodes with their correct indicies.'''
    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)
    changed_layer_index = -1
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    filters = context.scene.coater_layer_filters
    filter_added = False
    filter_deleted = False

    # 1. Check for a newly added filter (signified by a tilda at the end of the node's name).
    for i in range(0, len(filters)):
        temp_filter_node = material_channel_node.node_tree.nodes.get("FILTER" + "_" + str(selected_layer_index) + "_" + str(i) + "~")
        if temp_filter_node:
            filter_added = True
            changed_layer_index = i
            break

    # 2. Check for a deleted filter.
    if not filter_added:
        for i in range(0, len(filters)):
            temp_filter_node = material_channel_node.node_tree.nodes.get("FILTER" + "_" + str(selected_layer_index) + "_" + str(i))

            if not  temp_filter_node:
                filter_deleted = True
                changed_layer_index = i
                break

    # 3. Rename the all layer nodes starting with the changed layer and remove the tilda from the newly added layer.
    if filter_added:
        for i in range(len(filters), changed_layer_index + 1, -1):
            filter_node = material_channel_node.node_tree.nodes.get("FILTER_" + str(selected_layer_index) + "_" + str(i - 1))
            if filter_node:
                filter_node.name = "FILTER_" + str(selected_layer_index) + "_" + str(i)
                filter_node.label = filter_node.name
                filters[i].layer_stack_index = i

        # Remove the tilda from the newly added filter.
        new_filter_node = material_channel_node.node_tree.nodes.get("FILTER_" + str(selected_layer_index) + "_" + str(changed_layer_index) + "~")
        if new_filter_node:
            new_filter_node.name = "FILTER_" + str(selected_layer_index) + "_" + str(changed_layer_index)
            new_filter_node.label = new_filter_node.name
            filters[changed_layer_index].layer_stack_index = i

    # 4. Rename filter layer nodes past the deleted filter layer if they exist.
    if filter_deleted and len(filters) > 0:
        for i in range(changed_layer_index, len(filters), 1):
            old_filter_node_name = "FILTER_" + str(selected_layer_index) + "_" + str(i + 1)
            filter_node = material_channel_node.node_tree.nodes.get(old_filter_node_name)

            if filter_node:
                filter_node.name = "FILTER_" + str(selected_layer_index) + "_" + str(i)
                filter_node.label = filter_node.name
                filters[i + 1].layer_stack_index = i

def re_link_filter_nodes(material_channel_name, context):
    '''Re-links all filter nodes in the given material channel.'''
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    filter_nodes = get_all_layer_filter_nodes(selected_layer_index, material_channel_name, context)

    material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)
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

            if next_filter_node:
                material_channel_node.node_tree.links.new(filter_node.outputs[0], next_filter_node.inputs[0])

def add_layer_filter(layer_filter_type, default_name, context):
    '''Creates a new filter slot.'''
    filters = context.scene.coater_layer_filters
    filter_stack = context.scene.coater_layer_filter_stack
    selected_layer_filter_index = context.scene.coater_layer_filter_stack.selected_filter_index
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    # Add a new layer filter slot with a default layer filter name and select it.
    filters.add()
    filters[len(filters) - 1].name = default_name

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

    # Add a shader node for the layer filter.
    new_filter_index = 0
    if len(filters) == 0:
        new_filter_index = 0
    else:
        new_filter_index = selected_layer_filter_index

    material_channel_list = material_channel_nodes.get_material_channel_list()
    for material_channel_name in material_channel_list:
        material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)
        if material_channel_node:
                
                # Create new filter node, with tilda to indicate it's a newly added node.
                filter_node = material_channel_node.node_tree.nodes.new(layer_filter_type)
                filter_node.name = "FILTER_" + str(selected_layer_index) + "_" + str(new_filter_index) + "~"
                filter_node.label = filter_node.name

                # Add the new node to the layer frame.
                frame = layer_nodes.get_layer_frame(material_channel_name, selected_layer_index, context)
                if frame:
                    filter_node.parent = frame

    # Update and re-link and organize filter nodes.
    update_filter_nodes(context)

    # Organize nodes.
    layer_nodes.organize_layer_nodes_in_material_channel(material_channel_name, context)

    # Re-link material layer nodes.
    layer_nodes.link_layers_in_material_channel(material_channel_name, context)

class COATER_OT_add_layer_filter_invert(Operator):
    '''Adds an invert filter to the selected layer.'''
    bl_idname = "coater.add_layer_filter_invert"
    bl_label = "Add Invert"
    bl_description = "Adds an invert filter to the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    # Disable the button when there is no active object.
    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
        add_layer_filter('ShaderNodeInvert', "Invert", context)
        return{'FINISHED'}

class COATER_OT_add_layer_filter_levels(Operator):
    '''Adds level adjustment to the selected layer.'''
    bl_idname = "coater.add_layer_filter_levels"
    bl_label = "Add Levels"
    bl_description = "Adds a level adjustment (color ramp) to the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
        add_layer_filter('ShaderNodeValToRGB', "Levels Adjustment", context)
        return{'FINISHED'}

class COATER_OT_add_layer_filter_hsv(Operator):
    '''Adds a hue, saturation, value adjustment to the selected layer.'''
    bl_idname = "coater.add_layer_filter_hsv"
    bl_label = "Add HSV"
    bl_description = "Adds a HSV adjustment to the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
        add_layer_filter('ShaderNodeHueSaturation', "HSV Adjustment", context)
        return{'FINISHED'}

class COATER_OT_add_layer_filter_rgb_curves(Operator):
    '''Adds level adjustment to the selected layer.'''
    bl_idname = "coater.add_layer_filter_rgb_curves"
    bl_label = "Add RGB Curves"
    bl_description = "Adds a RGB curves adjustment to the selected layer"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
        add_layer_filter('ShaderNodeRGBCurve', "RGB Curves Adjustment", context)
        return{'FINISHED'}

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

#----------------------------- LAYER FILTER STACK OPERATIONS -----------------------------#

class COATER_OT_delete_layer_filter(Operator):
    '''Deletes the selected layer filter.'''
    bl_idname = "coater.delete_layer_filter"
    bl_label = "Delete Layer Filter"
    bl_description = "Deletes the selected layer filter"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
        filters = context.scene.coater_layer_filters
        selected_layer_index = context.scene.coater_layer_stack.layer_index
        selected_layer_filter_index = context.scene.coater_layer_filter_stack.selected_filter_index
        material_channel_list = material_channel_nodes.get_material_channel_list()
        for material_channel_name in material_channel_list:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)
            
            filter_node = material_channel_node.node_tree.nodes.get("FILTER_" + str(selected_layer_index) + "_" + str(selected_layer_filter_index))

            if filter_node:
                material_channel_node.node_tree.nodes.remove(filter_node)

        # Update the filter nodes.
        update_filter_nodes(context)

        # Reset the selected filter index.
        context.scene.coater_layer_filter_stack.selected_filter_index = max(min(selected_layer_filter_index + 1, len(filters) - 1), 0)

        # Remove the filter stack slot.
        filters.remove(selected_layer_filter_index)
            
        return{'FINISHED'}

def move_filter_layer(direction, context):
    filters = context.scene.coater_layer_filters
    selected_layer_filter_index = context.scene.coater_layer_filter_stack.selected_filter_index
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    material_channel_names = material_channel_nodes.get_material_channel_list()

    if direction == "DOWN":
        # Get the filter layer index under the selected layer filter. 
        under_filter_layer_index = max(min(selected_layer_filter_index - 1, len(filters) - 1), 0)
        if selected_layer_filter_index - 1 < 0:
            return

        # Add a tilda to the end of the filter node's name for the filter node that will be moved down on the layer stack.
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)
            filter_node = material_channel_node.node_tree.nodes.get("FILTER_" + str(selected_layer_index) + "_" + str(selected_layer_filter_index))
            filter_node.name = filter_node.name + "~"
            filter_node.label = filter_node.name
        
        # Update the layer filter for the layer filter below.
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)
            filter_node = material_channel_node.node_tree.nodes.get("FILTER_" + str(selected_layer_index) + "_" + str(under_filter_layer_index))
            filter_node.name = "FILTER_" + str(selected_layer_index) + "_" + str(selected_layer_filter_index)
            filter_node.label = filter_node.name

        # Remove the tilda from the end of the layer filter node and decrease it's index.
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)
            filter_node = material_channel_node.node_tree.nodes.get("FILTER_" + str(selected_layer_index) + "_" + str(selected_layer_filter_index) + "~")
            filter_node.name = "FILTER_" + str(selected_layer_index) + "_" + str(selected_layer_filter_index - 1)
            filter_node.label = filter_node.name

        # Update the filter layer stack index stored in the filter layer.
        filters[selected_layer_filter_index].layer_stack_index -= 1
        filters[under_filter_layer_index].layer_stack_index += 1

        # Move the layer stack slot.
        index_to_move_to = max(min(selected_layer_filter_index - 1, len(filters) -1), 0)
        filters.move(selected_layer_filter_index, index_to_move_to)
        context.scene.coater_layer_filter_stack.selected_filter_index = index_to_move_to

    if direction == "UP":
        # Get the filter layer index above the selected later filter.
        over_layer_index = max(min(selected_layer_filter_index + 1, len(filters) - 1), 0)
        if selected_layer_filter_index + 1 > len(filters) - 1:
            return
        
        # Add a tilda to the end of the layer frame and the layer nodes names for the selected layer.
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)
            filter_node = material_channel_node.node_tree.nodes.get("FILTER_" + str(selected_layer_index) + "_" + str(selected_layer_filter_index))
            filter_node.name = filter_node.name + "~"
            filter_node.label = filter_node.name
        
        # Update the layer nodes for the layer below to have the selected layer index.
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)
            filter_node = material_channel_node.node_tree.nodes.get("FILTER_" + str(selected_layer_index) + "_" + str(over_layer_index))
            filter_node.name = "FILTER_" + str(selected_layer_index) + "_" + str(selected_layer_filter_index)
            filter_node.label = filter_node.name

        # Remove the tilda from the end of the filter node and increase it's index.
        for material_channel in material_channel_names:
            material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel)
            filter_node = material_channel_node.node_tree.nodes.get("FILTER_" + str(selected_layer_index) + "_" + str(selected_layer_filter_index) + "~")
            filter_node.name = "FILTER_" + str(selected_layer_index) + "_" + str(selected_layer_filter_index + 1)
            filter_node.label = filter_node.name
        
        # Update the filter layer stack index stored in the filter layer.
        filters[selected_layer_filter_index].layer_stack_index += 1
        filters[over_layer_index].layer_stack_index -= 1

        index_to_move_to = max(min(selected_layer_filter_index + 1, len(filters) - 1), 0)
        filters.move(selected_layer_filter_index, index_to_move_to)
        context.scene.coater_layer_filter_stack.selected_filter_index = index_to_move_to

    # Re-link layer filter nodes.
    for material_channel_name in material_channel_names:
        re_link_filter_nodes(material_channel_name, context)

    # Re-organize the nodes.
    for material_channel_name in material_channel_names:
        material_channel_node = material_channel_nodes.get_material_channel_node(context, material_channel_name)
        layer_nodes.organize_layer_nodes_in_material_channel(material_channel_name, context)

class COATER_OT_move_layer_filter_up(Operator):
    '''Moves the filter up on the filter layer stack.'''
    bl_idname = "coater.move_filter_up"
    bl_label = "Move Filter Up"
    bl_description = "Moves the selected layer filter up on the layer stack"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
        move_filter_layer("UP", context)
        return{'FINISHED'}

class COATER_OT_move_layer_filter_down(Operator):
    '''Moves the filter up on the filter layer stack.'''
    bl_idname = "coater.move_filter_down"
    bl_label = "Move Filter Down"
    bl_description = "Moves the selected layer filter down on the layer stack"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return bpy.context.scene.coater_layers

    def execute(self, context):
        move_filter_layer("DOWN", context)
        return{'FINISHED'}
    
def refresh_filter_stack(context):
    '''Reads layer nodes to re-construct the filter layer stack.'''
    layer_filters = context.scene.coater_layer_filters
    selected_layer_index = context.scene.coater_layer_stack.layer_index
    selected_material_channel = context.scene.coater_layer_stack.selected_material_channel

    # Clear all layer filters.
    layer_filters.clear()

    # TODO: Read the material nodes and re-add layer filters to the layer stack.

    layer_filter_nodes = get_all_layer_filter_nodes(selected_layer_index, selected_material_channel, context)

    for x in range(0, len(layer_filter_nodes)):
        layer_filters.add()
        node_name = layer_filter_nodes[x].name.split("_")
        layer_filters[x].name = node_name[0]
        layer_filters[x].layer_stack_index = x