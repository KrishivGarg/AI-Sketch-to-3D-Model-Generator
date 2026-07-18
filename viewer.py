import open3d as o3d

def display_model_spinning(file_path: str):
    print(f"\n  [viewer] Launching 3D preview for: {file_path}")
    print("  [viewer] Close the window to exit the program.")
    
    # Load the 3D mesh
    mesh = o3d.io.read_triangle_mesh(file_path, enable_post_processing=True)
    
    # Compute normals so lighting works correctly
    if not mesh.has_vertex_normals():
        mesh.compute_vertex_normals()

    # Define the animation callback
    def rotate_view(vis):
        # vis.get_view_control() allows us to manipulate the camera
        ctr = vis.get_view_control()
        
        # Rotate the camera (X_axis_speed, Y_axis_speed)
        # 10.0 provides a smooth, slow rotation. 
        ctr.rotate(10.0, 0.0) 
        
        # Return False to tell the visualizer to keep running
        return False

    # Launch the visualizer with the callback attached
    o3d.visualization.draw_geometries_with_animation_callback(
        [mesh], 
        rotate_view, 
        window_name="EDP - 3D Auto-Viewer",
        width=1024,
        height=768
    )