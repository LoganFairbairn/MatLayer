import bpy
from bpy.types import Operator

def show_message_box(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

class MATLAY_OT_popup_message(Operator):
    '''Prints an message of the given type to the screen. Used for info and error messages that should be displayed to the user.'''
    bl_idname = "matlay.print_message"
    bl_label = "Print Message"
    bl_description = "Prints an message of the given type to the screen. Used for info and error messages that should be displayed to the user."

    message: bpy.props.StringProperty(name="Message", default="MESSAGE HERE")
    message_type: bpy.props.StringProperty(name="Message Type", default="ERROR")

    def execute(self, context):
        self.report({'WARNING'}, self.message)
        return {'FINISHED'}