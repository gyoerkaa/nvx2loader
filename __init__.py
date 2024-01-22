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

import bpy
import bpy_extras

from . import import_nvx2
from . import import_nax


# Enables the use of reloading the entire addon without restarting blender
if 'bpy' in locals():
    # Doing this in here: Importing this twice will result in an error
    import importlib
    # Checking for import_nvx2 is enough, if present: Already loaded,
    # explicity reload
    if 'import_nvx2' in locals():
        # reload main modules
        importlib.reload(import_nvx2)
        importlib.reload(import_nax)


bl_info = {
    "name": "nvx2loader",
    "author": "Attila Gyoerkoes",
    'version': (2, 0),
    "blender": (4, 0, 0),
    "location": "File > Import-Export",
    "description": "Import Nebula NVX files",
    "warning": "",
    "wiki_url": ""
                "",
    "tracker_url": "",
    "category": "Import-Export"}


class ImportNVX2(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a Nebula NVX2 File"""
    bl_idname = "import_scene.nvx2"
    bl_label = "Import NVX2"
    bl_options = {'UNDO'}

    filename_ext = ".nvx2"
    filter_glob : bpy.props.StringProperty(default="*.nvx2", options={'HIDDEN'})

    reuse_materials : bpy.props.BoolProperty(
            name="Re-use Materials",
            description="Re-uses materials with the same name instead of creating new ones",
            default=False)
    use_image_search : bpy.props.BoolProperty(
            name="Image Search",
            description="Searches subdirs for any associated images (Warning, may be slow)",
            default=False)
    use_smooth : bpy.props.BoolProperty(
            name="Use Smooth",
            description="Sets all polygons to smooth",
            default=False)
    create_parent_empty : bpy.props.BoolProperty(
            name="Create Parent Empty",
            description="Creates an empty to which all imported objects will be parented to",
            default=True)
    create_weights : bpy.props.BoolProperty(
            name="Create Vertex Weights",
            description="Creates vertex weights",
            default=True)
    create_colors : bpy.props.BoolProperty(
            name="Create Vertex Colors",
            description="Creates colors weights",
            default=False)

    def execute(self, context):
        options = import_nvx2.default_options
        options["reuse_materials"]  = self.reuse_materials
        options["reuse_textures"]  = self.reuse_materials
        options["use_image_search"] = self.use_image_search
        options["use_smooth"] = self.use_smooth
        options["create_parent_empty"]  = self.create_parent_empty
        options["create_weights"]  = self.create_weights
        options["create_colors"]  = self.create_colors

        return import_nvx2.load(context, options, self.filepath)


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


def menu_func_import(self, context):
    """TODO:Doc."""
    self.layout.operator(ImportNVX2.bl_idname, text="Nebula mesh (.nvx2)")
    # self.layout.operator(ImportNAX.bl_idname, text="Nebula animation (.nax2, .nax3)")


def register():
    """TODO:Doc."""
    bpy.utils.register_class(ImportNVX2)
    bpy.utils.register_class(ImportNAX)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    """TODO:Doc."""
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

    bpy.utils.unregister_class(ImportNAX)
    bpy.utils.unregister_class(ImportNVX2)


if __name__ == "__main__":
    register()