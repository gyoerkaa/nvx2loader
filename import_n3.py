"""Library to import n3 data files"""

import os
import pathlib
import bpy
import bpy_extras.image_utils

from . import n3
from . import nvx2
from . import import_nvx2


def find_dir(start_dir, dirname_to_search_for):
    """Loop through dirs (going up) until one contains the desired dirname."""
    # Might be in start dir
    if os.path.isdir(os.path.join(start_dir, dirname_to_search_for)):
        return os.path.join(start_dir, dirname_to_search_for)
    # Check parent dirs
    for parent_dir in pathlib.Path(start_dir).parents:
        if os.path.isdir(os.path.join(parent_dir, dirname_to_search_for)):
            return os.path.join(parent_dir, dirname_to_search_for)

    return ""


def create_armature(am_name, n3joints, collection):
    """Create an armutre from a list of n3 node definitions."""
    # n3joints = list of (joint_idx, parent_idx, translation, rotation, scale, name)

    am = bpy.data.armatures.new(am_name)
    # TODO: Create bones
    ob = bpy.data.objects.new(am_name, am)
    collection.objects.link(ob)
    return ob


def create_image(n3_texture_res, options: n3.Options):
    """Helper function to load image files into blender images."""
    img_path = n3_texture_res[4:]
    img_dir, img_name = os.path.split(img_path)

    possible_paths_list = []

    # Attempt to find existing blender image
    if options.reuse_images and img_name in bpy.data.images:
        return bpy.data.images[img_name]

    # Case 1: Texture is in same directory as the n3file
    n3_path = options.n3filepath
    n3_dir, _ = os.path.split(n3_path)
    possible_path = os.path.join(n3_dir, img_name)
    possible_paths_list.append(possible_path)

    # Case 2: Search in typical nebula project structure
    # root/anims/... => nax an nac files
    # root/models/... => n3 files
    # root/meshes/... => nvx2 files
    # root/textures/... => textures (WE WANT THIS)
    project_tex_dir = find_dir(n3_dir, "textures")
    possible_path = os.path.join(project_tex_dir, img_dir)
    possible_path = os.path.normpath(possible_path)
    if os.path.isdir(possible_path):
        possible_path = os.path.join(possible_path, img_name)
        possible_paths_list.append(possible_path)

    # Attempt to load one of the images in path list
    # One is enough!
    img = None
    for pp in possible_paths_list:
        img = bpy_extras.image_utils.load_image(img_name + '.dds',
                                                pp,
                                                recursive=options.use_image_search,
                                                place_holder=False,
                                                ncase_cmp=True)
        if img:
            break

    # Create dummy image, if none was found
    if img:
        img.name = img_name
    else:
        print('WARNING: Could not load image ' + img_name)
        img = bpy.data.images.new(img_name, 512, 512)

    return img


def create_material(material_name, texture_list, options: n3.Options):
    """Create a blender material and attach it to blender object."""
    # Try to re-use existing material with the same name
    if options.reuse_materials and material_name in bpy.data.materials:
        return bpy.data.materials[material_name]

    # Create new material
    blen_material = bpy.data.materials.new(material_name)
    blen_material.use_nodes = True
    blen_material.node_tree.nodes.clear()
    nodes = blen_material.node_tree.nodes
    links = blen_material.node_tree.links

    # Create an output node
    node_out = nodes.new('ShaderNodeOutputMaterial')
    node_out.label = "nvx2_output"
    node_out.location = (936, 577)

    # Create shader node
    node_shader = nodes.new('ShaderNodeBsdfPrincipled')
    node_shader.name = 'shader_bsdf'
    node_shader.location = (-81, 552)
    # Connect to output
    links.new(node_out.inputs[0], node_shader.outputs[0])

    # Create Diffuse texture node
    node_diff_tex = nodes.new('ShaderNodeTexImage')
    node_diff_tex.label = "Texture: Diffuse"
    node_diff_tex.name = "nvx2_tex_diffuse"
    node_diff_tex.location = (-2000, 763)
    texture = texture_list['DiffMap0']
    if texture:
        node_diff_tex.image = create_image(texture, options)
        node_diff_tex.image.colorspace_settings.name = 'sRGB'
    # Connect to shader
    links.new(node_shader.inputs['Alpha'], node_diff_tex.outputs['Alpha'])
    links.new(node_shader.inputs['Base Color'], node_diff_tex.outputs['Color'])

    # Create specular texture node
    node_spec_tex = nodes.new('ShaderNodeTexImage')
    node_spec_tex.label = "Texture: Specular"
    node_spec_tex.name = "nvx2_tex_specular"
    node_spec_tex.location = (-1373, 371)
    texture = texture_list['SpecMap0']
    if texture:
        node_spec_tex.image = create_image(texture, options)
        node_spec_tex.image.colorspace_settings.name = 'Non-Color'
    # Connect to shader
    links.new(node_shader.inputs[13], node_spec_tex.outputs['Color'])

    # Create Normal/Bump node
    node_bump = nodes.new('ShaderNodeBump')
    node_bump.name = "nvx2_bump"
    node_bump.location = (-384, -232)
    node_bump.invert = True
    links.new(node_shader.inputs['Normal'], node_bump.outputs['Normal'])
    # Create bump texture node
    node_bump_tex = nodes.new('ShaderNodeTexImage')
    node_bump_tex.label = "Texture: Bump"
    node_bump_tex.name = "nvx2_tex_bump"
    node_bump_tex.location = (-940, -429)
    texture = texture_list['BumpMap0']
    if texture:
        node_bump_tex.image = create_image(texture, options)
        node_bump_tex.image.colorspace_settings.name = 'Non-Color'
    links.new(node_bump.inputs['Height'], node_bump_tex.outputs['Color'])

    return blen_material


def import_nvx2_mesh(n3_mesh_res, context, options: n3.Options):
    """Create a blender object from an nvx2 mesh file."""
    nvx2_path = n3_mesh_res[4:]
    nvx2_dir, nvx2_name = os.path.split(nvx2_path)

    possible_paths_list = []

    # Case 1: Mesh is in same directory as the n3file
    n3_path = options.n3filepath
    n3_dir, _ = os.path.split(n3_path)
    possible_path = os.path.join(n3_dir, nvx2_name)
    possible_paths_list.append(possible_path)

    # Case 2: Search in typical nebula project structure
    # root/anims/... => nax an nac files
    # root/models/... => n3 files
    # root/meshes/... => nvx2 files (WE WANT THIS)
    # root/textures/... => textures
    project_mesh_dir = find_dir(n3_dir, "meshes")
    possible_path = os.path.join(project_mesh_dir, nvx2_dir)
    possible_path = os.path.normpath(possible_path)
    if os.path.isdir(possible_path):
        possible_path = os.path.join(possible_path, nvx2_name)
        possible_paths_list.append(possible_path)

    # Attempt to load one of the nvx2 meshes in path list
    # One is enough!
    blen_object = None
    for pp in possible_paths_list:
        print(pp)
        nvx2options = nvx2.Options()
        nvx2options.nvx2filepath = pp
        if import_nvx2.load(context, nvx2options) == {'FINISHED'}:
            print("found!")
            return blen_object

    return blen_object


def load(context, operator, options: n3.Options):
    """Called by the user interface or another script."""
    n3parser = n3.Parser(operator, options)
    n3parser.parse_file(options.n3filepath)
    operator.report({'INFO'}, "Parsing Complete. Output written to console.")

    # Loop through nodes and create stuff
    # TODO: This is actually a tree structure, need to adjust for it
    #       after everything is halfway working (will also fix material names)
    scene = context.scene
    collection = scene.collection
    for n3node in n3parser.n3node_list:
        # Create mesh
        if options.import_meshes and n3node.mesh_ressource_id:
            mesh_filepath = n3node.mesh_ressource_id
            blen_object = import_nvx2_mesh(mesh_filepath,
                                           context,
                                           options)
        # Create material
        if options.create_materials and n3node.shader_textures:
            blen_material = create_material(n3node.node_name,
                                            n3node.shader_textures,
                                            options)
            if blen_object:
                blen_object.data.materials.append(blen_material)
        # Create armature
        if options.create_armatures and n3node.joints:
            create_armature(n3node.node_name+"_armature",
                            n3node.joints,
                            collection)

    return {'FINISHED'}
