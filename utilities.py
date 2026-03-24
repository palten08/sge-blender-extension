import bpy
import math
import os
import re
import struct
import mathutils

SHADING_MODEL_MAPPING = {
	'SHADING_FLAT': 0,
	'SHADING_PHONG': 1,
	'SHADING_PBR': 2,
}


def sanitize_name(name):
	return re.sub(r'[^A-Za-z0-9_]', '', name.replace(' ', '_'))


def to_relative_path(absolute_path):
	"""Convert an absolute path to a path relative to the .blend file's directory.
	Normalizes to forward slashes for cross-platform compatibility."""
	project_root = bpy.path.abspath("//")
	resolved = bpy.path.abspath(absolute_path).rstrip('/\\')
	try:
		relative = os.path.relpath(resolved, project_root)
	except ValueError:
		# On Windows, relpath fails if paths are on different drives
		relative = resolved
	return relative.replace('\\', '/')


def get_material_count():
	"""Count materials that have an sge_shading_model assigned."""
	count = 0
	for mat in bpy.data.materials:
		if 'sge_shading_model' in mat:
			count += 1
	return count


def get_mesh_count():
	"""Count unique meshes that belong to SGE entities."""
	seen_meshes = set()
	for obj in bpy.data.objects:
		entity = resolve_sge_entity(obj)
		if entity and entity == obj:
			mesh = find_mesh_on_entity(obj)
			if mesh and mesh.data.name not in seen_meshes:
				seen_meshes.add(mesh.data.name)
	return len(seen_meshes)


def get_entity_count():
	count = 0
	for obj in bpy.data.objects:
		if obj.type == 'EMPTY' and 'sge_entity_name' in obj:
			count += 1
	return count


def generate_scene_file_header(material_count, mesh_count, entity_count):
	header = struct.pack('<4sI', b'SGE0', 1)
	header += struct.pack('<III', material_count, mesh_count, entity_count)
	return header


def resolve_sge_entity(obj):
	"""Walk up the parent chain from any object to find the top-level SGE entity.
	An SGE entity is an Empty with an sge_entity_name custom property."""
	if obj is None:
		return None
	current = obj
	while current is not None:
		if current.type == 'EMPTY' and 'sge_entity_name' in current:
			return current
		current = current.parent
	return None


def find_mesh_on_entity(entity):
	"""Find the first mesh object under an SGE entity's hierarchy."""
	if entity is None:
		return None
	for child in entity.children:
		if child.type == 'MESH':
			return child
		for grandchild in child.children:
			if grandchild.type == 'MESH':
				return grandchild
	return None


def find_material_on_entity(entity):
	"""Find the active material on the first mesh under an SGE entity."""
	mesh = find_mesh_on_entity(entity)
	if mesh and mesh.active_material:
		return mesh.active_material
	return None


def find_material_on_mesh(mesh):
	"""Find the active material on a mesh object."""
	if mesh and mesh.active_material:
		return mesh.active_material
	return None


def get_single_component_on_entity(entity, component_name):
	for child in entity.children:
		if child.get('sge_component_name') == component_name:
			return child
	return None


def get_all_components_on_entity(entity):
	components = []
	for child in entity.children:
		if child.type == 'EMPTY' and 'sge_component_name' in child:
			components.append(child)
	return components


def get_component_count_on_entity(entity):
	count = 0
	for child in entity.children:
		if child.type == 'EMPTY' and 'sge_component_name' in child:
			count += 1
	return count


def pack_string(s):
	"""Pack a string as a length-prefixed byte sequence (uint32 length + UTF-8 bytes)."""
	encoded = s.encode('utf-8')
	return struct.pack('<I', len(encoded)) + encoded


def blender_to_engine_vec3(vec):
	"""Convert a Blender Z-up vector to engine Y-up: (x, y, z) -> (x, z, -y)."""
	return (vec[0], vec[2], -vec[1])


def blender_to_engine_euler(euler):
	"""Convert Blender Z-up euler rotation to engine Y-up.
	Swaps Y and Z axes for the rotation as well."""
	return (euler[0], euler[2], -euler[1])


def blender_to_engine_scale(scale):
	"""Convert Blender Z-up scale to engine Y-up: swap Y and Z."""
	return (scale[0], scale[2], scale[1])


def serialize_directional_light(light_object):
	"""Serialize a Blender Sun light object to binary. Converts Z-up to Y-up."""
	light_data = light_object.data
	direction = light_object.matrix_world.to_quaternion() @ mathutils.Vector((0.0, 0.0, -1.0))
	engine_direction = blender_to_engine_vec3(direction)
	ambient_intensity = light_data.get('sge_ambient_intensity', 0.1)

	serialized = struct.pack('<3f', *engine_direction)
	serialized += struct.pack('<3f', light_data.color[0], light_data.color[1], light_data.color[2])
	serialized += struct.pack('<f', light_data.energy)
	serialized += struct.pack('<f', ambient_intensity)
	return serialized


def serialize_camera(camera_object):
	"""Serialize a Blender Camera object to binary. Converts Z-up to Y-up."""
	camera_data = camera_object.data
	look_target = camera_data.get('sge_look_target', (0.0, 0.0, 0.0))

	engine_position = blender_to_engine_vec3(camera_object.location)
	engine_rotation = blender_to_engine_euler(camera_object.rotation_euler)
	engine_look_target = blender_to_engine_vec3(look_target)

	serialized = struct.pack('<3f', *engine_position)
	serialized += struct.pack('<3f', *engine_rotation)
	serialized += struct.pack('<3f', *engine_look_target)
	serialized += struct.pack('<f', camera_data.sensor_width / camera_data.sensor_height if camera_data.sensor_height > 0 else 1.25)
	serialized += struct.pack('<f', math.degrees(camera_data.angle))
	serialized += struct.pack('<f', camera_data.clip_start)
	serialized += struct.pack('<f', camera_data.clip_end)
	return serialized


def serialize_material(material):
	"""Serialize a material to binary. Referenced by name, engine assigns IDs at load time."""
	shading_model = SHADING_MODEL_MAPPING.get(material.get('sge_shading_model', 'SHADING_FLAT'), 0)
	file_path = material.get('sge_material_filepath', '')

	serialized = struct.pack('<I', shading_model)
	serialized += pack_string(material.name)
	serialized += pack_string(file_path)
	return serialized


def serialize_mesh(entity):
	"""Serialize mesh info from an SGE entity to binary. References material by name."""
	mesh_obj = find_mesh_on_entity(entity)
	if not mesh_obj:
		return b''

	mesh_component = None
	for child in entity.children:
		if child.type == 'EMPTY' and child.name.startswith('SGE_mesh_'):
			mesh_component = child
			break

	material = find_material_on_mesh(mesh_obj)
	material_name = material.name if material else ''
	mesh_filepath = mesh_component.get('sge_mesh_filepath', '') if mesh_component else ''

	serialized = pack_string(mesh_obj.data.name)
	serialized += pack_string(material_name)
	serialized += pack_string(mesh_filepath)
	return serialized


def serialize_entity(entity):
	"""Serialize an SGE entity and all its components to binary. Converts Z-up to Y-up. All references by name."""
	entity_name = entity.get('sge_entity_name', entity.name)

	# Transform data — convert from Blender Z-up to engine Y-up
	engine_position = blender_to_engine_vec3(entity.location)
	engine_rotation = blender_to_engine_euler(entity.rotation_euler)
	engine_scale = blender_to_engine_scale(entity.scale)
	transform_data = struct.pack('<3f', *engine_position)
	transform_data += struct.pack('<3f', *engine_rotation)
	transform_data += struct.pack('<3f', *engine_scale)

	# Collect custom components
	components = get_all_components_on_entity(entity)
	has_mesh = find_mesh_on_entity(entity) is not None

	# Total: transform (always) + mesh (if present) + custom components
	total_component_count = 1 + (1 if has_mesh else 0) + len(components)

	serialized = pack_string(entity_name)
	serialized += struct.pack('<I', total_component_count)

	# Transform component (always present)
	serialized += pack_string("transform")
	serialized += struct.pack('<I', 36)  # 9 floats * 4 bytes
	serialized += transform_data

	# Mesh component — stores mesh_name so engine can look it up
	if has_mesh:
		mesh_obj = find_mesh_on_entity(entity)
		mesh_name_packed = pack_string(mesh_obj.data.name)
		serialized += pack_string("mesh")
		serialized += struct.pack('<I', len(mesh_name_packed))
		serialized += mesh_name_packed

	# Custom components
	for component in components:
		component_name = component.get('sge_component_name', 'unknown')
		properties = {k: v for k, v in component.items() if k not in ['sge_component_id', 'sge_component_name']}

		prop_data = struct.pack('<I', len(properties))
		for prop_name, prop_value in properties.items():
			prop_data += pack_string(prop_name)
			if isinstance(prop_value, (int, float)):
				prop_data += struct.pack('<Bf', 0, float(prop_value))
			elif isinstance(prop_value, str):
				encoded = prop_value.encode('utf-8')
				prop_data += struct.pack('<BI', 1, len(encoded)) + encoded
			else:
				prop_data += struct.pack('<Bf', 0, 0.0)

		serialized += pack_string(component_name)
		serialized += struct.pack('<I', len(prop_data))
		serialized += prop_data

	return serialized
