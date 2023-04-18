# MatLay
MatLay is an add-on for Blender that drastically speeds up the material workflow by replacing the material node workflow in Blender with a layer stack workflow, offering automation for common mesh map baking, and automating file handling.

Note: Current version availabe is a development build, expect bugs.

![alt text](https://raw.githubusercontent.com/LoganFairbairn/matlay/main/ExampleScreenShot.png?raw=true)

Pros:
- Free, and always will be
- Layer stack user interface and workflow
- Material layers support multiple filters
- Layers support multiple masks
- One-click baking for mesh maps
- One-click exporting for textures
- Texture set material channel management
- Texture file management
- Custom group nodes can be added to the layer stack

Cons:
- No layer folders
- Baking and exporting for textures can be very slow
- No ID map masking support
- No displacement layer stack
- Currently no blur filter

Development Principles:
- Simplicity
- Ease of use
- Workflow Speed

Workflow Help:
- When using this add-on, you are intended to only use the add-on ui, and NOT manually edit the material nodes.
- This add-on currently supports 1 material per object.