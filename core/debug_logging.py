import bpy
import datetime
from .. import preferences

def log(message, message_type='INFO', sub_process=False):
    '''Prints the given message to Blender's console window. This function helps log functions called by this add-on for debugging purposes.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    
    match message_type:
        case 'ERROR':
            error_prefix = "ERROR: "
        case 'WARNING':
            error_prefix = "WARNING: "
        case _:
            error_prefix = ""
    
    logged_message = "[{0}]: {1}{2}".format(datetime.datetime.now(), error_prefix, message)
    
    if sub_process:
        if addon_preferences.log_sub_operations:
            print(logged_message)
    else:
        if addon_preferences.log_main_operations:
            print(logged_message)

def log_status(message, self, type='ERROR'):
    '''Prints the given message to Blender's console window and displays the message in Blender's status bar.'''
    if type == 'ERROR':
        message = "Error: {0}".format(message)
    log(message)
    self.report({type}, message)

def popup_message_box(message = "", title = "Message Box", icon = 'INFO'):
    def draw_popup_box(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw_popup_box, title = title, icon = icon)
    print(title + ": " + message)