"""Artifact file handling for Hypha."""

import io
import locale
import os
from typing import Self
from types import TracebackType
import httpx
from .utils import FileMode


class ArtifactHttpFile(io.IOBase):
    """A file-like object that supports both sync and async context manager protocols.

    This implements a file interface for Hypha artifacts, handling HTTP operations
    via the httpx library instead of relying on Pyodide.
    """

    name: str | None
    mode: str

    def __init__(
        self: Self,
        url: str,
        mode: FileMode = "r",
        encoding: str | None = None,
        newline: str | None = None,
        name: str | None = None,
    ) -> None:
        self._url = url
        self._pos = 0
        self._mode = mode
        self._encoding = encoding or locale.getpreferredencoding()
        self._newline = newline or os.linesep
        self.name = name
        self._closed = False
        self._buffer = io.BytesIO()

        if "r" in mode:
            # For read mode, download the content immediately
            self._download_content()
            self._size = len(self._buffer.getvalue())
        else:
            # For write modes, initialize an empty buffer
            self._size = 0

    def _download_content(self: Self, range_header: str | None = None) -> None:
        """Download content from URL into buffer, optionally using a range header."""
        try:
            headers: dict[str, str | None] = {
                "Accept-Encoding": "identity"  # Prevent gzip compression
            }
            if range_header:
                headers["Range"] = range_header

            with httpx.Client(timeout=10.0) as client:
                response = client.get(self._url, headers=headers)
                response.raise_for_status()
                self._buffer = io.BytesIO(response.content)
        except httpx.HTTPStatusError as e:
            # More detailed error information for debugging
            status_code = e.response.status_code
            message = str(e)
            raise IOError(
                f"Error downloading content (status {status_code}): {message}"
            ) from e
        except httpx.RequestError as e:
            raise IOError(f"Request error downloading content: {str(e)}") from e
        except Exception as e:
            raise IOError(f"Unexpected error downloading content: {str(e)}") from e

    def _upload_content(self: Self) -> httpx.Response:
        """Upload buffer content to URL"""
        try:
            content = self._buffer.getvalue()

            headers = {
                "Content-Type": "",
                "Content-Length": str(len(content)),
            }

            with httpx.Client(timeout=3.0) as client:
                response = client.put(self._url, content=content, headers=headers)
                response.raise_for_status()
                return response
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            error_msg = e.response.text
            raise IOError(
                f"HTTP error uploading content (status {status_code}): {error_msg}"
            ) from e
        except httpx.RequestError as e:
            raise IOError(f"Request error uploading content: {str(e)}") from e
        except Exception as e:
            raise IOError(f"Error uploading content: {str(e)}") from e

    def tell(self: Self) -> int:
        """Return current position in the file"""
        return self._pos

    def seek(self: Self, offset: int, whence: int = 0) -> int:
        """Change stream position"""
        if whence == 0:  # os.SEEK_SET
            self._pos = offset
        elif whence == 1:  # os.SEEK_CUR
            self._pos += offset
        elif whence == 2:  # os.SEEK_END
            self._pos = self._size + offset

        # Make sure buffer's position is synced
        self._buffer.seek(self._pos)
        return self._pos

    def read(self: Self, size: int = -1) -> bytes | str:
        """Read up to size bytes from the file, using HTTP range if necessary."""
        if "r" not in self._mode:
            raise IOError("File not open for reading")

        if size < 0:
            self._download_content()
        else:
            range_header = f"bytes={self._pos}-{self._pos + size - 1}"
            self._download_content(range_header=range_header)

        data = self._buffer.read()
        self._pos += len(data)

        if "b" not in self._mode:
            return data.decode(self._encoding)
        return data

    def write(self: Self, data: str | bytes) -> int:
        """Write data to the file"""
        if "w" not in self._mode and "a" not in self._mode:
            raise IOError("File not open for writing")

        # Convert string to bytes if necessary
        if isinstance(data, str) and "b" in self._mode:
            data = data.encode(self._encoding)
        elif isinstance(data, bytes) and "b" not in self._mode:
            data = data.decode(self._encoding)
            data = data.encode(self._encoding)

        # Ensure we're at the right position
        self._buffer.seek(self._pos)

        # Write the data
        if isinstance(data, str):
            bytes_written = self._buffer.write(data.encode(self._encoding))
        else:
            bytes_written = self._buffer.write(data)

        self._pos = self._buffer.tell()
        if self._pos > self._size:
            self._size = self._pos

        return bytes_written

    def readable(self: Self) -> bool:
        """Return whether the file is readable"""
        return "r" in self._mode

    def writable(self: Self) -> bool:
        """Return whether the file is writable"""
        return "w" in self._mode or "a" in self._mode

    def seekable(self: Self) -> bool:
        """Return whether the file is seekable"""
        return True

    def close(self: Self) -> None:
        """Close the file and upload content if in write mode"""
        if self._closed:
            return

        try:
            if ("w" in self._mode or "a" in self._mode) and self._buffer.tell() > 0:
                self._upload_content()
        finally:
            self._closed = True
            self._buffer.close()

    @property
    def closed(self: Self) -> bool:
        """Return whether the file is closed"""
        return self._closed

    def __enter__(self: Self) -> Self:
        """Enter context manager"""
        return self

    def __exit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit context manager"""
        self.close()

    def __aenter__(self: Self) -> Self:
        """Enter async context manager"""
        return self

    def __aexit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context manager"""
        self.close()
