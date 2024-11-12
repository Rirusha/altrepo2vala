#!/usr/bin/python3
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

import requests
import sys

from utils import fix_type, resolve_ref
from object_defs import create_object
from client_defs import create_client
import global_args


# doc_url = sys.argv[1]
# api_base = sys.argv[2]
# author = sys.argv[3]
# namespace = sys.argv[4]
# target_path = sys.argv[5]
doc_url = 'https://rdb.altlinux.org/api/swagger.json'
api_base = 'https://rdb.altlinux.org/api'
author = 'Vladimir Vaskov'
namespace = 'AltRepo'
target_path = '/home/rirusha/Downloads/doc'

# CHECK

global_args.author = author
global_args.namespace = namespace
global_args.target_path = target_path

swagger_doc = requests.get(doc_url).json()

for model_name, obj in swagger_doc['definitions'].items():
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
            create_object(namespace, fix_type(model_name), final_model['properties'], ref, target_path)
        case _:
            raise TypeError ()

create_client (namespace, api_base, swagger_doc['paths'], target_path)
