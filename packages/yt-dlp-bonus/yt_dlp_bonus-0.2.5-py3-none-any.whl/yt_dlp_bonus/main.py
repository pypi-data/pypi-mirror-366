import json
import os
import re
import shutil
import warnings
import typing as t
from uuid import uuid4
from pathlib import Path
from yt_dlp import YoutubeDL
from yt_dlp_bonus.models import (
    ExtractedInfo,
    VideoFormats,
    ExtractedInfoFormat,
    SearchExtractedInfo,
)
from yt_dlp_bonus.constants import (
    videoExtensions,
    audioExtensions,
    videoQualities,
    audioQualities,
    mediaQualities,
    audioBitrates,
    videoExtensionsType,
    audioExtensionsType,
    audioQualitiesType,
    videoQualitiesType,
    mediaQualitiesType,
    audioBitratesType,
    video_audio_quality_map,
)
from yt_dlp_bonus.utils import (
    logger,
    assert_instance,
    assert_type,
    assert_membership,
    get_size_string,
    run_system_command,
)
from yt_dlp_bonus.exceptions import (
    UserInputError,
    FileSizeOutOfRange,
    UknownDownloadFailure,
    IncompatibleMediaFormats,
)

from yt_dlp_bonus.utils import sanitize_filename

qualityExtractedInfoType = dict[mediaQualitiesType, ExtractedInfoFormat]

height_quality_map: dict[int | None, videoQualitiesType] = {
    144: "144p",
    240: "240p",
    360: "360p",
    480: "480p",
    720: "720p",
    1080: "1080p",
    1350: "1440p",
    2026: "2160p",
    4320: "4320p",
    None: "medium",
}
"""Maps the ExtractedInfoFormat.height to the video quality"""

_height_quality_map = height_quality_map.copy()

_height_quality_map.pop(None)

quality_height_map: dict[videoQualitiesType, int] = dict(
    zip(_height_quality_map.values(), _height_quality_map.keys())
)
quality_height_map.update({"2k": 1350, "4k": 2026, "8k": 4320})

"""Maps video quality to it's respective video height"""

protocol_informat_map = {
    "m3u8_native": "m3u8_native",
    "https+https": "m3u8_native",
    "m3u8_native+https": "m3u8_native",
    "https": "https",
}
"""Maps the `ExtractedInfo.protocol` to `ExtractedInfoFormat.protocol`"""


class YoutubeDLBonus(YoutubeDL):
    """An extension class of YoutubeDL which pydantically models url & search results and manipulate them."""

    def __init__(self, params: dict = {}, auto_init: bool = True):
        """`YoutubeDLBonus` Constructor

        Args:
            params (dict, optional): YoutubeDL options. Defaults to {}.
            auto_init (optional, bool): Whether to load the default extractors and print header (if verbose).
                            Set to 'no_verbose_header' to not print the header. Defaults to True.
        """
        params.setdefault("noplaylist", True)
        super().__init__(params, auto_init)

    def __enter__(self) -> "YoutubeDLBonus":
        self.save_console_title()
        return self

    def get_format_quality(
        self, info_format: ExtractedInfoFormat
    ) -> mediaQualitiesType:
        """Tries to find out the quality of a format.

        Args:
            info_format (ExtractedInfoFormat): Format

        Returns:
            mediaQualitiesType: Format quality
        """
        assert_instance(info_format, ExtractedInfoFormat, "info_format")

        if info_format.format_note:
            if info_format.format_note in mediaQualities:
                return info_format.format_note
            if (
                info_format.format_note == "Default"
                and info_format.resolution == "audio only"
            ):
                return "medium"

        return height_quality_map.get(info_format.height)

    def process_extracted_info(
        self, extracted_info: ExtractedInfo, filter_best_protocol: bool = True
    ) -> ExtractedInfo:
        """Updates https chunk size to formats, filter best protocol and update ip param in download url.

        Args:
            extracted_info (ExtractedInfo)
            filter_best_protocol (bool, optional): Retain only formats that can be downloaded faster. Defaults to True.

        Returns:
            ExtractedInfo: Processed ExtractedInfo
        """
        assert_instance(extracted_info, ExtractedInfo, "extracted_info")
        sorted_formats = []
        target_format_protocol = protocol_informat_map.get(
            extracted_info.protocol, "https"
        )
        # print(data["protocol"], target_format_protocol)
        for format in extracted_info.formats:
            if filter_best_protocol:
                if format.protocol == target_format_protocol:
                    # print(target_format_protocol, format.protocol)
                    if not format.format_note:
                        # fragmented
                        format.format_note = self.get_format_quality(format)
                    else:
                        # https
                        format.downloader_options.http_chunk_size = (
                            format.filesize_approx
                        )
                sorted_formats.append(format)
            else:
                format.downloader_options.http_chunk_size = format.filesize_approx

                sorted_formats.append(format)

        extracted_info.formats = sorted_formats
        return extracted_info

    def model_extracted_info(
        self,
        data: dict,
        filter_best_protocol: bool = True,
        drop_requested_formats=False,
    ) -> ExtractedInfo:
        """Generate a model for the extracted video info.

        Args:
            data (dict): Extracted video info.
            filter_best_protocol (optional, bool): Retain only formats that can be downloaded faster. Defaults to True.
            drop_requested_formats (bool, optional): Drop requested formats. Ideal for use with ytdlp methods. Defaults to False.

        Returns:
            ExtractedInfo: Modelled video info
        """
        extracted_info = ExtractedInfo(**data)
        if drop_requested_formats:
            extracted_info.requested_formats = None
            extracted_info.requested_subtitles = None

        return self.process_extracted_info(extracted_info, filter_best_protocol)

    def extract_info_and_form_model(
        self,
        url: str,
        filter_best_protocol: bool = True,
        process=True,
        drop_requested_formats=False,
    ) -> ExtractedInfo:
        """Exract info for a particular url and model the response.

        Args:
            url (str): Youtube video url
            filter_best_protocol (optional, bool): Retain only formats that can be downloaded faster. Defaults to True.
            process (bool, optional): Process the extracted info. Defaults to True.
            drop_requested_formats (bool, optional): Drop requested formats. Ideal for use with ytdlp methods. Defaults to False.

        Returns:
            ExtractedInfo: Modelled video info
        """
        extracted_info = self.extract_info(url, download=False, process=process)
        return self.model_extracted_info(
            extracted_info, filter_best_protocol, drop_requested_formats
        )

    def search_and_form_model(
        self, query: str, limit: int = 5, filter_best_protocol: bool = True
    ) -> SearchExtractedInfo:
        """Perform a video search and model the response.

        Args:
            query (str): Search query.
            limit (int, optional): Search results (video) amount. Defaults to 5.
            filter_best_protocol (bool, optional): Retain only formats that can be downloaded faster. Defaults to True.
        Returns:
            SearcheExtractedInfo: Modelled search results
        """
        assert (
            self.params.get("noplaylist", True) is True
        ), f"This function is only useful when playlist searching is disabled. Deactivate it on params 'noplaylist=True'"
        assert limit > 0, f"Results Limit should be greater than 0 not {limit}."
        search_extracted_info = self.extract_info(
            f"ytsearch{limit}:{query}", download=False
        )
        modelled_search_extracted_info = SearchExtractedInfo(**search_extracted_info)
        processed_entries = []
        for extracted_info in modelled_search_extracted_info.entries:
            processed_entries.append(
                self.process_extracted_info(extracted_info, filter_best_protocol)
            )
        modelled_search_extracted_info.entries = processed_entries
        return modelled_search_extracted_info

    def load_extracted_info_from_json_file(
        self, to_json_path: Path | str, **kwargs
    ) -> ExtractedInfo:
        """Read extracted video info from .json and return it's modelled version

        Args:
            to_json_path (Path | str): Path to `.json` file containing the extracted video info.

        Returns:
            ExtractedInfo: Modelled video info.
        """
        with open(to_json_path) as fh:
            data = json.load(fh)
        return self.model_extracted_info(data, **kwargs)

    def dump_extracted_info_to_json_file(
        self,
        extracted_info: t.Union[ExtractedInfo, SearchExtractedInfo],
        save_to: t.Union[Path, str],
        **kwargs,
    ) -> t.NoReturn:
        """Save extracted info to a json file.

        Args:
            extracted_info (t.Union[ExtractedInfo, SearchExtractedInfo]): Video extracted-info or search extracted-info.
            save_to(t.Union[Path, str]): Path to save contents to.
            **kwargs: Keyworded args for `json.dump`

        Returns:
            t.NoReturn
        """
        assert_instance(
            extracted_info, (ExtractedInfo, SearchExtractedInfo), "extracted_info"
        )
        with open(save_to, "w") as fh:
            json.dump(extracted_info.model_dump(), fh, **kwargs)

    def separate_videos_by_extension(
        self, extracted_info: ExtractedInfo
    ) -> VideoFormats:
        """Separate videos available based on their extensions (webm, mp4)

        Args:
            extracted_info (ExtractedInfo): Modelled extracted video info.

        Returns:
            VideoFormats: Video separated into webm and mp4.
        """
        assert_instance(extracted_info, ExtractedInfo, "extracted_info")
        webm_videos: list = []
        mp4_videos: list = []

        for format in extracted_info.formats:
            if format.ext in audioExtensions:
                ## video = [ext=webm, format_note = videoQualities]
                ## audio = [ext=webm, format_note = audioQualities]
                if format.format_note in audioQualities:
                    # Let's append audio to be accessible from both extensions
                    webm_videos.append(format)
                    mp4_videos.append(format)
                else:
                    webm_videos.append(format)
            elif format.ext == "mp4":
                mp4_videos.append(format)

        return VideoFormats(webm=webm_videos, mp4=mp4_videos)

    def get_video_qualities_with_extension(
        self,
        extracted_info: ExtractedInfo,
        ext: videoExtensionsType = "mp4",
        audio_ext: audioExtensionsType = "webm",
    ) -> qualityExtractedInfoType:
        """Create a map of video qualities and their metadata.

        Args:
            extracted_info (ExtractedInfo): Extracted video info (modelled)
            ext (t.Literal["webm", "mp4"], optional): Video extensions. Defaults to "mp4".
            audio_ext (t.Literal["m4a", "webm", "opus"], optional): Audio extensions. Defaults to "webm".

        Returns:
            dict[mediaQualities,ExtractedInfoFormat]
        """
        separated_videos = self.separate_videos_by_extension(extracted_info)
        assert_membership(videoExtensions, ext, "Extension (ext)")
        assert_membership(audioExtensions, audio_ext, "Audio extension (audio_ext)")
        formats: list[ExtractedInfoFormat] = getattr(separated_videos, ext)
        response_items = {}
        for format in formats:
            if format.format_note and format.format_note in mediaQualities:
                if format.resolution == "audio only" and not format.ext == audio_ext:
                    continue
                response_items[format.format_note] = format

        return t.cast(qualityExtractedInfoType, response_items)

    def update_audio_video_size(
        self,
        quality_extracted_info: qualityExtractedInfoType,
        audio_quality: audioQualitiesType = "medium",
    ) -> qualityExtractedInfoType:
        """Takes the targeted audio size and adds it with that of each video.
        Updates the value to `filesize_approx` variable.

        Args:
            quality_extracted_info (qualityExtractedInfoType): Video qualities mapped to their ExtractedInfo.
            audio_quality (audioQualities): Audio qaulity from `ultralow`, `low`, `medium`.

        Returns:
            qualityExtractedInfoType: Updated qualityExtractedInfoType.
        """
        assert_type(
            quality_extracted_info,
            (qualityExtractedInfoType, dict),
            "quality_extracted_info",
        )
        assert_type(audio_quality, (audioQualitiesType, str), "audio_quality")
        try:
            chosen_audio_format = (
                quality_extracted_info.get(audio_quality)
                or quality_extracted_info.get("medium")
                or quality_extracted_info.get("low")
                or quality_extracted_info["ultralow"]
            )
            filesize_approx = chosen_audio_format.filesize_approx
        except KeyError:
            warnings.warn(
                (
                    "Failed to get any audio quality for estimating total video size. "
                    "Audio filesize approximation will be 0."
                ),
                UserWarning,
            )
            filesize_approx = 0

        for quality, format in quality_extracted_info.items():
            if quality in videoQualities:
                if format.filesize_approx > 0:
                    format.audio_video_size = format.filesize_approx + filesize_approx
            else:
                format.audio_video_size = format.filesize_approx
            quality_extracted_info[quality] = format

        return t.cast(qualityExtractedInfoType, quality_extracted_info)


class PostDownload:
    """Provides post download utilities"""

    merge_audio_and_video_command_template = 'ffmpeg -i "%(video_path)s" -i "%(audio_path)s" -c copy "%(output)s" -y -threads auto'
    audio_to_mp3_conversion_command_template = (
        'ffmpeg -i "%(input)s" -b:a %(bitrate)s "%(output)s" -y -threads auto'
    )

    def __init__(self, clear_temps: bool = False):
        """Constructor for `PostDownload`

        Args:
            clear_temps (bool, optional): Delete temporary files. Defaults to False.
        """
        self.clear_temps: bool = clear_temps
        self.temp_dir: Path = None

    def __enter__(self) -> "PostDownload":
        return self

    def clear_temp_files(self, *temp_files: Path | str):
        """Remove temporary files.

        Args:
            temp_files t.Sequence[Path|str]: temporary files.
        """
        if not self.clear_temps:
            logger.info(f"Ignoring temp-file clearance.")
            if self.temp_dir:
                for temp_file in temp_files:
                    try:
                        shutil.move(temp_file, self.temp_dir)
                    except Exception as e:
                        logger.error(
                            f"Error while moving temp_file '{temp_file}' to temp_dir '{self.temp_dir}' - {e} "
                        )
            return
        for temp_file in temp_files:
            logger.warning(f"Clearing temporary file - {temp_file}")
            try:
                os.remove(temp_file)
            except Exception as e:
                logger.exception(f"Failed to clear temp-file {temp_file}")

    def merge_audio_and_video(
        self, audio_path: Path, video_path: Path, output: Path | str
    ) -> Path:
        """Combines separate audio and video into one.

        Args:
            audio_path (Path): Path to audio file.
            video_path (Path): Path to video file.
            output (Path | str): Path to save the combined clips.

        Returns:
            Path: The clip path.

        ## Requires `ffmpeg` installed in system.
        """
        assert (
            audio_path.is_file()
        ), f"Audio file does not exists in path - {audio_path} "
        assert (
            video_path.is_file()
        ), f"Video file does not exists in path - {video_path}"
        assert not Path(
            str(output)
        ).is_dir(), f"Output path cannot be a directory - {output}"
        command = self.merge_audio_and_video_command_template % (
            dict(video_path=video_path, audio_path=audio_path, output=output)
        )
        logger.info(
            f"Merging audio and video - ({audio_path}, {video_path}) - {output}"
        )
        is_successful, resp = run_system_command(command)
        if not is_successful:
            raise RuntimeError("Failed to merge audio and video clips") from resp
        self.clear_temp_files(audio_path, video_path)
        return Path(str(output))

    def convert_audio_to_mp3_format(
        self, input: Path, output: Path | str, bitrate: audioBitratesType = "128k"
    ) -> Path:
        """Converts `.webm` and `.m4a` audio formats to `.mp3`.

        Args:
            input (Path): Path to audio file.
            output (Path | str): Path to save the mp3 file.
            bitrate (audioBitratesType, optional): Encoding bitrates. Defaults to "128k".

        Raises:
            RuntimeError: Incase conversion fails.

        Returns:
            Path: The clip path.
        """
        assert input.is_file(), f"Invalid value for input file - {input}"
        assert not Path(
            str(output)
        ).is_dir(), f"Output path cannot be a directory - {output}"
        assert_membership(audioBitrates, bitrate)
        command = self.audio_to_mp3_conversion_command_template % dict(
            input=input, bitrate=bitrate, output=output
        )
        logger.info(f"Converting audio file to mp3 - ({input}, {output})")
        is_successful, resp = run_system_command(command)
        if not is_successful:
            raise RuntimeError("Failed to convert audio to mp3") from resp
        self.clear_temp_files(input)
        return Path(str(output))


class Downloader(PostDownload):
    """Download audios and videos"""

    video_output_ext = ["mkv", "webm", "mp4"]
    audio_format_ext = ["aac", "opus", "mp3", "flac", "vorbis", "m4a", "webm"]
    default_ydl_output_format = "%(title)s (%(format_note)s, %(id)s).%(ext)s"

    default_video_extension_for_sorting: videoExtensionsType = "mp4"
    default_audio_extension_for_sorting: audioExtensionsType = "webm"

    def __init__(
        self,
        yt: YoutubeDLBonus,
        working_directory: Path | str = os.getcwd(),
        clear_temps: bool = True,
        filename_prefix: str = "",
        audio_quality: audioQualitiesType = None,
        default_audio_quality: audioQualitiesType = "medium",
        default_video_quality: videoQualitiesType = "720p",
        min_filesize: int = None,
        max_filesize: int = None,
    ):
        """`Download` Constructor

        Args:
            working_directory (Path | str, optional): Diretory for saving files. Defaults to os.getcwd().
            clear_temps (bool, optional): Flag for clearing temporary files after download. Defaults to True.
            filename_prefix (str, optional): Downloaded filename prefix. Defaults to "".
            audio_quality (str, audioQualitieType): Default audio quality to be merged with video. Defaults to None [auto].
            min_filesize(int, Optional): Minimum downloadable filesize (bytes). Defaults to ytdl.param's min_filesize.
            max_filesize(int, Optional): Maximum downloadable filesize (bytes). Defaults to ytdl.param's max_filesize.
        """
        super().__init__(clear_temps=clear_temps)
        assert_membership(
            audioQualities, default_audio_quality, "Default audio quality"
        )
        assert_membership(
            videoQualities, default_video_quality, "Default video quality"
        )

        self.yt = yt
        self.working_directory = Path(str(working_directory))
        self.clear_temps = clear_temps
        self.filename_prefix = filename_prefix
        self.audio_quality = audio_quality
        self.default_audio_quality = default_audio_quality
        self.default_video_quality = default_video_quality
        assert (
            self.working_directory.is_dir()
        ), f"Working directory chosen is invalid - {self.working_directory}"
        self.temp_dir = self.working_directory.joinpath("temps")
        os.makedirs(self.temp_dir, exist_ok=True)

        self.minimum_filesize = (min_filesize or yt.params.get("min_filesize")) or 0
        self.maximum_filesize = (
            max_filesize or yt.params.get("max_filesize")
        ) or 1_073_741_824

    def __enter__(self) -> "Download":
        return self

    def save_to(self, title: str, ext: str = "", is_temp: bool = False) -> Path:
        """Get sanitized path to save a file

        Args:
            title (str): Video title.
            ext (str): File extension. defaults to "".
            is_temp (bool, optional): Flag for temporary file. Defaults to False.

        Returns:
            Path: Path of the file.
        """
        sanitized_filename = sanitize_filename(self.filename_prefix + title)
        parent = self.temp_dir if is_temp else self.working_directory
        extension = ext if ext.startswith(".") else ("." + ext)
        return parent.joinpath(sanitized_filename + extension)

    def _verify_download(self, download_resp: tuple[str]) -> t.NoReturn:
        """Tries to detect presence of download failure and raise exception if found.

        Args:
            download_resp (tuple[str]): response of `self.yt.download`

        Raises:
            FileSizeOutOfRange: When a file to be downloaded is not within the min_filesize and max_filesize.
            UknownDownloadFailure: When ytdl fails to download a file due to unknown reasons.

        Returns:
            t.NoReturn
        """
        is_sucessful, is_new_download = download_resp
        if not is_sucessful:
            min_filesize = self.yt.params.get("min_filesize")
            max_filesize = self.yt.params.get("max_filesize")
            if min_filesize or max_filesize:
                raise FileSizeOutOfRange(
                    "The file-size of the requested quality is out of downloadable "
                    f"range ({get_size_string(min_filesize)} - {get_size_string(max_filesize)})."
                )
            raise UknownDownloadFailure(
                f"File of the requested quality could not be downloaded due to unknown reasons. "
                "Try downloading other smaller qualities."
            )

    def assert_is_downloadable(
        self, info_format: ExtractedInfoFormat
    ) -> ExtractedInfoFormat:
        """Checks if the file is within downloadable range or raise FileSizeOutOfRange exception

        Args:
            info_format (ExtractedInfoFormat)

        Returns:
            ExtractedInfoFormat
        """
        assert_instance(info_format, ExtractedInfoFormat, "info_format")
        if info_format.audio_video_size > self.maximum_filesize:
            raise FileSizeOutOfRange(
                "The file-size of the requested quality is greater than the maximum "
                f"downloadable size ({get_size_string(self.maximum_filesize)})"
            )
        elif info_format.audio_video_size < self.minimum_filesize:
            raise FileSizeOutOfRange(
                "The file-size of the requested quality is lesser than the minimum "
                f"downloadable size ({get_size_string(self.minimum_filesize)})"
            )
        return info_format

    def run(
        self,
        title: str,
        qualities_format: qualityExtractedInfoType,
        quality: mediaQualitiesType = None,
        bitrate: audioBitratesType = "128k",
        retain_extension: bool = False,
    ) -> Path:
        """Download the media and save in disk.

        Args:
            title (str): Video title.
            qualities_format (qualityExtractedInfoType): Dictionary of qualities mapped to their `ExtractedInfoFormats`.
            quality (mediaQualitiesType): Quality of the media to be downloaded. Defaults to "720p|medium".
            bitrate (audioBitratesType, optional): Audio encoding bitrates. Make it None to retains its's initial format. Defaults to "128k".
            retain_extension (bool, optional): Use the format's extension and not default mp4 for videos. Defaults to False.

        Returns:
              Path: Path to the downloaded file.
        """
        assert title, "Video title cannot be null"
        assert_type(
            qualities_format, (qualityExtractedInfoType, dict), "qualities_format"
        )
        title = f"{title} {quality}"
        sample_info_format = qualities_format.get(list(qualities_format.keys())[0])
        if sample_info_format.audio_video_size == 0:
            qualities_format = self.yt.update_audio_video_size(
                qualities_format, self.default_audio_quality
            )
        if quality in videoQualities:
            if not quality:
                quality = self.default_video_quality
            else:
                assert_membership(videoQualities, quality, "Video quality")
            assert (
                quality in qualities_format
            ), f"The video does not support the targeted video quality - {quality}"
            target_format = self.assert_is_downloadable(qualities_format[quality])
            target_audio_format = self.assert_is_downloadable(
                qualities_format[
                    (
                        self.audio_quality
                        if self.audio_quality
                        else video_audio_quality_map.get(quality, "medium")
                    )
                ]
            )

            if target_format.ext == "webm" and target_audio_format.ext == "m4a":
                raise IncompatibleMediaFormats(
                    f"Cannot merge a video with 'webm' extension and an audio with 'm4a' extension."
                )
            # Video being handled
            save_to = self.save_to(
                title, ext=target_format.ext if retain_extension else "mp4"
            )
            if save_to.exists():
                # let's presume it was previously processed.
                return save_to

            # Need to download both audio and video and then merge
            logger.info(
                f"Downloading video - {title} ({target_format.resolution}) [{get_size_string(target_format.filesize_approx)}]"
            )
            # Let's download video
            video_temp = f"temp_{str(uuid4())}.{target_format.ext}"
            self._verify_download(
                self.yt.dl(name=video_temp, info=target_format.model_dump())
            )
            # Let's download audio
            logger.info(
                f"Downloading audio - {title} ({target_audio_format.resolution}) [{get_size_string(target_audio_format.filesize_approx)}]"
            )
            audio_temp = f"temp_{str(uuid4())}.{target_audio_format.ext}"
            self._verify_download(
                self.yt.dl(name=audio_temp, info=target_audio_format.model_dump())
            )

            self.merge_audio_and_video(
                audio_path=Path(audio_temp),
                video_path=Path(video_temp),
                output=save_to,
            )
        elif quality in audioQualities:
            # Download the desired audio quality
            assert_membership(audioBitrates + (None,), bitrate, "bitrate")
            if not quality:
                quality = self.default_audio_quality
            else:
                assert_membership(audioQualities, quality, "Audio quality")
            assert (
                quality in qualities_format
            ), f"The video does not support the targeted audio quality - {quality}"
            target_format = self.assert_is_downloadable(qualities_format[quality])
            title = f"{title} {bitrate}" if bitrate else title
            save_to = self.save_to(title, ext="mp3" if bitrate else target_format.ext)
            if save_to.exists():
                # let's presume it was previously processed.
                return save_to
            logger.info(
                f"Downloading audio - {title} ({target_format.resolution}) [{get_size_string(target_format.filesize_approx)}]"
            )
            audio_temp = f"temp_{str(uuid4())}.{target_format.ext}"
            self._verify_download(
                self.yt.dl(name=audio_temp, info=target_format.model_dump())
            )
            # Move audio to static
            if bitrate:
                # Convert to mp3
                self.convert_audio_to_mp3_format(
                    input=Path(audio_temp), output=save_to, bitrate=bitrate
                )
            else:
                # Retain in it's format
                # Move the file from tempfile to working directory
                shutil.move(Path(audio_temp), save_to)
        else:
            raise UserInputError(
                f"The targeted format and quality mismatched - {quality}"
            )
        return save_to

    def _get_updated_ytdl_params(
        self, update: dict, progress_hooks: list[t.Callable]
    ) -> dict:
        params = self.yt.params.copy()
        if (
            params.get("outtmpl", {}).get("default", "%(title)s [%(id)s].%(ext)s")
            == "%(title)s [%(id)s].%(ext)s"
        ):
            params["outtmpl"]["default"] = (
                self.filename_prefix + self.default_ydl_output_format
            )
        update["progress_hooks"] = params.get("progress_hooks", []) + progress_hooks
        params.update(update)
        return params

    def ydl_run(
        self,
        extracted_info: ExtractedInfo,
        video_format: t.Union[videoQualitiesType, str] = "bestvideo",
        audio_format: t.Union[
            t.Literal["aac", "opus", "mp3", "flac", "vorbis", "m4a", "webm"],
            str,
            audioQualitiesType,
        ] = "bestaudio",
        default_format: str = "best",
        output_ext: t.Literal["mkv", "webm", "mp4"] = None,
        progress_hooks: list[t.Callable] = [],
        ytdl_params: dict = {},
    ) -> dict:
        """
        Run the video download process using yt-dlp with specified formats and options.
        Args:
            extracted_info (ExtractedInfo): The extracted information about the video.
            video_format (t.Union[videoQualitiesType, str], optional): The desired video format. format_id etc are accepted. Defaults to "bestvideo".
            audio_format (t.Union[t.Literal['aac', 'opus', 'mp3', 'flac', 'vorbis'], str, audioQualitiesType], optional): The desired audio format. format_id etc are accepted. Defaults to "bestaudio".
            default_format (str, Optional) Default format to be used as fallback incase both video_format and audio_format are None. Defaults to "best".
            output_ext (t.Literal["mkv", "webm", "mp4"], Optional): The desired output file extension. Defaults to None (default).
            progress_hooks (list[t.Callable], Optional): Functions that get called on download progress, with a dictionary with the entries. Defaults to [].
            ytdl_params (dict, Optional): YoutubeDL options. Defaults to {}.
        returns:
            dict: A dictionary containing the result of the download process.

        """
        assert_instance(extracted_info, ExtractedInfo, "extracted_info")
        extracted_info.requested_formats = None
        if video_format and str(video_format) in quality_height_map.keys():
            video_format = f"bestvideo[height={quality_height_map[video_format]}]"

        if audio_format and str(audio_format) in audioQualities:
            format_ext = self.yt.get_video_qualities_with_extension(
                extracted_info,
                ext=self.default_video_extension_for_sorting,
                audio_ext=self.default_audio_extension_for_sorting,
            )
            target_audio_format = format_ext.get(audio_format)
            assert target_audio_format, (
                f"The desired audio format '{audio_format}' is not supported by the video."
                f" Try other formats from {audioQualities} or use audio format_id."
            )
            audio_format = target_audio_format.format_id

        if video_format and audio_format:
            format = f"{video_format}+{audio_format}"
        elif video_format:
            format = f"{video_format}"
        elif audio_format:
            format = f"{audio_format}"

        elif default_format:
            format = default_format
        else:
            raise Exception(
                "Atleast one of the following parameters must have a positive value for download "
                "process to take place : audio_format, video_format and default_format."
            )

        ytdl_params.update(
            {
                "format": format,
            }
        )
        if output_ext is not None:
            ytdl_params["merge_output_format"] = output_ext

        params = self._get_updated_ytdl_params(
            ytdl_params,
            progress_hooks,
        )
        ytdl = YoutubeDL(params)
        info_dict = extracted_info.model_dump()
        processed_info_dict = ytdl.process_video_result(info_dict, download=True)
        processed_info_dict["filepath"] = processed_info_dict["requested_downloads"][0][
            "filepath"
        ]
        return processed_info_dict

    def ydl_run_audio(
        self,
        extracted_info: ExtractedInfo,
        bitrate: audioBitratesType = "128k",
        **kwargs,
    ) -> dict:
        """Download `audio only` shortcut for `.ydl_run`. Convert to `mp3` on demand.
        Args:
            extracted_info (ExtractedInfo) The extracted information about the video.
            bitrate (audioBitratesType, Optional): Mp3 conversion bitrate. Set None to retain in its original extension. Defaults to 128k.
            **kwargs: Additional keyword arguments for `ydl_run`
        Returns:
            A dictionary containing the results of the video download and processing.
        """
        assert_membership(audioBitrates + (None,), bitrate, "bitrate")
        kwargs["video_format"] = None
        kwargs["output_ext"] = None
        kwargs.setdefault("audio_format", "bestaudio")

        if bitrate:
            ytdl_params: dict = kwargs.get("ytdl_params", {})
            postprocessors: list[dict] = ytdl_params.get("postprocessors", [])
            postprocessors.append(
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": bitrate[:-1],
                }
            )
            ytdl_params["postprocessors"] = postprocessors
            kwargs["ytdl_params"] = ytdl_params

        processed_info = self.ydl_run(extracted_info, **kwargs)

        return processed_info

    def ydl_run_video(
        self,
        extracted_info: ExtractedInfo,
        video_format: t.Union[videoQualitiesType, str] = "bestvideo",
        output_ext: t.Literal["mkv", "webm", "mp4"] = "mp4",
        **kwargs,
    ) -> dict:
        """
        Download **videos** shortcut for `ydl_run`,

        Args:
            extracted_info (ExtractedInfo): The extracted information about the video.
            video_format (Union[videoQualitiesType, str], optional): The desired video format or quality. Defaults to "bestvideo".
            output_ext (Literal["mkv", "webm", "mp4"], optional): The desired output file extension. Defaults to "mp4".
            **kwargs: Additional keyword arguments for `ydl_run`

        Returns:
            dict: A dictionary containing the results of the video download and processing.
        """
        kwargs.setdefault("output_ext", output_ext)
        return self.ydl_run(
            extracted_info=extracted_info, video_format=video_format, **kwargs
        )

    def ydl_run_ids(
        self, extracted_info: ExtractedInfo, format_ids: t.Iterable, **kwargs
    ) -> dict:
        """Download shortcut for `ydl_run` using format_ids only

        Args:
            extracted_info (ExtractedInfo): The extracted information about the video.
            format_ids (t.Iterable): Formats ids e.g (139, 340) or (139)
            **kwargs: Additional keyword arguments for `ydl_run`

        Returns:
            dict: A dictionary containing the results of the video download and processing.
        """
        assert_instance
        format = f"{'+'.join(map(lambda id: str(id), format_ids))}"
        return self.ydl_run(
            extracted_info=extracted_info,
            video_format=None,
            audio_format=None,
            default_format=format,
            **kwargs,
        )


Download = Downloader
# for short-term cross-compatibility
