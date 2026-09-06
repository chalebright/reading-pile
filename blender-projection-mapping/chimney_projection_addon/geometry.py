import math

import bmesh
import bpy

OBJECT_NAME = "Chimney_StandIn"


def _height_fractions(ring_count):
    """Normalized (0..1) heights for the two caps plus evenly spaced coupling rings."""
    fracs = [0.0]
    for i in range(1, ring_count + 1):
        fracs.append(i / (ring_count + 1))
    fracs.append(1.0)
    return fracs


def build_chimney_mesh(settings):
    radial_segments = settings.radial_segments
    height = settings.chimney_height_m
    base_r = settings.base_radius_m
    top_r = base_r * settings.top_radius_factor
    seam_offset = math.radians(settings.seam_rotation_deg)

    fracs = _height_fractions(settings.ring_count)

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("ProjectionUV")

    rings = []
    for v_frac in fracs:
        z = v_frac * height
        r = base_r + (top_r - base_r) * v_frac
        ring_verts = []
        for i in range(radial_segments):
            angle = seam_offset + (2 * math.pi * i / radial_segments)
            ring_verts.append(bm.verts.new((r * math.cos(angle), r * math.sin(angle), z)))
        rings.append(ring_verts)

    bm.verts.ensure_lookup_table()

    for level in range(len(rings) - 1):
        bottom, top = rings[level], rings[level + 1]
        v_bottom, v_top = fracs[level], fracs[level + 1]
        for i in range(radial_segments):
            i2 = (i + 1) % radial_segments
            face = bm.faces.new((bottom[i], bottom[i2], top[i2], top[i]))
            u0, u1 = i / radial_segments, (i + 1) / radial_segments
            face.loops[0][uv_layer].uv = (u0, v_bottom)
            face.loops[1][uv_layer].uv = (u1, v_bottom)
            face.loops[2][uv_layer].uv = (u1, v_top)
            face.loops[3][uv_layer].uv = (u0, v_top)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.get(OBJECT_NAME)
    if mesh is None:
        mesh = bpy.data.meshes.new(OBJECT_NAME)
    else:
        mesh.clear_geometry()

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    obj = bpy.data.objects.get(OBJECT_NAME)
    if obj is None:
        obj = bpy.data.objects.new(OBJECT_NAME, mesh)
        bpy.context.collection.objects.link(obj)
    else:
        obj.data = mesh

    for name in list(obj.vertex_groups.keys()):
        obj.vertex_groups.remove(obj.vertex_groups[name])

    # Skip the first/last fraction (the caps) — only the interior fracs are coupling rings.
    for ring_idx, level in enumerate(range(1, len(fracs) - 1), start=1):
        vg = obj.vertex_groups.new(name=f"ring_{ring_idx}")
        vg.add([v.index for v in rings[level]], 1.0, 'REPLACE')

    return obj
