import bpy
from bpy.types import Operator

def popup_message_box(message = "", title = "Message Box", icon = 'INFO'):
    def draw_popup_box(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw_popup_box, title = title, icon = icon)
    print(title + ": " + message)