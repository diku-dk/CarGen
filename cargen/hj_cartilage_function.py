import cargen
import numpy as np
import igl
import meshplot as mp


def get_hj_cartilage(vertices_p, faces_p,
                     vertices_s, faces_s,
                     param):
    """
    This function generates hip joint articulating cartilages based on the bone geometries ( femur and pelvis bones )

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

    " Step B. Curvature-Based Region Filling "

    if param.extend_cartilage_flag:

        # bone curvature measures
        curvature_value = cargen.get_curvature_measures(vertices_p,
                                                        faces_p,
                                                        param.neighbourhood_size,
                                                        param.curvature_type,
                                                        param.curve_info)

        # grow cartilage surface
        base_face_idxs = cargen.grow_cartilage(faces_p,
                                               int_face_idxs,
                                               face_adjacency,
                                               cumulative_sum,
                                               curvature_value,
                                               param.min_curvature_threshold,
                                               param.max_curvature_threshold)

        # trim one layer
        base_face_idxs = cargen.trim_boundary(faces_p,
                                              base_face_idxs,
                                              face_adjacency,
                                              cumulative_sum,
                                              1)

        # remove ears
        for i in range(3):
            int_face_idxs = cargen.remove_ears(faces_p,
                                               int_face_idxs)

    else:
        base_face_idxs = int_face_idxs

    # separate and smooth
    boundary_edges = igl.boundary_facets(faces_p[base_face_idxs])
    boundary_vertex_idxs = np.unique(boundary_edges.flatten())

    vertices_p = cargen.smooth_and_separate_boundaries(vertices_p,
                                                       boundary_edges,
                                                       param.smoothing_factor,
                                                       param.smoothing_iteration_base)
    # snap back to the primary bone
    vertices_p = cargen.snap_to_surface(vertices_p,
                                        boundary_vertex_idxs,
                                        vertices_bp,
                                        faces_p)

    # remove ears
    base_face_idxs = cargen.remove_ears(faces_p,
                                        base_face_idxs)

    # cartilage area
    cartilage_area = cargen.get_area(vertices_p,
                                     faces_p[base_face_idxs])

    # viz
    frame = mp.plot(vertices_p, faces_p, c=cargen.bone, shading=cargen.sh_false)
    frame.add_mesh(vertices_p, faces_p[base_face_idxs], c=cargen.sweet_pink, shading=cargen.sh_true)
    frame.add_mesh(vertices_p, faces_p[int_face_idxs], c=cargen.pastel_yellow, shading=cargen.sh_true)


    " Part C. Extrusion "

    # array indicating the thickness value for each vertex
    if not param.extend_cartilage_flag:
        int_face_idxs = cargen.trim_boundary(faces_p,
                                             int_face_idxs,
                                             face_adjacency,
                                             cumulative_sum,
                                             param.no_extend_trimming_iteration)
        # remove ears
        for i in range(3):
            int_face_idxs = cargen.remove_ears(faces_p,
                                               int_face_idxs)


    # (optional: for better results but ...)
    #     int_face_idxs  = trim_boundary ( b1_faces, int_face_idxs, face_idxs, cumulative_sum, 1 )

    thickness_profile = cargen.assign_thickness(vertices_p,
                                                faces_p,
                                                vertices_s,
                                                faces_s,
                                                int_face_idxs,
                                                param.thickness_factor)

    " Part D. Harmonic Boundary Blending "

    # external boundary to be set to zero height
    edge_vertex_idxs = igl.boundary_facets(faces_p[base_face_idxs])
    edge_vertex_idxs = np.unique(edge_vertex_idxs.flatten())

    # internal boundary to be set to the thickness
    int_vertex_idxs = np.unique(faces_p[int_face_idxs].flatten())

    # thickness profile
    harmonic_weights = cargen.boundary_value(vertices_p,
                                             faces_p,
                                             edge_vertex_idxs,
                                             int_vertex_idxs,
                                             thickness_profile,
                                             param.blending_order)

    base_vertex_idxs = np.unique(faces_p[base_face_idxs].flatten())

    harmonic_weights = harmonic_weights[base_vertex_idxs]

    # extrude surface
    top_vertices = cargen.extrude_cartilage(vertices_p,
                                            faces_p,
                                            base_face_idxs,
                                            harmonic_weights)

    # flip normals of the bottom surface
    base_faces = faces_p[base_face_idxs]
    base_faces[:, [0, 1]] = base_faces[:, [1, 0]]

    # merge the top and bottom vertices
    cartilage_vertices, cartilage_faces = cargen.merge_surface_mesh(vertices_p,
                                                                    base_faces,
                                                                    top_vertices,
                                                                    faces_p[base_face_idxs])

    # visualizing normals
    #     norm_visualization ( cartilage_vertices, cartilage_faces )

    # clean output
    # cartilage_vertices, cartilage_faces, _, _ = igl.remove_unreferenced(cartilage_vertices, cartilage_faces)
    cartilage_vertices, cartilage_faces = cargen.clean(cartilage_vertices, cartilage_faces)

    top_vertices, top_faces = cargen.clean( top_vertices, faces_p[base_face_idxs])

    # viz
    frame = mp.plot(vertices_bp, faces_p, c=cargen.bone, shading=cargen.sh_false)
    frame.add_mesh(cartilage_vertices, cartilage_faces, c=cargen.pastel_orange, shading=cargen.sh_true)

    frame = mp.plot(top_vertices, top_faces, c=cargen.pastel_green, shading=cargen.sh_true)


    # geometry
    print("cartilage area is: ", np.round(cartilage_area, 2))
    print("mean cartilage thickness is: ", np.round(np.mean(harmonic_weights), 2))
    print("maximum cartilage thickness is: ", np.round(np.max(harmonic_weights), 2))

    return cartilage_vertices, cartilage_faces, top_vertices, top_faces
