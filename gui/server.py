import time
import numpy as np
from typing_extensions import assert_never
import viser
from utils.data_parser import DataParser
from utils.fusion_util import PointCloudToImageMapper
import os
import trimesh

class ServerGUI:

    def __init__(self, data_dir):
        self.server = viser.ViserServer()

        ## variables
        self.dataParser = DataParser(data_dir)
        self.master_id_list = {}
        self.DATA_BASE_PATH = os.path.abspath(self.dataParser.data_root_path)
        for i in os.listdir(self.DATA_BASE_PATH):
            if os.path.isdir(os.path.join(self.DATA_BASE_PATH, i)) and i != "test":
                for j in os.listdir(os.path.join(self.DATA_BASE_PATH, i)):
                    if os.path.isdir(os.path.join(self.DATA_BASE_PATH, i, j)):
                        if i in self.master_id_list:
                            self.master_id_list[i].append(j)
                        else:
                            self.master_id_list[i] = [j]

        ## UI Components
        with self.server.gui.add_folder("Main Options"):
            self.gui_reset_scene = self.server.gui.add_button("Reset Frame")
            self.gui_project_rgb_on_laser_scan = self.server.gui.add_button("RGB on Laser Scan")
            self.show_annotations_checkbox = self.server.gui.add_checkbox("Show Annotations", initial_value=False)
        
        with self.server.gui.add_folder("Data Inputs"):
            self.visit_id_dropdown  = self.server.gui.add_dropdown(
                "Visit ID", list(self.master_id_list.keys())
            )

            self.video_id_dropdown  = self.server.gui.add_dropdown(
                "Video ID", self.master_id_list[self.visit_id_dropdown.value]
            )

        with self.server.gui.add_folder("View Options"):
            self.visibility_threshold = self.server.gui.add_slider(
                    "Visibility Threshold", min=0.0, max=1.0, step=0.05, initial_value=0.25
                )
            self.cut_bound = self.server.gui.add_slider(
                    "Cut Bound", min=0, max=50, step=1, initial_value=5
                )
            self.show_frame = self.server.gui.add_checkbox("Show Frame", initial_value=True)
            self.crop_extraneous = self.server.gui.add_checkbox("Crop Extraneous", initial_value=True)

        ## adding all events to UI components
        self.gui_project_rgb_on_laser_scan.on_click(self.show_rgb_on_laser_scan)
        self.gui_reset_scene.on_click(self.show_empty_frame)

        ## on update events
        self.show_frame.on_update(lambda _ : self.draw_frame())
        self.visit_id_dropdown.on_update(lambda event : self.update_visit_id_dropdowns(event))
        self.show_annotations_checkbox.on_update(lambda event : self.show_anotations(event))

    def run(self):
        while True:
            time.sleep(0.2)

    def update_visit_id_dropdowns(self, event):
        self.video_id_dropdown.options = self.master_id_list[self.visit_id_dropdown.value]
        self.video_id_dropdown.value = self.master_id_list[self.visit_id_dropdown.value][0] if len(self.master_id_list[self.visit_id_dropdown.value])>0 else None


    def draw_frame(self):
        self.server.scene.add_frame(
                        "/frame",
                        wxyz=(1.0, 0.0, 0.0, 0.0),
                        position = (0.0, 0.0, 0.0),
                        show_axes=self.show_frame.value,
                        axes_length=5.0,
                    )

    def show_empty_frame(self, gui_event : viser.GuiEvent):
        self.server.scene.reset()
        self.draw_frame()
        
    
    def show_rgb_on_laser_scan(self, gui_event):
        self.server.scene.reset()

        # adding loading notification
        loading_notif = gui_event.client.add_notification(
            title="Loading RGB on Laser Scan",
            body="This indicates the values selected loading is in progress! It will be updated once its completly loaded",
            loading=True,
            with_close_button=False,
            auto_close=False,
        )

        # Read all data assets
        pointcloud = self.dataParser.get_laser_scan(self.visit_id_dropdown.value)
        poses_from_traj = self.dataParser.get_camera_trajectory(self.visit_id_dropdown.value, self.video_id_dropdown.value, pose_source="colmap")
        rgb_frame_paths = self.dataParser.get_rgb_frames(self.visit_id_dropdown.value, self.video_id_dropdown.value, data_asset_identifier="hires_wide")
        depth_frame_paths = self.dataParser.get_depth_frames(self.visit_id_dropdown.value, self.video_id_dropdown.value, data_asset_identifier="hires_depth")
        intrinsics_paths = self.dataParser.get_camera_intrinsics(self.visit_id_dropdown.value, self.video_id_dropdown.value, data_asset_identifier="hires_wide_intrinsics")

        # Process pointcloud
        if self.crop_extraneous.value:
            pointcloud = self.dataParser.get_cropped_laser_scan(self.visit_id_dropdown.value, pointcloud)
        point_positions = np.array(pointcloud.points)
        num_points = point_positions.shape[0]

        # Compute the 3D-2D mapping
        width, height, _, _, _, _ = self.dataParser.read_camera_intrinsics(next(iter(intrinsics_paths.values())))
        point2img_mapper = PointCloudToImageMapper((int(width), int(height)), self.visibility_threshold.value, self.cut_bound.value)

        # Iterate over the frames and compute the average color of the points
        counter = np.zeros((num_points, 1))
        sum_features = np.zeros((num_points, 3))
        skipped_frames = []
        sorted_timestamps = sorted(rgb_frame_paths.keys())
        subsample = 10  # for faster processing

        for cur_timestamp in sorted_timestamps[::subsample]:
            pose = self.dataParser.get_nearest_pose(cur_timestamp, poses_from_traj)
            if pose is None:
                print(f"Skipping frame {cur_timestamp}.")
                skipped_frames.append(cur_timestamp)
                continue

            color = self.dataParser.read_rgb_frame(rgb_frame_paths[cur_timestamp], normalize=True) 
            depth = self.dataParser.read_depth_frame(depth_frame_paths[cur_timestamp]) 
            intrinsic = self.dataParser.read_camera_intrinsics(intrinsics_paths[cur_timestamp], format ="matrix")
            
            # compute the 3D-2D mapping based on the depth
            mapping = np.ones([num_points, 4], dtype=int)
            mapping[:, 1:4] = point2img_mapper.compute_mapping(pose, point_positions, depth, intrinsic)

            if mapping[:, 3].sum() == 0: # no points corresponds to this image, skip
                continue
            
            mask = mapping[:, 3]
            feat_2d_3d = color[mapping[:, 1], mapping[:,2], :]    
            valid_mask = mask != 0
            valid_indices = np.nonzero(valid_mask)[0]
            counter[valid_indices] += 1
            sum_features[valid_indices] += feat_2d_3d[valid_indices]
        
        if len(skipped_frames) > 0:
            print(f"{len(skipped_frames)} frames were skipped because of unmet conditions.")

        counter[counter==0] = 1e-5
        feat_bank = sum_features / counter
        feat_bank[feat_bank[:, 0:3] == [0.0, 0.0, 0.0]] = 169.0 / 255.0

        self.server.scene.add_point_cloud("pcd",
                                    points=point_positions[::subsample] - np.mean(point_positions, axis=0),
                                    colors=feat_bank[::subsample],
                                    point_size=0.01)
        
        loading_notif.title = "Show Default Example Completed"
        loading_notif.body = "Loading show default example is completely loaded"
        loading_notif.loading = False
        loading_notif.with_close_button = True
        loading_notif.auto_close = 5000
        loading_notif.color = "green"


    def show_anotations(self, gui_event):
        if self.show_annotations_checkbox.value:
            self.server.scene.reset()
            # adding loading notification
            loading_notif = gui_event.client.add_notification(
                title="Loading Anotations",
                body="This indicates that default loading example is in progress! It will be updated once its completly loaded",
                loading=True,
                with_close_button=False,
                auto_close=False,
            )        

            laser_point_cloud = self.dataParser.get_laser_scan(self.visit_id_dropdown.value)
            points = np.array(laser_point_cloud.points) - np.mean(laser_point_cloud.points, axis=0)
            colors = np.array(laser_point_cloud.colors)
            
            arkit_mesh = self.dataParser.get_arkit_reconstruction(self.visit_id_dropdown.value,
                                                                self.video_id_dropdown.value, format="mesh")
            transform = self.dataParser.get_transform(self.visit_id_dropdown.value, 
                                                    self.video_id_dropdown.value)
            arkit_mesh.transform(np.linalg.inv(transform))
            arkit_mesh.translate(-np.mean(laser_point_cloud.points, axis=0))
            vertices = np.asarray(arkit_mesh.vertices)
            faces = np.asarray(arkit_mesh.triangles)
            mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
            
            points = np.array(laser_point_cloud.points) - np.mean(laser_point_cloud.points, axis=0)
            colors = np.array(laser_point_cloud.colors)
            annotations = self.dataParser.get_annotations(self.visit_id_dropdown.value)
            descriptions = self.dataParser.get_descriptions(self.visit_id_dropdown.value)
            motions = self.dataParser.get_motions(self.visit_id_dropdown.value)
            
            # server.scene.add_point_cloud(f"scene", points=points[::10], colors=colors[::10], point_size=0.01)
            self.server.scene.add_mesh_trimesh(name="/trimesh", mesh=mesh)
            
            annotation_positions = {}
            for i, annotation in enumerate(annotations):
                annot_id = annotation["annot_id"]
                label = annotation["label"]
                if label == "exclude":
                    continue
                point_ids = annotation["indices"]
                annotation_positions[annot_id] = np.mean(points[point_ids], axis=0)
                self.server.scene.add_point_cloud(f"annotations/{i}/mask",
                                            points=points[point_ids],
                                            colors=colors[point_ids],
                                            point_size=0.01)
                self.server.scene.add_label(f"annotations/{i}/label",
                                    label,
                                    position=annotation_positions[annot_id])
            
            for i, description in enumerate(descriptions):
                annot_id = description["annot_id"][0]
                description_text = description["description"]
                self.server.scene.add_label(f"descriptions/{i}/description",
                                    f'"{description_text}"',
                                    position=annotation_positions[annot_id] - np.array([0.0, 0.0, 0.1]))
                
            for i, motion in enumerate(motions):
                annot_id = motion["annot_id"]
                motion_type = motion["motion_type"]
                motion_dir = motion["motion_dir"]
                motion_origin_idx = motion["motion_origin_idx"]
                motion_viz_orient = motion["motion_viz_orient"]
                if motion_type == "trans":  # translateion
                    if motion_viz_orient == "inwards":
                        segment = np.array([points[motion_origin_idx], points[motion_origin_idx] - (np.array(motion_dir) / 5.0)])  
                        self.server.scene.add_line_segments(f"motions/{i}/inwards", points=np.expand_dims(segment, 0), colors=[0, 255, 0], line_width=5)
                    elif motion_viz_orient == "outwards":
                        segment = np.array([points[motion_origin_idx], points[motion_origin_idx] + (np.array(motion_dir) / 5.0)])  
                        self.server.scene.add_line_segments(f"motions/{i}/outwards", points=np.expand_dims(segment, 0), colors=[255, 0, 0], line_width=5)
                elif motion_type == "rot":  # rotation
                    vector1 = annotation_positions[annot_id] - points[motion_origin_idx]
                    vector1_norm = np.linalg.norm(vector1)
                    segments = np.array([
                        [annotation_positions[annot_id], points[motion_origin_idx] + (np.array(motion_dir)) * vector1_norm*0.5],
                        [annotation_positions[annot_id], points[motion_origin_idx] - (np.array(motion_dir)) * vector1_norm*0.5],
                        [points[motion_origin_idx] + (np.array(motion_dir)) * vector1_norm * 0.5,
                        points[motion_origin_idx] - (np.array(motion_dir)) * vector1_norm * 0.5],
                        ])
                    self.server.scene.add_line_segments(f"motions/{i}/outwards", points=segments, colors=[0, 0, 255], line_width=5)

            loading_notif.title = "Loading Anotations Completed"
            loading_notif.body = "Loading Show Anotations is completely loaded"
            loading_notif.loading = False
            loading_notif.with_close_button = True
            loading_notif.auto_close = 5000
            loading_notif.color = "green"