"""
Configure .mp4 file metadata.

This module provides basic functionality
to add metadata to .mp4 files using ffmpeg.

Author: Jens Lordén
Date: 2026-01-17
"""

import glob
import subprocess
from dataclasses import dataclass
from pathlib import Path

import tyro


@dataclass
class MediaConfig:
    """
    Config for the .mp4 file(s) used to generate cli interface.

    Attributes:
        dir (str): Directory with target .mp4 files.
        filename (str): Name of the .mp4 file
        title (str): Title of the song.
    """

    dir: str
    img: str = ""
    artist: str = ""
    genre: str = ""
    track: str = ""
    album: str = ""
    title: str = ""
    filename: str = "*.mp3"
    askTitle: bool = False
    replaceWhitespace: bool = False
    cleanupFiles: bool = False


def getFilePaths(dir: str, filename: str, img: str) -> (list[str], str):
    """Find all .mp4 files in dir."""
    path = Path(dir)
    if "*" in filename:
        files = list(path.glob(filename))
    else:
        files = [path / filename]
    assert files or len(files) > 0
    imageFile = list(path.glob(img))[0] if img else None
    return files, imageFile


def getRmCommand(file: Path) -> list[str]:
    """
    Generate rm command to cleanup files.

    Attributes:
        file: File to remove
    """
    command = ["rm", file._str]
    return command


def getMvCommand(originalFilename: str, newFilename: str) -> list[str]:
    """

    Attributes:
        originalFilename: Name of file to rename
        newFilename: Name of new file
    """
    command = ["mv", originalFilename, newFilename]
    return command


def getFfmpegCommand(
    file: Path, config: tyro.cli, imageFile: Path, outputFilename: str
):
    """
    Generate ffmpeg command based on config.

    Attributes:
        file: File to add metadata to.
        config: Config object with metadata.
        outputFilename: Name of newly created copy.
    """
    title = config.title
    if config.askTitle:
        title = input("Please provide a title for the song: ")

    command = ["ffmpeg", "-i", file._str]
    if imageFile:
        command.extend(["-i", imageFile._str, "-map", "0:0", "-map", "1:0"])

    metadataMap = {
        "title": title,
        "artist": config.artist,
        "genre": config.genre,
        "track": config.track,
        "album": config.album,
    }
    for key, value in metadataMap.items():
        if value:
            command.extend(["-metadata", f"{key}={value}"])

    command.extend(["-id3v2_version", "3"])
    command.extend(["-c", "copy", outputFilename])
    return command


def trimStr(filename: str) -> str:
    """
    Trim a filename to remove whitespaces and chars.

    Attributes:
        filename: Filename to trim.
    """
    return filename.replace(" ", "_").replace("'", "")


def getOutputFilename(config: tyro.cli, file) -> str:
    """
    Get a filename for the outputed copy .mp3 file.

    Attributes:
        config: Config object with met.adata
        file: File to add metadata to.
    """
    if config.replaceWhitespace:
        path = file.as_posix()
        outputFilename = trimStr(f"{path[: path.rindex('/')]}/copy_{file.name}")
    else:
        outputFilename = f"copy_{file.name}"
    return outputFilename


def cleanupFiles(file: Path, copyFilename: str, trimFilename: bool = False):
    """Delete original file and rename the copy to the original name."""
    command = getRmCommand(file)
    subprocess.run(command)
    command = getMvCommand(
        copyFilename, file._str if not trimFilename else trimStr(file._str)
    )
    subprocess.run(command)
    print("Finished cleaning up files")


def addMetadata(config: tyro.cli, files: list[str], imageFile: Path):
    """Add metadata to files using ffmpeg"""
    outputFiles = []
    for file in files:
        outputFilename = getOutputFilename(config, file)
        outputFiles.append(outputFilename)

        print(f"Adding metadata to file: {file.name}")
        command = getFfmpegCommand(file, config, imageFile, outputFilename)
        subprocess.run(command)
        if not config.cleanupFiles:
            continue

        cleanupFiles(file, outputFilename, config.replaceWhitespace)


def main(config):
    """Main function."""
    files, imageFile = getFilePaths(config.dir, config.filename, config.img)
    addMetadata(config, files, imageFile)


if __name__ == "__main__":
    config = tyro.cli(MediaConfig)
    print(config)
    assert config.dir != ""
    assert (
        config.img != ""
        or config.artist != ""
        or config.genre != ""
        or config.track != ""
        or config.album != ""
        or config.title != ""
    )
    assert config.title != "" or config.askTitle
    main(config)
