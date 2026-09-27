"""Capture one M4 aperture pose from the saved demo map."""

import os
import traceback
import unreal

try:
    unreal.EditorLevelLibrary.load_level("/Game/PlanetAnimora/POC/M4/MAP_M4_RadialMouth_POC")
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    mouth = next(a for a in actors if isinstance(a, unreal.M4RadialMouthPOCActor))
    camera = next(a for a in actors if isinstance(a, unreal.CameraActor))
    value = float(os.environ.get("M4_CAPTURE_APERTURE", "0.5"))
    mouth.set_editor_property("auto_oscillate", False)
    mouth.apply_aperture(value)
    output = os.path.join(
        unreal.Paths.project_saved_dir(),
        "M4_Aperture_%s.png" % str(value).replace(".", "p"))
    task = unreal.AutomationLibrary.take_high_res_screenshot(800, 800, output, camera)
    unreal.log("M4 CAPTURE TASK " + str(task))
except Exception:
    unreal.log_error("M4 capture failed:\n" + traceback.format_exc())
    raise
