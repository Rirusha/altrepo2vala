# Copyright (C) 2024 Vladimir Vaskov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime

from structures import HEADER
import global_args

def remove_end(target:str, end:str) -> str:
    if target.endswith(end):
        return target[:len(target) - len(end)]
    return target

def pascal_to_kebeb(camel_string:str) -> str:
    builder = []
    for (i, char) in enumerate(camel_string):
        if char.isupper() and i != 0:
            builder.append("-")

        builder.append(char.lower())

    return ''.join(builder)

def fix_type(_type:str) -> str:
    return(remove_end(_type, 'Model'))

def format_description(description:str) -> str:
    return f'    /**\n     * {description}\n     */\n'

def resolve_ref (ref:str) -> str:
    return fix_type(ref.lstrip('#/definitions/').replace('/', '.'))

def format_header () -> str:
    return HEADER.format(year=str(datetime.now().year), author=global_args.author)
