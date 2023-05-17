# MatLay

# IMPORTANT: Current version available is a development build, expect bugs.

MatLay is a free add-on for Blender that drastically speeds up the material workflow by replacing the material node workflow in Blender with a layer stack workflow, in addition to offering automation for common mesh map baking, and file handling.

Features:
- Simple user interface
![alt text](https://raw.githubusercontent.com/LoganFairbairn/matlay/main/ExampleScreenShot.png?raw=true)
- Filters for specific material channels.

- Fast material masking with support for multiple masks

- Fast PBR texture set importing
![alt text](https://raw.githubusercontent.com/LoganFairbairn/matlay/main/promo/ImportTextureSet.gif?raw=true)

- Multiple masks per layer

- One-click batch baking for mesh maps
![alt text](https://raw.githubusercontent.com/LoganFairbairn/matlay/main/promo/BakingExamples.png?raw=true)

- One-click batch exporting for textures

- Fast material channel management

- Automatic texture file and setting management

- Decal layers

- Layers support custom group nodes

- Auto corrections for normal map rotations

- Custom triplanar projection with correct normal projection

- Faster workflow for exporting and reloading from an external image editor

Limitations:
- No layer folders
- Baking and exporting for textures can be very slow
- Displacement is not supported
- (currently) no ID map masking support
- (currently) no blur filter

Workflow Tips:
- When using this add-on, you are intended to use ONLY the add-on ui, and NOT manually edit the material nodes.
- This add-on currently supports 1 material per object, using multiple material slots on an object will likely result in errors. It will very likely support multiple material slots on one object in the future.
- Generally it's best to isolate your object you wish to apply materials to in it's own blend file, this can also help with file management in many cases.
- You can have as many material layers as you'd like, however it's better to minimize the amount of layers you use for optimization purposes. Most object's materials can be created with 3 - 15 material layers.
- It's better for performance to use color, uniform values, or image textures when possible instead of procedural textures like noise, voronoi and musgrave.
- Almost all user interface elements have a detailed tooltip when you hover your mouse over them.
- Toggling off unused material channels globally and per material layer will help increase performance.
- Typing in values, rather than sliding their values is much more performant as sliding values for material properties on complex materials can cause a lot of vram usage.
- Editing objects in the material editing viewport shading mode rather than in a rendered mode will be better for performance.

Platforms: Windows, Linux (untested)
Tested with Blender versions: 3.4.1