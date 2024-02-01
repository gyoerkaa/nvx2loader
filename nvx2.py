"""Library for Parsing Nebula nvx2 files"""

import collections
from enum import IntEnum
from dataclasses import dataclass


@dataclass
class Options:
    """Nvx2 options."""
    use_smooth: bool = False
    use_mesh_validation: bool = True
    create_parent_empty: bool = True
    create_uvs: bool = False,
    create_weights: bool = True
    create_colors: bool = False
    nvx2filepath: str = ""
    nvx2version: int = 3


Header = collections.namedtuple('Header', 'magic \
                                           num_groups \
                                           num_vertices \
                                           vertex_width \
                                           num_triangles \
                                           num_edges \
                                           vertex_components')


Group = collections.namedtuple('Group', 'vertex_first \
                                         vertex_count \
                                         triangle_first \
                                         triangle_count \
                                         edge_first \
                                         edge_count')


VertexComponentData = collections.namedtuple('VertexComponent', 'format count size')


class VertexComponentMaskN3(IntEnum):
    """Indicates presence of certain vertex data, for nebula3 nvx2 files"""
    Coord = 1 << 0
    Normal = 1 << 1
    NormalUB4N = 1 << 2
    Uv0 = 1 << 3
    Uv0S2 = 1 << 4
    Uv1 = 1 << 5
    Uv1S2 = 1 << 6
    Uv2 = 1 << 7
    Uv2S2 = 1 << 8
    Uv3 = 1 << 9
    Uv3S2 = 1 << 10
    Color = 1 << 11
    ColorUB4N = 1 << 12
    Tangent = 1 << 13
    TangentUB4N = 1 << 14
    Binormal = 1 << 15
    BinormalUB4N = 1 << 16
    Weights = 1 << 17
    WeightsUB4N = 1 << 18
    JIndices = 1 << 19
    JIndicesUB4 = 1 << 20


VertexComponentsN3 = {VertexComponentMaskN3.Coord:        VertexComponentData('3f', 3, 4),
                      VertexComponentMaskN3.Normal:       VertexComponentData('3f', 3, 4),
                      VertexComponentMaskN3.NormalUB4N:   VertexComponentData('4B', 4, 1),
                      VertexComponentMaskN3.Uv0:          VertexComponentData('2f', 2, 4),
                      VertexComponentMaskN3.Uv0S2:        VertexComponentData('2h', 2, 2),
                      VertexComponentMaskN3.Uv1:          VertexComponentData('2f', 2, 4),
                      VertexComponentMaskN3.Uv1S2:        VertexComponentData('2h', 2, 2),
                      VertexComponentMaskN3.Uv2:          VertexComponentData('2f', 2, 4),
                      VertexComponentMaskN3.Uv2S2:        VertexComponentData('2h', 2, 2),
                      VertexComponentMaskN3.Uv3:          VertexComponentData('2f', 2, 4),
                      VertexComponentMaskN3.Uv3S2:        VertexComponentData('2h', 2, 2),
                      VertexComponentMaskN3.Color:        VertexComponentData('4f', 4, 4),
                      VertexComponentMaskN3.ColorUB4N:    VertexComponentData('4B', 4, 1),
                      VertexComponentMaskN3.Tangent:      VertexComponentData('3f', 4, 4),
                      VertexComponentMaskN3.TangentUB4N:  VertexComponentData('4B', 4, 1),
                      VertexComponentMaskN3.Binormal:     VertexComponentData('3f', 3, 4),
                      VertexComponentMaskN3.BinormalUB4N: VertexComponentData('4B', 4, 1),
                      VertexComponentMaskN3.Weights:      VertexComponentData('4f', 4, 4),
                      VertexComponentMaskN3.WeightsUB4N:  VertexComponentData('4B', 4, 1),
                      VertexComponentMaskN3.JIndices:     VertexComponentData('4f', 4, 4),
                      VertexComponentMaskN3.JIndicesUB4:  VertexComponentData('4B', 4, 1)}


class VertexComponentMaskN2(IntEnum):
    """Indicates presence of certain vertex data, for nebula2 nvx2 files"""
    Coord = 1 << 0
    Normal = 1 << 1
    Uv0 = 1 << 2
    Uv1 = 1 << 3
    Uv2 = 1 << 4
    Uv3 = 1 << 5
    Color = 1 << 6
    Tangent = 1 << 7
    Binormal = 1 << 8
    Weights = 1 << 9
    JIndices = 1 << 10
    Coord4 = 1 << 11


VertexComponentsN2 = {VertexComponentMaskN2.Coord:     VertexComponentData('3f', 3, 4),
                      VertexComponentMaskN2.Normal:    VertexComponentData('3f', 3, 4),
                      VertexComponentMaskN2.Uv0:       VertexComponentData('2f', 2, 4),
                      VertexComponentMaskN2.Uv1:       VertexComponentData('2f', 2, 4),
                      VertexComponentMaskN2.Uv2:       VertexComponentData('2f', 2, 4),
                      VertexComponentMaskN2.Uv3:       VertexComponentData('2f', 2, 4),
                      VertexComponentMaskN2.Color:     VertexComponentData('4f', 4, 4),
                      VertexComponentMaskN2.Tangent:   VertexComponentData('3f', 4, 4),
                      VertexComponentMaskN2.Binormal:  VertexComponentData('3f', 3, 4),
                      VertexComponentMaskN2.Weights:   VertexComponentData('4f', 4, 4),
                      VertexComponentMaskN2.JIndices:  VertexComponentData('4f', 4, 4),
                      VertexComponentMaskN2.Coord4:    VertexComponentData('4f', 4, 4)}
