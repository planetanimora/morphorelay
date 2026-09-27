"""Generate the 12 radial bones and mathematical vertex weights for M4."""

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


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def main():
    assets = unreal.EditorAssetLibrary
    mesh = require(assets.load_asset(DEST + "/SK_M4_RadialMouth"), "Missing skeletal mesh")
    skeleton = require(assets.load_asset(DEST + "/SKEL_M4_RadialMouth"), "Missing skeleton")
    dynamic = unreal.DynamicMesh()
    dynamic, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(
        mesh, dynamic, unreal.GeometryScriptCopyMeshFromAssetOptions(), unreal.GeometryScriptMeshReadLOD()
    )
    vertex_count = dynamic.get_vertex_count()
    require(vertex_count > 0, "Skeletal mesh has no geometry: " + str(outcome))
    positions = []
    for vertex_id in range(vertex_count):
        position, valid = dynamic.get_vertex_position(vertex_id)
        require(valid, "Invalid vertex ID " + str(vertex_id))
        positions.append(position)
    radii = [math.hypot(p.y, p.z) for p in positions]
    inner, outer = min(radii), max(radii)
    require(outer > inner > 0.01, "Invalid annular radius range")
    rest_radius = inner + 0.28 * (outer - inner)
    report("Vertices", vertex_count, "inner", inner, "outer", outer, "rest bone radius", rest_radius)

    modifier = unreal.SkeletonModifier()
    require(modifier.set_skeletal_mesh(mesh), "Skeleton modifier setup failed")
    existing = {str(name) for name in modifier.get_all_bone_names()}
    require("M4_Root" in existing, "M4_Root missing")
    if "M4_MouthCenter" not in existing:
        require(modifier.add_bone("M4_MouthCenter", "M4_Root", unreal.Transform()), "Add center failed")
    for i in range(12):
        name = "M4_Radial_%02d" % i
        if name in existing:
            continue
        theta = math.tau * i / 12
        offset = unreal.Vector(0, rest_radius * math.sin(theta), rest_radius * math.cos(theta))
        require(modifier.add_bone(name, "M4_MouthCenter", unreal.Transform(location=offset)), "Add " + name + " failed")
    require(modifier.commit_skeleton_to_skeletal_mesh(), "Skeleton commit failed")
    report("Bones", list(modifier.get_all_bone_names()))

    weights = unreal.SkinWeightModifier()
    require(weights.set_skeletal_mesh(mesh), "Skin weight modifier setup failed")
    count = weights.get_num_vertices()
    require(count == vertex_count, "Vertex mapping differs after skeletal conversion: %d vs %d" % (count, vertex_count))
    span = outer - inner
    for vertex_id, p in enumerate(positions):
        radius = radii[vertex_id]
        normalized_radius = (radius - inner) / span
        radial_weight = 1.0 - smoothstep(0.15, 1.0, normalized_radius)
        sector = ((math.atan2(p.y, p.z) % math.tau) * 12 / math.tau)
        a = int(math.floor(sector)) % 12
        b = (a + 1) % 12
        blend = sector - math.floor(sector)
        influence = {"M4_MouthCenter": 1.0 - radial_weight}
        if radial_weight * (1.0 - blend) > 1e-6:
            influence["M4_Radial_%02d" % a] = radial_weight * (1.0 - blend)
        if radial_weight * blend > 1e-6:
            influence["M4_Radial_%02d" % b] = radial_weight * blend
        require(weights.set_vertex_weights(vertex_id, influence, True), "Weight assignment failed at %d" % vertex_id)
    require(weights.commit_weights_to_skeletal_mesh(), "Skin weight commit failed")
    require(assets.save_loaded_asset(mesh), "Saving skeletal mesh failed")
    require(assets.save_loaded_asset(skeleton), "Saving skeleton failed")
    report("STAGE 2 COMPLETE", "weighted vertices", count)


try:
    main()
except Exception:
    unreal.log_error("M4 stage 2 failed:\n" + traceback.format_exc())
    raise
