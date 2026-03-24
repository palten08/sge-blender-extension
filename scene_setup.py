import bpy


def delete_existing_scene_tree():
	bpy.ops.object.select_all(action='SELECT')
	bpy.ops.object.delete(use_global=False)

	for collection in bpy.data.collections:
		bpy.data.collections.remove(collection)


def create_default_sge_camera():
	bpy.ops.object.camera_add(location=(0, -5, 5), rotation=(1.1, 0, 0))
	camera = bpy.context.active_object
	camera.name = "SGE_Camera"
	camera.data.lens = 35
	camera.data.clip_start = 0.1
	camera.data.clip_end = 1000
	camera.data.sensor_width = 36
	camera.data.sensor_height = 24
	camera.data['sge_look_target'] = (0, 0, 0)
	return camera


def create_default_sge_light():
	bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
	light = bpy.context.active_object
	light.name = "SGE_Directional_Light"
	light.data.energy = 1
	light.data['sge_ambient_intensity'] = 0.1
	light.data['sge_direction'] = (0, 0, -1)
	return light
