import bpy

panelName = "Open Pipeline"

# --- Pipeline Variables Stored in the WindowManager
class OP_props(bpy.types.PropertyGroup):
    episode: bpy.props.StringProperty(name="episode",default="101")
    sequence: bpy.props.StringProperty(name="sequence",default="010")
    shot: bpy.props.StringProperty(name="shot",default="010")

# --- PANELS ---
class OP_infoPanel(bpy.types.Panel):
    bl_idname = "OP_PT_info"
    bl_label = "Current File Info"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = panelName

    def draw(self,context):
        layout = self.layout
        layout.label(text="Pipeline Tools:", icon='TOOL_SETTINGS')

class OP_savePanel(bpy.types.Panel):
    bl_idname = "OP_PT_save"
    bl_label = "Save/Publish"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = panelName

    def draw(self,context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("op.save", text="Save")
        row.operator("op.savenew", text="Save Increment")
        
        layout.operator("op.publish", text="Publish")

class OP_loadAssetPanel(bpy.types.Panel):
    bl_idname = "OP_PT_loadAsset"
    bl_label = "Load Asset"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = panelName

    def draw(self,context):
        layout = self.layout

        #row = layout.row(align=True)
        layout.operator("op.loadasset", text="Load Asset")

# We store classes here so __init__.py can easily grab them
classes = (
    OP_infoPanel,
    OP_savePanel,
    OP_loadAssetPanel,
    OP_props
)