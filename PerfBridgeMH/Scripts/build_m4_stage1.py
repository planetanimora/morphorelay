"""Import the M4 FBX and create the initial Unreal skeletal mesh asset."""

from pathlib import Path
import traceback
import unreal

DEST = "/Game/PlanetAnimora/POC/M4"
FBX = str(Path(__file__).resolve().parents[2] / "assets" / "mouth" / "Mouth.fbx")


def report(*items):
    unreal.log("M4: " + " ".join(str(item) for item in items))


def require(value, message):
    if not value:
        raise RuntimeError(message)
    return value


def main():
    assets = unreal.EditorAssetLibrary
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    static_path = DEST + "/SM_M4_RadialMouth_Source"
    skeleton_path = DEST + "/SKEL_M4_RadialMouth"
    skeletal_path = DEST + "/SK_M4_RadialMouth"

    if not assets.does_asset_exist(static_path):
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", FBX)
        task.set_editor_property("destination_path", DEST)
        task.set_editor_property("destination_name", "SM_M4_RadialMouth_Source")
        task.set_editor_property("automated", True)
        task.set_editor_property("save", True)
        task.set_editor_property("replace_existing", False)
        tools.import_asset_tasks([task])
        report("Imported", list(task.get_editor_property("imported_object_paths")))
    source = require(assets.load_asset(static_path), "Static mesh import failed")
    report("Static bounds", source.get_bounds())

    if not assets.does_asset_exist(skeleton_path):
        skeleton = unreal.M4AssetBootstrap.create_base_skeleton(skeleton_path)
        require(skeleton, "Skeleton creation failed")
        assets.save_loaded_asset(skeleton)
    skeleton = require(assets.load_asset(skeleton_path), "Skeleton load failed")
    report("Skeleton", skeleton.get_path_name())

    if not assets.does_asset_exist(skeletal_path):
        dynamic = unreal.DynamicMesh()
        dynamic, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(
            source,
            dynamic,
            unreal.GeometryScriptCopyMeshFromAssetOptions(),
            unreal.GeometryScriptMeshReadLOD(),
        )
        report("Copied source mesh", outcome, "vertices", dynamic.get_vertex_count())
        require(dynamic.get_vertex_count() > 0, "Dynamic mesh is empty")
        dynamic = unreal.GeometryScript_BoneWeights.copy_bones_from_skeleton(skeleton, dynamic)
        dynamic, existed = dynamic.mesh_create_bone_weights()
        report("Weight profile existed", existed)
        dynamic.set_all_vertex_bone_weights([unreal.GeometryScriptBoneWeight(bone_index=0, weight=1.0)])
        options = unreal.GeometryScriptCreateNewSkeletalMeshAssetOptions()
        skeletal, outcome = unreal.GeometryScript_NewAssetUtils.create_new_skeletal_mesh_asset_from_mesh(
            dynamic, skeleton, skeletal_path, options
        )
        require(skeletal, "Skeletal mesh creation failed: " + str(outcome))
        assets.save_loaded_asset(skeletal)
        report("Created skeletal mesh", skeletal.get_path_name(), "bounds", skeletal.get_bounds())
    report("STAGE 1 COMPLETE")


try:
    main()
except Exception:
    unreal.log_error("M4 stage 1 failed:\n" + traceback.format_exc())
    raise
