import bpy
from .utilities import sanitize_name


def create_empty_sge_entity(name="SGE_Entity"):
	name = sanitize_name(name)
	bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
	empty = bpy.context.active_object
	empty.name = name
	empty['sge_entity_name'] = name
	return empty


def add_mesh_component_to_sge_entity(entity, mesh):
	entity_name = entity.get('sge_entity_name', entity.name)
	bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
	mesh_component_empty = bpy.context.active_object
	mesh_component_empty.name = f"SGE_mesh_{entity_name}"
	mesh_component_empty.parent = entity
	mesh_component_empty.matrix_parent_inverse = entity.matrix_world.inverted()

	mesh.parent = mesh_component_empty
	mesh.matrix_parent_inverse = mesh_component_empty.matrix_world.inverted()
