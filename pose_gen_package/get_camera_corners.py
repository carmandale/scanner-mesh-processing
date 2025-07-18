import os
import bpy
import sys
from mathutils import Vector


print('\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬ GET CAM BOUNDS ▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 07.17.25 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n')


def get_ortho_camera_bounds(distance=1.0, debug=False):
    camera = bpy.data.objects['Camera']
    if camera is None:
        print("ERROR: No camera found in the scene.")
        return sys.exit(1)

    if camera.data.type != 'ORTHO':
        print("ERROR: The active camera is not an orthographic camera.")
        return sys.exit(1)

    render = bpy.context.scene.render
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
            print(f"{name}: World Pos: x={corner_location.x:.4f}, y={corner_location.y:.4f}, z={corner_location.z:.4f}")

    return corners_world_space_dict


def main():
    CORNERS = get_ortho_camera_bounds(distance=1.0, debug=False)
    BLEND_DIR = bpy.path.abspath("//")
    BLEND_FILENAME = bpy.path.basename(bpy.data.filepath).split(".")[0]
    OUT_TXT = os.path.join(BLEND_DIR, (f"{BLEND_FILENAME}_camera_corners.txt"))

    if not CORNERS:
        print("No camera corners found. Exiting.")
        return

    print(f"Writing camera corners to: {OUT_TXT}")
    with open(OUT_TXT, 'w') as f:
        for name, corner in CORNERS.items():
            f.write(f"{name} {corner.x:.4f} {corner.y:.4f} {corner.z:.4f}\n")


if __name__ == '__main__':
    main()