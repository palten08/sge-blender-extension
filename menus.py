from bpy.types import Menu


class SGE_MT_main_menu(Menu):
	bl_idname = "SGE_MT_main_menu"
	bl_label = "SGE"

	def draw(self, context):
		layout = self.layout
		layout.menu("SGE_MT_scene_init", icon='SCENE_DATA')
		layout.separator()
		layout.menu("SGE_MT_create_menu", icon='ADD')
		layout.separator()
		layout.menu("SGE_MT_modify_menu", icon='MODIFIER')
		layout.separator()
		layout.menu("SGE_MT_export_menu", icon='EXPORT')


class SGE_MT_scene_init(Menu):
	bl_idname = "SGE_MT_scene_init"
	bl_label = "Scene Initialization"

	def draw(self, context):
		layout = self.layout
		layout.operator("sge.scene_init", icon='SCENE_DATA')


class SGE_MT_create_menu(Menu):
	bl_idname = "SGE_MT_create_menu"
	bl_label = "Create SGE Objects"

	def draw(self, context):
		layout = self.layout
		layout.operator("sge.create_entity", icon='ADD')
		layout.operator("sge.create_component_type", icon='ADD')


class SGE_MT_modify_menu(Menu):
	bl_idname = "SGE_MT_modify_menu"
	bl_label = "Modify selected SGE Object"

	def draw(self, context):
		layout = self.layout
		layout.operator("sge.add_mesh_to_entity", icon='MESH_CUBE')
		layout.operator("sge.add_component_to_entity", icon='ADD')
		layout.operator("sge.add_shading_model_to_material", icon='MATERIAL')
		layout.operator("sge.set_object_filepaths", icon='FILE_FOLDER')


class SGE_MT_export_menu(Menu):
	bl_idname = "SGE_MT_export_menu"
	bl_label = "Export SGE Scene"

	def draw(self, context):
		layout = self.layout
		layout.operator("sge.set_scene_export_path", icon='FILE_FOLDER')
		layout.operator("sge.export_scene", icon='EXPORT')


def draw_menu(self, context):
	self.layout.menu("SGE_MT_main_menu")

