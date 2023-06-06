# This module contains functions for logging functions for debugging purposes, and displaying info and error messages for users and developers.

import bpy
from bpy.types import PropertyGroup
from bpy.props import IntProperty
from .. import preferences
from ..core import matlayer_materials
from ..core import material_channels
from ..core import layer_nodes
import datetime

def log(message):
    '''Prints the given message to Blender's console window. This function helps log functions called by this add-on for debugging purposes.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    if addon_preferences.logging:
        print("[{0}]: {1}".format(datetime.datetime.now(), message))

def log_status(message, self, type='ERROR'):
    '''Prints the given message to Blender's console window and displays the message in Blender's status bar.'''
    log(message)
    self.report({type}, message)

def popup_message_box(message = "", title = "Message Box", icon = 'INFO'):
    def draw_popup_box(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw_popup_box, title = title, icon = icon)
    print(title + ": " + message)

def update_total_node_and_link_count():
    '''Counts the number of nodes and links created by this add-on to give a quantitative value to the work saved with this plugin.'''
    settings = bpy.context.scene.matlayer_settings
    settings.total_node_count = 0
    settings.total_node_link_count = 0

    # List of group nodes that have their active nodes and node links already counted.
    counted_group_nodes = []

    if not matlayer_materials.verify_material(bpy.context):
        return

    for material_channel_name in material_channels.get_material_channel_list():

        material_channel_node = material_channels.get_material_channel_node(bpy.context, material_channel_name)
        if not material_channel_node:
            continue 

        if layer_nodes.get_node_active(material_channel_node):
            settings.total_node_count += 1
            settings.total_node_link_count += 1
        
            # Count all nodes and their nodes links within the material channel group node.
            for node in material_channel_node.node_tree.nodes:
                # Do not count group input or output nodes in the total node count.
                if node.name == 'Group Input' or node.name == 'Group Output':
                    continue

                if layer_nodes.get_node_active(node):
                    settings.total_node_count += 1
                    for output in node.outputs:
                        for l in output.links:
                            if l != 0:
                                settings.total_node_link_count += 1

                    # Count subnodes in group nodes, once for each group node.
                    if node.bl_static_type == 'GROUP':
                        if node.node_tree:
                            if node.node_tree not in counted_group_nodes:
                                counted_group_nodes.append(node.node_tree)
                                for subnode in node.node_tree.nodes:
                                    if layer_nodes.get_node_active(subnode):
                                        settings.total_node_count += 1
                                        for output in subnode.outputs:
                                            for l in output.links:
                                                if l != 0:
                                                    settings.total_node_link_count += 1

class MatlayerSettings(PropertyGroup):
    total_node_count: IntProperty(name="Total Node Count", description="The total number of nodes automatically created by matlayer for this material")
    total_node_link_count: IntProperty(name="Total Node Link Count", description="The total number of node links automatically by matlayer for this material")