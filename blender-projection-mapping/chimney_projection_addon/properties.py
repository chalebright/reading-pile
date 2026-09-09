import bpy


class ChimneyProjectionSettings(bpy.types.PropertyGroup):
    # Media / content
    media_width: bpy.props.IntProperty(
        name="Media Width (px)",
        default=572,
        min=1,
        description="Width of the source content canvas, e.g. 572x2429",
    )
    media_height: bpy.props.IntProperty(
        name="Media Height (px)",
        default=2429,
        min=1,
        description="Height of the source content canvas, e.g. 572x2429",
    )
    media_fps: bpy.props.FloatProperty(
        name="Media FPS",
        default=30.0,
        min=1.0,
        description="Frame rate of the source video content, used by Sync Timeline",
    )
    media_filepath: bpy.props.StringProperty(
        name="Media File",
        subtype='FILE_PATH',
        description="Image or movie to load onto the stand-in material as a preview",
    )

    # Rough geometry — replace with real survey numbers once available
    chimney_height_m: bpy.props.FloatProperty(
        name="Height (m, rough)",
        default=30.0,
        min=0.1,
        description="Rough real-world height; update when real measurements are known",
    )
    base_radius_m: bpy.props.FloatProperty(
        name="Base Radius (m, rough)",
        default=1.2,
        min=0.01,
        description="Rough radius at the base; use 'Match Radius to Media Aspect' to avoid stretch on the demo cylinder",
    )
    top_radius_factor: bpy.props.FloatProperty(
        name="Top Radius Factor",
        default=1.0,
        min=0.05,
        max=1.0,
        description="1.0 = straight cylinder stand-in. Lower for a tapered frustum once the real profile is known.",
    )

    radial_segments: bpy.props.IntProperty(
        name="Radial Segments",
        default=48,
        min=8,
        max=256,
    )
    ring_count: bpy.props.IntProperty(
        name="Coupling Rings",
        default=2,
        min=0,
        max=8,
        description="Evenly spaced edge loops + vertex groups marking pipe-section joints, for later per-section masking",
    )
    seam_rotation_deg: bpy.props.FloatProperty(
        name="UV Seam Rotation",
        default=0.0,
        min=-180.0,
        max=180.0,
        description="Rotates the UV seam/mesh seam around the axis, e.g. to hide it from the main projector angle",
    )


def register():
    bpy.utils.register_class(ChimneyProjectionSettings)
    bpy.types.Scene.chimney_projection_settings = bpy.props.PointerProperty(
        type=ChimneyProjectionSettings
    )


def unregister():
    del bpy.types.Scene.chimney_projection_settings
    bpy.utils.unregister_class(ChimneyProjectionSettings)
