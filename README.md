# MatLayer

Download the latest version from the releases - https://github.com/LoganFairbairn/matlayer/releases

...or use the green code button to download the development version which may have new features and fixes, but can be less stable.

Here's a tutorial to help you get started - https://www.youtube.com/watch?v=o-fT5MXs5ds

-----

MatLayer is a free add-on for Blender that drastically speeds up the material workflow by replacing the material node workflow in Blender with a layer stack workflow, in addition to offering automation for common mesh map baking, and file handling.

If you like this add-on please star it on github to let me know!

If you're interested in seeing new upcoming features and bug fixes, check out the projects board https://github.com/users/LoganFairbairn/projects/1

-----

Features:
- Simple user interface
![alt text](https://raw.githubusercontent.com/LoganFairbairn/matlayer/main/promo/UIExample.png?raw=true)

- Material channel filters

- Multi-masking for material layers

- Fast PBR texture set importing
![alt text](https://raw.githubusercontent.com/LoganFairbairn/matlayer/main/promo/ImportTextureSetShowcase.gif?raw=true)

- One-click batch baking for mesh maps
![alt text](https://raw.githubusercontent.com/LoganFairbairn/matlayer/main/promo/BakingExamples.jpg?raw=true)

- One-click batch exporting for textures

- Decals that bake properly to exported textures
![alt text](https://raw.githubusercontent.com/LoganFairbairn/matlayer/main/promo/DecalShowcase.gif?raw=true)

- Auto corrections for normal map rotations
![alt text](https://raw.githubusercontent.com/LoganFairbairn/matlayer/main/promo/NormalRotationCorrectionShowcase.gif?raw=true)

- Triplanar projection with correct normal projection
![alt text](https://raw.githubusercontent.com/LoganFairbairn/matlayer/main/promo/TriplanarShowcase.gif?raw=true)

- Layers support custom group nodes

- Fast material channel management

- Automatic texture file and setting management

- Blurring for materials and masks

- Basic brush presets

Limitations:
- No layer folders
- Baking and exporting for textures can be very slow
- Displacement is not supported
- (currently) no ID map masking support

-----

Tips:
- When using this add-on, you are intended to use ONLY the add-on ui, and NOT manually edit the material nodes. If you need custom nodes, you should add custom group nodes into material channel or masks through the interface.

- It's best to isolate your object into it's own blend file for material editing, for best performance and file management cases.

- Minimize the amount of layers you use when possible, most object's materials can be created with 3 - 10 material layers.

- When possible and required, use multiple materials in multiple material slots.

- It's better for performance to use color, uniform values, or image textures when possible instead of procedural textures like noise, voronoi and musgrave. This will in most cases also result in better materials.

- Most user interface elements have a detailed tooltip when you hover your mouse over them.

- Toggling off unused material channels globally and per material layer when they are not needed will help decrease shader compilation times.

- For slower computers, you can temporarily stop automatic shader compilation by switching the viewport mode to solid, make material edits and then switch back to material or shader mode to view your changes.

-----

Platforms: Windows, Linux (untested)

-----

Thanks to Mok for helping translate.