# MatLayer

MatLayer is a free and open-source libre add-on that drastically speeds up and simplifies the material editing workflow by providing a wrapper user interface for Blender's vanilla material nodes. You can use MatLayer to make optimized, professional quality materials and textures for game engines, VRChat, still renders, movies and more.

I've invested over 2000 hours over the past 3 years to designing, programming, researching, testing and making assets for MatLayer so there will be a great, free 3D material editing solution available, and everyone will have the freedom to create.

If you would like to help support this add-ons development you can...
- Donate to my [PayPal](https://paypal.me/RyverCA?country.x=CA&locale.x=en_US)
- Star and follow the repository on Github
- Share MatLayer
- Report issues and give suggestions through the Github issues page

Get the latest release here: https://github.com/LoganFairbairn/matlayer/releases

Cheers!

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

## Limitations & Issues

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

## System Requirements
Supported Platforms: Windows, Linux