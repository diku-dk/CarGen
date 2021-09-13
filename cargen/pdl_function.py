import cargen
import numpy as np
import igl
import meshplot as mp

def get_pdl_layer(vertices_p,
                  faces_p,
                  vertices_s,
                  faces_s,
                  param):
    """
    This function generates gap-based cartilages based on the bone geometries

    :param vertices_p: list of vertex positions of the primary surface
    :param faces_p: list of triangle indices of the primary surface
    :param vertices_s: list of vertex positions of the secondary surface
    :param faces_s: list of triangle indices of the secondary surface
    :param param: list of parameters needed to generate hip joint cartilage models from "all_params.py"

    :return: vertices and faces of hip joint articulating cartilages
    """

    " Step A. distance filtering "

    # save primary bone vertices separately
    vertices_bp = np.copy(vertices_p)
    vertices_bs = np.copy(vertices_s)

    # bone adjacency faces
    face_adjacency, cumulative_sum = igl.vertex_triangle_adjacency(faces_p, len(vertices_p))

    # initial cartilage surface definition
    intt_face_idxs = cargen.get_initial_surface(vertices_p,
                                                faces_p,
                                                vertices_s,
                                                faces_s,
                                                param.gap_distance)

    # delete the cartilage boundary layer
    int_face_idxs = cargen.trim_boundary(faces_p,
                                         intt_face_idxs,
                                         face_adjacency,
                                         cumulative_sum,
                                         param.trimming_iteration)

    # removing extra components
    int_face_idxs = cargen.get_largest_component(faces_p,
                                                 int_face_idxs)

    # remove ears
    for i in range(3):
        int_face_idxs = cargen.remove_ears(faces_p,
                                           int_face_idxs)

    base_face_idxs = np.copy(int_face_idxs)

    # determine the vertex indices
    boundary_vertex_idxs = igl.boundary_loop(faces_p[base_face_idxs])
    base_vertex_idxs = np.unique(faces_p[base_face_idxs].flatten())

    # smooth the edges
    for i in range(param.smoothing_iteration):
        vertices_p = cargen.smooth_boundary(vertices_p,
                                            boundary_vertex_idxs,
                                            param.smoothing_factor)

    # snap back to the primary bone
    vertices_p = cargen.snap_to_surface(vertices_p,
                                        boundary_vertex_idxs,
                                        vertices_bp,
                                        faces_p)

    # cartilage area
    cartilage_area = cargen.get_area(vertices_p,
                                     faces_p[base_face_idxs])

    # viz
    frame = mp.plot(vertices_p, faces_p, c=cargen.mandible, shading=cargen.sh_false)
    frame.add_mesh(vertices_p, faces_p[base_face_idxs], c=cargen.blue, shading=cargen.sh_true)

    " Part B. Extrusion "

    thickness_profile = cargen.assign_thickness(vertices_p,
                                                faces_p,
                                                vertices_s,
                                                faces_s,
                                                base_face_idxs,
                                                param.thickness_factor)

    weights = thickness_profile[base_vertex_idxs]

    # extrude surface
    ex_vertices_p = cargen.extrude_cartilage(vertices_p,
                                             faces_p,
                                             base_face_idxs,
                                             weights)

    # smooth the edges
    for i in range(param.smoothing_iteration):
        ex_vertices_p = cargen.smooth_boundary(ex_vertices_p,
                                               boundary_vertex_idxs,
                                               param.smoothing_factor)

    # snap back to the primary bone
    ex_vertices_p = cargen.snap_to_surface(ex_vertices_p,
                                           boundary_vertex_idxs,
                                           vertices_bs,
                                           faces_s)

    # viz
    frame = mp.plot(vertices_p, faces_p, c=cargen.mandible, shading=cargen.sh_false)
    frame.add_mesh(vertices_p, faces_p[base_face_idxs], c=cargen.blue, shading=cargen.sh_true)
    frame.add_mesh(ex_vertices_p, faces_p[base_face_idxs], c=cargen.green, shading=cargen.sh_true)
    frame.add_points(vertices_p[boundary_vertex_idxs], shading={"point_size": 0.3, "point_color": "red"})
    frame.add_points(ex_vertices_p[boundary_vertex_idxs], shading={"point_size": 0.3, "point_color": "red"})

    " Part C. Build the closed surface"

    # flip normals of the bottom surface
    base_faces = faces_p[base_face_idxs]
    base_faces[:, [0, 1]] = base_faces[:, [1, 0]]

    # build wall
    roof_faces = cargen.get_wall(vertices_p,
                                 boundary_vertex_idxs)

    # merge left, top, and right faces
    si_vertices = np.concatenate((ex_vertices_p, vertices_p))
    si_faces = np.concatenate((faces_p[base_face_idxs], roof_faces, base_faces + len(ex_vertices_p)))

    # increase the number of facet rows in the wall
    usi_vertices, usi_faces = igl.upsample(si_vertices, si_faces, param.upsampling_iteration)
    roof_vertices, roof_faces = igl.upsample(usi_vertices, roof_faces, param.upsampling_iteration)

    # final touch
    usi_vertices, usi_faces = cargen.clean(usi_vertices,
                                           usi_faces)

    roof_vertices, roof_faces = cargen.clean(roof_vertices,
                                             roof_faces)

    # viz
    frame = mp.plot(ex_vertices_p, faces_p[base_face_idxs], c=cargen.green, shading=cargen.sh_true)
    frame.add_mesh(vertices_p, base_faces, c=cargen.blue, shading=cargen.sh_true)
    frame.add_mesh(roof_vertices, roof_faces, c=cargen.organ, shading=cargen.sh_true)
    frame.add_points(vertices_p[boundary_vertex_idxs], shading={"point_size": 0.3, "point_color": "red"})
    frame.add_points(ex_vertices_p[boundary_vertex_idxs], shading={"point_size": 0.3, "point_color": "red"})

    f = mp.plot(roof_vertices, roof_faces, c=cargen.organ, shading=cargen.sh_true)
    f.add_mesh(vertices_s, faces_s, c=cargen.tooth, shading=cargen.sh_false)

    frame = mp.plot(vertices_p, faces_p, c=cargen.mandible, shading=cargen.sh_false)
    frame.add_mesh(usi_vertices, usi_faces, c=cargen.organ, shading=cargen.sh_true)

    # geometry
    print("pdl base area is: ", np.round(cartilage_area, 2))
    print("mean pdl thickness is: ", np.round(np.mean(thickness_profile[base_vertex_idxs]), 2))
    print("maximum pdl thickness is: ", np.round(np.max(thickness_profile[base_vertex_idxs]), 2))

    return usi_vertices, usi_faces, roof_vertices, roof_faces
