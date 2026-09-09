bl_info = {
    "name": "Chimney Projection Mapping Stand-in",
    "author": "chalebright",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Projection",
    "description": (
        "Builds a cylinder/frustum stand-in rig, cylindrical UV unwrap and "
        "emissive material for previz'ing chimney projection-mapping content"
    ),
    "category": "Object",
}

from . import properties, operators, panel

_modules = (properties, operators, panel)


def register():
    for module in _modules:
        module.register()


def unregister():
    for module in reversed(_modules):
        module.unregister()
