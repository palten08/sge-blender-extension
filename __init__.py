import bpy

from .menus import (
	SGE_MT_main_menu,
	SGE_MT_scene_init,
	SGE_MT_create_menu,
	SGE_MT_modify_menu,
	SGE_MT_export_menu,
	draw_menu,
)
from .panels import (
	SGE_PT_main_panel,
	SGE_PT_component_registry_panel,
)
from .operators.scene_init import SGE_OT_scene_init
from .operators.create import SGE_OT_create_entity, SGE_OT_create_component_type
from .operators.modify import SGE_OT_add_mesh_to_entity, SGE_OT_add_component_to_entity, SGE_OT_add_shading_model_to_material, SGE_OT_set_object_filepaths
from .operators.component_registry import SGE_OT_delete_component_type, SGE_OT_edit_component_type
from .operators.export import SGE_OT_export_scene, SGE_OT_set_scene_export_path

bl_info = {
	"name": "SGE Blender Extension",
	"blender": (5, 0, 0),
	"category": "Import-Export",
	"version": (0, 0, 1),
	"description": "Add on for authoring scenes for SGE",
}

classes = [
	SGE_MT_main_menu,
	SGE_MT_scene_init,
	SGE_MT_create_menu,
	SGE_MT_modify_menu,
	SGE_PT_main_panel,
	SGE_PT_component_registry_panel,
	SGE_OT_scene_init,
	SGE_OT_create_entity,
	SGE_OT_create_component_type,
	SGE_OT_add_mesh_to_entity,
	SGE_OT_add_component_to_entity,
	SGE_OT_delete_component_type,
	SGE_OT_edit_component_type,
	SGE_OT_export_scene,
	SGE_OT_add_shading_model_to_material,
	SGE_OT_set_object_filepaths,
	SGE_MT_export_menu,
	SGE_OT_set_scene_export_path,
]


def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.TOPBAR_MT_editor_menus.append(draw_menu)


def unregister():
	bpy.types.TOPBAR_MT_editor_menus.remove(draw_menu)
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)


if __name__ == "__main__":
	register()
