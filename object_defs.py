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
from utils import resolve_ref, format_header, format_description, pascal_to_kebeb
from structures import PROPERTY, CLASS_DEFINITION

def format_property (prop_class:str, prop_name:str, is_array:bool=False, default_value:str|None=None) -> str:
    return PROPERTY.format(
        prop_class,
        prop_name.lower(),
        f'default = {default_value}; ' if default_value else ''
    )

def create_object (namespace:str, model_name:str, model_properties:dict, ref:str|None, base_path:str) -> None:
    objects_path = os.path.join(base_path, 'objects')
    path = os.path.join(objects_path, pascal_to_kebeb(model_name) + '.vala')

    if not os.path.exists(objects_path):
        os.makedirs(objects_path)

    with (open(path, 'w') as file):
        file.write(format_header())
        file.write('\n\n')
        file.write((CLASS_DEFINITION + ' {{\n').format(
            namespace,
            model_name,
            ref if ref else 'Object'            
        ))

        for prop_name, prop_data in model_properties.items():
            file.write('\n')

            if 'description' in prop_data:
                file.write(format_description(prop_data['description']) + '\n')

            if 'allOf' in prop_data:
                file.write(format_property(
                    resolve_ref(prop_data['allOf'][0]['$ref']),
                    prop_name
                ))
            elif '$ref' in prop_data:
                file.write(format_property(
                    resolve_ref(prop_data['$ref']),
                    prop_name
                ))
            elif prop_data['type'] == 'array':
                if '$ref' in prop_data['items']:
                    file.write(format_property(
                        f'Gee.ArrayList<{resolve_ref(prop_data['items']['$ref'])}>',
                        prop_name,
                        True,
                        f'new Gee.ArrayList<{resolve_ref(prop_data['items']['$ref'])}> ()'
                    ))
                else:
                    _type = prop_data['items']['type']
                    if _type == 'integer' or _type == 'number':
                        _type = 'int64?'
                    elif _type == 'boolean':
                        _type = 'bool'
                    elif _type == 'object':
                        _type = 'Object'

                    file.write(format_property(
                        f'Gee.ArrayList<{_type}>',
                        prop_name,
                        True,
                        f'new Gee.ArrayList<{_type}> ()'
                    ))
            else:
                _type = prop_data['type']
                if _type == 'integer' or _type == 'number':
                    _type = 'int64'
                elif _type == 'boolean':
                    _type = 'bool'
                elif _type == 'object':
                    _type = 'Object'
                
                file.write(format_property(
                    _type,
                    prop_name
                ))
        file.write('}\n')
