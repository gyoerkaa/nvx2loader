# ##### BEGIN GPL LICENSE BLOCK #####
#
# nvx2loader. Copyright 2012-2017 Attila Gyoerkoes
#
# Neverblender is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Neverblender is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Neverblender.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

"""TODO: DOC."""


import os
import importlib

import bpy
import bpy_extras

from . import nvx2
from . import import_nvx2
from . import import_nax
from . import n3
from . import import_n3


bl_info = {
    "name": "nvx2loader",
    "author": "Attila Gyoerkoes",
    'version': (2, 0),
    "blender": (4, 0, 1),
    "location": "File > Import-Export",
    "description": "Import Nebula NVX files",
    "warning": "",
    "wiki_url": ""
                "",
    "tracker_url": "",
    "category": "Import-Export"}


def reload_package():
    """Enables reloading the entire add-on with 'Reload Scripts' from Blender"""
    importlib.reload(nvx2)
    importlib.reload(import_nvx2)
    importlib.reload(n3)
    importlib.reload(import_n3)
    importlib.reload(import_nax)


if "bpy" in locals():
    reload_package()


class ImportNVX2(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a Nebula NVX2 File"""
    bl_idname = "import_scene.nvx2"
    bl_label = "Import NVX2"
    bl_options = {'UNDO'}

    filename_ext = ".nvx2"
    filter_glob : bpy.props.StringProperty(default="*.nvx2", options={'HIDDEN'})
    files: bpy.props.CollectionProperty(
        name='File Path',
        description='Path used for importing the file',
        type=bpy.types.OperatorFileListElement)

    nvx2_version : bpy.props.EnumProperty(
            name="Engine Version",
            description="Nebula version this file was packed for",
            items=(('0', "Auto Detect", "", 0),
                   ('2', "Nebula 2", "", 2),
                   ('3', "Nebula 3", "", 3)),
            default='0')
    use_smooth : bpy.props.BoolProperty(
            name="Use Smooth",
            description="Sets all polygons to smooth",
            default=False)
    create_parent_empty : bpy.props.BoolProperty(
            name="Create Parent Empty",
            description="Creates an empty to which all imported objects will be parented to",
            default=True)
    create_uvs : bpy.props.BoolProperty(
            name="Create UV maps",
            description="Creates uv maps",
            default=True)
    create_weights : bpy.props.BoolProperty(
            name="Create Vertex Weights",
            description="Creates vertex weights",
            default=True)
    create_colors : bpy.props.BoolProperty(
            name="Create Vertex Colors",
            description="Creates colors weights",
            default=False)

    def import_file(self, context, filepath):
        """Imports a single nvx2 file"""
        options = nvx2.Options()
        options.use_smooth = self.use_smooth
        options.create_parent_empty  = self.create_parent_empty
        options.create_uvs  = self.create_uvs
        options.create_weights  = self.create_weights
        options.create_colors = self.create_colors

        options.nvx2filepath = filepath
        options.nvx2version = int(self.nvx2_version)

        return import_nvx2.load(context, self, options)

    def execute(self, context):
        # Multiple file import
        if self.files:
            ret = {'CANCELLED'}
            dirname = os.path.dirname(self.filepath)
            for file in self.files:
                path = os.path.join(dirname, file.name)
                if self.import_file(context, path) == {'FINISHED'}:
                    ret = {'FINISHED'}
            return ret

        # Single file import
        return self.import_file(context, self.filepath)


class ImportNAX(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a Nebula NAX2 File"""
    bl_idname = "import_scene.nax"
    bl_label = "Import NAX"
    bl_options = {'UNDO'}

    filename_ext = ".nax2"
    filter_glob : bpy.props.StringProperty(
            default="*.nax2",
            options={'HIDDEN'})

    def execute(self, context):
        options = import_nax.default_options

        return import_nax.load(context, options, self.filepath)


class ImportN3(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a Nebula N3 File"""
    bl_idname = "import_scene.n3"
    bl_label = "Import N3"
    bl_options = {'UNDO'}

    filename_ext = ".n3"
    filter_glob : bpy.props.StringProperty(
            default="*.n3",
            options={'HIDDEN'})

    ignore_version : bpy.props.BoolProperty(
            name="Ignore Version",
            description="Ignore file version",
            default=True)
    create_armatures : bpy.props.BoolProperty(
            name="Create Armatures",
            description="Create Armatures from n3 node data",
            default=True)
    create_materials : bpy.props.BoolProperty(
            name="Create Materials",
            description="Create Materials from n3 node data",
            default=True)
    reuse_materials : bpy.props.BoolProperty(
            name="Re-use Materials",
            description="Re-uses materials with the same name instead of creating new ones",
            default=False)
    use_image_search : bpy.props.BoolProperty(
            name="Image Search",
            description="Searches subdirs for any associated images (Warning, may be slow)",
            default=False)
    import_meshes : bpy.props.BoolProperty(
            name="Import Meshes",
            description="Atempt to import nvx2 meshes from references",
            default=True)

    def execute(self, context):
        options = n3.Options
        options.ignore_version = self.ignore_version
        options.create_armatures = self.create_armatures
        options.create_materials = self.create_materials
        options.import_meshes = self.import_meshes
        options.reuse_materials = self.reuse_materials
        options.use_image_search = self.use_image_search

        options.n3filepath = self.filepath

        return import_n3.load(context, self, options)


def menu_func_import(self, context):
    """Add menu functions for importing nebula files."""
    self.layout.operator(ImportNVX2.bl_idname, text="Nebula mesh (.nvx2)")
    #self.layout.operator(ImportNAX.bl_idname, text="Nebula animation (.nax2, .nax3)")
    self.layout.operator(ImportN3.bl_idname, text="Nebula model (.n3)")


def register():
    """Register all operators and menu entries."""
    bpy.utils.register_class(ImportNVX2)
    #bpy.utils.register_class(ImportNAX)
    bpy.utils.register_class(ImportN3)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    """Unregister all operators and menu entries."""
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

    bpy.utils.unregister_class(ImportN3)
    #bpy.utils.unregister_class(ImportNAX)
    bpy.utils.unregister_class(ImportNVX2)


if __name__ == "__main__":
    register()
