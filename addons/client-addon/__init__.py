bl_info = {
    "name": "Open Pipeline",
    "author": "Joshua Palfrey",
    "version": (1, 0, 0),
    "blender": (5, 1, 0), # Minimum Blender version required
    "location": "View3D > Sidebar > Open Pipeline",
    "description": "Custom pipeline tools and UI.",
    "warning": "",
    "doc_url": "",
    "category": "Pipeline",
}

import bpy
from . import operators
from . import ui

modules = [
    operators,ui
]

def register():
    for module in modules:
        for cls in module.classes:
            bpy.utils.register_class(cls)
    
    # Custom properties on window
    bpy.types.WindowManager.OP_data = bpy.props.PointerProperty(type=ui.OP_props)

def startWatcher(*_):
    # Call after registration, needs a valid context so hook into load_post
    bpy.ops.op.messagewatcher('INVOKE_DEFAULT')

bpy.app.handlers.load_post.append(startWatcher)

def unregister():
    # Delete custom properties
    del bpy.types.WindowManager.OP_data

    bpy.app.handlers.load_post.remove(startWatcher)

    # Unregister classes in reverse order
    for module in reversed(modules):
        for cls in reversed(module.classes):
            bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()