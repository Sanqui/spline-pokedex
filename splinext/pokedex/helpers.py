# encoding: utf8
"""Collection of small functions and scraps of data that don't belong in the
pokedex core -- either because they're inherently Web-related, or because
they're very flavorful and don't belong or fit well in a database.
"""

from __future__ import absolute_import, division

import math
import re
from itertools import groupby, chain, repeat
from operator import attrgetter

from pylons import url

import pokedex.db.tables as tables
import pokedex.formulae as formulae
from pokedex.roomaji import romanize

import spline.lib.helpers as h

# We can't translate at import time, but _ will mark strings as translatable
# Functions that need translation will take a "_" parameter, which defaults
# to this:
_ = unicode

def make_thingy_url(thingy, subpage=None):
    u"""Given a thingy (Pokémon, move, type, whatever), returns a URL to it.
    """
    # Using the table name as an action directly looks kinda gross, but I can't
    # think of anywhere I've ever broken this convention, and making a
    # dictionary to get data I already have is just silly
    args = {}

    # Pokémon with forms need the form attached to the URL
    if getattr(thingy, 'forme_base_pokemon_id', None):
        args['form'] = thingy.forme_name

    # Items are split up by pocket
    if isinstance(thingy, tables.Item):
        args['pocket'] = thingy.pocket.identifier

    action = thingy.__tablename__
    if subpage:
        action += '_' + subpage

    return url(controller='dex',
               action=action,
               name=thingy.name.lower(),
               **args)

def render_flavor_text(flavor_text, literal=False):
    """Makes flavor text suitable for HTML presentation.

    If `literal` is false, collapses broken lines into single lines.

    If `literal` is true, linebreaks are preserved exactly as they are in the
    games.
    """

    # n.b.: \u00ad is soft hyphen

    # Somehow, the games occasionally have \n\f, which makes no sense at all
    # and wouldn't render in-game anyway.  Fix this
    flavor_text = flavor_text.replace('\n\f', '\f')

    if literal:
        # Page breaks become two linebreaks.
        # Soft hyphens become real hyphens.
        # Newlines become linebreaks.
        html = flavor_text.replace(u'\f',       u'<br><br>') \
                          .replace(u'\u00ad',   u'-') \
                          .replace(u'\n',       u'<br>')

    else:
        # Page breaks are treated just like newlines.
        # Soft hyphens followed by newlines vanish.
        # Letter-hyphen-newline becomes letter-hyphen, to preserve real
        # hyphenation.
        # Any other newline becomes a space.
        html = flavor_text.replace(u'\f',       u'\n') \
                          .replace(u'\u00ad\n', u'') \
                          .replace(u'\u00ad',   u'') \
                          .replace(u' -\n',     u' - ') \
                          .replace(u'-\n',      u'-') \
                          .replace(u'\n',       u' ')

    return h.literal(html)

## Collapsing

def collapse_flavor_text_key(literal=True):
    """A wrapper around `render_flavor_text`. Returns a function to be used
    as a key for `collapse_versions`, or any other function which takes a key.
    """
    def key(text):
        return render_flavor_text(text.flavor_text, literal=literal)
    return key

def group_by_generation(things):
    """A wrapper around itertools.groupby which groups by generation."""
    things = iter(things)
    try:
        a_thing = things.next()
    except StopIteration:
        return ()
    key = get_generation_key(a_thing)
    return groupby(chain([a_thing], things), key)

def get_generation_key(sample_object):
    """Given an object, return a function which retrieves the generation.

    Tries x.generation, x.version_group.generation, and x.version.generation.
    """
    if hasattr(sample_object, 'generation'):
        return attrgetter('generation')
    elif hasattr(sample_object, 'version_group'):
        return (lambda x: x.version_group.generation)
    elif hasattr(sample_object, 'version'):
        return (lambda x: x.version.generation)
    raise AttributeError

def collapse_versions(things, key):
    """Collapse adjacent equal objects and remember their versions.

    Yields tuples of ([versions], key(x)). Uses itertools.groupby internally.
    """
    things = iter(things)
    # let the StopIteration bubble up
    a_thing = things.next()

    if hasattr(a_thing, 'version'):
        def get_versions(things):
            return [x.version for x in things]
    elif hasattr(a_thing, 'version_group'):
        def get_versions(things):
            return sum((x.version_group.versions for x in things), [])

    for collapsed_key, group in groupby(chain([a_thing], things), key):
        yield get_versions(group), collapsed_key

### Images and links

def filename_from_name(name):
    """Shorten the name of a whatever to something suitable as a filename.

    e.g. Water's Edge -> waters-edge
    """
    name = unicode(name)
    name = name.lower()

    # TMs and HMs share sprites
    if re.match(u'^[th]m\d{2}$', name):
        if name[0:2] == u'tm':
            return u'tm-normal'
        else:
            return u'hm-normal'

    # As do data cards
    if re.match(u'^data card \d+$', name):
        return u'data-card'

    name = re.sub(u'[ _]+', u'-', name)
    name = re.sub(u'[\'.]', u'', name)
    return name

def pokedex_img(src, **attr):
    return h.HTML.img(src=url(controller='dex', action='media', path=src), **attr)


# XXX Should these be able to promote to db objects, rather than demoting to
# strings and integers?  If so, how to do that without requiring db access
# from here?
def generation_icon(generation, _=_):
    """Returns a generation icon, given a generation number."""
    # Convert generation to int if necessary
    if not isinstance(generation, int):
        generation = generation.id

    return pokedex_img('versions/generation-%d.png' % generation,
                       alt=_(u"Generation %d") % generation,
                       title=_(u"Generation %d") % generation)

def version_icons(*versions, **kwargs):
    """Returns some version icons, given a list of version names.

    Keyword arguments:
    `dex_translate`: translation function for version names
    """
    # python's argument_list syntax is kind of limited here
    dex_translate = kwargs.get('dex_translate', _)
    version_icons = u''
    comma = chain([u''], repeat(u', '))
    for version in versions:
        # Convert version to string if necessary
        if not isinstance(version, basestring):
            version = version.name

        version_filename = filename_from_name(version)
        version_icons += pokedex_img(u'versions/%s.png' % version_filename,
                                     alt=comma.next() + dex_translate(version),
                                     title=dex_translate(version))

    return version_icons


def pokemon_sprite(pokemon, prefix='heartgold-soulsilver', **attr):
    """Returns an <img> tag for a Pokémon sprite."""

    # Kinda gross, but it's entirely valid to pass None as a form
    form = attr.pop('form', pokemon.forme_name)

    if 'animated' in prefix:
        ext = 'gif'
    else:
        ext = 'png'

    if form:
        # Use the overridden form name
        alt_text = "{0} {1}".format(form.title(), pokemon.name)
    else:
        # Use the Pokémon's default full-name
        alt_text = pokemon.full_name

    attr.setdefault('alt', alt_text)
    attr.setdefault('title', alt_text)

    if form:
        filename = '%d-%s.%s' % (pokemon.national_id,
                                 filename_from_name(form), ext)
    else:
        filename = '%d.%s' % (pokemon.national_id, ext)

    return pokedex_img("%s/%s" % (prefix, filename), **attr)

def pokemon_link(pokemon, content=None, to_flavor=False, **attr):
    """Returns a link to a Pokémon page.

    `pokemon`
        A name or a Pokémon object.

    `content`
        Link text (or image, or whatever).

    `form`
        An alternate form to link to.  If the form is only a sprite, the link
        will be to the flavor page.

    `to_flavor`
        If True, the link will always be to the flavor page, regardless of
        form.
    """

    # Kinda gross, but it's entirely valid to pass None as a form
    form = attr.pop('form', pokemon.forme_name)
    if form == pokemon.forme_name and not pokemon.forme_base_pokemon_id:
        # Don't use default form's name as part of the link
        form = None

    # Content defaults to the name of the Pokémon
    if not content:
        if form:
            content = "%s %s" % (form.title(), pokemon.name)
        else:
            content = pokemon.name

    url_kwargs = {}
    if form:
        # Don't want a ?form=None, so just only pass a form at all if there's
        # one to pass
        url_kwargs['form'] = form

    action = 'pokemon'
    if form and pokemon.normal_form.form_group \
            and not pokemon.normal_form.formes:
        # If a Pokémon does not have real (different species) forms, e.g.
        # Unown and its letters, then a form link only makes sense if it's to a
        # flavor page.
        action = 'pokemon_flavor'
    elif to_flavor:
        action = 'pokemon_flavor'

    return h.HTML.a(
        content,
        href=url(controller='dex', action=action,
                       name=pokemon.name.lower(), **url_kwargs),
        **attr
        )


def damage_class_icon(damage_class, dex_translate=_, _=_):
    return pokedex_img(
        "chrome/damage-classes/%s.png" % damage_class.name.lower(),
        alt=damage_class.name,
        title=_("%s: %s") % (
                dex_translate(damage_class.name),
                dex_translate(damage_class.description),
            )
    )


def type_icon(type):
    if not isinstance(type, basestring):
        type = type.name
    return pokedex_img('chrome/types/%s.png' % type, alt=type, title=type)

def type_link(type):
    return h.HTML.a(
        type_icon(type),
        href=url(controller='dex', action='types', name=type.name.lower()),
    )


def item_link(item, include_icon=True, dex_translate=_):
    """Returns a link to the requested item."""

    item_name = dex_translate(item.name)

    if include_icon:
        if item.pocket.identifier == u'machines':
            machines = item.machines
            prefix = u'hm' if machines[-1].is_hm else u'tm'
            filename = prefix + u'-' + machines[-1].move.type.name.lower()
        else:
            filename = filename_from_name(item_name)

        label = pokedex_img("items/%s.png" % filename,
            alt=item_name, title=item_name) + ' ' + item_name

    else:
        label = item_name

    return h.HTML.a(label,
        href=url(controller='dex', action='items',
                 pocket=item.pocket.identifier, name=item_name.lower()),
    )


### Labels

# Type efficacy, from percents to Unicode fractions
type_efficacy_label = {
    0: '0',
    25: u'¼',
    50: u'½',
    100: '1',
    200: '2',
    400: '4',
}

# Gender rates, translated from -1..8 to useful text
gender_rate_label = {
    -1: _(u'genderless'),
    0: _(u'always male'),
    1: _(u'⅞ male, ⅛ female'),
    2: _(u'¾ male, ¼ female'),
    3: _(u'⅝ male, ⅜ female'),
    4: _(u'½ male, ½ female'),
    5: _(u'⅜ male, ⅝ female'),
    6: _(u'¼ male, ¾ female'),
    7: _(u'⅛ male, ⅞ female'),
    8: _(u'always female'),
}

def article(noun, _=_):
    """Returns 'a' or 'an', as appropriate."""
    if noun[0].lower() in u'aeiou':
        return _(u'an')
    return _(u'a')

def evolution_description(evolution, _=_, dex_translate=_):
    """Crafts a human-readable description from a `pokemon_evolution` row
    object.
    """
    chunks = []

    # Trigger
    if evolution.trigger.identifier == u'level_up':
        chunks.append(_(u'Level up'))
    elif evolution.trigger.identifier == u'trade':
        chunks.append(_(u'Trade'))
    elif evolution.trigger.identifier == u'use_item':
        item_name = dex_translate(evolution.trigger_item.name)
        chunks.append(_(u"Use {article} {item}").format(
            article=article(item_name, _=_),
            item=dex_translate(item_name)))
    elif evolution.trigger.identifier == u'shed':
        chunks.append(
            _(u"Evolve {from_pokemon} ({to_pokemon} will consume "
            u"a Poké Ball and appear in a free party slot)").format(
                from_pokemon=dex_translate(evolution.from_pokemon.full_name),
                to_pokemon=dex_translate(evolution.to_pokemon.full_name)))
    else:
        chunks.append(_(u'Do something'))

    # Conditions
    if evolution.gender:
        chunks.append(_(u"{0}s only").format(evolution.gender))
    if evolution.time_of_day:
        chunks.append(_(u"during the {0}").format(evolution.time_of_day))

    if evolution.minimum_level:
        chunks.append(_(u"starting at level {0}").format(evolution.minimum_level))
    if evolution.location_id:
        chunks.append(_(u"around {0}").format(evolution.location.name))
    if evolution.held_item_id:
        chunks.append(_(u"while holding {article} {item}").format(
            article=article(evolution.held_item.name),
            item=evolution.held_item.name))
    if evolution.known_move_id:
        chunks.append(_(u"knowing {0}").format(evolution.known_move.name))
    if evolution.minimum_happiness:
        chunks.append(_(u"with at least {0} happiness").format(
            evolution.minimum_happiness))
    if evolution.minimum_beauty:
        chunks.append(_(u"with at least {0} beauty").format(
            evolution.minimum_beauty))

    if evolution.relative_physical_stats is not None:
        if evolution.relative_physical_stats < 0:
            op = _(u'<')
        elif evolution.relative_physical_stats > 0:
            op = _(u'>')
        else:
            op = _(u'=')

        chunks.append(_(u"when Attack {0} Defense").format(op))

    return u', '.join(chunks)


### Formatting

# Attempts at reasonable defaults for trainer size, based on the average
# American
trainer_height = 17.8  # dm
trainer_weight = 780   # hg

def format_height_metric(height):
    """Formats a height in decimeters as M m."""
    return "%.1f m" % (height / 10)

def format_height_imperial(height):
    """Formats a height in decimeters as F'I"."""
    return "%d'%.1f\"" % (
        height * 0.32808399,
        (height * 0.32808399 % 1) * 12,
    )

def format_weight_metric(weight):
    """Formats a weight in hectograms as K kg."""
    return "%.1f kg" % (weight / 10)

def format_weight_imperial(weight):
    """Formats a weight in hectograms as L lb."""
    return "%.1f lb" % (weight / 10 * 2.20462262)


### General data munging

def scale_sizes(size_dict, dimensions=1):
    """Normalizes a list of sizes so the largest is 1.0.

    Use `dimensions` if the sizes are non-linear, i.e. 2 for scaling area.
    """

    # x -> (x/max)^(1/dimensions)
    max_size = float(max(size_dict.values()))
    scaled_sizes = dict()
    for k, v in size_dict.items():
        scaled_sizes[k] = math.pow(v / max_size, 1.0 / dimensions)
    return scaled_sizes


def apply_pokemon_template(template, pokemon, dex_translate=_, _=_):
    u"""`template` should be a string.Template object.

    Uses safe_substitute to inject some fields from the Pokémon into the
    template.

    This cheerfully returns a literal, so be sure to escape the original format
    string BEFORE passing it to Template!
    """

    d = dict(
        icon=pokemon_sprite(pokemon, prefix=u'icons'),
        id=pokemon.national_id,
        name=pokemon.full_name,

        height=format_height_imperial(pokemon.height),
        height_ft=format_height_imperial(pokemon.height),
        height_m=format_height_metric(pokemon.height),
        weight=format_weight_imperial(pokemon.weight),
        weight_lb=format_weight_imperial(pokemon.weight),
        weight_kg=format_weight_metric(pokemon.weight),

        gender=_(gender_rate_label[pokemon.gender_rate]),
        species=dex_translate(pokemon.species),
        base_experience=pokemon.base_experience,
        capture_rate=pokemon.capture_rate,
        base_happiness=pokemon.base_happiness,
    )

    # "Lazy" loading, to avoid hitting other tables if unnecessary.  This is
    # very chumpy and doesn't distinguish between literal text and fields (e.g.
    # '$type' vs 'type'), but that's very unlikely to happen, and it's not a
    # big deal if it does
    if 'type' in template.template:
        types = pokemon.types
        d['type'] = u'/'.join(dex_translate(type_.name) for type_ in types)
        d['type1'] = dex_translate(types[0].name)
        d['type2'] = dex_translate(types[1].name) if len(types) > 1 else u''

    if 'egg_group' in template.template:
        egg_groups = pokemon.egg_groups
        d['egg_group'] = u'/'.join(dex_translate(group.name) for group in egg_groups)
        d['egg_group1'] = dex_translate(egg_groups[0].name)
        d['egg_group2'] = dex_translate(egg_groups[1].name) if len(egg_groups) > 1 else u''

    if 'ability' in template.template:
        abilities = pokemon.abilities
        d['ability'] = u'/'.join(dex_translate(ability.name) for ability in abilities)
        d['ability1'] = dex_translate(abilities[0].name)
        d['ability2'] = dex_translate(abilities[1].name) if len(abilities) > 1 else u''

    if 'color' in template.template:
        d['color'] = dex_translate(pokemon.color)

    if 'habitat' in template.template:
        d['habitat'] = dex_translate(pokemon.habitat)

    if 'shape' in template.template:
        if pokemon.shape:
            d['shape'] = dex_translate(pokemon.shape.name)
        else:
            d['shape'] = ''

    if 'hatch_counter' in template.template:
        d['hatch_counter'] = pokemon.hatch_counter

    if 'steps_to_hatch' in template.template:
        d['steps_to_hatch'] = (pokemon.hatch_counter + 1) * 255

    if 'stat' in template.template or \
       'hp' in template.template or \
       'attack' in template.template or \
       'defense' in template.template or \
       'speed' in template.template or \
       'effort' in template.template:
        d['effort'] = u', '.join("{0} {1}".format(_.effort, _.stat.name)
                                 for _ in pokemon.stats if _.effort)

        d['stats'] = u'/'.join(str(_.base_stat) for _ in pokemon.stats)

        for pokemon_stat in pokemon.stats:
            key = pokemon_stat.stat.name.lower().replace(' ', '_')
            d[key] = pokemon_stat.base_stat

    return h.literal(template.safe_substitute(d))

def apply_move_template(template, move):
    u"""`template` should be a string.Template object.

    Uses safe_substitute to inject some fields from the move into the template,
    just like the above.
    """

    d = dict(
        id=move.id,
        name=move.name,
        type=move.type.name,
        damage_class=move.damage_class.name,
        pp=move.pp,
        power=move.power,
        accuracy=move.accuracy,

        priority=move.move_effect.priority,
        effect_chance=move.effect_chance,
        effect=move.move_effect.short_effect,
    )

    return h.literal(template.safe_substitute(d))
