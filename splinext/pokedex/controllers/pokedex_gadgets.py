# encoding: utf8
from __future__ import absolute_import, division

from collections import defaultdict, namedtuple
import colorsys
import logging

import wtforms.validators
from wtforms import Form, ValidationError, fields
from wtforms.ext.sqlalchemy.fields import QuerySelectField

import pokedex.db
import pokedex.db.tables as tables
import pokedex.formulae
from pylons import config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from sqlalchemy import and_, or_, not_
from sqlalchemy.orm import aliased, contains_eager, eagerload, eagerload_all, join
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func

from spline import model
from spline.model import meta
from spline.lib import helpers as h
from spline.lib.base import BaseController, render
from spline.lib.forms import DuplicateField, QueryTextField

from splinext.pokedex import helpers as pokedex_helpers
import splinext.pokedex.db as db
from splinext.pokedex.forms import PokedexLookupField

log = logging.getLogger(__name__)


### Capture rate ("Pokéball performance") stuff
class OptionalLevelField(fields.IntegerField):
    """IntegerField subclass that requires either a number from 1 to 100, or
    nothing.

    Also overrides the usual IntegerField logic to default to an empty field.
    Defaulting to 0 means the field can't be submitted from scratch.
    """
    def __init__(self, label=u'', validators=[], **kwargs):
        validators.extend([
            wtforms.validators.NumberRange(min=1, max=100),
            wtforms.validators.Optional(),
        ])
        super(OptionalLevelField, self).__init__(label, validators, **kwargs)

    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        else:
            return unicode(self.data or u'')

class CaptureRateForm(Form):
    pokemon = PokedexLookupField(u'Wild Pokémon', valid_type='pokemon')
    current_hp = fields.IntegerField(u'% HP left', [wtforms.validators.NumberRange(min=1, max=100)],
                                     default=100)
    status_ailment = fields.SelectField('Status ailment',
        choices=[
            ('', u'—'),
            ('PAR', 'PAR'),
            ('SLP', 'SLP'),
            ('PSN', 'PSN'),
            ('BRN', 'BRN'),
            ('FRZ', 'FRZ'),
        ],
        default=u'',
    )

    ### Extras
    level = OptionalLevelField(u'Wild Pokémon\'s level', default=u'')
    your_level = OptionalLevelField(u'Your Pokémon\'s level', default=u'')
    terrain = fields.SelectField(u'Terrain',
        choices=[
            ('land',    u'On land'),
            ('fishing', u'Fishing'),
            ('surfing', u'Surfing'),
        ],
        default='land',
    )
    twitterpating = fields.BooleanField(u'Wild and your Pokémon are opposite genders AND the same species')
    caught_before = fields.BooleanField(u'Wild Pokémon is in your Pokédex')
    is_dark = fields.BooleanField(u'Nighttime or walking in a cave')

    # ...
    is_pokemon_master = fields.BooleanField(u'Holding Up+B')


def expected_attempts(catch_chance):
    u"""Given the chance to catch a Pokémon, returns approximately the number
    of attempts required to succeed.
    """
    # Hey, this one's easy!
    return 1 / catch_chance

def expected_attempts_oh_no(partitions):
    """Horrible version of the above, used for Quick and Timer Balls.

    Now there are a few finite partitions at the beginning.  `partitions` looks
    like:

        [
            (catch_chance, number_of_turns),
            (catch_chance, number_of_turns),
            ...
        ]

    For example, a Timer Ball might look like [(0.25, 10), (0.5, 10), ...].

    The final `number_of_turns` must be None to indicate that the final
    `catch_chance` lasts indefinitely.
    """

    turn = 0        # current turn
    p_got_here = 1  # probability that we HAVE NOT caught the Pokémon yet
    expected_attempts = 0

    # To keep this "simple", basically just count forwards each turn until the
    # partitions are exhausted
    for catch_chance, number_of_turns in partitions:
        if number_of_turns is None:
            # The rest of infinity is covered by the usual expected-value formula with
            # the final catch chance, but factoring in the probability that the Pokémon
            # is still uncaught, and that turns have already passed
            expected_attempts += p_got_here * (1 / catch_chance + turn)

            # Done!
            break

        for _ in range(number_of_turns):
            # Add the contribution of possibly catching it this turn.  That's
            # the chance that we'll catch it this turn, times the turn number
            # -- times the chance that we made it this long without catching
            turn += 1
            expected_attempts += p_got_here * catch_chance * turn

            # Probability that we get to the next turn is decreased by the
            # probability that we didn't catch it this turn
            p_got_here *= 1 - catch_chance

    return expected_attempts

CaptureChance = namedtuple('CaptureChance', ['condition', 'is_active', 'chances'])


class StatCalculatorForm(Form):
    pokemon = PokedexLookupField(u'Pokémon', valid_type='pokemon')
    level = fields.IntegerField(u'Level', [wtforms.validators.NumberRange(min=1, max=100)],
                                     default=100)
    nature = QuerySelectField('Nature',
        query_factory=lambda: db.pokedex_session.query(tables.Nature).order_by(tables.Nature.name),
        get_pk=lambda _: _.name.lower(),
        get_label=lambda _: _.name,
        allow_blank=True,
    )

def stat_graph_chunk_color(gene):
    """Returns a #rrggbb color, given a gene.  Used for the pretty graph."""
    hue = gene / 31
    r, g, b = colorsys.hls_to_rgb(hue, 0.75, 0.75)
    return "#%02x%02x%02x" % (r * 256, g * 256, b * 256)


class PokedexGadgetsController(BaseController):

    def capture_rate(self):
        """Find a page in the Pokédex given a name.

        Also performs fuzzy search.
        """

        c.javascripts.append(('pokedex', 'pokedex-gadgets'))
        c.form = CaptureRateForm(request.params)

        valid_form = False
        if request.params:
            valid_form = c.form.validate()

        if valid_form:
            c.results = {}

            c.pokemon = c.form.pokemon.data
            level = c.form.level.data

            # Overrule a 'yes' for opposite genders if this Pokémon has no
            # gender
            if c.pokemon.gender_rate == -1:
                c.form.twitterpating.data = False

            percent_hp = c.form.current_hp.data / 100

            status_bonus = 10
            if c.form.status_ailment.data in ('PAR', 'BRN', 'PSN'):
                status_bonus = 15
            elif c.form.status_ailment.data in ('SLP', 'FRZ'):
                status_bonus = 20

            # Little wrapper around capture_chance...
            def capture_chance(ball_bonus=10, **kwargs):
                return pokedex.formulae.capture_chance(
                    percent_hp=percent_hp,
                    capture_rate=c.pokemon.capture_rate,
                    status_bonus=status_bonus,
                    ball_bonus=ball_bonus,
                    **kwargs
                )

            ### Do some math!
            # c.results is a dict of ball_name => chance_tuples.
            # (It would be great, but way inconvenient, to use item objects.)
            # chance_tuples is a list of (condition, is_active, chances):
            # - condition: a string describing some mutually-exclusive
            #   condition the ball responds to
            # - is_active: a boolean indicating whether this condition is
            #   currently met
            # - chances: an iterable of chances as returned from capture_chance

            # This is a teeny shortcut.
            only = lambda _: [CaptureChance( '', True, _ )]

            normal_chance = capture_chance()

            # Gen I
            c.results[u'Poké Ball']   = only(normal_chance)
            c.results[u'Great Ball']  = only(capture_chance(15))
            c.results[u'Ultra Ball']  = only(capture_chance(20))
            c.results[u'Master Ball'] = only((1.0, 0, 0, 0, 0))
            c.results[u'Safari Ball'] = only(capture_chance(15))

            # Gen II
            # NOTE: All the Gen II balls, as of HG/SS, modify CAPTURE RATE and
            # leave the ball bonus alone.
            relative_level = None
            if c.form.level.data and c.form.your_level.data:
                # -1 because equality counts as bucket zero
                relative_level = (c.form.your_level.data - 1) \
                               // c.form.level.data

            # Heavy Ball partitions by 102.4 kg.  Weights are stored as...
            # hectograms.  So.
            weight_class = int((c.pokemon.weight - 1) / 1024)

            # Ugh.
            is_moony = c.pokemon.name in (
                u'Nidoran♀', u'Nidorina', u'Nidoqueen',
                u'Nidoran♂', u'Nidorino', u'Nidoking',
                u'Clefairy', u'Clefable', u'Jigglypuff', u'Wigglytuff',
                u'Skitty', u'Delcatty',
            )

            is_skittish = c.pokemon.stat('Speed').base_stat >= 100

            c.results[u'Level Ball']  = [
                CaptureChance(u'Your level ≤ target level',
                    relative_level == 0,
                    normal_chance),
                CaptureChance(u'Target level < your level ≤ 2 * target level',
                    relative_level == 1,
                    capture_chance(capture_bonus=20)),
                CaptureChance(u'2 * target level < your level ≤ 4 * target level',
                    relative_level in (2, 3),
                    capture_chance(capture_bonus=40)),
                CaptureChance(u'4 * target level < your level',
                    relative_level >= 4,
                    capture_chance(capture_bonus=80)),
            ]
            c.results[u'Lure Ball']   = [
                CaptureChance(u'Hooked on a rod',
                    c.form.terrain.data == 'fishing',
                    capture_chance(capture_bonus=30)),
                CaptureChance(u'Otherwise',
                    c.form.terrain.data != 'fishing',
                    normal_chance),
            ]
            c.results[u'Moon Ball']   = [
                CaptureChance(u'Target evolves with a Moon Stone',
                    is_moony,
                    capture_chance(capture_bonus=40)),
                CaptureChance(u'Otherwise',
                    not is_moony,
                    normal_chance),
            ]
            c.results[u'Friend Ball'] = only(normal_chance)
            c.results[u'Love Ball']   = [
                CaptureChance(u'Target is opposite gender of your Pokémon and the same species',
                    c.form.twitterpating.data,
                    capture_chance(capture_bonus=80)),
                CaptureChance(u'Otherwise',
                    not c.form.twitterpating.data,
                    normal_chance),
            ]
            c.results[u'Heavy Ball']   = [
                CaptureChance(u'Target weight ≤ 102.4 kg',
                    weight_class == 0,
                    capture_chance(capture_modifier=-20)),
                CaptureChance(u'102.4 kg < target weight ≤ 204.8 kg',
                    weight_class == 1,
                    capture_chance(capture_modifier=-20)),  # sic; game bug
                CaptureChance(u'204.8 kg < target weight ≤ 307.2 kg',
                    weight_class == 2,
                    capture_chance(capture_modifier=20)),
                CaptureChance(u'307.2 kg < target weight ≤ 409.6 kg',
                    weight_class == 3,
                    capture_chance(capture_modifier=30)),
                CaptureChance(u'409.6 kg < target weight',
                    weight_class >= 4,
                    capture_chance(capture_modifier=40)),
            ]
            c.results[u'Fast Ball']   = [
                CaptureChance(u'Target has base Speed of 100 or more',
                    is_skittish,
                    capture_chance(capture_bonus=40)),
                CaptureChance(u'Otherwise',
                    not is_skittish,
                    normal_chance),
            ]
            c.results[u'Sport Ball']  = only(capture_chance(15))

            # Gen III
            is_nettable = any(_.name in ('bug', 'water')
                              for _ in c.pokemon.types)

            c.results[u'Premier Ball'] = only(normal_chance)
            c.results[u'Repeat Ball'] = [
                CaptureChance(u'Target is already in Pokédex',
                    c.form.caught_before.data,
                    capture_chance(30)),
                CaptureChance(u'Otherwise',
                    not c.form.caught_before.data,
                    normal_chance),
            ]
            # Timer and Nest Balls use a gradient instead of partitions!  Keep
            # the same desc but just inject the right bonus if there's enough
            # to get the bonus correct.  Otherwise, assume the best case
            c.results[u'Timer Ball']  = [
                CaptureChance(u'Better in later turns, caps at turn 30',
                    True,
                    capture_chance(40)),
            ]
            if c.form.level.data:
                c.results[u'Nest Ball']   = [
                    CaptureChance(u'Better against lower-level targets, worst at level 30+',
                        True,
                        capture_chance(max(10, 40 - c.form.level.data)))
                ]
            else:
                c.results[u'Nest Ball']   = [
                    CaptureChance(u'Better against lower-level targets, worst at level 30+',
                        False,
                        capture_chance(40)),
                ]
            c.results[u'Net Ball']   = [
                CaptureChance(u'Target is Water or Bug',
                    is_nettable,
                    capture_chance(30)),
                CaptureChance(u'Otherwise',
                    not is_nettable,
                    normal_chance),
            ]
            c.results[u'Dive Ball']   = [
                CaptureChance(u'Currently fishing or surfing',
                    c.form.terrain.data in ('fishing', 'surfing'),
                    capture_chance(35)),
                CaptureChance(u'Otherwise',
                    c.form.terrain.data == 'land',
                    normal_chance),
            ]
            c.results[u'Luxury Ball']  = only(normal_chance)

            # Gen IV
            c.results[u'Heal Ball']    = only(normal_chance)
            c.results[u'Quick Ball']  = [
                CaptureChance(u'First turn',
                    True,
                    capture_chance(40)),
                CaptureChance(u'Otherwise',
                    True,
                    normal_chance),
            ]
            c.results[u'Dusk Ball']    = [
                CaptureChance(u'During the night and while walking in caves',
                    c.form.is_dark.data,
                    capture_chance(35)),
                CaptureChance(u'Otherwise',
                    not c.form.is_dark.data,
                    normal_chance),
            ]
            c.results[u'Cherish Ball'] = only(normal_chance)
            c.results[u'Park Ball']    = only(capture_chance(2550))


            # Template needs to know how to find expected number of attempts
            c.capture_chance = capture_chance
            c.expected_attempts = expected_attempts
            c.expected_attempts_oh_no = expected_attempts_oh_no

            # Template also needs real item objects to create links
            pokeball_query = db.pokedex_session.query(tables.Item) \
                .join(tables.ItemCategory, tables.ItemPocket) \
                .filter(tables.ItemPocket.identifier == 'pokeballs')
            c.pokeballs = dict(
                (item.name, item) for item in pokeball_query
            )

        else:
            c.results = None

        return render('/pokedex/gadgets/capture_rate.mako')

    NUM_COMPARED_POKEMON = 8
    def _shorten_compare_pokemon(self, pokemon):
        u"""Returns a query dict for the given list of Pokémon to compare,
        shortened as much as possible.

        This is a bit naughty and examines the context for part of the query.
        """
        params = dict()

        # Drop blank Pokémon off the end of the list
        while pokemon and not pokemon[-1]:
            del pokemon[-1]
        params['pokemon'] = pokemon

        # Only include version group if it's not the default
        if c.version_group != c.version_groups[-1]:
            params['version_group'] = c.version_group.id

        return params

    def compare_pokemon(self):
        u"""Pokémon comparison.  Takes up to eight Pokémon and shows a page
        that lists their stats, moves, etc. side-by-side.
        """
        # Note that this gadget doesn't use wtforms at all, since there're only
        # two fields and the major one is handled very specially.

        c.did_anything = False

        # Form controls use version group
        c.version_groups = db.pokedex_session.query(tables.VersionGroup) \
            .order_by(tables.VersionGroup.id.asc()) \
            .options(eagerload('versions')) \
            .all()
        # Grab the version to use for moves, defaulting to the most current
        try:
            c.version_group = db.pokedex_session.query(tables.VersionGroup) \
                .get(request.params['version_group'])
        except (KeyError, NoResultFound):
            c.version_group = c.version_groups[-1]

        # Some manual URL shortening, if necessary...
        if request.params.get('shorten', False):
            short_params = self._shorten_compare_pokemon(
                request.params.getall('pokemon'))
            redirect(url.current(**short_params))

        FoundPokemon = namedtuple('FoundPokemon',
            ['pokemon', 'suggestions', 'input'])

        # The Pokémon themselves go into c.pokemon.  This list should always
        # have eight FoundPokemon elements
        c.found_pokemon = [None] * self.NUM_COMPARED_POKEMON

        # Run through the list, ensuring at least 8 Pokémon are entered
        pokemon_input = request.params.getall('pokemon') \
            + [u''] * self.NUM_COMPARED_POKEMON
        for i in range(self.NUM_COMPARED_POKEMON):
            raw_pokemon = pokemon_input[i].strip()
            if not raw_pokemon:
                # Use a junk placeholder tuple
                c.found_pokemon[i] = FoundPokemon(
                    pokemon=None, suggestions=None, input=u'')
                continue

            results = db.pokedex_lookup.lookup(
                raw_pokemon, valid_types=['pokemon'])

            # Two separate things to do here.
            # 1: Use the first result as the actual Pokémon
            pokemon = None
            if results:
                pokemon = results[0].object
                c.did_anything = True

            # 2: Use the other results as suggestions.  Doing this informs the
            # template that this was a multi-match
            suggestions = None
            if len(results) == 1 and results[0].exact:
                # Don't do anything for exact single matches
                pass
            else:
                # OK, extract options.  But no more than, say, three.
                # Remember both the language and the Pokémon, in the case of
                # foreign matches
                suggestions = [
                    (_.name, _.iso3166)
                    for _ in results[1:4]
                ]

            # Construct a tuple and slap that bitch in there
            c.found_pokemon[i] = FoundPokemon(pokemon, suggestions, raw_pokemon)

        # There are a lot of links to similar incarnations of this page.
        # Provide a closure for constructing the links easily
        def create_comparison_link(target, replace_with=None, move=0):
            u"""Manipulates the list of Pokémon before creating a link.

            `target` is the FoundPokemon to be operated upon.  It can be either
            replaced with a new string or moved left/right.
            """

            new_found_pokemon = c.found_pokemon[:]

            # Do the swapping first
            if move:
                idx1 = new_found_pokemon.index(target)
                idx2 = (idx1 + move) % len(new_found_pokemon)
                new_found_pokemon[idx1], new_found_pokemon[idx2] = \
                    new_found_pokemon[idx2], new_found_pokemon[idx1]

            # Construct a new query
            query_pokemon = []
            for found_pokemon in new_found_pokemon:
                if found_pokemon is None:
                    # Empty slot
                    query_pokemon.append(u'')
                elif found_pokemon is target and replace_with != None:
                    # Substitute a new Pokémon
                    query_pokemon.append(replace_with)
                else:
                    # Keep what we have now
                    query_pokemon.append(found_pokemon.input)

            short_params = self._shorten_compare_pokemon(query_pokemon)
            return url.current(**short_params)
        c.create_comparison_link = create_comparison_link

        # Setup only done if the page is actually showing
        if c.did_anything:
            c.stats = db.pokedex_session.query(tables.Stat).all()

            # Relative numbers -- breeding and stats
            # Construct a nested dictionary of label => pokemon => (value, pct)
            # `pct` is percentage from the minimum to maximum value
            c.relatives = dict()
            # Use the label from the page as the key, because why not
            relative_things = [
                (u'Base EXP',       lambda pokemon: pokemon.base_experience),
                (u'Base happiness', lambda pokemon: pokemon.base_happiness),
                (u'Capture rate',   lambda pokemon: pokemon.capture_rate),
            ]
            def relative_stat_factory(local_stat):
                return lambda pokemon: pokemon.stat(local_stat).base_stat
            for stat in c.stats:
                relative_things.append((stat.name, relative_stat_factory(stat)))

            relative_things.append((
                u'Base stat total',
                lambda pokemon: sum(pokemon.stat(stat).base_stat for stat in c.stats)
            ))

            # Assemble the data
            unique_pokemon = set(fp.pokemon
                for fp in c.found_pokemon
                if fp.pokemon
            )
            for label, getter in relative_things:
                c.relatives[label] = dict()

                # Get all the values at once; need to get min and max to figure
                # out relative position
                numbers = dict()
                for pokemon in unique_pokemon:
                    numbers[pokemon] = getter(pokemon)

                min_number = min(numbers.values())
                max_number = max(numbers.values())

                # Rig a little function to figure out the percentage, making
                # sure to avoid division by zero
                if min_number == max_number:
                    calc = lambda n: 1.0
                else:
                    calc = lambda n: 1.0 * (n - min_number) \
                                         / (max_number - min_number)

                for pokemon in unique_pokemon:
                    c.relatives[label][pokemon] \
                        = numbers[pokemon], calc(numbers[pokemon])

            ### Relative sizes
            raw_heights = dict(enumerate(
                fp.pokemon.height if fp and fp.pokemon else 0
                for fp in c.found_pokemon
            ))
            raw_heights['trainer'] = pokedex_helpers.trainer_height
            c.heights = pokedex_helpers.scale_sizes(raw_heights)

            raw_weights = dict(enumerate(
                fp.pokemon.weight if fp and fp.pokemon else 0
                for fp in c.found_pokemon
            ))
            raw_weights['trainer'] = pokedex_helpers.trainer_weight
            c.weights = pokedex_helpers.scale_sizes(raw_weights, dimensions=2)

            ### Moves
            # Constructs a table like the pokemon-moves table, except each row
            # is a move and it indicates which Pokémon learn it.  Still broken
            # up by method.
            # So, need a dict of method => move => pokemons.
            c.moves = defaultdict(lambda: defaultdict(set))
            # And similarly for level moves, level => pokemon => moves
            c.level_moves = defaultdict(lambda: defaultdict(list))
            q = db.pokedex_session.query(tables.PokemonMove) \
                .filter(tables.PokemonMove.version_group == c.version_group) \
                .filter(tables.PokemonMove.pokemon_id.in_(
                    _.id for _ in unique_pokemon)) \
                .options(
                    eagerload('move'),
                    eagerload('method'),
                )
            for pokemon_move in q:
                c.moves[pokemon_move.method][pokemon_move.move].add(
                    pokemon_move.pokemon)

                if pokemon_move.level:
                    c.level_moves[pokemon_move.level] \
                        [pokemon_move.pokemon].append(pokemon_move.move)

        return render('/pokedex/gadgets/compare_pokemon.mako')

    def stat_calculator(self):
        """Calculates, well, stats."""
        # XXX features this needs:
        # - short URLs
        # - more better error checking
        # - accept "characteristics"
        # - accept and print out hidden power
        # - accept..  anything else hint at IVs?
        # - back-compat URL
        # - also calculate stats or effort
        # - multiple levels
        # - track effort gained on the fly (as well as exp for auto level up?)
        #   - UI would need to be different and everything, ugh

        class F(StatCalculatorForm):
            pass

        # Add stat-based fields dynamically
        c.stat_fields = []  # just field names
        c.effort_fields = []
        c.stats = db.pokedex_session.query(tables.Stat) \
            .order_by(tables.Stat.id).all()
        for stat in c.stats:
            field_name = stat.name.lower().replace(u' ', u'_')

            c.stat_fields.append('stat_' + field_name)
            c.effort_fields.append('effort_' + field_name)

            setattr(F, 'stat_' + field_name,
                fields.IntegerField(u'', [wtforms.validators.NumberRange(min=5, max=700)]))

            setattr(F, 'effort_' + field_name,
                fields.IntegerField(u'', [wtforms.validators.NumberRange(min=0, max=255)]))

        ### Parse form and so forth
        c.form = F(request.params)

        c.results = None  # XXX shim
        if not request.GET or not c.form.validate():
            return render('/pokedex/gadgets/stat_calculator.mako')

        # Okay, do some work!
        # Dumb method for now -- XXX change this to do a binary search.
        # Run through every possible value for each stat, see if it matches
        # input, and give the green light if so.
        pokemon = c.form.pokemon.data
        nature = c.form.nature.data
        if nature and nature.is_neutral:
            # Neutral nature is equivalent to none at all
            nature = None
        level = c.form.level.data
        # Start with lists of possibly valid genes and cut down from there
        c.valid_range = {}  # stat => (min, max)
        valid_genes = {}
        for stat, stat_field, effort_field in zip(c.stats, c.stat_fields, c.effort_fields):
            ### Bunch of setup, per stat
            # XXX let me stop typing this, christ
            if stat.name == u'HP':
                func = pokedex.formulae.calculated_hp
            else:
                func = pokedex.formulae.calculated_stat

            base_stat = pokemon.stat(stat).base_stat

            nature_mod = 1.0
            if not nature:
                pass
            elif nature.increased_stat == stat:
                nature_mod = 1.1
            elif nature.decreased_stat == stat:
                nature_mod = 0.9

            stat_in = c.form[stat_field].data
            effort_in = c.form[effort_field].data

            def calculate_stat(gene):
                return int(nature_mod *
                    func(base_stat, level=level, iv=gene, effort=effort_in))

            c.valid_range[stat] = min_stat, max_stat = \
                calculate_stat(0), calculate_stat(31)

            ### Actual work!
            # Quick simple check: if the input is totally outside the valid
            # range, no need to calculate anything
            if not min_stat <= stat_in <= max_stat:
                valid_genes[stat] = {}
                continue

            # Start out with everything being considered valid
            valid_genes[stat] = dict((key, None) for key in range(32))

            # Run through and maybe invalidate each gene
            for gene in valid_genes[stat].keys():
                if calculate_stat(gene) != stat_in:
                    del valid_genes[stat][gene]

        # Turn those results into something more readable.
        # Template still needs valid_genes for drawing the graph
        c.results = {}
        c.valid_genes = valid_genes
        for stat in c.stats:
            # 1, 2, 3, 5 => "1-3, 5"
            # Find consecutive ranges of numbers and turn them into strings.
            # nb: The final dummy iteration with n = None is to more easily add
            # the last range to the parts list
            left_endpoint = None
            parts = []
            elements = valid_genes[stat].keys()
            elements.sort()

            for last_n, n in zip([None] + elements, elements + [None]):
                if (n is None and left_endpoint is not None) or \
                    (last_n is not None and last_n + 1 < n):

                    # End of a subrange; break off what we have
                    parts.append(u"{0}–{1}".format(left_endpoint, last_n))

                if left_endpoint is None or last_n + 1 < n:
                    # Starting a new subrange; remember the new left end
                    left_endpoint = n

            c.results[stat] = u','.join(parts)

        c.stat_graph_chunk_color = stat_graph_chunk_color

        return render('/pokedex/gadgets/stat_calculator.mako')

    def whos_that_pokemon(self):
        u"""A silly game that asks you to identify Pokémon by silhouette, cry,
        et al.
        """
        c.javascripts.append(('pokedex', 'whos-that-pokemon'))

        return render('/pokedex/gadgets/whos_that_pokemon.mako')
