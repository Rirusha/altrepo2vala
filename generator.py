#!/usr/bin/python3

import requests
import json
import sys
import os

# doc_url = sys.argv[1]
doc_url = 'https://rdb.altlinux.org/api/swagger.json'
header = """/*
 * Copyright (C) 2024 Vladimir Vaskov
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
 */"""
target_path = "/home/rirusha/Downloads/doc"

swagger_doc = requests.get(doc_url).json()
definitions = swagger_doc['definitions']
namespace = "TestObjects"


def resolve_ref (ref:str) -> str:
    return ref.lstrip('#/definitions/').replace('/', '.')

def create_object (namespace:str, model_name:str, model_properties:dict, ref:str|None, base_path:str) -> None:
    objects_path = os.path.join(base_path, 'objects')
    path = os.path.join(objects_path, model_name + '.vala')
    
    if not os.path.exists(objects_path):
        os.makedirs(objects_path)
    
    with (open(path, 'w') as file):
        file.write(header)
        file.write('\n\n')
        file.write('public class {{0} : {1} {{\n'.format(
            model_name,
            ref if ref else 'Object',
            namespace
        ))
        
        for prop_name, prop_data in model_properties.items():
            if 'description' in prop_data:
                file.write('\n\t/**\n')
                file.write('\t * {0}\n'.format(prop_data['description']))
                file.write('\t */\n')
            if 'allOf' in prop_data:
                file.write('\tpublic {0} {1} {{ get; set; }}\n'.format(
                    resolve_ref(prop_data['allOf'][0]['$ref']),
                    prop_name
                ))
            elif '$ref' in prop_data:
                file.write('\tpublic {0} {1} {{ get; set; }}\n'.format(
                    resolve_ref(prop_data['$ref']),
                    prop_name
                ))
            elif prop_data['type'] == 'array':
                if '$ref' in prop_data['items']:
                    file.write('\tpublic Gee.ArrayList<{0}> {1} {{ get; set; default=new Gee.ArrayList<{0}> () }}\n'.format(
                        resolve_ref(prop_data['items']['$ref']),
                        prop_name
                    ))
                else:
                    _type = prop_data['items']['type']
                    if _type == 'integer':
                        _type = 'int'
                    file.write('\tpublic Gee.ArrayList<{0}> {1} {{ get; set; default=new Gee.ArrayList<{0}> () }}\n'.format(
                        _type,
                        prop_name
                    ))
            else:
                _type = prop_data['type']
                if _type == 'integer':
                    _type = 'int'
                file.write('\tpublic {0} {1} {{ get; set; }}\n'.format(
                    _type,
                    prop_name
                ))
        file.write('}\n')


for model_name, obj in definitions.items():
    final_model = None
    ref = None
    
    if 'allOf' in obj:
        for model in obj['allOf']:
            if ('$ref' in model):
                ref = resolve_ref(model['$ref'])
            else:
                final_model = model
    else:
        final_model = obj
    
    match final_model['type']:
        case 'object':
            create_object(namespace, model_name, final_model['properties'], ref, target_path)
        case _:
            raise TypeError ()
