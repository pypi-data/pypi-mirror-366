import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation


# Utils
def points_to_df(points):
  positions = points['positions'].reshape(-1, 3)
  return pd.DataFrame({
    'x': positions[:, 0],
    'y': positions[:, 1],
    'z': positions[:, 2],
    'intensity': points['intensities'],
    'timestamp': points['timestamps'],
  })


def df_to_points(df):
  return {
    'positions': np.float32(df[['x', 'y', 'z']]),
    'intensities': np.uint8(df['intensity']),
    'timestamps': np.uint32(df['timestamp'])
  }


# Downsample functions
def voxel_downsample(df, voxel_size):
  df = df.sample(frac=1)
  df[['vx', 'vy', 'vz']] = (df[['x', 'y', 'z']] / voxel_size).astype(int)
  return df.groupby(['vx', 'vy', 'vz']).mean()


def voxel_rand_downsample(df, voxel_size):
  df = df.sample(frac=1)
  df[['vx', 'vy', 'vz']] = (df[['x', 'y', 'z']] / voxel_size).astype(int)
  return df.groupby(['vx', 'vy', 'vz']).first()


def hypervoxel_rand_downsample(df, voxel_size, time_window):
  df = df.sample(frac=1)
  df[['vx', 'vy', 'vz']] = (df[['x', 'y', 'z']] / voxel_size).astype(int)
  df['vt'] = (df['timestamp'] / time_window).astype(int)
  return df.groupby(['vx', 'vy', 'vz', 'vt']).first()


def random_downsample(df, ratio: float):
  return df.sample(int(len(df) * ratio))


# Scene downsample
def take_timestamp(elem):
    return elem['timestamp']


def downsample_scene(scene: dict, downsampler):
  total_points = 0
  downsampled_points = 0
  for sensor in scene['sensors']:
    if sensor['type'] == 'lidar':
      sensor['frames'] = sorted(sensor['frames'][:200], key=take_timestamp)
      for frame in sensor['frames']:
        points_df = points_to_df(frame['points'])
        downsampled_df = downsampler(points_df)
        frame['points'] = df_to_points(downsampled_df)
        total_points += len(points_df)
        downsampled_points += len(downsampled_df)
  print(f"Downsampled {total_points} to {downsampled_points} ({downsampled_points/total_points:.04f})")
  return scene
