#!/usr/bin/env python
# encoding: utf8
"""Script to create a bunch of tarballs and montages, made available on the
/dex/downloads page.
"""
from __future__ import division
import math
import os, os.path
import pkg_resources
import re
import subprocess
from subprocess import PIPE
import sys
import tarfile


phi = (1 + 5 ** 0.5) / 2

# Find the spline-pokedex downloads dir as relative to this script; it's not a
# data dir, so pkg_resources isn't much help
this_dir, _ = os.path.split(__file__)
downloads_dir = os.path.abspath(
    os.path.join(this_dir, '../splinext/pokedex/public/downloads')
)
media_dir = pkg_resources.resource_filename('pokedex', 'data/media')

def create_downloads():
    # Gotta chdir to get the gzip header right; see Python bug 4750
    os.chdir(downloads_dir)

    # Per-generation Pokémon tarballs
    make_tarball('generation-1.tar.gz', ['red-green', 'red-blue', 'yellow'])
    make_tarball('generation-2.tar.gz', ['gold', 'silver', 'crystal'])
    make_tarball('generation-3.tar.gz', ['ruby-sapphire', 'emerald', 'firered-leafgreen'])
    make_tarball('generation-4.tar.gz', ['diamond-pearl', 'platinum', 'heartgold-soulsilver'])

    # Other Pokémon stuff
    make_tarball('overworld.tar.gz', ['overworld'])
    make_tarball('pokemon-cries.tar.gz', ['cries'])
    make_tarball('pokemon-sugimori.tar.gz', ['sugimori'])
    make_tarball('pokemon-footprints.tar.gz', ['footprints'])
    make_tarball('pokemon-trozei.tar.gz', ['trozei'])
    make_tarball('pokemon-icons.tar.gz', ['icons'])

    # Not Pokémon at all!
    make_tarball('chrome.tar.gz', ['chrome', 'ribbons'])
    make_tarball('items.tar.gz', ['items'])

    # Bunch o' montages
    make_montage('red-green.png',       'red-green/gray/{0}.png',   56, 151)
    make_montage('red-green-sgb.png',   'red-green/{0}.png',        56, 151)
    make_montage('red-blue.png',        'red-blue/gray/{0}.png',    56, 151)
    make_montage('red-blue-sgb.png',    'red-blue/{0}.png',         56, 151)
    make_montage('yellow.png',          'yellow/gray/{0}.png',      56, 151)
    make_montage('yellow-sgb.png',      'yellow/{0}.png',           56, 151)
    make_montage('yellow-gbc.png',      'yellow/gbc/{0}.png',       56, 151)
    make_montage('generation-1-back.png',
        'red-blue/back/gray/{0}.png',       32, 151)
    make_montage('red-green-blue-back-sgb.png',
        'red-blue/back/{0}.png',            32, 151)
    make_montage('yellow-back-sgb.png', 'yellow/back/{0}.png',      32, 151)
    make_montage('yellow-back-gbc.png', 'yellow/back/gbc/{0}.png',  32, 151)

    make_montage('gold.png',            'gold/{0}.png',             56, 251)
    make_montage('gold-shiny.png',      'gold/shiny/{0}.png',       56, 251)
    make_montage('silver.png',          'silver/{0}.png',           56, 251)
    make_montage('silver-shiny.png',    'silver/shiny/{0}.png',     56, 251)
    make_montage('crystal.png',         'crystal/{0}.png',          56, 251)
    make_montage('crystal-shiny.png',   'crystal/shiny/{0}.png',    56, 251)
    make_montage('gold-silver-back.png',
        'silver/back/{0}.png',              48, 251)
    make_montage('gold-silver-back-shiny.png',
        'silver/back/shiny/{0}.png',        48, 251)
    make_montage('crystal-back.png',
        'crystal/back/{0}.png',              48, 251)
    make_montage('crystal-back-shiny.png',
        'crystal/back/shiny/{0}.png',        48, 251)

    make_montage('generation-3.png',
        'ruby-sapphire/{0}.png',            64, 386, transparent=True)
    make_montage('generation-3-shiny.png',
        'ruby-sapphire/shiny/{0}.png',      64, 386, transparent=True)
    make_montage('emerald-frame2.png',
        'emerald/frame2/{0}.png',           64, 386, transparent=True)
    make_montage('emerald-frame2-shiny.png',
        'emerald/shiny/frame2/{0}.png',     64, 386, transparent=True)
    make_montage('firered-leafgreen.png',
        'firered-leafgreen/{0}.png',        64, 151, transparent=True)
    make_montage('firered-leafgreen-shiny.png',
        'firered-leafgreen/shiny/{0}.png',  64, 151, transparent=True)
    make_montage('generation-3-back.png',
        'ruby-sapphire/back/{0}.png',       64, 386, transparent=True)
    make_montage('generation-3-back-shiny.png',
        'ruby-sapphire/back/shiny/{0}.png', 64, 386, transparent=True)
    make_montage('firered-leafgreen-back.png',
        'firered-leafgreen/back/{0}.png',   64, 151, transparent=True)
    make_montage('firered-leafgreen-back-shiny.png',
        'firered-leafgreen/back/shiny/{0}.png', 64, 151, transparent=True)

    make_montage('diamond-pearl.png',
        'diamond-pearl/{0}.png',            80, 493, transparent=True)
    make_montage('diamond-pearl-shiny.png',
        'diamond-pearl/shiny/{0}.png',      80, 493, transparent=True)
    make_montage('diamond-pearl-frame2.png',
        'diamond-pearl/frame2/{0}.png',     80, 493, transparent=True)
    make_montage('diamond-pearl-shiny-frame2.png',
        'diamond-pearl/shiny/frame2/{0}.png', 80, 493, transparent=True)
    make_montage('platinum.png',
        'platinum/{0}.png',                 80, 493, transparent=True)
    make_montage('platinum-shiny.png',
        'platinum/shiny/{0}.png',           80, 493, transparent=True)
    make_montage('platinum-frame2.png',
        'platinum/frame2/{0}.png',          80, 493, transparent=True)
    make_montage('platinum-shiny-frame2.png',
        'platinum/shiny/frame2/{0}.png',    80, 493, transparent=True)
    make_montage('heartgold-soulsilver.png',
        'heartgold-soulsilver/{0}.png',     80, 493, transparent=True)
    make_montage('heartgold-soulsilver-shiny.png',
        'heartgold-soulsilver/shiny/{0}.png', 80, 493, transparent=True)
    make_montage('heartgold-soulsilver-frame2.png',
        'heartgold-soulsilver/frame2/{0}.png', 80, 493, transparent=True)
    make_montage('heartgold-soulsilver-shiny-frame2.png',
        'heartgold-soulsilver/shiny/frame2/{0}.png', 80, 493, transparent=True)
    make_montage('diamond-pearl-back.png',
        'diamond-pearl/back/{0}.png',       80, 493, transparent=True)
    make_montage('diamond-pearl-back-shiny.png',
        'diamond-pearl/back/shiny/{0}.png', 80, 493, transparent=True)
    make_montage('platinum-back.png',
        'platinum/back/{0}.png',            80, 493, transparent=True)
    make_montage('platinum-back-shiny.png',
        'platinum/back/shiny/{0}.png',      80, 493, transparent=True)
    make_montage('platinum-back-frame2.png',
        'platinum/back/frame2/{0}.png',     80, 493, transparent=True)
    make_montage('platinum-back-shiny-frame2.png',
        'platinum/back/shiny/frame2/{0}.png', 80, 493, transparent=True)
    make_montage('heartgold-soulsilver-back.png',
        'heartgold-soulsilver/back/{0}.png', 80, 493, transparent=True)
    make_montage('heartgold-soulsilver-back-shiny.png',
        'heartgold-soulsilver/back/shiny/{0}.png', 80, 493, transparent=True)
    make_montage('heartgold-soulsilver-back-frame2.png',
        'heartgold-soulsilver/back/frame2/{0}.png', 80, 493, transparent=True)
    make_montage('heartgold-soulsilver-back-shiny-frame2.png',
        'heartgold-soulsilver/back/shiny/frame2/{0}.png', 80, 493, transparent=True)

    # And female montages, which are a little different
    make_diff_montage(
        filename='diamond-pearl-female-diff.png',
        other_filename='diamond-pearl.png',
        pattern='diamond-pearl/female/{0}.png',
        fallback_pattern='diamond-pearl/{0}.png',
        sprite_size=80,
        pokemon=493,
    )
    make_diff_montage(
        filename='platinum-female-diff.png',
        other_filename='platinum.png',
        pattern='platinum/female/{0}.png',
        fallback_pattern='platinum/{0}.png',
        sprite_size=80,
        pokemon=493,
    )
    make_diff_montage(
        filename='heartgold-soulsilver-female-diff.png',
        other_filename='heartgold-soulsilver.png',
        pattern='heartgold-soulsilver/female/{0}.png',
        fallback_pattern='heartgold-soulsilver/{0}.png',
        sprite_size=80,
        pokemon=493,
    )
    make_diff_montage(
        filename='diamond-pearl-back-female-diff.png',
        other_filename='diamond-pearl-back.png',
        pattern='diamond-pearl/back/female/{0}.png',
        fallback_pattern='diamond-pearl/back/{0}.png',
        sprite_size=80,
        pokemon=493,
    )
    make_diff_montage(
        filename='platinum-back-female-diff.png',
        other_filename='platinum-back.png',
        pattern='platinum/back/female/{0}.png',
        fallback_pattern='platinum/back/{0}.png',
        sprite_size=80,
        pokemon=493,
    )
    make_diff_montage(
        filename='heartgold-soulsilver-back-female-diff.png',
        other_filename='heartgold-soulsilver-back.png',
        pattern='heartgold-soulsilver/back/female/{0}.png',
        fallback_pattern='heartgold-soulsilver/back/{0}.png',
        sprite_size=80,
        pokemon=493,
    )

    # Overworld
    make_montage('overworld-right.png',
        'overworld/right/{0}.png', 32, 493, transparent=True)
    make_montage('overworld-down.png',
        'overworld/down/{0}.png', 32, 493, transparent=True)
    make_montage('overworld-up.png',
        'overworld/up/{0}.png', 32, 493, transparent=True)
    make_montage('overworld-right-shiny.png',
        'overworld/shiny/right/{0}.png', 32, 493, transparent=True)
    make_montage('overworld-down-shiny.png',
        'overworld/shiny/down/{0}.png', 32, 493, transparent=True)
    make_montage('overworld-up-shiny.png',
        'overworld/shiny/up/{0}.png', 32, 493, transparent=True)

    # Other miscellaneous
    make_montage('footprints.png', 'footprints/{0}.png', 48, 493,
        subst_forms=False)
    make_montage('sugimori.png', 'sugimori/{0}.png', 96, 493,
        padding=2, subst_forms=False, filter='lanczos')
    make_labeled_montage(
        'items.png', 'items', suffix='.png',
        sprite_size=24, horiz_padding=36, vert_padding=6,
    )
    make_labeled_montage(
        'berries.png', 'items/big', suffix='-berry.png',
        sprite_size=48, horiz_padding=4, vert_padding=4,
    )

def make_tarball(filename, contents):
    """Packs `contents` into the tar file `filename`."""
    print "Generating", filename + "...",
    sys.stdout.flush()

    tar = tarfile.open(filename, 'w:gz')
    for content in contents:
        tar.add(os.path.join(media_dir, content), arcname=content)
    tar.close()

    print "ok"

def make_montage(filename, pattern, sprite_size, pokemon,
    padding=0, subst_forms=True, filter='point', transparent=False):

    u"""Creates a montage in `filename` out of PNG images matching `pattern`,
    which should be a str.format pattern.  `sprite_size` is the size of each
    sprite, for calculating the dimensions of the final product, and `pokemon`
    is the number of Pokémon that should be in the resulting image.

    The background will be transparent iff `transparent` is true.
    """
    print "Generating", filename + "...",
    sys.stdout.flush()

    transparent_switches = []
    if transparent:
        transparent_switches = ['-background', 'transparent']

    # Find all the files we want
    files = [
        os.path.join(media_dir, pattern.format(n))
        for n in range(1, pokemon + 1)
    ]
    if subst_forms:
        # Fill in reliable forms for overworld sprites
        for n, form in [(201, 'j'), (386, 'normal'),
                        (412, 'plant'), (413, 'plant'),
                        (422, 'west'), (423, 'west')]:
            if n >= len(files): break
            img = "{0}-{1}".format(n, form)
            files[n - 1] = os.path.join(media_dir, pattern.format(img))

    # Figure out the dimensions of the image.  Try to keep to the golden ratio,
    # because it rocks.
    # Thus: rows * (phi * rows) = pokemon
    rows = int(math.ceil( (pokemon / phi) ** 0.5 ))

    outfile = os.path.join(downloads_dir, filename)
    subprocess.Popen(
        ['montage',
            '-filter',      filter,
            '-geometry',    "{0}x{0}+{1}+{1}>".format(sprite_size, padding),
            '-tile',        "x{0}".format(rows),
        ]
            + files
            + transparent_switches
            + [outfile]
    ).wait()

    # Optipng it
    subprocess.Popen(['optipng', '-quiet', outfile]).wait()

    print "ok"

def make_diff_montage(filename, other_filename, pattern, fallback_pattern,
    sprite_size, pokemon):

    u"""Similar to `make_montage`, except!  This version assumes `pattern`
    refers to a file that may or may not exist, and `fallback_pattern` fills in
    the gaps.  Also it then diffs the generated image with `other_filename`.
    """
    print "Generating", filename + "...",
    sys.stdout.flush()

    # Find all the files we want
    files = []
    for n in range(1, pokemon + 1):
        img = os.path.join(media_dir, pattern.format(n))
        if os.path.exists(img):
            files.append(img)
        else:
            files.append(
                os.path.join(media_dir, fallback_pattern.format(n)))

    # Golden ratio blah blah
    rows = int(math.ceil( (pokemon / phi) ** 0.5 ))

    outfile = os.path.join(downloads_dir, filename)
    subprocess.Popen(
        ['montage',
            '-background',  'transparent',
            '-geometry',    "{0}x{0}+0+0>".format(sprite_size),
            '-tile',        "x{0}".format(rows),
        ]
            + files
            + [outfile]
    ).wait()

    # Do the comparison in-place
    subprocess.Popen([
        'compare',
        outfile, os.path.join(downloads_dir, other_filename),
        outfile,
    ]).wait()

    # Optipng it
    subprocess.Popen(['optipng', '-quiet', outfile]).wait()

    print "ok"

def make_labeled_montage(filename, directory, suffix,
    sprite_size, horiz_padding, vert_padding):

    u"""Makes a montage, with labels, of the files in the named directory.
    Only files ending in `suffix` will be used, and the suffix will be removed.

    The rest is a bunch of boring math.
    """
    print "Generating", filename + "...",
    sys.stdout.flush()

    # Find all the files we want
    s = len(suffix)
    file_args = []
    file_count = 0
    filenames = os.listdir(os.path.join(media_dir, directory))
    filenames.sort()
    for img in filenames:
        if not img.endswith(suffix):
            continue

        # Cut off .png
        label = img[:-s]

        file_args.extend([
            '-label',
            label,
            os.path.join(media_dir, directory, img),
        ])
        file_count += 1

    # Golden ratio blah blah.  Except with the padding it becomes...
    tile_h = sprite_size + vert_padding * 2 + 16  # 16 for label height
    tile_w = sprite_size + horiz_padding * 2
    # tile_h * rows * phi == tile_w * (n / rows)
    # => rows = sqrt((tile_w * n) / (tile_h * phi)
    rows = int(math.ceil(
        ((tile_w * file_count) / (tile_h * phi)) ** 0.5
    ))

    outfile = os.path.join(downloads_dir, filename)
    subprocess.Popen(
        ['montage',
            '-background',  'transparent',
            '-geometry',    "+{0}+{1}".format(horiz_padding, vert_padding),
            '-tile',        "x{0}".format(rows),
        ]
            + file_args
            + [outfile]
    ).wait()

    # Optipng it
    subprocess.Popen(['optipng', '-quiet', outfile]).wait()

    print "ok"


if __name__ == '__main__':
    create_downloads()
