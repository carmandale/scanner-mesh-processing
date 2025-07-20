import bpy
from mathutils import Vector


def get_ortho_camera_bounds(camera, scene, distance=1.0, debug=False):
    if camera.data.type != 'ORTHO':
        raise ValueError("Camera must be orthographic")

    render = scene.render
    res_x = render.resolution_x
    res_y = render.resolution_y
    ortho_scale = camera.data.ortho_scale

    max_dim = max(res_x, res_y)
    x_range = ortho_scale * (res_x / max_dim)  # Local X-axis (horizontal)
    y_range = ortho_scale * (res_y / max_dim)  # Local Y-axis (vertical)

    min_x = -x_range / 2
    max_x = x_range / 2
    min_y = -y_range / 2
    max_y = y_range / 2

    cam_matrix = camera.matrix_world

    corners_local_dict = {
        'bottom_left': Vector((min_x, min_y, -distance)),
        'bottom_right': Vector((max_x, min_y, -distance)),
        'top_left': Vector((min_x, max_y, -distance)),
        'top_right': Vector((max_x, max_y, -distance))
    }

    corners_world_space_dict = {
        'bottom_left': cam_matrix @ corners_local_dict['bottom_left'],
        'bottom_right': cam_matrix @ corners_local_dict['bottom_right'],
        'top_left': cam_matrix @ corners_local_dict['top_left'],
        'top_right': cam_matrix @ corners_local_dict['top_right']
    }

    if debug:
        print("")
        for name, corner_location in corners_world_space_dict.items():
            # Create empty at world position
            empty = bpy.data.objects.new(f"{name}", None)
            empty.empty_display_type = 'PLAIN_AXES'
            empty.empty_display_size = 0.1
            empty.location = corner_location
            bpy.context.collection.objects.link(empty)
            print(f"{name}: Local Pos: x={corner_location.x:.4f}, y={corner_location.y:.4f}, z={corner_location.z:.4f}")

    return corners_world_space_dict

# Example usage
camera = bpy.data.objects['Camera']
scene = bpy.context.scene
bounds = get_ortho_camera_bounds(camera, scene, distance=1.0, debug=True)