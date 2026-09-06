import bpy


class CHIMNEY_PT_main_panel(bpy.types.Panel):
    bl_label = "Chimney Projection Mapping"
    bl_idname = "CHIMNEY_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Projection"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.chimney_projection_settings

        box = layout.box()
        box.label(text="Media (per-panel content)")
        box.prop(settings, "media_width")
        box.prop(settings, "media_height")
        box.prop(settings, "media_fps")
        box.prop(settings, "media_filepath")

        box = layout.box()
        box.label(text="Rough Geometry (update once measured)")
        box.prop(settings, "chimney_height_m")
        box.prop(settings, "base_radius_m")
        box.operator("chimney.match_radius_to_aspect", icon='UV')
        box.prop(settings, "top_radius_factor")
        box.prop(settings, "radial_segments")
        box.prop(settings, "ring_count")
        box.prop(settings, "seam_rotation_deg")

        layout.separator()
        layout.operator("chimney.build_rig", icon='MESH_CYLINDER')
        layout.operator("chimney.sync_timeline_to_media", icon='TIME')
        layout.operator("chimney.export_uv_template", icon='EXPORT')


classes = (CHIMNEY_PT_main_panel,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
