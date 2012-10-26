#!/opt/local/bin/python2

import __future__

import os
import shutil
import fileinput

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
    if vars(args)['d']:
        print('  Build directory changed to ' + build_dir)
else:
    build_dir = 'build'

if vars(args)['link']:
    vars(args)['clean'] = True

# extension cleaning
if vars(args)['clean']:
    if vars(args)['d']:
        print('  Cleaning ' + build_dir)

    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir)

# extension linking
if vars(args)['link']:
    if vars(args)['d']:
        print('  Linking to ' + build_dir)

        print('    Copying bases into ' + build_dir)
    shutil.copytree('base', build_dir)

    import codecs
    import json

    # load base manifest
    file_path = 'lib' + os.sep + 'manifest.json'
    file = codecs.open(file_path, 'r', 'utf8')
    manifest = json.loads(file.read())
    file.close()

    ##
    ## Userscript/Userstyle base
    ##
    if vars(args)['d']:
        print('')  # space between different build dirs
        print('    Building Userscript/Userstyle etc files into ' + build_dir + os.sep + 'User')
        print('      Note: fonts and icons not built into User directory')

    for filename in os.listdir('lib'):
        if filename.split('.')[-1] not in ['js', 'css']:
            continue
        if filename not in ['manifest.json', 'BabelExt.js']:
            if ('js' in filename) and ('user.js' not in filename):
                continue
            if vars(args)['d']:
                print('        Copying file ' + filename)
            shutil.copyfile('lib' + os.sep + filename, build_dir + os.sep + 'User' + os.sep + filename)

    if vars(args)['d']:
        print('')  # space between different build dirs

    ##
    ## Chrome manifest
    ##
    # @-moz-document messes up files for the Chrome files
    if vars(args)['d']:
        print('    Building Chrome manifest and files into ' + build_dir + os.sep + 'Chrome')
    chrome_manifest = {}
    chrome_manifest["manifest_version"] = 2
    chrome_manifest['content_scripts'] = [{}]
    #chrome_manifest['content_scripts'][0]['all_frames'] = True

    if 'fonts' in manifest['base']['files']:
        if vars(args)['d']:
            print('        Building font file')
        chrome_filepath = 'chrome-extension://__MSG_@@extension_id__/'
        fontfile = ''

        for font in manifest['base']['files']['fonts']:
            for fontformat in manifest['base']['files']['fonts'][font]:
                if fontformat in ['truetype']:
                    for fontface in manifest['base']['files']['fonts'][font][fontformat]:
                        fontfile += '@font-face {\n'
                        fontfile += "    font-family: '" + font + "';\n"
                        fontfile += "    src: url('" + chrome_filepath + fontface[1] + "') format('" + fontformat + "');\n"
                        fontfile += "    font-weight: " + fontface[0][0] + ";\n"
                        fontfile += "    font-style: " + fontface[0][1] + ";\n"
                        fontfile += "}\n\n"

        file_path = build_dir + os.sep + 'Chrome' + os.sep + 'fonts.css'
        chrome_font_file = codecs.open(file_path, 'w', 'utf8')
        chrome_font_file.write(fontfile)
        chrome_font_file.close()

    chrome_manifest['name'] = manifest['base']['name']
    chrome_manifest['version'] = manifest['base']['version']
    chrome_manifest['description'] = manifest['base']['description']
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
    for filetype in manifest['base']['files']:
        if filetype == 'fonts':
            continue
        chrome_manifest['content_scripts'][0][filetype] = []
        for name in manifest['base']['files'][filetype]:
            chrome_manifest['content_scripts'][0][filetype].append(name)

    chrome_manifest.update(manifest['chrome'])

    # aaand copy the actual lib files into there
    for filename in os.listdir('lib'):
        if filename not in ['manifest.json', '.DS_Store']:
            if vars(args)['d']:
                print('        Copying file ' + filename)
            shutil.copyfile('lib' + os.sep + filename, build_dir + os.sep + 'Chrome' + os.sep + filename)

    # font files, do this here to get past the manual chrome manifest
    if 'fonts' in manifest['base']['files']:
        chrome_manifest['content_scripts'][0]['css'].append('fonts.css')

    # save manifest
    if vars(args)['d']:
        print('        Saving manifest')
    file_path = build_dir + os.sep + 'Chrome' + os.sep + 'manifest.json'
    chrome_file = codecs.open(file_path, 'w', 'utf8')
    chrome_file.write(json.dumps(chrome_manifest, sort_keys=True, indent=4))
    chrome_file.close()

    if vars(args)['d']:
        print('')  # space between different build dirs

    ##
    ## Firefox manifest
    ##
    if vars(args)['d']:
        print('    Building Firefox manifest and files into ' + build_dir + os.sep + 'Firefox')
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

    firefox_manifest.update(manifest['firefox'])

    # generate firefox css/js include lists
    firefox_css = '['
    for filename in manifest['base']['files']['css']:
        firefox_css += "self.data.url('" + filename + "'), "
    firefox_css = firefox_css[:-2] + ']'

    firefox_js = '['
    for filename in manifest['base']['files']['js']:
        firefox_js += "self.data.url('" + filename + "'), "
    firefox_js = firefox_js[:-2] + ']'

    # add files to main js
    firefox_main = open('build' + os.sep + 'Firefox' + os.sep + 'lib' + os.sep + 'main.js', 'w')
    for line in fileinput.input(['base' + os.sep + 'Firefox' + os.sep + 'lib' + os.sep + 'main.js']):
        line = line.replace('include: ["*.babelext.com"]', 'include: ' + str(manifest['base']['sites']))
        line = line.replace("contentScriptFile: [self.data.url('BabelExt.js'), self.data.url('extension.js')]", 'contentScriptFile: ' + firefox_js + ',\n  contentStyleFile: ' + firefox_css)
        firefox_main.write(line)
    firefox_main.close()

    # aaand copy the actual lib files into there
    for filename in os.listdir('lib'):
        if filename not in ['manifest.json', '.DS_Store']:
            if vars(args)['d']:
                print('        Copying file ' + filename)
            shutil.copyfile('lib' + os.sep + filename, build_dir + os.sep + 'Firefox' + os.sep + 'data' + os.sep + filename)

    # save manifest
    if vars(args)['d']:
        print('        Saving manifest')
    file_path = 'build' + os.sep + 'Firefox' + os.sep + 'package.json'
    firefox_file = codecs.open(file_path, 'w', 'utf8')
    firefox_file.write(json.dumps(firefox_manifest, sort_keys=True, indent=4))
    firefox_file.close()

    if vars(args)['d']:
        print('')  # space between different build dirs
