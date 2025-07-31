import os
import numpy.typing as npt
import numpy as np
from typing import Any, List, Iterable, Optional, Union
from dataclasses import dataclass
from subprocess import Popen, PIPE
from tqdm import tqdm

import ffmpeg
from turbojpeg import TurboJPEG
import tempfile

turbo_jpeg = TurboJPEG()


DATA_DIR: str = (
    os.environ["DATA_DIR"]
    if "DATA_DIR" in os.environ
    else f'{os.environ.get("HOME", ".")}/data'
)


@dataclass
class VideoReader:
    video: Union[str, bytes]
    cache_dir: str
    threads: int = 0

    def __init__(
        self,
        video: Union[str, bytes],
        cache_dir: Optional[str] = None,
        threads: int = 0,
    ) -> None:
        self.video = video

        if cache_dir is None:
            if isinstance(video, str):
                with open(video, "rb") as f:
                    video_bytes = f.read()
            else:
                video_bytes = video

            self.cache_dir = os.path.join(
                tempfile.gettempdir(), f"video_reader_{hash(video_bytes)}"
            )
        else:
            self.cache_dir = cache_dir

        os.makedirs(self.cache_dir, exist_ok=True)

        self.threads = threads

    def build_cmd(self, video_file: str) -> List[str]:
        """Creates a command to extract frames from a video file path into
        an output directory using ffmpeg.

        After running the command, images will be outputted as
        `<self.cache_dir>/<1_index_frame_num>.jpg`.

        Parameters
        ----------
        video_file : str
            Path to the input video file

        Returns
        -------
        List[str]
            The ffpmeg command.
        """

        params = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel error",
            "-f mp4",
            f"-i {video_file}",
            os.path.join(self.cache_dir, "%d.jpg"),
        ]

        return [item for param in params for item in param.split(" ", 1)]

    def __get_or_write_video_file(self) -> str:
        """Gets self.video if it is a string, otherwise writes self.video to
        `<self.cache_dir>/video.mp4`.

        Parameters
        ----------
        cache_dir : str
            Directory to write the video file to, if self.video is not a string.

        Returns
        -------
        str
            The path to self.video.
        """

        if isinstance(self.video, str):
            return self.video

        video_file = os.path.join(self.cache_dir, "video.mp4")

        if not os.path.exists(video_file):
            with open(video_file, "wb") as fp:
                fp.write(self.video)

        return video_file

    def get_frame_count(self) -> int:
        """Returns the number of frames in the video."""
        video_file = self.__get_or_write_video_file()
        try:
            probe = ffmpeg.probe(video_file)
        except ffmpeg.Error as e:
            raise ValueError(f"Failed to probe video file: {e}")

        video_streams = [stream for stream in probe.get("streams", []) if stream.get("codec_type") == "video"]
        if not video_streams:
            raise ValueError("No video stream found in file")
        video_stream = video_streams[0]

        nb_frames = video_stream.get("nb_frames", None)
        if nb_frames is not None:
            return int(nb_frames)

        # Fallback: estimate using duration and frame rate
        duration = float(video_stream.get("duration", 0))
        r_frame_rate = video_stream.get("r_frame_rate", "0/0")
        try:
            num, den = map(int, r_frame_rate.split("/"))
            fps = num / den
        except Exception:
            raise ValueError("Could not determine frame rate from stream metadata")
        if fps == 0:
            raise ValueError("Frame rate is zero")
        return int(duration * fps)

    def get_frame_rate(self) -> float:
        """Returns the frame rate (fps) of the video."""
        video_file = self.__get_or_write_video_file()
        try:
            probe = ffmpeg.probe(video_file)
        except ffmpeg.Error as e:
            raise ValueError(f"Failed to probe video file: {e}")

        video_streams = [
            stream for stream in probe.get("streams", []) if stream.get("codec_type") == "video"
        ]
        if not video_streams:
            raise ValueError("No video stream found in file")
        video_stream = video_streams[0]
        # Use avg_frame_rate instead of r_frame_rate because avg_frame_rate provides
        # the average frame rate over the entire video, which is more reliable for
        # determining the overall frame rate, especially for videos with variable frame rates.
        avg_frame_rate = video_stream.get("avg_frame_rate", "0/0")
        try:
            num, den = map(int, avg_frame_rate.split("/"))
            fps = num / den
        except Exception:
            raise ValueError("Could not determine frame rate from stream metadata")
        if fps == 0:
            raise ValueError("Frame rate is zero")
        return fps

    def get_duration(self) -> float:
        """Returns the duration of the video in seconds."""
        video_file = self.__get_or_write_video_file()
        try:
            probe = ffmpeg.probe(video_file)
        except ffmpeg.Error as e:
            raise ValueError(f"Failed to probe video file: {e}")

        format_info = probe.get("format", {})
        duration = format_info.get("duration", None)
        if duration is None:
            raise ValueError("Could not determine duration from video file")
        return float(duration)

    def load(self, frame_num: int) -> npt.NDArray[np.uint8]:
        """Loads a frame from `self.video`.
        Saves video and frames with `self.cache_dir` if defined.
        Will fetch from `self.cache_dir` without loading if possible.

        Parameters
        ----------
        frame_num : int
            0 indexed frame number to return.

        Returns
        -------
        npt.NDArray[np.uint8]
            An image.

        Raises
        ------
        ValueError
            If ffmpeg fails to open.
        """

        image_file = os.path.join(self.cache_dir, f"{frame_num+1}.jpg")

        # Note: I tried to pipe through stdin, but was running into all kinda of errors
        # getting ffmpeg to dmux the raw bytes
        if not os.path.exists(image_file):
            video_file = self.__get_or_write_video_file()

            cmd = self.build_cmd(video_file)

            # start ffmpeg process
            with Popen(cmd, stdin=PIPE) as process:
                if process.stdin is None:
                    raise ValueError("Failed to open ffmpeg process")
                # wait for process to finish
                process.wait()

        with open(image_file, "rb") as fd:
            return turbo_jpeg.decode(fd.read(), 0)


@dataclass
class VideoWriter:
    target_file: str
    fps: Optional[int] = 10
    threads: Optional[int] = 0
    crf: Optional[int] = 24
    show_progress: Optional[bool] = True
    count: int = 0

    def build_cmd(self) -> List[str]:
        params = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel error",
            "-f image2pipe",
            f"-r {self.fps}",
            "-i -",
            "-vcodec libx264",
            "-x264-params keyint=2:scenecut=0",
            "-pix_fmt yuv420p",
            f"-crf {self.crf}",
            f"-r {self.fps}",
            f"-threads {self.threads}",
            "-preset fast",
            self.target_file,
        ]

        return [item for param in params for item in param.split(" ", 1)]

    def encode(self, images: Iterable[Union[str, bytes]]) -> None:
        cmd = self.build_cmd()

        # start ffmpeg process
        process = Popen(cmd, stdin=PIPE)
        if process.stdin is None:
            raise ValueError("Failed to open ffmpeg process")

        if self.show_progress:
            images = tqdm(images)

        # stream images to ffmpeg
        for image in images:
            if isinstance(image, str):
                with open(image, "rb") as fp:
                    image = fp.read()

            process.stdin.write(image)
        process.stdin.close()

        # wait for process to finish
        process.wait()

    def get_video(self) -> bytes:
        with open(self.target_file, "rb") as fp:
            return fp.read()

    def writeFrame(self, im: npt.NDArray) -> None:
        self.jpeg_bytes.append(turbo_jpeg.encode(im, quality=95))
        self.count += 1

    def __enter__(self) -> "VideoWriter":
        self.jpeg_bytes: List[bytes] = []
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        if self.count > 0:
            self.encode(self.jpeg_bytes)


# Util function to generate a video from a list of images
def generate_video(
    image_files: List[str],
    target_file: str,
    fps: Optional[int] = 10,
    threads: Optional[int] = 0,
) -> None:
    encoder = VideoWriter(target_file, fps, threads)
    encoder.encode(image_files)


def write_audio_and_video(audio_file: str, video_file: str, output_file: str) -> None:
    if not os.path.isfile(audio_file) or not os.path.isfile(video_file):
        raise ValueError("Audio or video file does not exist")

    input_video = ffmpeg.input(video_file)
    input_audio = ffmpeg.input(audio_file)
    ffmpeg.concat(input_video, input_audio, v=1, a=1).output(
        output_file, loglevel="error"
    ).overwrite_output().run()
