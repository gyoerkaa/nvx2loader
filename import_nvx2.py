"""Library to import nvx2 model files"""

import os
import struct

import bpy
from bpy_extras.io_utils import unpack_list

from . import nvx2


def fps2float(n):
    """Convert fixed point short into a float"""
    return float(n) / 8191.0


def fpb2float(n):
    """Convert fixed point byte into a float"""
    return float(n) / 255.0


def make_vertexformat(vertex_components, nvx2version=3):
    """Build the struct format string to read vertices"""
    vertex_fmt = '<'
    if nvx2version == 2:
        # nvx2 files for Nebula 2
        for vcmask, vcdata in nvx2.VertexComponentsN2.items():
            if vcmask & vertex_components:
                vertex_fmt += vcdata.format
    else:
        # DEFAULT: nvx2 files for Nebula 3
        for vcmask, vcdata in nvx2.VertexComponentsN3.items():
            if vcmask & vertex_components:
                vertex_fmt += vcdata.format
    return vertex_fmt


def detect_version(vertex_components, vertex_width):
    """Attempt to detect nvx2 version from vertex components and vertex width."""
    versions = [3, 2]
    for v in versions:
        vertex_fmt = make_vertexformat(vertex_components, v)
        if struct.calcsize(vertex_fmt) == vertex_width:
            return v
    # Always default to 3
    return 3


def unpack_vertexdata(vertices, vertex_components, nvx2version=3):
    """TODO:Doc."""
    vert_coords = []
    vert_uvs = [[], [], [], []]
    vert_weights = []
    vert_weight_idx = []
    vert_colors = []
    offset = 0

    # Data sources depends on nvx3 version
    vcmask_data = None
    vcdata = None
    if nvx2version == 2:
        vcmask_data = nvx2.VertexComponentMaskN2
        vcdata = nvx2.VertexComponentsN2
    else:
        # Default to N3
        vcmask_data = nvx2.VertexComponentMaskN3
        vcdata = nvx2.VertexComponentsN3

    vcmask = vcmask_data.Coord
    if vcmask & vertex_components:
        vert_coords = [(v[offset+0], v[offset+1], v[offset+2]) for v in vertices]
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.Normal
    if vcmask & vertex_components:
        # Ignoring normals for now
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.NormalUB4N
    if vcmask & vertex_components:
        # Ignoring normals for now
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.Uv0
    if vcmask & vertex_components:
        vert_uvs[0] = [(v[offset+0], v[offset+1]) for v in vertices]
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.Uv0S2
    if vcmask & vertex_components:
        vert_uvs[0] = [(fps2float(v[offset+0]), 1-fps2float(v[offset+1]))
                        for v in vertices]
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.Uv1
    if vcmask & vertex_components:
        vert_uvs[1] = [(v[offset+0], v[offset+1]) for v in vertices]
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.Uv1S2
    if vcmask & vertex_components:
        vert_uvs[1] = [(fps2float(v[offset+0]), 1-fps2float(v[offset+1]))
                        for v in vertices]
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.Uv2
    if vcmask & vertex_components:
        vert_uvs[2] = [(v[offset+0], v[offset+1]) for v in vertices]
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.Uv2S2
    if vcmask & vertex_components:
        vert_uvs[2] = [(fps2float(v[offset+0]), 1-fps2float(v[offset+1]))
                        for v in vertices]
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.Uv3
    if vcmask & vertex_components:
        vert_uvs[3] = [(v[offset+0], v[offset+1]) for v in vertices]
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.Uv3S2
    if vcmask & vertex_components:
        vert_uvs[3] = [(fps2float(v[offset+0]), 1-fps2float(v[offset+1])) for v in vertices]
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.Color
    if vcmask & vertex_components:
        vert_colors = [(v[offset+0], v[offset+1], v[offset+2], v[offset+3]) for v in vertices]
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.ColorUB4N
    if vcmask & vertex_components:
        vert_colors = [(fpb2float(v[offset+0]),
                        fpb2float(v[offset+1]),
                        fpb2float(v[offset+2]),
                        fpb2float(v[offset+3])) for v in vertices]
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.Tangent
    if vcmask & vertex_components:
        # Ignoring tangents for now
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.TangentUB4N
    if vcmask & vertex_components:
        # Ignoring tangents for now
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.Binormal
    if vcmask & vertex_components:
        # Ignoring binormal sign for now
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.BinormalUB4N
    if vcmask & vertex_components:
        # Ignoring binormal sign for now
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.Weights
    if vcmask & vertex_components:
        vert_weights = [(v[offset+0], v[offset+1], v[offset+2], v[offset+3]) for v in vertices]
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.WeightsUB4N
    if vcmask & vertex_components:
        vert_weights = [(fpb2float(v[offset+0]),
                         fpb2float(v[offset+1]),
                         fpb2float(v[offset+2]),
                         fpb2float(v[offset+3])) for v in vertices]
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.JIndices
    if vcmask & vertex_components:
        vert_weight_idx = [(v[offset+0], v[offset+1], v[offset+2], v[offset+3]) for v in vertices]
        offset += vcdata[vcmask].count

    vcmask = vcmask_data.JIndicesUB4
    if vcmask & vertex_components:
        vert_weight_idx = [(fpb2float(v[offset+0]),
                            fpb2float(v[offset+1]),
                            fpb2float(v[offset+2]),
                            fpb2float(v[offset+3])) for v in vertices]
        offset += vcdata[vcmask].count

    return vert_coords, vert_uvs, vert_weights, vert_weight_idx, vert_colors


def create_weights(blen_object, nvx2_weights, nvx2_weight_idx):
    """Adds vertex groups to an blender object."""
    if nvx2_weights and nvx2_weight_idx:
        # Every vertex may have up to four weights
        # TODO: Find out why the weight index is a float (which bone the weight belongs to)
        #       Apparently, sorting the floats will match the int index (maybe)
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


def create_mesh(nvx2_vertices, nvx2_faces, nvx2_uvlayers, nvx2_colors, options: nvx2.Options):
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

    if options.use_smooth:
        blen_mesh.polygons.foreach_set('use_smooth', [True] * num_blen_polygons)

    # Add texture coordinates
    if options.create_uvs:
        for uv_idx, uv_data in enumerate(nvx2_uvlayers):
            # uv_data contains per-vertex uv coordinates
            if uv_data:
                face_uv_coords = [(uv_data[f[0]], uv_data[f[1]], uv_data[f[2]])
                                  for f in nvx2_faces]
                face_uv_coords = unpack_list(unpack_list(face_uv_coords))
                uv_layer = blen_mesh.uv_layers.new(do_init=False)
                uv_layer.name = "nvx2_uv"+str(uv_idx)
                uv_layer.data.foreach_set('uv', face_uv_coords[:2*len(uv_layer.data)])

    if options.create_colors and nvx2_colors:
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
                    blen_colors.data[lidx].color = nvx2_colors[vidx][0:4]
        else:  # Keep the right way separate for speed
            for vidx in vert_loop_map:
                for lidx in vert_loop_map[vidx]:
                    blen_colors.data[lidx].color = nvx2_colors[vidx][0:3]

    if options.use_mesh_validation:
        blen_mesh.validate(verbose=False, clean_customdata=False)

    blen_mesh.update()
    return blen_mesh


def load(context, operator, options: nvx2.Options):
    """Called by the user interface or another script."""
    filepath = options.nvx2filepath
    filename = os.path.splitext(os.path.split(filepath)[1])[0]
    try:
        f = open(filepath, mode='rb')
    except FileNotFoundError:
        operator.report({'ERROR'}, "File " + filename + " not found.")
        print("File not found: '" + filepath + "'")
        return {'CANCELLED'}
    except PermissionError:
        operator.report({'ERROR'}, "Insufficient permissions to access file.")
        print("Insufficient permissions to access file.")
        return {'CANCELLED'}
    else:
        with f:
            scene = context.scene
            collection = scene.collection

            # Read header
            nvx2_header = nvx2.Header._make(struct.unpack('<4s6i', f.read(28)))

            # Read "groups" = objects
            nvx2_groups = [nvx2.Group._make(struct.unpack('<6i', f.read(24)))
                           for i in range(nvx2_header.num_groups)]
            if not nvx2_groups:
                operator.report({'ERROR'}, "File does not contain groups.")
                print("File does not contain groups.")
                return {'CANCELLED'}

            # Attempt to auto detect nvx2 version from vertex format and width
            # NOTE: This may fail!
            if options.nvx2version == 0:
                options.nvx2version = detect_version(nvx2_header.vertex_components,
                                                     nvx2_header.vertex_width * 4)
                operator.report({'INFO'}, "Detected nvx2 version: " + str(options.nvx2version))
                print("Detected nvx2 version: 2" + str(options.nvx2version))

            # Create a format string for struct.unpack() matching the
            # vertex components from the header
            vertex_fmt = make_vertexformat(nvx2_header.vertex_components, options.nvx2version)
            # Check if something was returned
            if not vertex_fmt:
                operator.report({'ERROR'}, "Empty vertex format.")
                print("Empty vertex format")
                return {'CANCELLED'}

            # Check validity of format string, should be same size as header vertex_width*4
            vertex_fmt_size = struct.calcsize(vertex_fmt)
            if vertex_fmt_size != nvx2_header.vertex_width * 4:
                operator.report({'ERROR'}, "Invalid vertex format size.")
                print("Invalid vertex format size " + str(vertex_fmt_size) +
                      ", expected " + str(nvx2_header.vertex_width * 4))
                return {'CANCELLED'}

            # Read Vertex data (for ALL objects in the file)
            vertex_data = [struct.unpack(vertex_fmt, f.read(vertex_fmt_size))
                           for i in range(nvx2_header.num_vertices)]
            nvx2_vertices, nvx2_uvlayers, nvx2_weights, nvx2_weight_idx, nvx2_colors = \
                unpack_vertexdata(vertex_data, nvx2_header.vertex_components)

            # Read faces (for ALL objects in the file)
            nvx2_faces = [list(struct.unpack('<3H', f.read(6)))
                          for i in range(nvx2_header.num_triangles)]

            parent_empty = None
            if options.create_parent_empty:
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
                mesh = create_mesh(grp_verts, grp_faces, grp_uvs, grp_colors, options)
                obj = bpy.data.objects.new('nvx2_object', mesh)
                if options.create_weights and nvx2_weights and nvx2_weight_idx:
                    create_weights(obj,
                                   nvx2_weights[gvf:gvf+g.vertex_count],
                                   nvx2_weight_idx[gvf:gvf+g.vertex_count])
                # Link new object to scene/collection
                if parent_empty:
                    obj.parent = parent_empty
                collection.objects.link(obj)

    return {'FINISHED'}
