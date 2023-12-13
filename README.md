# MatLayer

MatLayer is a free and open-source libre add-on that drastically speeds up and simplifies the material editing workflow within Blender by providing a wrapper user interface for the vanilla material nodes.

MatLayer is currently developed by a one-man team. I've put over 2000 hours into development of MatLayer.

Get the latest release for free [here](https://github.com/LoganFairbairn/matlayer/releases).

You can support this add-ons development by...
- Donating to my PayPal [here]("https://paypal.me/RyverCA?country.x=CA&locale.x=en_US")
- Starring and following on Github
- Sharing MatLayer

## Features

- PBR material layer stack user interface.
![alt text](https://raw.githubusercontent.com/LoganFairbairn/matlayer/main/promo/LayeredMaterialBall.png?raw=true)

- One-click mesh map baking for high poly to low poly normals, ambient occlusion, curvature, thickness, and world space normals.
![alt text](https://raw.githubusercontent.com/LoganFairbairn/matlayer/main/promo/MaterialBall_MeshMapBakes.png?raw=true)

- One-click texture exporting for common formats and software.
![alt text](https://raw.githubusercontent.com/LoganFairbairn/matlayer/main/promo/ExportingWithChannelPacking.png?raw=true)

- Appendable workspace ideal for material editing.
- Fast texture set importing.
- Triplanar projection.
- The ability to merge materials with automatic mesh map application (a.k.a smart materials).
- The ability to export all materials on an object to a single texture set.
- Full global and per layer texture set control.
- Integrated default filters for material channels.
- Multi-masking for material layers.
- Custom export templates with texture channel packing.
- Non-destructive decal layers.
- Auto-corrections for normal map rotations.
- Better normal map blending using Re-oriented normal map blending.
- Support for adding custom group nodes to layers.
- Integrated blurring for textures.
- Basic brush presets.
- Automatic image file management options.
- HDRI setup for rendered view.

## Limitations

- No UDIM support (currently).
- Usage of only 1 UV map per object is supported (currently).
- No ID map baking (currently).
- No material layer folders.

## Tips

- Only edit materials made with MatLayer through the add-on interface. MatLayer materials are created using strict formatting to allow them to be read into the interface properly, editing the nodes manually will cause errors. If you need custom materials or effects, you can add custom group nodes into the material channels through the interface.
- Most user interface elements have detailed tooltips when you hover your mouse over them.

## FAQ

Q: Why should I use MatLayer over other material solutions?
- MatLayer is 100% free.
- You can keep your workflow within Blender.
- You support free and open-source software.
- You can mod MatLayer to improve your workflow with Python scripting.

## Platforms

- Windows, Linux



















Download the latest version from the releases - 

...or use the green code button to download the development version which may have new features and fixes, but can be less stable.

Here's a tutorial to help you get started - https://www.youtube.com/watch?v=o-fT5MXs5ds

-----

MatLayer is a free add-on for Blender that drastically speeds up the material workflow by replacing the material node workflow in Blender with a layer stack workflow, in addition to offering automation for common mesh map baking, and file handling.

If you like this add-on please star it on github to let me know!

I plan on releasing updates and bug fixes for this add-on at my own speed. If you're interested in seeing new upcoming features and bug fixes, check out the projects board https://github.com/users/LoganFairbairn/projects/1

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

- Texture export templates for popular software and formats

- Custom channel packing

- Decals that bake properly to exported textures


- Auto corrections for normal map rotations


- Triplanar projection with correct normal projection


- Layers support custom group nodes

- Fast material channel management

- Automatic texture file and setting management

- Blurring for materials and masks

- Basic brush presets

Limitations:
- No layer folders
- Displacement is not supported
- (currently) no ID map masking support
- (currently) no UDIM support

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

References:
- https://bgolus.medium.com/normal-mapping-for-a-triplanar-shader-10bf39dca05a
- https://blog.selfshadow.com/publications/blending-in-detail/

-----

Thanks to Mok for helping translate.