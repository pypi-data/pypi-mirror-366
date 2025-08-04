""" 
This module was created to manage files and directories
of system.

"""

import os
from typing import List, Optional
from drtools.utils import (
    get_os_name,
    join_path
)
import json
import gzip


def split_path(
    path: str
) -> List[str]:
    """Handle path split by of os.

    Parameters
    ----------
    path : str
        Path to be splited

    Returns
    -------
    List[str]
        List with pieces of path.
    """
    if get_os_name() == "Windows": return path.split("\\")
    elif get_os_name() == "Linux": return path.split("/")
    elif get_os_name() == "Darwin": return path.split("\\")


def move_file(
    current_path: str,
    destination_path: str,
) -> None:
    """Move file handling when file already exists.

    Parameters
    ----------
    current_path : str
        Current path location
    destination_path : str
        Destination path

    Raises
    ------
    Exception
        If current path does not exists
    Exception
        If destination path already exists
    """
    
    if not os.path.exists(current_path):
        raise Exception('Current path does not exists.')
    if os.path.exists(destination_path):
        raise Exception('Destination path already exists.')   
    
    create_directories_of_path(destination_path)
    os.rename(current_path, destination_path)


def get_files_path(
    parent_path: str, 
    content_arr: Optional[List[str]]=None,
    ignore_files: Optional[List[str]]=None,
    ignore_folders: Optional[List[str]]=None,
    ignore_if_contain_some_of_the_words: Optional[List[str]]=None,
) -> List:
    """Return array containing all abs path of files inside directory.

    Parameters
    ----------
    parent_path : str
        Directory to search files.
    content_arr : List[str], optional
        Array of content of parent path directory, by default []
    ignore_files : List[str], optional
        Ignore files if name equal some of this list, by default [] 
    ignore_folders : List[str], optional
        Ignore folders if name equal some of this list, by default []
    ignore_if_contain_some_of_the_words : List[str], optional
        Ignore folders and files if name cotain some of 
        the names presented on this list, by default []

    Returns
    -------
    List
        List of files path inside parent path directory.
    """
    
    if content_arr is None:
        content_arr = []

    if ignore_files is None:
        ignore_files = []

    if ignore_folders is None:
        ignore_folders = []

    if ignore_if_contain_some_of_the_words is None:
        ignore_if_contain_some_of_the_words = []    
    
    files_path_arr = []
    ignore_cuz_content_name_have_some_of_the_words = False
    for content_name in content_arr:
        
        content_path = f'{parent_path}/{content_name}'
        
        ignore_words_len = len(ignore_if_contain_some_of_the_words)
        for index1, word in enumerate(ignore_if_contain_some_of_the_words):
            if word in content_name:
                ignore_cuz_content_name_have_some_of_the_words = True
                break
            elif index1 == ignore_words_len - 1:
                ignore_cuz_content_name_have_some_of_the_words = False
                
        if os.path.isfile(content_path):
            if content_name not in ignore_files \
            and not ignore_cuz_content_name_have_some_of_the_words:
                files_path_arr.append(
                    join_path(parent_path, content_name)
                )
                
        elif content_name not in ignore_folders \
        and not ignore_cuz_content_name_have_some_of_the_words:
            next_parent_path = join_path(parent_path, content_name)
            next_content_arr = os.listdir(next_parent_path)
            files_path_arr = files_path_arr \
                + get_files_path(
                    next_parent_path, 
                    next_content_arr, 
                    ignore_files, 
                    ignore_folders, 
                    ignore_if_contain_some_of_the_words
                )
    return files_path_arr


def list_path_of_all_files_inside_directory(
    root_directory_path: str,
    ignore_files: Optional[List[str]]=None,
    ignore_folders: Optional[List[str]]=None,
    ignore_if_contain_some_of_the_words: Optional[List[str]]=None,
) -> List:
    """Return array containing all abs path inside some directory.

    Parameters
    ----------
    root_directory_path : str
        Directory abs path. Search for files inside this directory
    ignore_files : List[str], optional
        Ignore files if name equal some of this list, by default []
    ignore_folders : List[str], optional
        Ignore folders if name equal some of this list, by default []
    ignore_if_contain_some_of_the_words : List[str], optional
        Ignore folders and files if name cotain some of 
        the names presented on this list, by default []

    Returns
    -------
    List
        List of files path inside parent path directory.
    """
    if ignore_files is None:
        ignore_files = []
        
    if ignore_folders is None:
        ignore_folders = []
        
    if ignore_if_contain_some_of_the_words is None:
        ignore_if_contain_some_of_the_words = []
        
    
    try:
      dataDirectoryContent = os.listdir(root_directory_path)
    except:
      dataDirectoryContent = []
    itemsPath = []
    if len(dataDirectoryContent) > 0:
      itemsPath = get_files_path(
            parent_path=root_directory_path, 
            content_arr=dataDirectoryContent, 
            ignore_files=ignore_files, 
            ignore_folders=ignore_folders, 
            ignore_if_contain_some_of_the_words=ignore_if_contain_some_of_the_words
        )
    return itemsPath
    
    
def create_directories_of_path(
    path: str
) -> None:
    """Create all directories of path.

    Parameters
    ----------
    path : str
        Desired path.
        
    Returns
    -----
    None
        None is returned
    """
    
    split_path = None
    
    if get_os_name() == "Windows": 
        split_path = path.split("\\")
    elif get_os_name() == "Linux": 
        split_path = path.split("/")
    elif get_os_name() == "Darwin": 
        split_path = path.split("\\")
        
    temp_path = None
    
    for index, env_path in enumerate(split_path):
        if not env_path: 
            continue
        if len(env_path.split(".")) > 1 and index == len(split_path) - 1: 
            break
        if temp_path == None: 
            if get_os_name() == "Windows": 
                temp_path = env_path + '\\'
                continue
            elif get_os_name() == "Linux": 
                temp_path = "/"
        temp_path = join_path(temp_path, env_path)
        if not os.path.exists(temp_path): 
            try:
                os.makedirs(temp_path, exist_ok=True)
            except Exception as e:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(e).__name__, e.args)
                print("Error: " + str(e))
                print(message)


def save_json(
    data: any, 
    path: str,
    indent: int=4,
    sort_keys: bool=False,
    overwrite: bool=False
) -> None:
    """Save JSON file.

    Parameters
    ----------
    data : any
        Json data
    path : str
        Destination path of file that will be saved
    indent : int, optional
        Indentation of JSON, by default 4
    sort_keys : bool, optional
        If keys of JSON will be sorted, by default False
    
    Returns
    ------
    None
        None is returned
        
    Raises
    ------
    Exception
        If path already exists.
    """
    
    if os.path.exists(path) \
    and not overwrite:
        raise Exception('Path already exists.')
    
    create_directories_of_path(path)
    
    if path.endswith('.gz'):
        with gzip.open(path, 'wt', encoding="ascii") as zipfile:
            json.dump(data, zipfile)
    else:
        with open(path, 'w') as f:
            json.dump(data, f, indent=indent, sort_keys=sort_keys)
                
        
def load_json(
    path: str,
) -> any:
    """Load JSON file.

    Parameters
    ----------
    path : str
        Path of file that will be loaded.
    
    Returns
    ------
    None
        None is returned
        
    Raises
    ------
    Exception
        If path does not exists.
    """
    if not os.path.exists(path):
        raise Exception('Path does not exists.')
    methods_by_type_of_file = {
        '.gz': {'open': gzip.open,'apply_on_data': lambda data: data.decode('utf-8')},
        'others': {'open': open,'apply_on_data': lambda data: data},
    }
    extension_path = '.' + path.split('.')[-1]
    methods = methods_by_type_of_file.get(
        extension_path, methods_by_type_of_file['others']
    )
    open_method = methods['open']
    apply_on_data_method = methods['apply_on_data']
    try:
        with open_method(path, "r") as f:
            data = f.read()
            data = json.loads(
                apply_on_data_method(data)
            )
    except json.JSONDecodeError as exc:
        data = []
        for line in open_method(path, 'r'):
            try:
                row = json.loads(line)
                data.append(row)
            except Exception as exc:
                pass
    return data
    
    
def rm_file(
    path: str, 
    ignore_if_path_not_exists: bool=False
) -> None: 
    """Delete file

    Parameters
    ----------
    path : str
        Abs path of file
    ignore_if_path_not_exists : bool, optional
        If True, if path not exists, do not raise Exception, 
        if False, if path not exists, raise Exception, 
        by default False
    """
    if ignore_if_path_not_exists:
      if os.path.exists(path):
        os.remove(path)
    else:
      os.remove(path)