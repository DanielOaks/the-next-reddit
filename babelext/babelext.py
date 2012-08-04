#!/opt/local/bin/python2

import __future__

import os
import sys
import shutil

# Argument Parsing

try:
    import argparse
except ImportError:
    print('You need argparse to run BabelExt. Python2.7 and above provide this.')

parser = argparse.ArgumentParser(description='Linking BabelExt extentions.')

parser.add_argument('-d', help='debug mode', action='store_true')
# example line to print debug info, given this argument:
#if vars(args)['d']: print('    Cleaning build/')

parser.add_argument('-b', help='build directory, defaults to: build', dest='build_dir')

parser.add_argument('--clean', '-c', help='clean the build directory', action='store_true')
parser.add_argument('--link', '-l', help='link together the BabelExt extention', action='store_true')

args = parser.parse_args()

# because all the args are optional, we need to manually print the help
#  if the user doesn't select any thing to do
if not (vars(args)['clean'] or vars(args)['link']):
    parser.print_help()
    exit()


if vars(args)['build_dir']:
    build_dir = vars(args)['build_dir']
    if vars(args)['d']: print('  Build directory changed to ' + build_dir)
else:
    build_dir = 'build'

if vars(args)['link']:
    vars(args)['clean'] = True


# extension cleaning
if vars(args)['clean']:
    if vars(args)['d']: print('  Cleaning ' + build_dir)

    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir)


# extension linking
if vars(args)['link']:
    if vars(args)['d']: print('  Linking to ' + build_dir)

    if vars(args)['d']: print('    Copying bases into ' + build_dir)
    shutil.copytree('base', build_dir)


    import codecs
    import json


    # load base manifest
    file_path = 'lib' + os.sep + 'manifest.json'
    file = codecs.open(file_path, 'r', 'utf8')
    manifest = json.loads(file.read())
    file.close()


    ##
    ## Chrome manifest
    ##
    if vars(args)['d']: print('    Building Chrome manifest and files into ' + build_dir + os.sep + 'Chrome')
    chrome_manifest = {}

    chrome_manifest['name'] = manifest['base']['name']
    chrome_manifest['version'] = manifest['base']['version']
    chrome_manifest['description'] = manifest['base']['description']
    chrome_manifest['content_scripts'] = [{}]
    chrome_manifest['content_scripts'][0]['matches'] = []
    for match in manifest['base']['sites']:
        chrome_manifest['content_scripts'][0]['matches'].append('http://' + match + '/*')
        chrome_manifest['content_scripts'][0]['matches'].append('https://' + match + '/*')

    if 'icons' in manifest['base']:
        chrome_manifest['icons'] = {}
        for size in ['16', '48', '128']:
            if size in manifest['base']['icons']:
                chrome_manifest['icons'][size] = manifest['base']['icons'][size]

    # automagically add files
    chrome_manifest['content_scripts'][0]['files'] = {}

    for filetype in manifest['base']['files']:
        chrome_manifest['content_scripts'][0]['files'][filetype] = []
        for name in manifest['base']['files'][filetype]:
            chrome_manifest['content_scripts'][0]['files'][filetype].append(name)

    chrome_manifest.update(manifest['chrome'])

    # aaand copy the actual lib files into there
    for filename in os.listdir('lib'):
        if filename != 'manifest.json':
            if vars(args)['d']: print('        Copying file ' + filename)
            shutil.copyfile('lib' + os.sep + filename, build_dir + os.sep + 'Chrome' + os.sep + filename)

    # save manifest
    if vars(args)['d']: print('        Saving manifest')
    file_path = build_dir + os.sep + 'Chrome' + os.sep + 'manifest.json'
    chrome_file = codecs.open(file_path, 'w', 'utf8')
    chrome_file.write(json.dumps(chrome_manifest, sort_keys=True, indent=4))
    chrome_file.close()


    ##
    ## Firefox manifest
    ##
    if vars(args)['d']: print('    Building Firefox manifest and files into ' + build_dir + os.sep + 'Firefox')
    firefox_manifest = {}

    firefox_manifest['name'] = manifest['base']['progname']
    firefox_manifest['fullName'] = manifest['base']['name']
    firefox_manifest['description'] = manifest['base']['description']
    firefox_manifest['author'] = manifest['base']['author']
    if 'icons' in manifest['base']:
        if 'default' in manifest['base']['icons']:
            firefox_manifest['icon'] = manifest['base']['icons']['default']
        if '64' in manifest['base']['icons']:
            firefox_manifest['icon64'] = manifest['base']['icons']['64']
    firefox_manifest['license'] = manifest['base']['license']
    firefox_manifest['version'] = manifest['base']['version']

    # TODO: add files automagically

    # change around main.js style and script arrays

    firefox_manifest.update(manifest['firefox'])

    # save manifest
    if vars(args)['d']: print('        Saving manifest')
    file_path = 'build' + os.sep + 'Firefox' + os.sep + 'package.json'
    firefox_file = codecs.open(file_path, 'w', 'utf8')
    firefox_file.write(json.dumps(firefox_manifest, sort_keys=True, indent=4))
    firefox_file.close()
