"""Run with Blender --background --python this.py -- INPUT.fbx OUTPUT_DIRECTORY.

Imports geometry, replaces imported materials, removes custom properties and
external images, then writes a Blender source and a self-contained mesh FBX.
Preserves the mesh's world-space positions; provenance is documented separately.
"""
import bpy
import sys
import json
from pathlib import Path

args = sys.argv[sys.argv.index('--') + 1:]
source, output = Path(args[0]).resolve(), Path(args[1]).resolve()
output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(source), use_custom_props=False)
meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
assert len(meshes) == 1, 'Expected a single mouth mesh'
obj = meshes[0]
before = [tuple(obj.matrix_world @ v.co) for v in obj.data.vertices]
for other in list(bpy.data.objects):
    if other != obj:
        bpy.data.objects.remove(other, do_unlink=True)
obj.name = 'Mouth'
obj.data.name = 'MouthMesh'
for block in (obj, obj.data, bpy.context.scene):
    for key in list(block.keys()):
        del block[key]
obj.data.materials.clear()
for material in list(bpy.data.materials):
    bpy.data.materials.remove(material)
for img in list(bpy.data.images):
    bpy.data.images.remove(img)
material = bpy.data.materials.new('M_Mouth_Neutral')
material.use_nodes = True
bsdf = material.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (0.5, 0.5, 0.5, 1)
bsdf.inputs['Roughness'].default_value = 0.65
obj.data.materials.append(material)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
after = [tuple(obj.matrix_world @ v.co) for v in obj.data.vertices]
assert max(abs(a-b) for p,q in zip(before,after) for a,b in zip(p,q)) < 1e-6
report = {'blender_version': bpy.app.version_string, 'vertices':len(obj.data.vertices),
          'polygons':len(obj.data.polygons), 'world_bounds': [[min(p[i] for p in after),max(p[i] for p in after)] for i in range(3)],
          'external_images': len(bpy.data.images), 'geometry_preserved_on_material_cleanup':True}
bpy.ops.wm.save_as_mainfile(filepath=str(output / 'Mouth.blend'))
bpy.ops.export_scene.fbx(filepath=str(output / 'Mouth.fbx'), use_selection=True,
    object_types={'MESH'}, use_mesh_modifiers=True, use_custom_props=False,
    bake_anim=False, axis_forward='-Z', axis_up='Y', path_mode='STRIP', embed_textures=False)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(output / 'Mouth.fbx'), use_custom_props=False)
roundtrip = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
points = [tuple(roundtrip.matrix_world @ v.co) for v in roundtrip.data.vertices]
assert len(points) == len(after), 'Vertex count changed on round-trip'
# FBX may reorder vertices; compare both point sets using nearest neighbors.
from mathutils.kdtree import KDTree
tree = KDTree(len(points))
for i, p in enumerate(points):
    tree.insert(p, i)
tree.balance()
error = max(tree.find(p)[2] for p in after)
assert error < 1e-5, 'Geometry changed on round-trip: %s' % error
report['fbx_roundtrip_max_coordinate_error_m'] = error
(output / 'blender-validation.json').write_text(json.dumps(report, indent=2)+'\n')
print('MORPHORELAY BLENDER VALIDATION', json.dumps(report))
