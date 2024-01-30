"""Library to import nvx2 model files"""

import os
import struct

import bpy
import bpy_extras.image_utils
from bpy_extras.io_utils import unpack_list
#from bpy_extras.io_utils import unpack_face_list

from . import nvx2


texture_suffix = {"diffuse" : "_color",
                  "specular" : "_spec",
                  "bump" : "_bump"}


default_options = {"reuse_materials" : False,
                   "reuse_images" : True,
                   "alt_texture_paths" : [],
                   "use_image_search": False,
                   "use_smooth" : False,
                   "use_mesh_validation": True,
                   "create_parent_empty": True,
                   "create_weights": True,
                   "create_colors": False}


def fps2float(n):
    """Convert fixed point short into a float"""
    return float(n) / 8191.0


def fpb2float(n):
    """Convert fixed point byte into a float"""
    return float(n) / 255.0


def make_vertexformat(vertex_components):
    """Build the struct format string to read vertices"""
    vertex_fmt = '<'
    for vcmask, vcdata in nvx2.VertexComponents.items():
        if vcmask & vertex_components:
            vertex_fmt += vcdata.format
    return vertex_fmt


def unpack_vertexdata(vertices, vertex_components):
    """TODO:Doc."""
    vert_coords = []
    vert_uvs = [[], [], [], []]
    vert_weights = []
    vert_weight_idx = []
    vert_colors = []
    offset = 0

    vcmask = nvx2.VertexComponentMask.Coord
    if vcmask & vertex_components:
        vert_coords = [(v[offset+0], v[offset+1], v[offset+2]) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.Normal
    if vcmask & vertex_components:
        # Ignoring normals for now
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.NormalUB4N
    if vcmask & vertex_components:
        # Ignoring normals for now
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.Uv0
    if vcmask & vertex_components:
        vert_uvs[0] = [(v[offset+0], v[offset+1]) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.Uv0S2
    if vcmask & vertex_components:
        vert_uvs[0] = [(fps2float(v[offset+0]), 1-fps2float(v[offset+1]))
                        for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.Uv1
    if vcmask & vertex_components:
        vert_uvs[1] = [(v[offset+0], v[offset+1]) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.Uv1S2
    if vcmask & vertex_components:
        vert_uvs[1] = [(fps2float(v[offset+0]), 1-fps2float(v[offset+1]))
                        for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.Uv2
    if vcmask & vertex_components:
        vert_uvs[2] = [(v[offset+0], v[offset+1]) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.Uv2S2
    if vcmask & vertex_components:
        vert_uvs[2] = [(fps2float(v[offset+0]), 1-fps2float(v[offset+1]))
                        for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.Uv3
    if vcmask & vertex_components:
        vert_uvs[3] = [(v[offset+0], v[offset+1]) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.Uv3S2
    if vcmask & vertex_components:
        vert_uvs[3] = [(fps2float(v[offset+0]), 1-fps2float(v[offset+1])) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.Color
    if vcmask & vertex_components:
        vert_colors = [(v[offset+0], v[offset+1], v[offset+2], v[offset+3]) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.ColorUB4N
    if vcmask & vertex_components:
        vert_colors = [(fpb2float(v[offset+0]),
                        fpb2float(v[offset+1]),
                        fpb2float(v[offset+2]),
                        fpb2float(v[offset+3])) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.Tangent
    if vcmask & vertex_components:
        # Ignoring tangents for now
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.TangentUB4N
    if vcmask & vertex_components:
        # Ignoring tangents for now
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.Binormal
    if vcmask & vertex_components:
        # Ignoring binormal sign for now
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.BinormalUB4N
    if vcmask & vertex_components:
        # Ignoring binormal sign for now
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.Weights
    if vcmask & vertex_components:
        vert_weights = [(v[offset+0], v[offset+1], v[offset+2], v[offset+3]) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.WeightsUB4N
    if vcmask & vertex_components:
        vert_weights = [(fpb2float(v[offset+0]),
                         fpb2float(v[offset+1]),
                         fpb2float(v[offset+2]),
                         fpb2float(v[offset+3])) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.JIndices
    if vcmask & vertex_components:
        vert_weight_idx = [(v[offset+0], v[offset+1], v[offset+2], v[offset+3]) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    vcmask = nvx2.VertexComponentMask.JIndicesUB4
    if vcmask & vertex_components:
        vert_weight_idx = [(fpb2float(v[offset+0]),
                            fpb2float(v[offset+1]),
                            fpb2float(v[offset+2]),
                            fpb2float(v[offset+3])) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    return vert_coords, vert_uvs, vert_weights, vert_weight_idx, vert_colors


def create_image(img_name, options):
    """Helper function to load image files into blender images."""
    if options["reuse_images"] and img_name in bpy.data.images:
        return bpy.data.images[img_name]

    img_path_list = [""] + options["alt_texture_paths"]
    img = None
    for img_path in img_path_list:
        img = bpy_extras.image_utils.load_image(img_name + '.dds',
                                                img_path,
                                                recursive=options["use_image_search"],
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


def create_material(material_name, options):
    """Creates a blender material."""

    # Try to re-use existing material with the same name
    if options["reuse_materials"] and material_name in bpy.data.materials:
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
    node_diff_tex.image = create_image(material_name+texture_suffix["diffuse"], options)
    node_diff_tex.image.colorspace_settings.name = 'sRGB'
    # Connect to shader
    links.new(node_shader.inputs['Alpha'], node_diff_tex.outputs['Alpha'])
    links.new(node_shader.inputs['Base Color'], node_diff_tex.outputs['Color'])

    # Create specular texture node
    node_spec_tex = nodes.new('ShaderNodeTexImage')
    node_spec_tex.label = "Texture: Specular"
    node_spec_tex.name = "nvx2_tex_specular"
    node_spec_tex.location = (-1373, 371)
    node_spec_tex.image = create_image(material_name+texture_suffix["specular"], options)
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
    node_bump_tex.image = create_image(material_name+texture_suffix["bump"], options)
    node_bump_tex.image.colorspace_settings.name = 'Non-Color'
    links.new(node_bump.inputs['Height'], node_bump_tex.outputs['Color'])

    return blen_material


def create_weights(blen_object, nvx2_weights, nvx2_weight_idx):
    """Adds vertex groups to an blender object."""
    if nvx2_weights and nvx2_weight_idx:
        # Every vertex may have up to four weights
        # TODO: Find out why the weight index is a float? (which bone the weight belongs to)
        created_groups = 0
        for vert_id, (weight_list, index_list) in enumerate(zip(nvx2_weights, nvx2_weight_idx)):
            for weight, weight_idx in zip(weight_list, index_list):
                vgroup_name = "nvx2_"+str(weight_idx)
                if vgroup_name in blen_object.vertex_groups:
                    vgroup = blen_object.vertex_groups[vgroup_name]
                else:
                    vgroup = blen_object.vertex_groups.new(name=vgroup_name)
                    created_groups += 1

                vgroup.add([vert_id], weight, 'REPLACE')
        print('created_groups='+str(created_groups))


def create_mesh(nvx2_vertices, nvx2_faces, nvx2_uvlayers, nvx2_colors, nvx2_mat_name, options):
    """Create a mesh for use with an blender object."""
    blen_mesh = bpy.data.meshes.new('nvx2_mesh')
    # Add vertices
    blen_mesh.vertices.add(len(nvx2_vertices))
    blen_mesh.vertices.foreach_set('co', unpack_list(nvx2_vertices))
    # Create loops
    blen_mesh.loops.add(len(nvx2_faces) * 3)
    blen_mesh.loops.foreach_set('vertex_index', unpack_list(nvx2_faces))
    # Create polygons
    blen_mesh.polygons.add(len(nvx2_faces))
    blen_mesh.polygons.foreach_set('loop_start', range(0, len(nvx2_faces) * 3, 3))
    blen_mesh.polygons.foreach_set('loop_total', (3,) * len(nvx2_faces))
    # Whole thing might still be empty. If so, there is nothing further to do
    if not blen_mesh.polygons:
        return

    num_blen_polygons = len(blen_mesh.polygons)

    if options["use_smooth"]:
        blen_mesh.polygons.foreach_set('use_smooth', [True] * num_blen_polygons)

    # Create material
    material = create_material(nvx2_mat_name, options)
    if material:
        blen_mesh.materials.append(material)

    # Add texture coordinates
    for uv_idx, uv_data in enumerate(nvx2_uvlayers):
        # uv_data contains per-vertex uv coordinates
        if uv_data:
            face_uv_coords = [(uv_data[f[0]], uv_data[f[1]], uv_data[f[2]]) for f in nvx2_faces]
            face_uv_coords = unpack_list(unpack_list(face_uv_coords))
            uv_layer = blen_mesh.uv_layers.new(do_init=False)
            uv_layer.name = "nvx2_uv"+str(uv_idx)
            uv_layer.data.foreach_set('uv', face_uv_coords[:2*len(uv_layer.data)])

    if options['create_colors'] and nvx2_colors:
        blen_colors = blen_mesh.vertex_colors.new("nvx2_colors")
        # Get all loops for each vertex
        vert_loop_map = {}
        for lp in blen_mesh.loops:
            if lp.vertex_index in vert_loop_map:
                vert_loop_map[lp.vertex_index].append(lp.index)
            else:
                vert_loop_map[lp.vertex_index] = [lp.index]
        # Set color for each vertex (in every loop)
        # BUGFIX: colors have dim 4 on some systems
        #         (should be 3 as per documentation)
        color_dim = len(blen_colors.data[0].color)
        if color_dim > 3:
            for vidx in vert_loop_map:
                for lidx in vert_loop_map[vidx]:
                    blen_colors.data[lidx].color = (nvx2_colors[vidx][0:4])
        else:  # Keep the right way separate for speed
            for vidx in vert_loop_map:
                for lidx in vert_loop_map[vidx]:
                    blen_colors.data[lidx].color = nvx2_colors[vidx][0:3]

    if options["use_mesh_validation"]:
        blen_mesh.validate(verbose=True, clean_customdata=False)

    blen_mesh.update()
    return blen_mesh


def load(context, options, filepath=''):
    """Called by the user interface or another script."""
    with open(filepath, mode='rb') as f:
        filename = os.path.splitext(os.path.split(filepath)[1])[0]
        scene = context.scene
        collection = scene.collection

        # Read header
        header = nvx2.Header._make(struct.unpack('<4s6i', f.read(28)))
        vertex_fmt = make_vertexformat(header.vertex_components)
        vertex_size = struct.calcsize(vertex_fmt)
        if vertex_size != header.vertex_width * 4:
            return {'CANCELLED'}

        # Read "groups" = objects
        nvx2_groups = [nvx2.Group._make(struct.unpack('<6i', f.read(24)))
                       for i in range(header.num_groups)]
        # Geometry data (for ALL objects in the file)
        vertex_data = [struct.unpack(vertex_fmt, f.read(vertex_size))
                       for i in range(header.num_vertices)]
        nvx2_vertices, nvx2_uvlayers, nvx2_weights, nvx2_weight_idx, nvx2_colors = \
            unpack_vertexdata(vertex_data, header.vertex_components)
        nvx2_faces = [list(struct.unpack('<3H', f.read(6)))
                      for i in range(header.num_triangles)]

        parent_empty = None
        if options["create_parent_empty"]:
            parent_empty = bpy.data.objects.new(filename, None)
            parent_empty.location = (0.0, 0.0, 0.0)
            collection.objects.link(parent_empty)

        # Create objects
        for i, g in enumerate(nvx2_groups):
            gvf = g.vertex_first
            gtf = g.triangle_first
            gtc = g.triangle_count
            # Get vertex data for this object
            grp_faces = [[vid-gvf for vid in f] for f in nvx2_faces[gtf:gtf+gtc]]
            grp_verts = nvx2_vertices[gvf:gvf+g.vertex_count]
            grp_uvs = [uvl[gvf:gvf+g.vertex_count] for uvl in nvx2_uvlayers]
            grp_colors = nvx2_colors[gvf:gvf+g.vertex_count]
            # Create the blender objects
            grp_mat_name = filename+str(i) if (i>0) else filename
            mesh = create_mesh(grp_verts, grp_faces, grp_uvs, grp_colors, grp_mat_name, options)
            obj = bpy.data.objects.new('nvx2_object', mesh)
            if options["create_weights"] and nvx2_weights and nvx2_weight_idx:
                create_weights(obj,
                               nvx2_weights[gvf:gvf+g.vertex_count],
                               nvx2_weight_idx[gvf:gvf+g.vertex_count])

            if parent_empty:
                obj.parent = parent_empty
            collection.objects.link(obj)

    return {'FINISHED'}
