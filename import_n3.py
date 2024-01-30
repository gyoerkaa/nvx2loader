"""Library to import n3 data files"""

import bpy

from . import n3


def create_armature_object(am_name, n3joints, collection):
    """Create an armutre from a list of n3 node definitions."""
    # (joint_idx, parent_idx, translation, rotation, scale, name)
    # TODO: Create blender armature
    print(n3joints)
    am = bpy.data.armatures.new(am_name)

    ob = bpy.data.objects.new(am_name, am)
    collection.objects.link(ob)
    return ob


def create_material(mat_name, texture_list, blen_object=None):
    """Create a blender material and attach it to blender object."""
    # TODO: Create blender material
    print(mat_name)


def create_nvx2_mesh(nvx2_filepath, collection):
    """Create a blender object from an nvx2 mesh file."""
    # TODO: Use the nvx2loader to load models
    print(nvx2_filepath)


def load(context, operator, options, filepath=''):
    """Called by the user interface or another script."""
    n3parser = n3.Parser(operator, options)
    n3parser.parse_file(filepath)

    scene = context.scene
    collection = scene.collection

    operator.report({'INFO'}, "Output written to console.")

    # Create armature
    if options['create_armatures']:
        for n3node in n3parser.n3node_list:
            if n3node.joints:
                create_armature_object(n3node.node_name+"_armature", n3node.joints, collection)

    # Create meshes
    if options['import_meshes']:
        for n3node in n3parser.n3node_list:
            if n3node.mesh_ressource_id:
                mesh_filepath = n3node.mesh_ressource_id
                create_nvx2_mesh(mesh_filepath, collection)

    return {'FINISHED'}
