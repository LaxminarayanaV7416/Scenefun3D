#!/bin/bash

echo "Started Downloading the things"
uv run python -m data_downloader.data_asset_download --split test_set --download_only_one_video_sequence --download_dir data/test --dataset_assets hires_wide_intrinsics hires_poses hires_wide hires_depth

uv run python -m data_downloader.data_asset_download --split custom --download_dir data --visit_id 420673 --video_id 42445198 --dataset_assets hires_wide_intrinsics laser_scan_5mm hires_poses hires_wide hires_depth crop_mask

uv run python -m data_downloader.data_asset_download --split custom --download_dir data --visit_id 420673 --video_id 42445198 --dataset_assets hires_wide_intrinsics laser_scan_5mm hires_poses hires_wide hires_depth crop_mask annotations descriptions motions arkit_mesh transform

uv run python -m data_downloader.data_asset_download --split custom --download_dir data --visit_id 420683 --video_id 42445137 --dataset_assets hires_wide_intrinsics laser_scan_5mm hires_poses hires_wide hires_depth crop_mask annotations descriptions motions arkit_mesh transform

uv run python -m data_downloader.data_asset_download --split custom --download_dir data --visit_id 420693 --video_id 42445173 --dataset_assets hires_wide_intrinsics laser_scan_5mm hires_poses hires_wide hires_depth crop_mask annotations descriptions motions arkit_mesh transform

echo "Downloading completed!!!"