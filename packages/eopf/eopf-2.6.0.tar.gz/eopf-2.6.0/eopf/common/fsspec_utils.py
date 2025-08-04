#
# Copyright (C) 2025 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import re

import fsspec


def fs_match_path(pattern: str, filesystem: fsspec.FSMap) -> str:
    """Find and return the first occurrence of a path matching
    a given pattern.

    If there is no match, pattern is return as it is.

    Parameters
    ----------
    pattern: str
        regex pattern to match
    filesystem    filesystem representation

    Returns
    -------
    str
        matching path if find, else `pattern`
    """
    filepath_regex = re.compile(pattern)
    for file_path in filesystem:
        if filepath_regex.fullmatch(file_path):
            return file_path
    return pattern
