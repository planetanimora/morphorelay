# Reproduce the proof of concept

## Build

Use Unreal Engine **5.8.3** on Windows. The development build used Visual Studio 2026, MSVC 14.50 and Windows SDK 10.0.22621.0. Install the **Game development with C++** workload with C++ tools and a Windows SDK. [Epic's compatibility table](https://dev.epicgames.com/documentation/en-us/unreal-engine/setting-up-visual-studio-development-environment-for-cplusplus-projects-in-unreal-engine) also lists VS 2022 17.14+ for UE 5.8.

Generate project files from `PerfBridgeMH.uproject`, open the generated solution, and build **Development Editor | Win64**. Open the project. The Unreal module and asset paths retain the original `PerfBridgeMH`/`M4` identifiers.

## Optional asset regeneration

The prepared assets are included. To regenerate in a copy of the project, remove only `Content/PlanetAnimora/POC/M4` from that copy while the editor is closed, then open the editor and run these scripts through **Tools → Execute Python Script**, in order:

1. `Scripts/build_m4_stage1.py`: import the repository's `assets/mouth/Mouth.fbx`, create the base skeleton and skeletal mesh.
2. `Scripts/build_m4_stage2.py`: create radial bones and mathematical weights.
3. `Scripts/build_m4_stage3.py`: create the lit demo map and validate the actuator and weights.

Stage 3 reports `STAGE 3 COMPLETE` in the Output Log when all checks pass. The scripts are editor tools; they are not needed during Play. The project enables Python, Editor Scripting Utilities, Geometry Scripting and Skeletal Mesh Modeling Tools for this path.

## Blender source

Open `assets/mouth/Mouth.blend` in Blender 5.0.1 or a compatible newer version. The preparation tool can produce a fresh Blender source and FBX from an input mesh:

```powershell
blender --background --python-exit-code 1 --python tools/blender_prepare_mouth.py -- INPUT.fbx OUTPUT_FOLDER
```

Use a separate output folder when inspecting changes. The script verifies vertex count and geometry after an FBX round trip. Any geometry edit needs a new Unreal import and weight validation.

## Modes and diagnosis

| Mode | Settings before Play |
|---|---|
| Live phone | Use Live Link on; subject selected; Auto Oscillate off |
| Sine-wave demonstration | Use Live Link off; Auto Oscillate on |
| Manual pose | Use Live Link off; Auto Oscillate off; change M4 Aperture |

Save settings on the editor actor before entering Play. Changes to the temporary Play instance disappear when Play stops. A green Live Link subject confirms streaming; the actor's **Live Link Status** separately confirms the curve lookup. With valid data it displays the matched name and value. On missing data the actor holds its previous pose. A source preset is local to your setup; use your own phone address and save a Live Link preset if you want to restore it later.
