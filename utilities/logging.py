# This module contains functions for logging functions for debugging purposes, and displaying info and error messages for users and developers.

import bpy
from bpy.types import Operator

LOG_FUNCTIONS = True

def log(log_message):
    '''Prints the given message to Blender's console window. This function helps log functions called by this add-on for debugging purposes.'''
    if LOG_FUNCTIONS:
        print("Matlay Log: {0}".format(log_message))

def popup_message_box(message = "", title = "Message Box", icon = 'INFO'):
    def draw_popup_box(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw_popup_box, title = title, icon = icon)
    print(title + ": " + message)
