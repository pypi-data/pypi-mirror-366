"""xltekhdf5.py
A HDF5 file which contains data for XLTEK EEG data.
"""
# Package Header #
from ..header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
import pathlib
from typing import Any
from typing import Union

# Third-Party Packages #
from baseobjects.functions import singlekwargdispatch
from classversioning import VersionType, Version, TriNumberVersion
import h5py
from hdf5objects.dataset import ElectricalSeriesMap, TimeAxisMap, LabelAxisMap, CoordinateAxisMap
from hdf5objects.fileobjects import HDF5EEGMap, HDF5EEG
from hdf5objects.hdf5bases import HDF5File, HDF5Map

# Local Packages #


# Definitions #
# Classes #
class XLTEKHDF5Map(HDF5EEGMap):
    """A map for XLTEKHDF5 files."""
    _compression_kwargs = {"compression": "gzip", "compression_opts": 9}
    default_attribute_names = HDF5EEGMap.default_attribute_names | {
        "start_id": "start_id",
        "end_id": "end_id",
    }
    default_attributes = HDF5EEGMap.default_attributes | {"age": "", "sex": "U", "species": "Homo Sapien"}
    default_map_names = {"data": "ECoG"}
    default_maps = {
        "data": ElectricalSeriesMap(
            attributes={"units": "microvolts"},
            axis_maps=[
                {"time_axis": TimeAxisMap(object_kwargs=_compression_kwargs.copy())},
                {"channellabel_axis": LabelAxisMap(object_kwargs=_compression_kwargs.copy()),
                 "channelcoord_axis": CoordinateAxisMap(object_kwargs=_compression_kwargs.copy()),
                 },
            ],
            object_kwargs={"shape": (0, 0), "maxshape": (None, None)} | _compression_kwargs,
        ),
    }


class XLTEKHDF5(HDF5EEG):
    """A HDF5 file which contains data for XLTEK EEG data.

    Class Attributes:
        _registration: Determines if this class will be included in class registry.
        _VERSION_TYPE: The type of versioning to use.
        FILE_TYPE: The file type name of this class.
        VERSION: The version of this class.
        default_map: The HDF5 map of this object.
    """

    _registration: bool = True
    _VERSION_TYPE: VersionType = VersionType(name="XLTEKHDF5", class_=TriNumberVersion)
    VERSION: Version = TriNumberVersion(0, 0, 0)
    FILE_TYPE: str = "XLTEK_EEG"
    default_map: HDF5Map = XLTEKHDF5Map()

    # File Validation
    @classmethod
    @singlekwargdispatch("file")
    def validate_file_type(cls, file: pathlib.Path | str | HDF5File | h5py.File) -> bool:
        """Checks if the given file or path is a valid type.

        Args:
            file: The path or file object.

        Returns:
            If this is a valid file type.
        """
        raise TypeError(f"{type(file)} is not a valid type for validate_file_type.")

    @classmethod
    @validate_file_type.__wrapped__.register
    def _validate_file_type(cls, file: pathlib.Path) -> bool:
        """Checks if the given path is a valid type.

        Args:
            file: The path.

        Returns:
            If this is a valid file type.
        """
        t_name = cls.default_map.attribute_names["file_type"]

        if file.is_file():
            try:
                with h5py.File(file) as obj:
                    if t_name in obj.attrs:
                        return cls.FILE_TYPE == obj.attrs[t_name]
                    else:
                        return cls.get_version_class(TriNumberVersion(0, 1, 0)).validate_file_type(obj)
            except OSError:
                return False
        else:
            return False

    @classmethod
    @validate_file_type.__wrapped__.register
    def _validate_file_type(cls, file: str) -> bool:
        """Checks if the given path is a valid type.

        Args:
            file: The path.

        Returns:
            If this is a valid file type.
        """
        t_name = cls.default_map.attribute_names.get["file_type"]

        file = pathlib.Path(file)

        if file.is_file():
            try:
                with h5py.File(file) as obj:
                    if t_name in obj.attrs:
                        return cls.FILE_TYPE == obj.attrs[t_name]
                    else:
                        return cls.get_version_class(TriNumberVersion(0, 1, 0)).validate_file_type(obj)
            except OSError:
                return False
        else:
            return False

    @classmethod
    @validate_file_type.__wrapped__.register
    def _validate_file_type(cls, file: HDF5File) -> bool:
        """Checks if the given file is a valid type.

        Args:
            file: The file object.

        Returns:
            If this is a valid file type.
        """
        t_name = cls.default_map.attribute_names["file_type"]
        file = file._file
        if t_name in file.attrs:
            return cls.FILE_TYPE == file.attrs[t_name]
        else:
            return cls.get_version_class(TriNumberVersion(0, 1, 0)).validate_file_type(file)

    @classmethod
    @validate_file_type.__wrapped__.register
    def _validate_file_type(cls, file: h5py.File) -> bool:
        """Checks if the given file is a valid type.

        Args:
            file: The file fileect.

        Returns:
            If this is a valid file type.
        """
        t_name = cls.default_map.attribute_names["file_type"]
        if t_name in file.attrs:
            return cls.FILE_TYPE == file.attrs[t_name]
        else:
            return cls.get_version_class(TriNumberVersion(0, 1, 0)).validate_file_type(file)

    @classmethod
    @singlekwargdispatch("file")
    def new_validated(cls, file: pathlib.Path | str | HDF5File | h5py.File, **kwargs: Any) -> Union["XLTEKHDF5", None]:
        """Checks if the given file or path is a valid type and returns the file if valid.

        Args:
            file: The path or file object.

        Returns:
            The file or None.
        """
        raise TypeError(f"{type(file)} is not a valid type for new_validate.")

    @classmethod
    @new_validated.__wrapped__.register
    def _new_validated(cls, file: pathlib.Path, **kwargs: Any) -> Any:
        """Checks if the given path is a valid type and returns the file if valid.

        Args:
            file: The path.

        Returns:
            The file or None.
        """
        t_name = cls.default_map.attribute_names["file_type"]

        if file.is_file():
            try:
                file = h5py.File(file)
                if t_name in file.attrs and cls.FILE_TYPE == file.attrs[t_name]:
                    return cls(file=file, **kwargs)
                else:
                    return cls.get_version_class(TriNumberVersion(0, 1, 0)).new_validated(file)
            except OSError:
                return None
        else:
            return None

    @classmethod
    @new_validated.__wrapped__.register
    def _new_validated(cls, file: str, **kwargs: Any) -> Any:
        """Checks if the given path is a valid type and returns the file if valid.

        Args:
            file: The path.

        Returns:
            The file or None.
        """
        t_name = cls.default_map.attribute_names["file_type"]
        file = pathlib.Path(file)

        if file.is_file():
            try:
                file = h5py.File(file)
                if t_name in file.attrs and cls.FILE_TYPE == file.attrs[t_name]:
                    return cls(file=file, **kwargs)
                else:
                    return cls.get_version_class(TriNumberVersion(0, 1, 0)).new_validated(file)
            except OSError:
                return None
        else:
            return None

    @classmethod
    @new_validated.__wrapped__.register
    def _new_validated(cls, file: HDF5File, **kwargs: Any) -> Any:
        """Checks if the given file is a valid type and returns the file if valid.

        Args:
            file: The file.

        Returns:
            The file or None.
        """
        t_name = cls.default_map.attribute_names["file_type"]
        file = file._file
        if t_name in file.attrs and cls.FILE_TYPE == file.attrs[t_name]:
            return cls(file=file, **kwargs)
        else:
            return cls.get_version_class(TriNumberVersion(0, 1, 0)).new_validated(file)

    @classmethod
    @new_validated.__wrapped__.register
    def _new_validated(cls, file: h5py.File, **kwargs: Any) -> Any:
        """Checks if the given file is a valid type and returns the file if valid.

        Args:
            file: The file.

        Returns:
            The file or None.
        """
        t_name = cls.default_map.attribute_names["file_type"]
        if t_name in file.attrs and cls.FILE_TYPE == file.attrs[t_name]:
            return cls(file=file, **kwargs)
        else:
            return cls.get_version_class(TriNumberVersion(0, 1, 0)).new_validated(file)

    @classmethod
    def get_version_from_file(cls, file: pathlib.Path | str | h5py.File) -> tuple[Version, h5py.File]:
        """Return a version from a file.

        Args:
            file: The path to file to get the version from.

        Returns:
            The version from the file.
        """
        v_name = cls.default_map.attribute_names["file_version"]

        if isinstance(file, pathlib.Path):
            file = file.as_posix()

        if isinstance(file, str):
            file = h5py.File(file)

        if v_name in file.attrs:
            return TriNumberVersion(file.attrs[v_name]), file
        elif cls.get_version_class(TriNumberVersion(0, 1, 0)).validate_file_type(file):
            return TriNumberVersion(0, 1, 0), file
