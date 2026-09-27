"""Create the M4 demo map and verify the actuator and saved skin weights."""

import math
import traceback
import unreal

DEST = "/Game/PlanetAnimora/POC/M4"


def report(*items):
    unreal.log("M4: " + " ".join(str(item) for item in items))


def require(value, message):
    if not value:
        raise RuntimeError(message)
    return value


def main():
    assets = unreal.EditorAssetLibrary
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    mesh = require(assets.load_asset(DEST + "/SK_M4_RadialMouth"), "Missing skeletal mesh")
    bp_path = DEST + "/BP_M4_RadialMouth_POC"
    if not assets.does_asset_exist(bp_path):
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("parent_class", unreal.M4RadialMouthPOCActor)
        blueprint = require(tools.create_asset("BP_M4_RadialMouth_POC", DEST, unreal.Blueprint, factory), "Blueprint creation failed")
        assets.save_loaded_asset(blueprint)
        report("Created Blueprint", blueprint.get_path_name())

    map_path = DEST + "/MAP_M4_RadialMouth_POC"
    if not assets.does_asset_exist(map_path):
        require(unreal.EditorLevelLibrary.new_level(map_path), "Creating demo map failed")
        actor = require(unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.M4RadialMouthPOCActor, unreal.Vector(0, 0, 0)), "Spawning demo actor failed")
        actor.set_actor_label("M4 Radial Mouth - Aperture Demo")
        light = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.DirectionalLight, unreal.Vector(30, -20, 50), unreal.Rotator(-25, 0, 0))
        if light:
            light.set_actor_label("Demo Light")
        point = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.PointLight, unreal.Vector(20, 0, 0))
        if point:
            point.set_actor_label("Mouth Preview Light")
        camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.CameraActor, unreal.Vector(25, 0, 0), unreal.Rotator(0, 180, 0))
        if camera:
            camera.set_actor_label("Front Camera (+X view)")
            camera.set_editor_property("auto_activate_for_player", unreal.AutoReceiveInput.PLAYER0)
        require(unreal.EditorLevelLibrary.save_current_level(), "Saving demo map failed")
        report("Saved map", map_path)
    else:
        require(unreal.EditorLevelLibrary.load_level(map_path), "Loading demo map failed")
        actors = unreal.EditorLevelLibrary.get_all_level_actors()
        actor = next((a for a in actors if isinstance(a, unreal.M4RadialMouthPOCActor)), None)
        require(actor, "Demo actor missing from map")
        cameras = [a for a in actors if isinstance(a, unreal.CameraActor)]
        if cameras:
            cameras[0].set_actor_location(unreal.Vector(25, 0, 0), False, False)
            cameras[0].set_editor_property("auto_activate_for_player", unreal.AutoReceiveInput.PLAYER0)
        if not any(isinstance(a, unreal.PointLight) for a in actors):
            point = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.PointLight, unreal.Vector(20, 0, 0))
            if point:
                point.set_actor_label("Mouth Preview Light")
        require(unreal.EditorLevelLibrary.save_current_level(), "Updating demo map failed")

    component = require(actor.get_component_by_class(unreal.PoseableMeshComponent), "Poseable mesh component missing")
    actor.apply_aperture(0.5)
    neutral_top = component.get_bone_transform_by_name("M4_Radial_00", unreal.BoneSpaces.COMPONENT_SPACE)
    neutral_center = component.get_bone_transform_by_name("M4_MouthCenter", unreal.BoneSpaces.COMPONENT_SPACE)
    rest_radius = math.hypot(neutral_top.translation.y-neutral_center.translation.y,
                             neutral_top.translation.z-neutral_center.translation.z)
    for value in (0.0, 0.25, 0.5, 0.75, 1.0):
        actor.apply_aperture(value)
        top = component.get_bone_transform_by_name("M4_Radial_00", unreal.BoneSpaces.COMPONENT_SPACE)
        bottom = component.get_bone_transform_by_name("M4_Radial_06", unreal.BoneSpaces.COMPONENT_SPACE)
        center = component.get_bone_transform_by_name("M4_MouthCenter", unreal.BoneSpaces.COMPONENT_SPACE)
        radius = math.hypot(top.translation.y-center.translation.y, top.translation.z-center.translation.z)
        opposite = math.hypot(bottom.translation.y-center.translation.y, bottom.translation.z-center.translation.z)
        report("Aperture", value, "top radius", radius, "bottom radius", opposite)
        require(abs(radius-opposite) < 0.02, "Top and bottom bone radii differ")
        require(abs(radius - (rest_radius * (0.65 + 0.7*value))) < 0.04, "Radial bone scale wrong")

    # Restore the saved scene at its neutral pose; auto oscillation runs in Play.
    actor.apply_aperture(0.5)
    require(actor.apply_live_link_curves({"jawOpen": 0.8}), "Synthetic Live Link curve was rejected")
    driven = component.get_bone_transform_by_name("M4_Radial_00", unreal.BoneSpaces.COMPONENT_SPACE)
    driven_radius = math.hypot(driven.translation.y-neutral_center.translation.y,
                               driven.translation.z-neutral_center.translation.z)
    require(abs(driven_radius - rest_radius*(0.65+0.70*0.8)) < 0.04,
            "Live Link curve did not reach the radial bones")
    require(not actor.apply_live_link_curves({"otherCurve": 1.0}),
            "Missing jawOpen curve should not drive the mouth")
    actor.apply_aperture(0.5)
    report("Synthetic Live Link jawOpen 0.8 reached M4_Aperture; live subject still required")
    weights = unreal.SkinWeightModifier()
    require(weights.set_skeletal_mesh(mesh), "Could not read skin weights")
    n = weights.get_num_vertices()
    center_only = 0
    mixed = 0
    for i in range(n):
        influence = weights.get_vertex_weights(i)
        require(len(influence) <= 3, "Too many influences at vertex %d" % i)
        require(abs(sum(influence.values()) - 1.0) < 0.01, "Weights not normalized at vertex %d" % i)
        if len(influence) == 1:
            center_only += 1
        else:
            mixed += 1
    require(mixed > 0 and center_only > 0, "Missing radial/anchored weight zones")
    report("Weight validation", n, "vertices;", mixed, "mixed;", center_only, "anchored")

    dynamic = unreal.DynamicMesh()
    dynamic, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(
        mesh, dynamic, unreal.GeometryScriptCopyMeshFromAssetOptions(), unreal.GeometryScriptMeshReadLOD()
    )
    require(dynamic.get_vertex_count() == n, "Cannot compare skin weights to source positions")
    points = [dynamic.get_vertex_position(i)[0] for i in range(n)]
    radii = [math.hypot(p.y, p.z) for p in points]
    inner, outer = min(radii), max(radii)
    rest_offsets = {}
    for i in range(12):
        name = "M4_Radial_%02d" % i
        t = component.get_bone_transform_by_name(name, unreal.BoneSpaces.COMPONENT_SPACE)
        rest_offsets[name] = (t.translation.y-neutral_center.translation.y,
                              t.translation.z-neutral_center.translation.z)
    sample_indices = [i for i, r in enumerate(radii) if r < inner + 0.03*(outer-inner)]
    anchored_indices = [i for i, r in enumerate(radii) if r > outer - 0.03*(outer-inner)]
    require(sample_indices and anchored_indices, "Cannot identify inner/outer mouth bands")
    means = []
    for value in (0.0, 0.5, 1.0):
        factor = (0.65 + 0.70*value) - 1.0
        deformed_radii = []
        displacements = []
        for i, p in enumerate(points):
            dy = dz = 0.0
            for bone, weight in weights.get_vertex_weights(i).items():
                oy, oz = rest_offsets.get(str(bone), (0.0, 0.0))
                dy += weight * oy * factor
                dz += weight * oz * factor
            deformed_radii.append(math.hypot(p.y+dy, p.z+dz))
            displacements.append(math.hypot(dy, dz))
        require(min(deformed_radii) > 0.25, "Aperture collapsed at " + str(value))
        inner_mean = sum(deformed_radii[i] for i in sample_indices)/len(sample_indices)
        outer_move = sum(displacements[i] for i in anchored_indices)/len(anchored_indices)
        report("Simulated geometry", value, "inner mean radius", inner_mean,
               "outer mean motion", outer_move, "minimum radius", min(deformed_radii))
        require(outer_move < 0.05, "Outer attachment moved too far")
        means.append(inner_mean)
    require(means[0] < means[1] < means[2], "Inner aperture did not open monotonically")
    report("STAGE 3 COMPLETE")


try:
    main()
except Exception:
    unreal.log_error("M4 stage 3 failed:\n" + traceback.format_exc())
    raise
