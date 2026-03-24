import bpy
from bpy.types import Operator
from ..scene_setup import delete_existing_scene_tree, create_default_sge_camera, create_default_sge_light


class SGE_OT_scene_init(Operator):
	bl_idname = "sge.scene_init"
	bl_label = "Initialize Scene for SGE"
	bl_description = "Initializes a blank scene with basic objects and their settings for use in an SGE project"

	def execute(self, context):
		delete_existing_scene_tree()
		create_default_sge_camera()
		create_default_sge_light()
		self.report({'INFO'}, "Scene initialized for SGE")
		return {'FINISHED'}
