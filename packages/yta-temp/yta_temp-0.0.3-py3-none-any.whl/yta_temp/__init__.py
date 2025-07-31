from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from yta_file import FileHandler
from yta_file.filename import FilenameHandler
from yta_file.filename.dataclasses import Filename
from yta_programming.env import Environment
from yta_programming.path import DevPathHandler
from yta_programming.decorators import singleton_old
from yta_constants.file import FileEncoding, FileOpenMode
from yta_random import Random
from datetime import datetime
from typing import Union

import os
import tempfile


class Temp:
    """
    Class to simplify the way we work with temporary files.
    """

    # TODO: I don't like the way we handle this variable
    # so please, refactor and improve it :). I would like
    # it to be a class/static property to use .WIP_FOLDER
    @staticmethod
    def WIP_FOLDER(
    ) -> str:
        """
        The Work In Progress folder in which we store all
        the temporary files we are working with. Its value
        is loaded from the '.env' 'WIP_FOLDER' variable.
        """
        WIP_FOLDER = Environment.get_current_project_env('WIP_FOLDER')

        if not WIP_FOLDER:
            # We force creating the dir
            WIP_FOLDER = f'{DevPathHandler.get_project_abspath()}yta_wip/'

            if not FileHandler.file_exists(WIP_FOLDER):
                FileHandler.create_folder(WIP_FOLDER)

        return WIP_FOLDER

    @staticmethod
    def get_filename(
        filename: str
    ) -> str:
        """
        Get a temporary file name using the given 'filename'
        and including a random suffix related to the current
        datetime. This is just a filename that doesn't 
        include the temporary folder or any prefix.

        This method uses the current datetime and a random 
        integer to be always unique.

        If you provide 'file.wav' it will return something
        similar to 'file_202406212425.wav', but if you don't
        provide any extension, it will have no extension and
        would be like 'file_202406212425'.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = True)

        filename: Filename = FilenameHandler.parse(filename)

        # if not filename.has_extension:
        #     import warnings
        #     warnings.warn('The given "filename" has no extension. Creating a temporary name without extension.')

        time_moment = int((datetime.now() - datetime(1970, 1, 1)).total_seconds())

        aux = f'{filename.file_name}_{str(time_moment)}{str(Random.int_between(0, 10_000))}'

        return (
            f'{aux}.{filename.extension}'
            if filename.has_extension else
            f'{aux}'
        )
    
    @staticmethod
    def get_wip_filename(
        filename: str
    ) -> str:
        """
        Get a temporary file name using the given 'filename'
        and including a random suffix related to the current
        datetime. This is a filename that includes the 
        temporary folder as a prefix so it can be used in
        the app.

        This method uses the current datetime and a random 
        integer to be always unique.

        If you provide 'file.wav' it will return something
        similtar to '$WIP_FOLDER/file_202406212425.wav'.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = True)

        # TODO: Rename this as it uses wip and we do not mention it
        # TODO: Issue if no extension provided
        return Temp.get_custom_wip_filename(Temp.get_filename(filename))
    
    @staticmethod
    def get_custom_wip_filename(
        filename: str
    ) -> str:
        """
        Get a file name that includes the 'WIP_FOLDER' as
        a prefix but preserves the provided 'filename'. 
        This is useful when we need a temporary file to
        work with but with a specific name, maybe not for
        a long time but able to access it from different
        points of the app because of its known (and not
        random) name.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = True)
        
        return f'{Temp.WIP_FOLDER()}{filename}'

    @staticmethod
    def initialize(
    ) -> None:
        """
        Create the folder if necessary.
        """
        Temp.WIP_FOLDER()

    @staticmethod
    def clean_folder(
        do_remove_folder: bool = True
    ) -> None:
        """
        Remove all the existing files in the temporary 
        folder.
        """
        ParameterValidator.validate_mandatory_bool('do_remove_folder', do_remove_folder)

        FileHandler.delete_files(Temp.WIP_FOLDER())

        if do_remove_folder:
            FileHandler.delete_folder(Temp.WIP_FOLDER())

    # TODO: This code below is very recent and has to be checked
    # and improved
    @staticmethod
    def is_temporary_writing_enabled(
    ) -> bool:
        """
        Check if we have access to writing temporary files
        in the system (the official way).

        TODO: This code is very recent and can make this
        library change.
        """
        return os.access(tempfile.gettempdir(), os.W_OK)

@singleton_old
class BaseTemp:
    """
    Singleton class.

    Class to handle files with the basic 'tempfile' python
    library.

    This class will raise an Exception when instantiated if
    the writing temporary files permissions are not enabled.
    """

    temp_folder_abspath = FilenameHandler.sanitize(tempfile.gettempdir())
    """
    Get the temporary files folder name sanitized (that
    means that the back slashes have been replaced with
    normal slashes) but ending not in '/'.
    """
    

    def __init__(
        self
    ) -> None:
        self._validate_writing_permissions()
        self._filenames_to_delete = []
        """
        The temporary files that are created in execution time
        and must be removed before deleting the instance. These
        are the ones created with the 'do_delete' flag set as
        False.
        """

    def __del__(
        self
    ) -> None:
        self._delete_temporary_files()

    @property
    def log_filename(
        self
    ) -> str:
        """
        The filename of a register in which there are
        all the files that have been written as
        temporary files.
        """
        self._log_filename = (
            f'{self.temp_folder_abspath}/yta_temp_register.log'
            if not hasattr(self, '_log_filename') else
            self._log_filename
        )

        return self._log_filename

    @property
    def _is_temporary_writing_enabled(
        self
    ) -> bool:
        """
        Check if the option to write temporary files is
        enabled or not.
        """
        return os.access(tempfile.gettempdir(), os.W_OK)
    
    @property
    def _filenames_in_log(
        self
    ) -> list[str]:
        """
        Get a list with all the filenames that are written
        in the log file. Those file names are the files 
        that have been written previously with the
        'do_delete' flag set as False.
        """
        return (
            []
            if not FileHandler.file_exists(self.log_filename) else
            [
                filename.replace('\n', '')
                for filename in FileHandler.read_str_lines(self.log_filename)
            ]
        )
    
    @property
    def _number_of_filenames_in_log(
        self
    ) -> int:
        """
        Get the number of filenames that are written in
        the log file. Those file names are the files 
        that have been written previously with the
        'do_delete' flag set as False.
        """
        return len(self._filenames_in_log)
    
    def _write_filename_in_log_file(
        self,
        filename: str
    ) -> str:
        """
        Write a file in the log file to be able to remove
        it in the future. This log will include only the
        files that have been created with the 'do_delete'
        flag as False.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        FileHandler.append_str(self.log_filename, f'{filename}\n', FileEncoding.UTF8)

        return filename

    def _delete_temporary_files(
        self
    ) -> None:
        """
        Delete the files that have been created during the
        execution time with the 'do_delete' flag as True.
        """
        for filename in self._filenames_to_delete:
            # TODO: Indicate that this method does not raise
            # any exception, it only returns True or False
            FileHandler.delete_file(filename)

    # TODO: Maybe create 'get_filename' and
    # 'get_custom_filename' to use their system to obtain
    # the names and including the abspath (property)
    @classmethod
    def get_filename(
        cls,
    ) -> str:
        """
        Get a filename that has been created randomly by
        using the tempfile library. The filename returned
        includes only the file name and the dot and the
        extension if existing.
        """
        return cls._get_temp_filename(None)
    
    @classmethod
    def get_abspath(
        cls,
    ) -> str:
        """
        Get an absolute path which includes a filename
        that has been created randomly by using the
        tempfile library.
        """
        return f'{cls.temp_folder_abspath}/{cls.get_filename()}'
        
    @classmethod
    def get_custom_filename(
        cls,
        filename: str
    ) -> str:
        """
        Get a filename, using the given 'filename' parameter,
        which is located in the temporary folder. The filename
        returned includes only the file name and the dot and
        the extension if existing.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        return cls._get_temp_filename(filename)
    
    @classmethod
    def get_custom_abspath(
        cls,
        filename: str
    ) -> str:
        """
        Get an absolute path which includes a filename
        that has been created randomly by using the
        tempfile library and the given 'filename' 
        parameter.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        return f'{cls.temp_folder_abspath}/{cls.get_custom_filename(filename)}'
    
    @classmethod
    def _get_temp_filename(
        cls,
        filename: Union[str, None]
    ) -> str:
        """
        *For internal use only*

        Get a temporary filename using the 'filename'
        parameter as prefix if provided.
        """
        ParameterValidator.validate_string('filename', filename, do_accept_empty = True)

        filename = (
            None
            # TODO: Create a StringHandler that is able to sanitize
            # a string and know if it is empty (removing white 
            # spaces) and those things...
            if filename == '' else
            filename
        )

        with tempfile.NamedTemporaryFile(
            prefix = filename,
            delete = True
        ) as tmp_file:
            return FilenameHandler.parse(tmp_file.name).filename
        
    def delete_files_in_log(
        self
    ) -> None:
        """
        Delete the files that are stored in the log file
        and cleans that log file. This will clean up the
        local temporary folder and has to be done to
        avoid occupying a lot of space on the disk.
        """
        for filename in self._filenames_in_log:
            FileHandler.delete_file(filename)

        FileHandler.write_str(self.log_filename, '', FileEncoding.UTF8)
    
    def create_file(
        self,
        filename: Union[str, None] = None,
        extension: Union[str, 'FileExtension', None] = None,
        # TODO: What about the type of this content (?)
        content: Union[bytes, str, None] = None,
        do_delete: bool = True
    ) -> Filename:
        """
        Create a temporary file and return its name.

        The 'do_delete' flag indicates if they will live
        only during the life time of this instance or if
        they will remain stored in the system after the
        instance get cleaned up.
        """
        # TODO: Do I actually need the 'extension' (?) It 
        # can be included in the 'filename'...
        ParameterValidator.validate_string('filename', filename, do_accept_empty = True)
        # TODO: Is this 'content' validation ok?
        ParameterValidator.validate_instance_of('content', content, [bytes, str])
        ParameterValidator.validate_mandatory_bool('do_delete', do_delete)
        
        self._validate_writing_permissions()

        prefix = (
            None
            if filename in ['', None] else
            filename
        )

        # TODO: Parse suffix as FileExtension
        # TODO: We need to validate it with extension regex
        # Sufix must be '.{sufix}' to work as a Extension
        suffix = (
            None
            if extension in ['', None] else
            (
                f'.{extension}'
                if not extension.startswith('.') else
                extension
            )
        )

        mode = (
            FileOpenMode.READ_AND_WRITE_BINARY_CREATING
            if (
                content is None or
                PythonValidator.is_bytes(content)
            ) else
            FileOpenMode.READ_AND_WRITE_CREATING
        ).value

        # TODO: Why 'self.'? We don't need that
        self.temp_file = tempfile.NamedTemporaryFile(
            mode = mode,
            prefix = prefix,
            suffix = suffix,
            delete = do_delete
        )

        temp_filename = FilenameHandler.sanitize(self.temp_file.name)
        if not do_delete:
            self._write_filename_in_log_file(temp_filename)
        else:
            self._filenames_to_delete.append(temp_filename)

        if content is not None:
            # TODO: What if string instead of binary (?)
            self.temp_file.write(content)
            self.temp_file.flush()
            self.temp_file.seek(0)

        return FilenameHandler.parse(self.temp_file.name)
    
    def _validate_writing_permissions(
        self
    ) -> None:
        """
        Check if the writing temporary files permissions are
        enabled and raises an Exception if not.
        """
        if not self._is_temporary_writing_enabled:
            raise Exception('Sorry, the writing temporary files permissions are not enabled.')
    
            