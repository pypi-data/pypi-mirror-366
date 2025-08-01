import base64
from pathlib import Path
from typing import BinaryIO
from typing import ClassVar

from amsdal_models.classes.model import Model
from amsdal_utils.models.enums import ModuleType
from pydantic import field_validator
from pydantic.fields import Field


class File(Model):
    __module_type__: ClassVar[ModuleType] = ModuleType.CORE
    filename: str = Field(title='Filename')
    data: bytes = Field(title='Data')
    size: float | None = Field(None, title='Size')

    def __repr__(self) -> str:
        return f'File<{self.filename}>({self.size or len(self.data) or 0} bytes)'

    def __str__(self) -> str:
        return repr(self)

    async def apre_create(self) -> None:
        """
        Prepares the object for creation by setting its size attribute.

        This method calculates the size of the object's data and assigns it to the size attribute.
        If the data is None, it defaults to an empty byte string.

        Args:
            None
        """
        self.size = len(self.data or b'')

    async def apre_update(self) -> None:
        """
        Prepares the object for update by setting its size attribute.

        This method calculates the size of the object's data and assigns it to the size attribute.
        If the data is None, it defaults to an empty byte string.

        Args:
            None
        """
        self.size = len(self.data or b'')

    @field_validator('data')
    @classmethod
    def data_base64_decode(cls, v: bytes) -> bytes:
        """
        Decodes a base64-encoded byte string if it is base64-encoded.

        This method checks if the provided byte string is base64-encoded and decodes it if true.
        If the byte string is not base64-encoded, it returns the original byte string.

        Args:
            cls: The class this method belongs to.
            v (bytes): The byte string to be checked and potentially decoded.

        Returns:
            bytes: The decoded byte string if it was base64-encoded, otherwise the original byte string.
        """
        is_base64: bool = False
        try:
            is_base64 = base64.b64encode(base64.b64decode(v)) == v
        except Exception:
            ...
        if is_base64:
            return base64.b64decode(v)
        return v

    @classmethod
    def from_file(cls, file_or_path: Path | BinaryIO) -> 'File':
        """
        Creates a `File` object from a file path or a binary file object.

        Args:
            file_or_path (Path | BinaryIO): The file path or binary file object.

        Returns:
            File: The created `File` object.

        Raises:
            ValueError: If the provided path is a directory.
        """
        if isinstance(file_or_path, Path):
            if file_or_path.is_dir():
                msg = f'{file_or_path} is a directory'
                raise ValueError(msg)
            data = file_or_path.read_bytes()
            filename = file_or_path.name
        else:
            file_or_path.seek(0)
            data = file_or_path.read()
            filename = Path(file_or_path.name).name
        return cls(data=data, filename=filename)  # type: ignore[call-arg]

    @property
    def mimetype(self) -> str | None:
        """
        Returns the MIME type of the file based on its filename.

        This method uses the `mimetypes` module to guess the MIME type of the file.

        Returns:
            str | None: The guessed MIME type of the file, or None if it cannot be determined.
        """
        import mimetypes

        return mimetypes.guess_type(self.filename)[0]

    def pre_create(self) -> None:
        """
        Prepares the object for creation by setting its size attribute.

        This method calculates the size of the object's data and assigns it to the size attribute.
        If the data is None, it defaults to an empty byte string.

        Args:
            None
        """
        self.size = len(self.data or b'')

    def pre_update(self) -> None:
        """
        Prepares the object for update by setting its size attribute.

        This method calculates the size of the object's data and assigns it to the size attribute.
        If the data is None, it defaults to an empty byte string.

        Args:
            None
        """
        self.size = len(self.data or b'')

    def to_file(self, file_or_path: Path | BinaryIO) -> None:
        """
        Writes the object's data to a file path or a binary file object.

        Args:
            file_or_path (Path | BinaryIO): The file path or binary file object where the data will be written.

        Returns:
            None

        Raises:
            ValueError: If the provided path is a directory.
        """
        if isinstance(file_or_path, Path):
            if file_or_path.is_dir():
                file_or_path = file_or_path / self.name
            file_or_path.write_bytes(self.data)  # type: ignore[union-attr]
        else:
            file_or_path.write(self.data)
            file_or_path.seek(0)
