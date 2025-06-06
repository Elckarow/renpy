﻿# Copyright 2004-2025 Tom Rothamel <pytom@bishoujo.us>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from gui7.code import CodeGenerator, translate_define, translate_copy, translate_code
from gui7.images import ImageGenerator
from gui7.parameters import GuiParameters

import renpy.arguments
import os
import shutil


def copy_gitignore(p):
    """
    Copy gitignore.txt from the template directory to the game directory.
    """

    old = os.path.join(p.template, "..", "gitignore.txt")
    new = os.path.join(p.prefix, "..", ".gitignore")

    if not os.path.exists(old):
        return

    if os.path.exists(new):
        return

    with open(old, "r") as f:
        data = f.read()

    with open(new, "w") as f:
        f.write(data)


def finish(p):

    for dn in [ "images", "audio", "libs" ]:

            fulldn = os.path.join(p.prefix, dn)

            if not os.path.exists(fulldn):
                os.mkdir(fulldn)

    if hasattr(renpy.store, "LIBS_TXT"):
        with open(os.path.join(p.prefix, "libs", "libs.txt"), "w") as f:
            f.write(renpy.translation.translate_string(renpy.store.LIBS_TXT, language=p.language))

    copy_gitignore(p)


def generate_gui(p):

    ImageGenerator(p).generate_all()
    CodeGenerator(p).generate_gui("gui.rpy", defines=True)
    CodeGenerator(p).generate_gui("screens.rpy")
    CodeGenerator(p).generate_code("options.rpy")
    CodeGenerator(p).copy_script("script.rpy")
    CodeGenerator(p).copy_files()

    finish(p)


def generate_minimal(p):

    # Copy the template over.
    os.makedirs(os.path.dirname(p.prefix), 0o777)
    shutil.copytree(p.template, p.prefix)

    def delete(fn):
        fn = os.path.join(p.prefix, fn)

        if os.path.isdir(fn):
            shutil.rmtree(fn)
        elif os.path.exists(fn):
            os.unlink(fn)

    # Prune directories.
    delete("cache")
    delete("saves")
    delete("tl")

    # Prune files to be regenerated.
    delete("gui.rpy")
    delete("screens.rpy")
    delete("options.rpy")

    # Generate files.
    CodeGenerator(p).generate_code("gui.rpy")
    CodeGenerator(p).generate_code("screens.rpy")
    CodeGenerator(p).generate_code("options.rpy")
    CodeGenerator(p).copy_files()

    finish(p)


def generate_gui_command():

    ap = renpy.arguments.ArgumentParser()

    ap.add_argument("target", action="store", help="The game into which the generated gui should be placed.")
    ap.add_argument("--width", default=1280, action="store", type=int, help="The width of the generated gui.")
    ap.add_argument("--height", default=720, action="store", type=int, help="The height of the generated gui.")
    ap.add_argument("--accent", default="#00b8c3", action="store", help="The accent color used throughout the gui.")
    ap.add_argument("--boring", default="#000000", action="store", help="The boring color used for the gui background.")
    ap.add_argument("--light", default=False, action="store_true", help="True if this is considered a light theme.")
    ap.add_argument("--template", default="gui", action="store", help="The template directory containing source code.")
    ap.add_argument("--language", default=None, action="store", help="The language to translate strings and comments to.")

    ap.add_argument("--start", default=False, action="store_true", help="Starts a new project, replacing images and code.")
    ap.add_argument("--replace-images", default=False, action="store_true", help="True if existing images should be overwritten.")
    ap.add_argument("--replace-code", default=False, action="store_true", help="True if an existing gui.rpy file should be overwritten.")
    ap.add_argument("--update-code", default=False, action="store_true", help="True if an existing gui.rpy file should be updated.")

    ap.add_argument("--minimal", default=False, action="store_true", help="Only update option.rpy and translations.")

    args = ap.parse_args()

    if args.start:
        args.replace_images = True
        args.replace_code = True
        args.update_code = True

    if args.minimal:
        args.replace_code = True
        args.update_code = True

    prefix = os.path.join(args.target, "game")

    if os.path.exists(args.target):

        if not os.path.isdir(prefix):
            ap.error("{} does not appear to be a Ren'Py game.".format(prefix))

    template = os.path.join(args.template, "game")

    if not os.path.isdir(template):
        ap.error("{} does not appear to be a Ren'Py game.".format(template))

    p = GuiParameters(
        prefix,
        template,
        args.width,
        args.height,
        args.accent,
        args.boring,
        args.light,
        args.language,
        args.replace_images,
        args.replace_code,
        args.update_code,
        os.path.basename(args.target),
        )

    if args.minimal:
        generate_minimal(p)
    else:
        generate_gui(p)

renpy.arguments.register_command("generate_gui", generate_gui_command)
