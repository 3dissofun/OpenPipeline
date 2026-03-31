import bpy
import requests
import threading
import os
import sys

projectDir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.normpath(projectDir))

import utils
from . import messageStack

# --- METHODS (for threading and utlity) ---
def publishThread(url,payload):
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("Publish finished with code 200")
            messageStack.add("Publish finished with code 200")
        else:
            print(f"ERROR: Publish Failed with code: {response.status_code}")
            messageStack.add(f"ERROR: Publish Failed with code: {response.status_code}")

    except Exception as e:
        print(f"ERROR: Background Publish Failed: {e}")
        messageStack.add(f"ERROR: Background Publish Failed: {e}")


# --- OPERATORS (The Buttons) ---
class OP_save(bpy.types.Operator):
    """Save the current file"""
    bl_idname = "op.save"
    bl_label = "Save"
    bl_options = {'REGISTER'}

    def execute(self,context):
        currentPath = bpy.data.filepath
        if not currentPath: # File has never been saved
            bpy.ops.wm.save_as_mainfile('INVOKE_DEFAULT')
            return{'CANCELLED'}
        
        bpy.ops.wm.save_mainfile()
        self.report({'INFO'}, "Saved file")
        return {'FINISHED'}

class OP_saveNew(bpy.types.Operator):
    """Save a version of the current file"""
    bl_idname = "op.savenew"
    bl_label = "Save Increment"
    bl_options = {'REGISTER'}

    def invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self,context):
        currentPath = bpy.data.filepath
        if not currentPath: # File has never been saved
            bpy.ops.wm.save_as_mainfile('INVOKE_DEFAULT')
            return{'CANCELLED'}
        
        self.report({'INFO'}, "Saved as new version")
        return {'FINISHED'}

class OP_publish(bpy.types.Operator):
    """Publish the current task"""
    bl_idname = "op.publish"
    bl_label = "Publish"
    bl_options = {'REGISTER'}

    def invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self,context):
        self.report({'INFO'}, "Publishing in background")
        filePath = bpy.data.filepath
        fileName = os.path.basename(filePath)

        passed,message = utils.publishChecks(filePath)
        if not passed:
            self.report({'ERROR'}, f"Failed Publishing check with error: {message}")
            return{'FINISHED'}

        payload = {"name":fileName,
                   "path":filePath}
        url = "http://127.0.0.1:5000/publish"

        # Wait for response in BG
        thread = threading.Thread(target=publishThread,args=(url,payload))
        thread.start()

        return {'FINISHED'}

class OP_loadAsset(bpy.types.Operator):
    """Load the selected asset task"""
    bl_idname = "op.loadasset"
    bl_label = "Load Asset"

    def invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self,context):
        self.report({'INFO'}, "Loaded Asset")
        return {'FINISHED'}


class OP_MessageWatcher(bpy.types.Operator):
    bl_idname = "op.messagewatcher"
    bl_label = "Message Watcher"
    bl_options = {'INTERNAL'}

    _timer = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            if not messageStack.isEmpty():
                newMsg = messageStack.pop()
                if newMsg:
                    reportType = 'ERROR' if "ERROR" in newMsg else 'INFO'
                    self.report({reportType}, newMsg)

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

classes = (
    OP_saveNew,
    OP_save,
    OP_publish,
    OP_loadAsset,
    OP_MessageWatcher
)