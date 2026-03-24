import bpy
import json


class SGE_PT_main_panel(bpy.types.Panel):
	bl_idname = "SGE_PT_main_panel"
	bl_label = "SGE Scene Setup"
	bl_category = "SGE"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'

	def draw(self, context):
		layout = self.layout
		layout.operator("sge.scene_init", icon='SCENE_DATA')


class SGE_PT_component_registry_panel(bpy.types.Panel):
	bl_idname = "SGE_PT_component_registry_panel"
	bl_label = "SGE Component Registry"
	bl_category = "SGE"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'

	def draw(self, context):
		layout = self.layout
		registry_raw = context.scene.get('sge_component_registry', None)

		if registry_raw is None:
			layout.label(text="No component types registered")
			return

		if isinstance(registry_raw, str):
			try:
				registry = json.loads(registry_raw)
			except json.JSONDecodeError:
				layout.label(text="Component registry is corrupted")
				return
		else:
			registry = dict(registry_raw)

		for component_name, properties in registry.items():
			box = layout.box()
			box.label(text=component_name, icon='OBJECT_DATA')
			for prop_key, prop_value in properties.items():
				row = box.row()
				delete_operator = row.operator("sge.delete_component_type", text="", icon='X')
				delete_operator.component_name = component_name
				edit_operator = row.operator("sge.edit_component_type", text="", icon='GREASEPENCIL')
				edit_operator.component_name = component_name
				edit_operator.properties_json = json.dumps(properties)
				row.label(text=f"{prop_key}: {prop_value}")
