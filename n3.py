"""Library for Parsing Nebula n3 files"""

import struct
from dataclasses import dataclass, field


SUPPORTED_VERSIONS = {1, 2}


@dataclass
class Options:
    """N3 options."""
    ignore_version: bool = True
    create_armatures: bool = True
    create_materials: bool = True
    reuse_materials: bool = False
    reuse_images: bool = True
    use_image_search: bool = False
    import_meshes: bool = True
    n3filepath: str = ""


@dataclass
class Node:
    """Class holding node data."""
    node_name: str
    node_type: str
    node_parent: object = None
    node_children: list = field(default_factory=list)
    # transform node params
    position: list = field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])
    rotation: list = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    scale: list = field(default_factory=lambda: [1.0, 1.0, 1.0, 1.0])
    rotation_pivot: list = field(default_factory=list)
    scale_pivot: list = field(default_factory=list)
    view_in_space: bool = False
    locked_to_viewer: bool = False
    min_distance: float = -1.0
    max_distance: float = -1.0
    # state node params
    material_string : str = ""  # DEPRECATED
    material_name: str = ""
    shader_textures: dict = field(default_factory=dict)
    shader_parameters: dict = field(default_factory=dict)
    # shape node params
    mesh_ressource_id: str = ""
    primitive_group_idx: int = 0
    # character node params
    anim_ressource_id: str = ""
    variation_ressource_id: str = ""
    num_joints: int = 0
    joints: list = field(default_factory=list)
    num_joint_masks: int = 0
    joint_masks: list = field(default_factory=list)
    num_skin_lists: int = 0
    skin_lists: list = field(default_factory=list)
    # character skin node params
    num_skin_fragments: int = 0
    skin_fragments: dict = field(default_factory=dict)
    # data params
    model_node_type: str = ""  # DEPRECATED
    attributes: dict = field(default_factory=dict)
    bounding_box: list = field(default_factory=list)
    # Unknown origin, possibly deprecated, using fourCC as suffix
    unknown_cash: str = ""
    unknown_shdr: str = ""


class Parser():
    """Parse an n3 file."""

    def __init__(self, blen_operator, options):
        self.filepath = ""
        self.operator = blen_operator  # for sending reports to blender UI
        self.options = options

        self.byteorder = ""   # param for to_bytes()
        self.byteformat = ""  # oaram for struct.unpack()

        self.n3file = None
        self.n3version = 0
        self.n3modeltype = ""
        self.n3modelname = ""
        self.n3node_list = []  # collections.OrderedDict()
        self.n3attribues = {}


    def report(self, rep_type, rep_msg):
        """Send a message from the blender operator."""
        self.operator.report(rep_type, rep_msg)


    def read_n3_value(self, struct_format, num_bytes):
        """Read an n3 value, wrapper for struct.unpack()."""
        return struct.unpack(self.byteformat+struct_format, self.n3file.read(num_bytes))


    def read_n3_string(self):
        """Read an n3 string."""
        # strings in n3 files consist of
        # - An unsigned short for strlen
        # - followed by as many chars
        n3strlen = self.read_n3_value("H", 2)[0]
        n3str = self.read_n3_value(str(n3strlen)+"s", n3strlen)[0]
        return n3str.decode('ascii')


    def read_n3_fourcc(self):
        """Read an n3 four character code."""
        four_cc = self.read_n3_value("I", 4)[0]
        return four_cc.to_bytes(4, byteorder=self.byteorder).decode()


    def parse_tag_other(self, tag_4cc: str, node: Node):
        """Tags I couldn't figore out where they come from, taken from file with hex editor"""
        if tag_4cc == 'CASH':
            # seems to be bool, something to do with shader
            node.unknown_cash = self.read_n3_value("b", 1)[0]
            print("        UNKNOWN_TAG 'CASH'="+str(node.unknown_cash))
        elif tag_4cc =='SHDR':
            # seems to be single string, shader name
            node.unknown_shdr = self.read_n3_string()
            print("        UNKNOWN_TAG 'SHDR'=" + str(node.unknown_shdr))
        else:
            # No valid fourCC found
            return False

        # Found a valid fourCC
        return True


    def parse_tag_shape(self, tag_4cc: str, node: Node):
        """Parse an n3 shape tag."""

        # model node tags, see
        # ShapeNode::ParseDataTag() (code/render/models/shapenode.cc)
        if tag_4cc == 'MESH':
            # Mesh (ressourceID)
            node.mesh_ressource_id = self.read_n3_string()
            print("        mesh_res_id="+node.mesh_ressource_id)
        elif tag_4cc =='PGRI':
            # Primitive group index
            node.primitive_group_idx = self.read_n3_value("i", 4)[0]
            print("        primitive_group_idx="+str(node.primitive_group_idx))
        else:
            # No valid fourCC found
            return False

        # Found a valid fourCC
        return True


    def parse_tag_data(self, tag_4cc: str, node: Node):
        """Parse an n3 data tag."""

        # model node tags, see
        # ModelNode::ParseDataTag() (code/render/models/modelnode.cc)
        if tag_4cc == 'LBOX':
            # bounding box
            center = self.read_n3_value("4f", 16)[:4]
            extends = self.read_n3_value("4f", 16)[:4]

            node.bounding_box = [center, extends]
            print("        model_bbox="+str(node.bounding_box))
        elif tag_4cc == 'MNTP':
            # DEPRECATED model node type
            node.model_node_type = self.read_n3_string()
            print("        DEPRECATED model_node_type="+str(node.model_node_type))
        elif tag_4cc =='SSTA':
            # String attribute
            n3key = self.read_n3_string()
            n3value = self.read_n3_string()

            node.attributes[n3key] = n3value
            print("attribute: (" + n3key + ":" + n3value + ")")
        else:
            # No valid fourCC found
            return False

        # Found a valid fourCC
        return True


    def parse_tag_transform(self, tag_4cc: str, node: Node):
        """Parse an n3 transform node."""
        # See TransformNode::ParseDataTag() (code/render/models/nodes/transformnode.cc)
        if tag_4cc == 'POSI':
            # position
            node.position = self.read_n3_value("4f", 16)[:4]
        elif tag_4cc == 'ROTN':
            # rotation
            node.rotation = self.read_n3_value("4f", 16)[:4]
        elif tag_4cc == 'SCAL':
            # scale
            node.scale = self.read_n3_value("4f", 16)[:4]
        elif tag_4cc == 'RPIV':
            # Rotate Pivot
            node.rotation_pivot = self.read_n3_value("4f", 16)[:4]
        elif tag_4cc == 'SPIV':
            # Scale Pivot
            node.scale_pivot = self.read_n3_value("4f", 16)[:4]
        elif tag_4cc == 'SVSP':
            # set view in space (single bool, reader->ReadBool())
            val = self.read_n3_value("b", 1)[0]
            node.view_in_space = bool(val)
        elif tag_4cc == 'SLKV':
            # Set Locked to viewer (single bool, reader->ReadBool())
            val = self.read_n3_value("b", 1)[0]
            node.locked_to_viewer = bool(val)
        elif tag_4cc == 'SMID':
            # Set Min Distance
            node.min_distance = self.read_n3_value("f", 1)[0]
        elif tag_4cc == 'SMAD':
            # Set max Distance
            node.max_distance = self.read_n3_value("f", 1)[0]
        else:
            # No valid fourCC found
            return False

        # Found a valid fourCC
        return True


    def parse_tag_state(self, tag_4cc: str, node: Node):
        """Parse an n3 state tag."""

        # state node tags, see
        # StateNode::ParseDataTag() (code/render/models/nodes/statenode.cc)
        if tag_4cc =='MNMT':
            # Material string DEPRECATED
            _ = self.read_n3_string()
        elif tag_4cc =='MATE':
            # Material name
            node.material_name = self.read_n3_string()
        elif tag_4cc =='STXT':
            # Shader texture
            tex_type = self.read_n3_string()
            tex_name = self.read_n3_string()

            node.shader_textures[tex_type] = tex_name
            print("        new_texture=" + str(node.shader_textures[tex_type]))
        elif tag_4cc == 'SINT':
            # Shader int param
            pname = self.read_n3_string()
            pval = self.read_n3_value("i", 4)[0]

            node.shader_parameters['pname'] = pval
            print("        new_shader_int=" + str((pname, pval)))
        elif tag_4cc == 'SFLT':
            # Shader float param
            pname = self.read_n3_string()
            pval = self.read_n3_value("f", 4)[0]

            node.shader_parameters['pname'] = pval
            print("        new_shader_float=" + str((pname, pval)))
        elif tag_4cc == 'SBOO':
            # Shader bool param
            pname = self.read_n3_string()
            pval = self.read_n3_value("b", 1)[0]

            node.shader_parameters['pname'] = pval
            print("        new_shader_bool=" + str((pname, pval)))
        elif tag_4cc == 'SFV2':
            # Shader 2-dim vector param
            pname = self.read_n3_string()
            pval = self.read_n3_value("2f", 8)[:2]

            node.shader_parameters['pname'] = pval
            print("        new_shader_vector2=" + str((pname, pval)))
        elif tag_4cc == 'SFV4' or tag_4cc == 'SVEC':
            # Shader 4-dim vector param
            pname = self.read_n3_string()
            pval = self.read_n3_value("4f", 16)[:4]

            node.shader_parameters['pname'] = pval
            print("        new_shader_vector4=" + str((pname, pval)))
        elif tag_4cc == 'STUS':
            # Indexed shader param (not implemented)
            pidx = self.read_n3_value("i", 1)[0]
            pval = self.read_n3_value("4f", 16)[:4]

            pname = "MLPUVStretch" + str(pidx)
            print("        MLPUVStretch=" + str((pname, pval)))
            node.shader_parameters['pname'] = pval
        elif tag_4cc == 'SSPI':
            # Indexed shader param (not implemented)
            pidx = self.read_n3_value("i", 1)[0]
            pval = self.read_n3_value("4f", 16)[:4]

            pname = "MLPSpecIntensity" + str(pidx)
            print("        MLPSpecIntensity=" + str((pname, pval)))
            node.shader_parameters['pname'] = pval
        else:
            # No valid fourCC found
            return False

        # Found a valid fourCC
        return True


    def parse_tag_characterskin(self, tag_4cc: str, node: Node):
        """Parse an n3 charactert skin tag."""

        # model node tags, see
        # CharacterSkinNode::ParseDataTag() (code/render/characters/characterskinnode.cc)
        if tag_4cc == 'NSKF':
            # Number of skin fragments
            # Don't actually need this, it's originally used to allocate memory which
            # we don't have to
            node.num_skin_fragments = self.read_n3_value("i", 4)[0]
            print("        num_skin_fragments="+str(node.num_skin_fragments))
        elif tag_4cc =='SFRG':
            # Skin fragment
            group_idx = self.read_n3_value("i", 4)[0]
            num_joints = self.read_n3_value("i", 4)[0]

            new_skin_fragment = self.read_n3_value(str(num_joints)+"i", num_joints*4)[:num_joints]
            node.skin_fragments[group_idx] = new_skin_fragment
            print("        new_skin_fragment=" + str(new_skin_fragment))
        else:
            # No valid fourCC found
            return False

        # Found a valid fourCC
        return True


    def parse_tag_character(self, tag_4cc: str, node: Node):
        """Parse an n3 character tag."""

        # model node tags, see
        # CharacterNode::ParseDataTag() (code/render/characters/characternode.cc)
        if tag_4cc == 'ANIM':
            # Animation
            node.anim_ressource_id = self.read_n3_string()
            print("        anim_res_id=" + node.anim_ressource_id)
        elif tag_4cc == 'NJNT':
            # Number of joints in skeleton
            # Don't actually need this, it's originally used to allocate memory which
            # we don't have to
            node.num_joints = self.read_n3_value('i', 4)[0]
            print("        num_joints=" + str(node.num_joints))
        elif tag_4cc == 'JONT':
            # Joint
            joint_idx        = self.read_n3_value('i', 4)[0]
            parent_joint_idx = self.read_n3_value('i', 4)[0]
            pose_translation = self.read_n3_value('4f', 16)[:4]
            pose_rotation    = self.read_n3_value('4f', 16)[:4]
            pose_scale       = self.read_n3_value('4f', 16)[:4]
            joint_name       = self.read_n3_string()

            new_joint = (joint_idx, parent_joint_idx,
                        pose_translation, pose_rotation, pose_scale,
                        joint_name)
            node.joints.append(new_joint)
            print("        new_joint=" + str(new_joint))
        elif tag_4cc == 'NJMS':
            # Number of joint masks
            # Don't actually need this, it's originally used to allocate memory which
            # we don't have to
            node.num_joint_masks = self.read_n3_value('i', 4)[0]
            print("        num_joint_masks=" + str(node.num_joint_masks))
        elif tag_4cc == 'JOMS':
            # Joint mask
            mask_name = self.read_n3_string()
            num_weights = self.read_n3_value('i', 4)[0]
            mask_weights = self.read_n3_value(str(num_weights)+'f', 4*num_weights)[0]

            new_mask = (mask_name, mask_weights)
            node.joint_masks.append(new_mask)
            print("        new_mask=" + str(new_mask))
        elif tag_4cc == 'VART':
            # Variation resource name
            node.variation_ressource_id = self.read_n3_string()
            print("        variation_ressource_id=" + node.variation_ressource_id)
        elif tag_4cc == 'NSKL':
            # Number of skin lists
            # Don't actually need this, it's originally used to allocate memory which
            # we don't have to
            node.num_skin_lists = self.read_n3_value('i', 4)[0]
            print("        num_skinlists=" + str(node.num_skin_lists))
        elif tag_4cc == 'SKNL':
            # Skin list
            skinlist_name = self.read_n3_string()
            num_skins = self.read_n3_value('i', 4)[0]
            print("        num_skins=" + str(num_skins))
            skins = []
            for _ in range(num_skins):
                skins.append(self.read_n3_string())

            # Sometimes this is followed by some random info
            # - 1 empty byte (maybe)
            # - string
            # TODO: Find out whether presence of this is n3 version dependent
            if self.n3version == 2:
                _ = self.read_n3_value('b', 1)[0]
                junk = self.read_n3_string()
                print("        junk=" + junk)

            new_skinlist = (skinlist_name, skins)
            node.skin_lists.append(new_skinlist)
            print("        new_skinlists=" + str(new_skinlist))
        else:
            # No valid fourCC found
            return False

        # Found a valid fourCC
        return True


    def parse_node_tag(self, tag_4cc: str, node: Node):
        """Parse an n3 node tag."""

        # TODO: Not all combinations are valid, find out which
        #       (doesn't matter for blender import though, just try everything)
        if (self.parse_tag_character(tag_4cc, node) or
            self.parse_tag_characterskin(tag_4cc, node) or
            self.parse_tag_state(tag_4cc, node) or
            self.parse_tag_transform(tag_4cc, node) or
            self.parse_tag_shape(tag_4cc, node) or
            self.parse_tag_data(tag_4cc, node) or
            self.parse_tag_other(tag_4cc, node)):
            return True

        # Unknown tag
        return False


    def parse_file(self, filepath):
        """Parse an n3 file."""

        self.filepath = filepath
        with open(self.filepath, mode='rb') as f:
            self.n3file = f
            #filename = os.path.splitext(os.path.split(filepath)[1])[0]

            # Read header
            # Contains FourCC and version

            # PROBLEM:
            # - Endianness of file depends on what platform it was packed for
            # - But we don't have that info, file could have been extracted from anywhere!
            # - We'll use the FourCC to determine endianness of file (UGLY, but no choice)
            # - It'll be either "3BEN" od "NEB3"
            # See StreamModelLoader::SetupModelFromStream (code/render/models/streammodelloader.cc)
            header_4cc = struct.unpack("<I", f.read(4))[0]
            header_4cc_little = header_4cc.to_bytes(4, byteorder="little").decode()
            header_4cc_big = header_4cc.to_bytes(4, byteorder="big").decode()

            if header_4cc_little == "NEB3":
                self.byteorder = "little"
                self.byteformat = "<"
            elif header_4cc_big == "NEB3":
                self.byteorder = "big"
                self.byteformat = "<"
            else:
                self.report({'ERROR'}, "Invalid file, unknown fourCC '" + str(header_4cc) + "'")
                return False  # {'CANCELLED'}

            # Parse file version
            header_version = self.read_n3_value("I", 4)[0]
            print("n3 Version: " + str(header_version))
            if header_version not in SUPPORTED_VERSIONS:
                if self.options["ignore_version"]:
                    self.report({'WARNING'}, "Unsupported version '" + str(header_version) + "'")
                else:
                    self.report({'ERROR'}, "Unsupported version '" + str(header_version) + "'")
                    return False  # {'CANCELLED'}

            self.n3version = header_version

            done = False
            current_node = None
            current_node_idx = -1
            while not done:
                tag_4cc = self.read_n3_fourcc()
                print(tag_4cc)

                # Model data blocks, see
                # StreamModelLoader::SetupModelFromStream (/code/render/models/streammodelloader.cc)
                if tag_4cc == '>MDL':
                    # Start of model
                    self.n3modeltype = self.read_n3_fourcc()
                    self.n3modelname = self.read_n3_string()
                    print("model_type_4cc: '" + str(self.n3modeltype) + "'")
                    print("model_name: '" + self.n3modelname + "'")
                elif tag_4cc == '<MDL':
                    # End of Model
                    done = True
                    current_node = None
                elif tag_4cc == '>MND':
                    # Start of model node
                    node_type_4cc = self.read_n3_fourcc()
                    node_name = self.read_n3_string()

                    # Create new node
                    new_node = Node(node_name, node_type_4cc, current_node)
                    print("    new_node: " + new_node.node_type + " - " + new_node.node_name)
                    if current_node:
                        current_node.node_children.append(new_node)

                    self.n3node_list.append(new_node)
                    current_node = new_node
                    current_node_idx += 1
                elif tag_4cc == '<MND':
                    # End of model node, get the previous one
                    print("    end node '" + current_node.node_name + "'")
                    current_node_idx -= 1
                    if current_node_idx >= 0:
                        current_node = self.n3node_list[current_node_idx]
                        print("    return to node '" + current_node.node_name + "'")
                    else:
                        current_node = None
                elif tag_4cc == 'EOF_':
                    # End of file (might not be present, maybe version dependent)
                    done = True
                    current_node = None
                else:
                    # Try parsing node data
                    if current_node and self.parse_node_tag(tag_4cc, current_node):
                        pass
                    else:
                        self.report({'ERROR'}, "Unknown tag '" + tag_4cc + "'")
                        return False # {'CANCELLED'}

        return True
