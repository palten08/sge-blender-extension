import bpy
import json
from bpy.types import Operator


class SGE_OT_delete_component_type(Operator):
	bl_idname = "sge.delete_component_type"
	bl_label = "Delete Component Type"
	bl_description = "Deletes a component type from the registry"
	bl_options = {'REGISTER', 'UNDO'}

	component_name: bpy.props.StringProperty(name="Component Name")

	def execute(self, context):
		registry = json.loads(context.scene.get('sge_component_registry', '{}'))
		if self.component_name in registry:
			del registry[self.component_name]
			context.scene['sge_component_registry'] = json.dumps(registry)
			for obj in bpy.data.objects:
				if obj.type == 'EMPTY' and obj.get("sge_entity_id") is not None:
					for child in obj.children:
						if child.name == f"SGE_{self.component_name}":
							bpy.data.objects.remove(child, do_unlink=True)
			self.report({'INFO'}, f"Deleted component type: {self.component_name}")
			return {'FINISHED'}
		else:
			self.report({'ERROR'}, f"Component type not found: {self.component_name}")
			return {'CANCELLED'}


class SGE_OT_edit_component_type(Operator):
	bl_idname = "sge.edit_component_type"
	bl_label = "Edit Component Type"
	bl_description = "Edits a component type in the registry"
	bl_options = {'REGISTER', 'UNDO'}

	component_name: bpy.props.StringProperty(name="Component Name")
	properties_json: bpy.props.StringProperty(name="Properties (JSON)")

	def invoke(self, context, event):
		registry = json.loads(context.scene.get('sge_component_registry', '{}'))
		if self.component_name in registry:
			self.properties_json = json.dumps(registry[self.component_name])
		else:
			self.report({'ERROR'}, f"Component type not found: {self.component_name}")
			return {'CANCELLED'}
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		registry = json.loads(context.scene.get('sge_component_registry', '{}'))
		registry[self.component_name] = json.loads(self.properties_json)
		context.scene['sge_component_registry'] = json.dumps(registry)
		self.report({'INFO'}, f"Updated component type: {self.component_name}")
		return {'FINISHED'}
