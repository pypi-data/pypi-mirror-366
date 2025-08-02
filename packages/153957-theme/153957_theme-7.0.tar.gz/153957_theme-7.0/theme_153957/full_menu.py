"""Add full menu to gallery"""

import os

from typing import Any

from sigal import signals
from sigal.gallery import Album


def path_to_root(album: Album) -> None:
    """url path back to gallery root"""

    path_to_root = os.path.relpath('.', album.path)
    if path_to_root == '.':
        path_to_root = ''
    else:
        path_to_root += '/'

    album.path_to_root = path_to_root


def path_from_root(album: Album) -> None:
    """url from gallery root"""

    album.path_from_root = album.path


def register(settings: dict[str, Any]) -> None:
    signals.album_initialized.connect(path_to_root)
    signals.album_initialized.connect(path_from_root)
