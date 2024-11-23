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

        for async_ in [False, True]:
            if async_:
                file.write('\n    //ASYNC\n')

            for path, methods in paths.items():
                if ('auth' in path):
                    continue

                path_argv = []
                path_argvd = []
                
                path_arg_names = []
                path_arg_descs = []
                
                for parameter in methods.get('parameters', []):
                    arg_type = None
                    if ('schema' in parameter):
                        arg_type = resolve_ref(parameter['schema']['$ref'])
                    else:
                        if parameter['type'] == 'integer':
                            arg_type = 'int64'
                        elif parameter['type'] == 'boolean':
                            arg_type = 'bool'
                        elif parameter['type'] == 'array':
                            arg_type = parameter['items']['type'] + '[]'
                        else:
                            arg_type = parameter['type']

                    default_value = None
                    if 'default' in parameter:
                        default_value = str(parameter['default'])
                        
                        if default_value == 'none':
                            default_value = None
                            
                    nullable = not parameter.get('required', False)

                    (path_argv if not default_value and not nullable else path_argvd).append(format_arg(
                        parameter['name'],
                        arg_type,
                        not parameter.get('required', False),
                        default_value
                    ))
                    
                    path_arg_descs.append('@param {name} {desc}'.format(
                        name=parameter['name'],
                        desc=parameter.get('description', '')
                    ))
                    path_arg_names.append(parameter['name'])

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
                        
                    name = method + '_' + path.replace('{', '').replace('}', '').strip('/').replace('/', '_') + ('_async' if async_ else '')
                    success = definition['responses']['200']
                    if 'schema' in success:
                        if 'type' in success['schema']:
                            if success['schema']['type'] == 'array':
                                if '$ref' in success['schema']['items']:
                                    return_type = 'Gee.ArrayList<{0}>'.format(resolve_ref(success['schema']['items']['$ref']))
                                else:
                                    return_type = 'Gee.ArrayList<{0}>'.format(resolve_ref(success['schema']['items']['type']))
                        else:
                            if ('$ref' in success['schema']):
                                return_type = resolve_ref(success['schema']['$ref'])
                            else:
                                return_type = 'void'
                    else:
                        return_type = 'string'

                    file.write('\n')
                    file.write(format_description([
                        *definition['description'].split('\n'),
                        '',
                        *path_arg_descs,
                        *param_descs,
                        '',
                        '@return {{@link {0}}}'.format(return_type)
                    ]))
                    file.write('\n')

                    argv = []
                    argvd = []
                    
                    # {name: [is_array, nullable]}
                    param_args:dict[str,list[bool]] = {}
                    body_name = None
                    
                    for parameter in definition.get('parameters', []):
                        arg_type = None
                        if ('schema' in parameter):
                            arg_type = resolve_ref(parameter['schema']['$ref'])
                        else:
                            if parameter['type'] == 'integer':
                                arg_type = 'int64'
                            elif parameter['type'] == 'boolean':
                                arg_type = 'bool'
                            elif parameter['type'] == 'array':
                                arg_type = parameter['items']['type'] + '[]'
                            else:
                                arg_type = parameter['type']

                        default_value = None
                        if 'default' in parameter:
                            default_value = str(parameter['default'])
                            
                            if default_value == 'none':
                                default_value = None
                                
                        nullable = not parameter.get('required', False)

                        (argv if not default_value and not nullable else argvd).append(format_arg(
                            parameter['name'],
                            arg_type,
                            not parameter.get('required', False),
                            default_value
                        ))
                        
                        if parameter['in'] == 'query':
                            param_args[parameter['name']] = []
                            param_args[parameter['name']].append (arg_type.endswith('[]'))
                            param_args[parameter['name']].append (nullable)
                        elif (parameter['in'] == 'body'):
                            body_name = parameter['name']

                    depricated_version = None
                    if definition.get('deprecated', False):
                        depricated_version = ''

                    file.write(format_method(return_type, name, argv + path_argv + argvd + path_argvd, format_body(path, param_args, path_arg_names, body_name, method, definition, return_type, async_), async_, depricated_version))
                    file.write('\n')

        file.write('}\n')

def format_body(path:str, param_args:dict[str,list[bool]], path_args:list[str], body_name:str, method:str, definition:dict[str,dict], return_type:str, async_:str) -> str:
    out = []
    
    if body_name:
        out.append('PostContent post_content = {')
        out.append('    PostContentType.JSON,')
        out.append(f'    {'yield ' if async_ else ''}Jsoner.serialize{'_async' if async_ else ''} ({body_name}, Case.SNAKE)')
        out.append('};\n')
    
    if param_args:
        params = []
        for arg_name, (is_array, nullable) in param_args.items():
            if is_array:
                if nullable:
                    params.append('    {{ "{arg_name}", {arg_name} != null ? string.joinv (",", {arg_name}) : null }},'.format(arg_name=arg_name))
                else:
                    params.append('    {{ "{arg_name}", string.joinv (",", {arg_name}) }},'.format(arg_name=arg_name))
            else:
                if nullable:
                    params.append('    {{ "{arg_name}", {arg_name} != null ? {arg_name}.to_string () : null }},'.format(arg_name=arg_name))
                else:
                    params.append('    {{ "{arg_name}", {arg_name}.to_string () }},'.format(arg_name=arg_name))
            
        params.insert(0, '{')
        params.append('},')
    else:
        params = ['null,']

    if method == 'get':
        out.append(f'var bytes = {'yield ' if async_ else ''}soup_wrapper.get{'_async' if async_ else ''} (')
        out.append(f'    @"$API_BASE{(path.replace('{' + path_args[0] + '}', f'${path_args[0]}')) if path_args else path}",')
        out.append('    null,')
        out.append('    ' + '\n            '.join(params))
        out.append('    null,')
        if async_:
            out.append('    priority,')
        out.append('    cancellable')
        out.append(');')
    elif method == 'post':
        out.append(f'var bytes = {'yield ' if async_ else ''}soup_wrapper.post{'_async' if async_ else ''} (')
        out.append(f'    @"$API_BASE{(path.replace('{' + path_args[0] + '}', f'${path_args[0]}')) if path_args else path}",')
        out.append('    null,')
        if body_name:
            out.append('    post_content,')
        else:
            out.append('    null,')
        out.append('    ' + '\n            '.join(params))
        out.append('    null,')
        if async_:
            out.append('    priority,')
        out.append('    cancellable')
        out.append(');\n')
    elif method == 'put':
        raise NotImplementedError (method)
    elif method == 'delete':
        raise NotImplementedError (method)
    else:
        raise TypeError (f'Unknown method {method}')
    
    if return_type == 'string':
        out.append(f'return (string) bytes.get_data ();')
        return out

    out.append('var jsoner = Jsoner.from_bytes (bytes, null, Case.SNAKE);\n')

    if return_type.startswith('Gee.ArrayList'):
        out.append(f'var array = new {return_type} ();')
        out.append(f'{'yield ' if async_ else ''}jsoner.deserialize_array{'_async' if async_ else ''} (array);\n')

        out.append('return array;')
    else:
        out.append(f'return ({return_type}) {'yield ' if async_ else ''}jsoner.deserialize_object{'_async' if async_ else ''} (typeof ({return_type}));')
    
    return out
