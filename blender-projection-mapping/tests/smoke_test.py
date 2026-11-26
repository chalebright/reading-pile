"""
Headless regression check for the chimney_projection_addon.

Run with:
    blender --background --factory-startup --python tests/smoke_test.py

Exits non-zero (and prints a traceback) on failure, so it can be wired into
CI or run by hand after touching geometry.py / materials.py / operators.py.
"""
import math
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bpy
import mathutils


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def run():
    from chimney_projection_addon import geometry, materials, register, unregister

    register()
    try:
        settings = bpy.context.scene.chimney_projection_settings

        # --- build + geometry sanity ---
        bpy.ops.chimney.build_rig()
        obj = bpy.data.objects.get(geometry.OBJECT_NAME)
        check(obj is not None, "build_rig did not create the stand-in object")
        check(len(obj.data.vertices) > 0, "stand-in mesh has no vertices")
        check(
            [vg.name for vg in obj.vertex_groups] == ["ring_1", "ring_2"],
            f"unexpected vertex groups for default ring_count=2: {[vg.name for vg in obj.vertex_groups]}",
        )

        bad_normals = 0
        for poly in obj.data.polygons:
            radial = mathutils.Vector((poly.center.x, poly.center.y, 0))
            if radial.length > 1e-6 and radial.normalized().dot(poly.normal) < 0:
                bad_normals += 1
        check(bad_normals == 0, f"{bad_normals} faces have inward-facing normals")

        # --- match-radius-to-aspect math ---
        bpy.ops.chimney.match_radius_to_aspect()
        expected = (settings.chimney_height_m * settings.media_width / settings.media_height) / (2 * math.pi)
        check(
            math.isclose(settings.base_radius_m, expected, rel_tol=1e-6),
            "match_radius_to_aspect did not set the expected radius",
        )

        # --- rebuild is idempotent: no duplicate datablocks, params take effect ---
        settings.ring_count = 3
        settings.radial_segments = 32
        bpy.ops.chimney.build_rig()
        bpy.ops.chimney.build_rig()

        objs = [o for o in bpy.data.objects if geometry.OBJECT_NAME in o.name]
        meshes = [m for m in bpy.data.meshes if geometry.OBJECT_NAME in m.name]
        mats = [m for m in bpy.data.materials if materials.MATERIAL_NAME in m.name]
        check(len(objs) == 1, f"expected exactly 1 stand-in object, found {len(objs)}")
        check(len(meshes) == 1, f"expected exactly 1 stand-in mesh, found {len(meshes)}")
        check(len(mats) == 1, f"expected exactly 1 stand-in material, found {len(mats)}")

        obj = bpy.data.objects.get(geometry.OBJECT_NAME)
        check(
            [vg.name for vg in obj.vertex_groups] == ["ring_1", "ring_2", "ring_3"],
            "vertex groups did not update after changing ring_count",
        )

        # --- rebuilding must not clobber manual material node edits ---
        mat = bpy.data.materials.get(materials.MATERIAL_NAME)
        mapping = mat.node_tree.nodes["Mapping"]
        mapping.inputs["Location"].default_value[1] = 0.42
        bpy.ops.chimney.build_rig()
        mat_after = bpy.data.materials.get(materials.MATERIAL_NAME)
        check(mat_after is mat, "rebuild replaced the material datablock")
        check(
            math.isclose(mat_after.node_tree.nodes["Mapping"].inputs["Location"].default_value[1], 0.42, rel_tol=1e-4),
            "rebuild reset a manual Mapping node tweak",
        )

        # --- sync_timeline_to_media: no media -> a reported error, not an unhandled crash ---
        # bpy.ops raises RuntimeError for an operator's ERROR-level report; that's the
        # expected, deliberate path here (see operators.CHIMNEY_OT_sync_timeline_to_media).
        try:
            bpy.ops.chimney.sync_timeline_to_media()
            raise AssertionError("expected sync_timeline_to_media to report an error with no media loaded")
        except RuntimeError as exc:
            check("No media loaded" in str(exc), f"unexpected error message: {exc}")

        # --- sync_timeline_to_media with a real image ---
        tmp_image_path = "/tmp/chimney_smoke_test_media.png"
        img = bpy.data.images.new("smoke_test_media", width=settings.media_width, height=settings.media_height)
        img.filepath_raw = tmp_image_path
        img.file_format = 'PNG'
        img.save()
        settings.media_filepath = tmp_image_path
        bpy.ops.chimney.build_rig()  # repoints the existing ProjectionMedia node at the new file
        result = bpy.ops.chimney.sync_timeline_to_media()
        check(result == {'FINISHED'}, f"sync_timeline_to_media failed with real media: {result}")
        check(bpy.context.scene.frame_start == 1, "frame_start not set to 1 for a still image")

        print("SMOKE TEST: ALL CHECKS PASSED")
    finally:
        unregister()


if __name__ == "__main__":
    try:
        run()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
