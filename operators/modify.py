import bpy
import json
import os
from bpy.types import Operator
from ..entity import add_mesh_component_to_sge_entity
from ..utilities import resolve_sge_entity, find_mesh_on_entity, find_material_on_entity, to_relative_path


class SGE_OT_add_mesh_to_entity(Operator):
	bl_idname = "sge.add_mesh_to_entity"
	bl_label = "Add Mesh Component to SGE Entity"
	bl_description = "Adds a selected mesh as a mesh component to the selected SGE entity"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		if len(context.selected_objects) != 2:
			self.report({'ERROR'}, "Please select exactly 2 objects: one SGE entity (or its child) and one mesh")
			return {'CANCELLED'}

		entity = None
		mesh_obj = None
		for obj in context.selected_objects:
			if obj.type == 'MESH' and mesh_obj is None:
				mesh_obj = obj
			else:
				resolved = resolve_sge_entity(obj)
				if resolved and entity is None:
					entity = resolved

		if not entity:
			entity = resolve_sge_entity(context.active_object)

		if not entity:
			self.report({'ERROR'}, "No SGE entity found in selection — select an entity or one of its children")
			return {'CANCELLED'}

		if not mesh_obj:
			self.report({'ERROR'}, "No mesh found in selection")
			return {'CANCELLED'}

		add_mesh_component_to_sge_entity(entity, mesh_obj)
		self.report({'INFO'}, f"Mesh component added to {entity.name}")
		return {'FINISHED'}


class SGE_OT_add_component_to_entity(Operator):
	bl_idname = "sge.add_component_to_entity"
	bl_label = "Add Component to SGE Entity"
	bl_description = "Adds a component to the selected SGE entity"
	bl_options = {'REGISTER', 'UNDO'}

	def get_component_types(self, context):
		registry = json.loads(context.scene.get('sge_component_registry', '{}'))
		return [(name, name, "") for name in registry.keys()]

	component_type: bpy.props.EnumProperty(
		name="Component Type",
		description="Type of component to add",
		items=get_component_types
	)

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		entity = resolve_sge_entity(context.active_object)
		if not entity:
			self.report({'ERROR'}, "No SGE entity found — select an entity or one of its children")
			return {'CANCELLED'}

		entity_name = entity.get('sge_entity_name', entity.name)
		registry = json.loads(context.scene.get('sge_component_registry', '{}'))
		template = registry.get(self.component_type, {})

		bpy.ops.object.empty_add(type='SINGLE_ARROW', location=entity.location)
		component = context.active_object
		component.name = f"SGE_{self.component_type}_{entity_name}"
		component.parent = entity
		component.matrix_parent_inverse = entity.matrix_world.inverted()
		component["sge_component_name"] = self.component_type

		for key, value in template.items():
			component[f"sge_{key}"] = value

		self.report({'INFO'}, f"Added {self.component_type} to {entity.name}")
		return {'FINISHED'}


class SGE_OT_add_shading_model_to_material(Operator):
	bl_idname = "sge.add_shading_model_to_material"
	bl_label = "Add SGE Shading Model"
	bl_description = "Adds a custom property to the material to specify the shading model for SGE"
	bl_options = {'REGISTER', 'UNDO'}

	shading_model_items: bpy.props.EnumProperty(
		name="Shading Model",
		description="Select a shading model for SGE",
		items=[
			('SHADING_FLAT', 'Flat', ''),
			('SHADING_PHONG', 'Phong', ''),
			('SHADING_PBR', 'PBR', ''),
		]
	)

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		entity = resolve_sge_entity(context.active_object)
		if entity:
			material = find_material_on_entity(entity)
		else:
			obj = context.active_object
			material = obj.active_material if obj else None

		if not material:
			self.report({'ERROR'}, "No material found on selection or its entity")
			return {'CANCELLED'}

		material["sge_shading_model"] = self.shading_model_items
		self.report({'INFO'}, f"Assigned SGE Shading Model '{self.shading_model_items}' to {material.name}")
		return {'FINISHED'}


class SGE_OT_set_object_filepaths(Operator):
	bl_idname = "sge.set_object_filepaths"
	bl_label = "Set SGE Object Filepaths"
	bl_description = "Sets custom properties on the object to store file paths for SGE"

	filepath: bpy.props.StringProperty(name="File Path", description="Path to the file for this object", subtype='FILE_PATH')

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def execute(self, context):
		entity = resolve_sge_entity(context.active_object)
		if not entity:
			self.report({'ERROR'}, "No SGE entity found — select an entity or one of its children")
			return {'CANCELLED'}

		entity_name = entity.get('sge_entity_name', entity.name)

		# Convert absolute path to relative (relative to .blend file location), normalize to forward slashes
		base_path = to_relative_path(self.filepath)

		mesh_component = next((child for child in entity.children if child.type == 'EMPTY' and child.name.startswith("SGE_mesh_")), None)
		if mesh_component:
			mesh_component["sge_mesh_filepath"] = f"{base_path}/{entity_name.lower()}.obj"

		mesh_obj = find_mesh_on_entity(entity)
		if mesh_obj and mesh_obj.active_material:
			material = mesh_obj.active_material
			material["sge_material_filepath"] = f"{base_path}/{material.name.lower()}.mtl"
			material["sge_texture_filepath"] = f"{base_path}/{material.name.lower()}.bmp"

		self.report({'INFO'}, f"Set SGE file paths for {entity_name}")
		return {'FINISHED'}
