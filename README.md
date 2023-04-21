# MatLay

# IMPORTANT: Current version available is a development build, expect bugs.

MatLay is a free add-on for Blender that drastically speeds up the material workflow by replacing the material node workflow in Blender with a layer stack workflow, in addition to offering automation for common mesh map baking, and file handling.

![alt text](https://raw.githubusercontent.com/LoganFairbairn/matlay/main/ExampleScreenShot.png?raw=true)

Features:
- Simple user interface
- Material layers support multiple filters
- Layers support multiple masks
- One-click baking for mesh maps
- One-click exporting for textures
- Fast material channel management
- Automatic texture file and setting management
- Layers support custom group nodes
- Exporting and reloading from an external image editor

Limitations:
- No layer folders
- Baking and exporting for textures can be very slow
- (Currently) No ID map masking support
- (Currently) No displacement layer stack
- (Currently) no blur filter

Workflow Help:
- When using this add-on, you are intended to use ONLY the add-on ui, and NOT manually edit the material nodes.
- This add-on currently supports 1 material per object, it will support editing multiple materials on the same object in the future.
- Almost all user interface elements have a detailed tooltip when you hover your mouse over them.

Platforms: Windows, Linux (untested)