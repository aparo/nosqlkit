#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import traceback
import logging
import pprint
log = logging.getLogger(__name__)

class InvalidModule(Exception):

    def __init__(self, message='Invalid Module'): # pylint: disable-msg=W0231
        self.message = message

    def __str__(self):
        return self.message

def get_function_by_name(module_name, function_name):
    
    module = __import__(module_name)
    tokens=module_name.split('.')
    for token in range(1,len(tokens)):
#        print tokens[token]
        module=getattr(module, tokens[token])

    return getattr(module, function_name)

def get_function_by_code(code):
    module_name='.'.join(code.split('.')[:-1])
    funcname=code.split('.')[-1]
    return get_function_by_name(module_name,funcname)

def get_module_by_code(code):
    mod = __import__(code, {}, {})
    components = code.split('.')
    for comp in components[1:]:
        try:
            mod = getattr(mod, comp)
        except AttributeError:
            return None
    return mod

def get_module_dir_by_string(text):
    """ Detect the path from the module name"""
    command_module = __import__(text, {}, {})
    module_pos=command_module
    for attr in text.split('.')[1:]:
        module_pos=getattr(module_pos,attr)
    return os.path.split(module_pos.__file__)[0]


def get_addins(code_path, filter=None, with_name=False):
    """
    Carica gli addin da una directory di addins
    
    code_path: codice python del path
    filter: possibile filtro di tipologia
    """
    mpath = get_module_dir_by_string(code_path)
    files = set([p.split('.')[0] for p in os.listdir(mpath) if p.lower().endswith(('.py', '.pyc'))])
    files = files - set(['__init__'])
    addins = []
    for fname in files:
        try:
            modulename = '%s.%s.%s'%(code_path,fname,fname)
            module = get_function_by_code(modulename)
            if filter:
                if isinstance(module, filter):
                    if with_name:
                        addins.append((modulename,module))
                    else:
                        addins.append(module)
            else:
                if with_name:
                    addins.append((modulename,module))
                else:
                    addins.append(module)
        except ImportError:
            log.debug('An error occurred: %s' % repr(traceback.format_exc()))
            
    return addins

#--- Load modules
def find_modules(path=None, modulesdir=None):
    """
    Given a path to a management directory, returns a list of all the command
    names that are available.

    Returns an empty list if no commands are defined.
    """
    if path:
        if modulesdir:
            command_dir = os.path.join(path, modulesdir)
        else:
            command_dir = path
    else:
        command_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], modulesdir)
        
    try:
        return list(set([f.replace('.pyc', '').replace('.py', '') for f in os.listdir(command_dir)
                if not f.startswith('_') and (f.endswith('.py') or f.endswith('.pyc'))]))
    except OSError:
        return []

def load_command_class(name, baseclass='Engine'):
    """
    Given a command name and an application name, returns the Command
    class instance. All errors raised by the import process
    (ImportError, AttributeError) are allowed to propagate.
    """
    return getattr(__import__(name, {}, {}, [baseclass]), baseclass)()

def load_engines(namespace=None, path=None, modulesdir=None, baseclass='Engine', debug=False):
    engines = []
    names = []
    if path:
        names = find_modules(path=path, modulesdir=modulesdir)
    if namespace:
        names = find_modules(path=get_module_dir_by_string(namespace))
        log.debug('find_modules: %s' % names)
    done = []
    for name in names:
        if namespace:
            name = '%s.%s'%(namespace, name)
        if name not in done:
            try:
                engines.append(load_command_class(name, baseclass=baseclass))
                done.append(name)
            except (AttributeError, ImportError):
                log.debug('An error occurred: %s' % traceback.format_exc())
    return engines

if __name__ == '__main__':
    pass