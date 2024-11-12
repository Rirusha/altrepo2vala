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

HEADER = """/*
 * Copyright (C) {year} {author}
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

// THIS CODE WAS GENERATED, DON'T MODIFY IT"""
 
PROPERTY = '    public {0} {1} {{ get; set; {2}}}\n'

CLASS_DEFINITION = 'public class {0}.{1} : {2}'

CLIENT_CLASS = 'public sealed class {namespace}.Client : Object'

METHOD = '    public {return_type} {name} (\n        {argvn}\n    ) throws CommonError, BadStatusCodeError {{\n        {body}\n    }}'

API_BASE = '    internal const string API_BASE = "{api_base}";\n\n'

SOUP_WRAPPER = '    SoupWrapper soup_wrapper { get; default = new SoupWrapper (); }\n\n'

CONSTRUCT = '    construct {\n\n    }\n'

ARG = '{arg_type} {name}{default}'

DEPRICATED = '    [Version (deprecated = true, deprecated_since = "{version}")]'
