import bpy
import json
from bpy.types import Operator
from ..entity import create_empty_sge_entity


class SGE_OT_create_entity(Operator):
	bl_idname = "sge.create_entity"
	bl_label = "Create SGE Entity"
	bl_description = "Creates a new entity with SGE-specific properties"
	bl_options = {'REGISTER', 'UNDO'}

	entity_name: bpy.props.StringProperty(name="Name")

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		create_empty_sge_entity(name=self.entity_name)
		self.report({'INFO'}, "SGE entity created")
		return {'FINISHED'}


class SGE_OT_create_component_type(Operator):
	bl_idname = "sge.create_component_type"
	bl_label = "Create SGE Component Type"
	bl_description = "Creates a new component type that can be added to SGE entities"
	bl_options = {'REGISTER', 'UNDO'}

	component_name: bpy.props.StringProperty(name="Name")
	properties_json: bpy.props.StringProperty(name="Properties (JSON)", default='{"custom_property": 1.0}')

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		registry = json.loads(context.scene.get('sge_component_registry', '{}'))
		registry[self.component_name] = json.loads(self.properties_json)
		context.scene['sge_component_registry'] = json.dumps(registry)
		self.report({'INFO'}, f"Registered component type: {self.component_name}")
		return {'FINISHED'}
