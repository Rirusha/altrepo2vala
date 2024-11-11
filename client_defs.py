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

import os
from utils import format_arg, resolve_ref, format_header, format_description, format_method
from structures import API_BASE, CLIENT_CLASS, CONSTRUCT, SOUP_WRAPPER

def create_method(path:str):
    pass

def create_client (namespace:str, api_base:str, paths:dict, target_path:str):
    path = os.path.join(target_path, 'client.vala')

    if not os.path.exists(target_path):
        os.makedirs(target_path)

    with (open(path, 'w') as file):
        file.write(format_header())
        file.write('\n\nusing ApiBase;\n\n')
        file.write((CLIENT_CLASS + ' {{\n\n').format(
            namespace=namespace
        ))
        file.write(API_BASE.format(
            api_base=api_base
        ))
        file.write(SOUP_WRAPPER)
        file.write(CONSTRUCT)

        for type_ in ['sync', 'async']:
            if type_ == 'async':
                file.write('\n//ASYNC\n\n')

            for path, methods in paths.items():
                if ('auth' in path):
                    continue

                path_args = []

                for method, definition in methods.items():
                    if method == 'parameters':
                        # dgsgsdg
                        continue

                    if '200' not in definition['responses']:
                        continue

                    param_descs = []
                    for parameter in definition.get('parameters', []):
                        param_descs.append('@param {name} {desc}'.format(
                            name=parameter['name'],
                            desc=parameter.get('description', '')
                        ))

                    file.write('\n')
                    file.write(format_description([
                        *definition['description'].split('\n'),
                        '',
                        *param_descs
                    ]))
                    file.write('\n')

                    name = method + '_' + path.split('{')[0].strip('/').replace('/', '_') + ('_async' if type_ == 'async' else '')
                    success = definition['responses']['200']
                    if 'schema' in success:
                        if 'type' in success['schema']:
                            if success['schema']['type'] == 'array':
                                if '$ref' in success['schema']['items']:
                                    return_type = 'Gee.ArrayList<{0}>'.format(resolve_ref(success['schema']['items']['$ref']))
                                else:
                                    return_type = 'Gee.ArrayList<{0}>'.format(resolve_ref(success['schema']['items']['type']))
                        else:
                            if ('type' in success['schema']):
                                return_type = resolve_ref(success['schema']['type'])
                            else:
                                return_type = 'void'
                    else:
                        return_type = 'string'

                    argv = []
                    for parameter in definition.get('parameters', []):
                        arg_type = None
                        if ('schema' in parameter):
                            arg_type = resolve_ref(parameter['schema']['$ref'])
                        else:
                            if parameter['type'] == 'integer':
                                arg_type = 'int'
                            elif parameter['type'] == 'boolean':
                                arg_type = 'bool'
                            elif parameter['type'] == 'array':
                                arg_type = parameter['items']['type'] + '[]'
                            else:
                                arg_type = parameter['type']

                        default_value = None
                        if 'default' in parameter:
                            default_value = str(parameter['default'])

                        argv.append(format_arg(
                            parameter['name'],
                            arg_type,
                            not parameter.get('required', False),
                            default_value
                        ))

                    file.write(format_method(return_type, name, argv, "\n", type_ == 'async'))
                    file.write('\n')

        file.write('}\n')
