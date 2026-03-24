import bpy
from bpy.types import Operator
from ..utilities import (
	get_material_count, get_mesh_count, get_entity_count,
	generate_scene_file_header,
	serialize_directional_light, serialize_camera,
	serialize_material, serialize_mesh, serialize_entity,
	find_mesh_on_entity,
)


class SGE_OT_export_scene(Operator):
	bl_idname = "sge.export_scene"
	bl_label = "Export SGE Scene"
	bl_description = "Exports the current scene to a binary file format compatible with SGE"
	bl_options = {'REGISTER'}

	filepath: bpy.props.StringProperty(subtype='FILE_PATH')

	def invoke(self, context, event):
		default_path = context.scene.get('sge_export_path', bpy.path.abspath("//scene.sge"))
		self.filepath = default_path
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def execute(self, context):
		scene_data = self.serialize_scene(context)
		if scene_data is None:
			return {'CANCELLED'}

		with open(self.filepath, 'wb') as f:
			f.write(scene_data)

		context.scene['sge_export_path'] = self.filepath
		self.report({'INFO'}, f"Scene exported to {self.filepath} ({len(scene_data)} bytes)")
		return {'FINISHED'}

	def serialize_scene(self, context):
		material_count = get_material_count()
		mesh_count = get_mesh_count()
		entity_count = get_entity_count()

		# Header
		scene_data = generate_scene_file_header(material_count, mesh_count, entity_count)

		# Directional light (first Sun light found)
		sun_found = False
		for obj in context.scene.objects:
			if obj.type == 'LIGHT' and obj.data.type == 'SUN':
				scene_data += serialize_directional_light(obj)
				sun_found = True
				break
		if not sun_found:
			self.report({'ERROR'}, "No Sun light found in scene")
			return None

		# Camera (first camera found)
		camera_found = False
		for obj in context.scene.objects:
			if obj.type == 'CAMERA':
				scene_data += serialize_camera(obj)
				camera_found = True
				break
		if not camera_found:
			self.report({'ERROR'}, "No Camera found in scene")
			return None

		# Materials (only those with sge_shading_model)
		for mat in bpy.data.materials:
			if 'sge_shading_model' in mat:
				scene_data += serialize_material(mat)

		# Meshes (from SGE entities, deduplicated by mesh data name)
		serialized_meshes = set()
		for obj in context.scene.objects:
			if obj.type == 'EMPTY' and 'sge_entity_name' in obj:
				mesh_obj = find_mesh_on_entity(obj)
				if mesh_obj and mesh_obj.data.name not in serialized_meshes:
					scene_data += serialize_mesh(obj)
					serialized_meshes.add(mesh_obj.data.name)

		# Entities
		for obj in context.scene.objects:
			if obj.type == 'EMPTY' and 'sge_entity_name' in obj:
				scene_data += serialize_entity(obj)

		return scene_data


class SGE_OT_set_scene_export_path(Operator):
	bl_idname = "sge.set_scene_export_path"
	bl_label = "Set SGE Scene Export Path"
	bl_description = "Sets the file path for exporting the SGE scene"

	filepath: bpy.props.StringProperty(subtype="FILE_PATH")

	def execute(self, context):
		context.scene['sge_export_path'] = self.filepath
		self.report({'INFO'}, f"Export path set to: {self.filepath}")
		return {'FINISHED'}

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
