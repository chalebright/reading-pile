import math

import bpy

from . import geometry, materials


class CHIMNEY_OT_build_rig(bpy.types.Operator):
    bl_idname = "chimney.build_rig"
    bl_label = "Build / Rebuild Chimney Stand-in"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.chimney_projection_settings
        obj = geometry.build_chimney_mesh(settings)
        mat = materials.build_stand_in_material(settings)
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        self.report({'INFO'}, f"Built {obj.name} ({settings.radial_segments} radial segments)")
        return {'FINISHED'}


class CHIMNEY_OT_match_radius_to_aspect(bpy.types.Operator):
    bl_idname = "chimney.match_radius_to_aspect"
    bl_label = "Match Radius to Media Aspect"
    bl_description = (
        "Set base radius so the unwrapped circumference matches the media "
        "aspect ratio at the current height, avoiding stretch on the demo cylinder"
    )
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.chimney_projection_settings
        aspect = settings.media_width / settings.media_height
        settings.base_radius_m = (settings.chimney_height_m * aspect) / (2 * math.pi)
        return {'FINISHED'}


class CHIMNEY_OT_sync_timeline_to_media(bpy.types.Operator):
    bl_idname = "chimney.sync_timeline_to_media"
    bl_label = "Sync Timeline to Media"
    bl_description = "Set scene frame range and fps from the loaded media"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.chimney_projection_settings
        mat = bpy.data.materials.get(materials.MATERIAL_NAME)
        if mat is None or not mat.use_nodes:
            self.report({'ERROR'}, "Build the rig first")
            return {'CANCELLED'}

        image_node = mat.node_tree.nodes.get(materials.IMAGE_NODE_NAME)
        if image_node is None or image_node.image is None:
            self.report({'ERROR'}, "No media loaded on the ProjectionMedia texture node")
            return {'CANCELLED'}

        image = image_node.image
        scene = context.scene
        scene.frame_start = 1
        scene.frame_end = max(1, image.frame_duration) if image.source == 'MOVIE' else 1
        scene.render.fps = round(settings.media_fps)
        self.report(
            {'INFO'},
            f"Timeline synced: {scene.frame_start}-{scene.frame_end} @ {scene.render.fps}fps",
        )
        return {'FINISHED'}


class CHIMNEY_OT_export_uv_template(bpy.types.Operator):
    bl_idname = "chimney.export_uv_template"
    bl_label = "Export UV Template"
    bl_description = "Export a PNG UV layout at the media resolution, for artists to paint/animate against"
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty(subtype='FILE_PATH', default="//uv_template.png")

    def execute(self, context):
        settings = context.scene.chimney_projection_settings
        obj = bpy.data.objects.get(geometry.OBJECT_NAME)
        if obj is None:
            self.report({'ERROR'}, "Build the rig first")
            return {'CANCELLED'}

        view_layer = context.view_layer
        for o in view_layer.objects:
            o.select_set(False)
        obj.select_set(True)
        view_layer.objects.active = obj

        prev_mode = obj.mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.export_layout(filepath=self.filepath, size=(settings.media_width, settings.media_height))
        bpy.ops.object.mode_set(mode=prev_mode)

        self.report({'INFO'}, f"UV template exported to {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


classes = (
    CHIMNEY_OT_build_rig,
    CHIMNEY_OT_match_radius_to_aspect,
    CHIMNEY_OT_sync_timeline_to_media,
    CHIMNEY_OT_export_uv_template,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
