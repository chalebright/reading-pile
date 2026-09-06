import bpy

MATERIAL_NAME = "Chimney_ProjectionStandIn"
IMAGE_NODE_NAME = "ProjectionMedia"


def build_stand_in_material(settings):
    mat = bpy.data.materials.get(MATERIAL_NAME)
    if mat is None:
        mat = bpy.data.materials.new(MATERIAL_NAME)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (400, 0)

    # Emission, not Principled BSDF: projected content is self-lit, not scene-lit.
    emission = nodes.new("ShaderNodeEmission")
    emission.location = (150, 0)
    emission.inputs["Strength"].default_value = 1.0

    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-600, 0)

    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-400, 0)

    image_tex = nodes.new("ShaderNodeTexImage")
    image_tex.location = (-150, 0)
    image_tex.name = IMAGE_NODE_NAME
    image_tex.extension = 'EXTEND'

    if settings.media_filepath:
        try:
            image_tex.image = bpy.data.images.load(settings.media_filepath, check_existing=True)
        except RuntimeError:
            pass

    links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], image_tex.inputs["Vector"])
    links.new(image_tex.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])

    return mat
