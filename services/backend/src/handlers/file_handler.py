
import os
import uuid
import shutil
import math
from typing import BinaryIO
from multipart import parse_form
from python_multipart.exceptions import FormParserError
from PIL import Image, UnidentifiedImageError
from typing import Union
from http.client import HTTPMessage

from exceptions.api_errors import APIError, MaxSizeExceedError, MultipleFilesUploadError, NotSupportedFormatError
from exceptions.repository_errors import EntityNotFoundError, RepositoryError
from db.dto import ImageDTO
from db.dependencies import get_image_repository
from settings.config import config
from settings.logging_config import get_logger

logger = get_logger(__name__)


class FileHandler:
    def __init__(self):
        self.file: BinaryIO = None
        self.filename: str = None
        self.original_name: str = None
        self.ext: str = None
        self.unique_name: str = None
        self.unique_name_ext: str = None
        self.size: int = None


    def define_size_file(self, file):
        file.file_object.seek(0, os.SEEK_END)
        self.size = file.file_object.tell()
        file.file_object.seek(0)


    def _valided_file_size(self, file) -> bool:
        self.define_size_file(file)

        if self.size > config.MAX_FILE_SIZE:
            raise MaxSizeExceedError(config.MAX_FILE_SIZE)

        return True


    def _valided_file_format(self, filename) -> bool:
        self.ext = os.path.splitext(filename)[1].lower()

        if self.ext not in config.SUPPORTED_FORMATS:
            raise NotSupportedFormatError(config.SUPPORTED_FORMATS)

        return True


    def _valided_file_content(self, file) -> bool:
        try:
            image = Image.open(file.file_object)
            image.verify()
            file.file_object.seek(0)
        except (UnidentifiedImageError, OSError):
            raise NotSupportedFormatError(config.SUPPORTED_FORMATS)

        return True


    def file_is_valid(self, file, filename) -> bool:
        if not self._valided_file_size(file):
            return False
        if not self._valided_file_format(filename):
            return False
        if not self._valided_file_content(file):
            return False
        return True


    def create_unique_filename(self, filename):
        self.original_name, self.ext = os.path.splitext(filename.lower())
        self.unique_name = f"{self.original_name}_{uuid.uuid4()}"
        self.unique_name_ext = f"{self.unique_name}{self.ext}"


    def parse_formdata(self, headers: Union[dict[str, str], HTTPMessage], rfile: BinaryIO):
        """Parses and validates multipart form data, extracts uploaded file."""

        # Convert headers if they are HTTPMessage (as in self.headers)
        if not isinstance(headers, dict):
            headers = {k: v for k, v in headers.items()}

        content_type = headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            raise APIError("Bad Request: Expected multipart/form-data")

        content_length = int(headers.get("Content-Length", 0))

        prepared_headers = {
            "Content-Type": content_type,
            "Content-Length": str(content_length)
        }

        files = []

        def on_file(file):
            if len(files) >= 1:
                raise MultipleFilesUploadError()
            files.append(file)

        try:
            parse_form(prepared_headers, rfile, lambda _: None, on_file)
        except FormParserError as e:
            raise e

        if not files:
            raise APIError("No file was uploaded.")

        self.file = files[0]
        filename = self.file.file_name.decode("utf-8") if self.file.file_name else "uploaded_file"
        self.filename = filename if len(filename)<100 else filename[:100]


    def save_file(self, file):
        if not self.file_is_valid(file, self.filename):
            raise APIError("File validation failed")

        self.create_unique_filename(self.filename)

        # write to DB
        image_dto = ImageDTO(
            filename=self.unique_name,
            original_name=self.original_name,
            size=self.size,
            file_type=self.ext
        )

        repository = get_image_repository()

        repository.create(image_dto)

        # save file
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(config.UPLOAD_DIR, self.unique_name_ext)

        try:
            with open(file_path, "wb") as f:
                file.file_object.seek(0)
                shutil.copyfileobj(file.file_object, f)
                logger.info(f"File '{self.filename}' uploaded successfully.")
        except Exception as e:
            logger.error(f"File '{self.filename}' is not saved." + str(e))
            repository.delete_by_filename(self.filename)
            raise APIError(f"Failed to save file: {e}")


    def delete_file(self, filename: str):

        self.unique_name = os.path.splitext(filename)[0].lower()

        if not self._valided_file_format(filename):
            raise APIError

        # Delete from DB
        repository = get_image_repository()

        try:
            is_deleted = repository.delete_by_filename(self.unique_name)
            if not is_deleted:
                logger.warning(f"File '{self.unique_name}' was not found in database while deleting")
                raise EntityNotFoundError("Image", self.unique_name)
        except Exception as e:
            logger.error(f"File '{filename}' is not deleted." + str(e))
            raise RepositoryError

        # delete file
        filepath = os.path.join(config.UPLOAD_DIR, filename)

        try:
            os.remove(filepath)
        except PermissionError:
            logger.error("Permission denied to delete file.")
            return
        except Exception as e:
            logger.error(f"Internal Server Error: {str(e)}")
            return


    def get_list_images(self, limit: int = 8, offset: int = 0, sort_param: str = 'upload_time', sort_value: str = 'desc') -> dict:

        repository = get_image_repository()

        images_dto = repository.get_list_paginated_sorted(limit, offset, sort_param, sort_value)

        total_images = repository.count_all()
        per_page = limit
        total_pages = math.ceil(total_images / per_page)

        images_filenames = []
        for image in images_dto:
            images_filenames.append(image.filename + image.file_type)

        return {
          "files": images_filenames,
          "total_pages": total_pages
        }





