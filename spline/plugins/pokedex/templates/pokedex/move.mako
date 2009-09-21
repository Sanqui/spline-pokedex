<%inherit file="/base.mako"/>
<%namespace name="lib" file="lib.mako"/>

<%def name="title()">${c.move.name} – Move #${c.move.id}</%def>

<div id="dex-header">
    <a href="${url.current(name=c.prev_move.name.lower(), form=None)}" id="dex-header-prev" class="dex-box-link">
        <img src="${h.static_uri('spline', 'icons/control-180.png')}" alt="«">
        ${c.prev_move.id}: ${c.prev_move.name}
    </a>
    <a href="${url.current(name=c.next_move.name.lower(), form=None)}" id="dex-header-next" class="dex-box-link">
        ${c.next_move.id}: ${c.next_move.name}
        <img src="${h.static_uri('spline', 'icons/control.png')}" alt="»">
    </a>
    ${c.move.id}: ${c.move.name}
</div>

<h1>Essentials</h1>

<div id="dex-page-portrait">
    <p id="dex-page-name">${c.move.name}</p>
    <p id="dex-page-types">
        ${h.pokedex.type_link(c.move.type)}
        ${h.pokedex.damage_class_icon(c.move.damage_class)}
    </p>
    <p>${h.pokedex.generation_icon(c.move.generation)}</p>
</div>

<div id="dex-page-beside-portrait">
<h2>Summary</h2>
<p>${h.literal(c.move.short_effect.as_html)}</p>
</div>

<h2>Damage Dealt</h2>
<ul id="dex-page-damage">
    % for type, damage_factor in sorted(c.type_efficacies.items(), \
                                        key=lambda x: x[0].name):
    <li class="dex-damage-dealt-${damage_factor}">
        ${h.pokedex.type_link(type)} ${h.pokedex.type_efficacy_label[damage_factor]}
    </li>
    % endfor
</ul>
</div>

<div class="dex-column-container">
<div class="dex-column">
    <h2>Stats</h2>
    <dl>
        <dt>Power</dt>
        % if c.move.damage_class.name == 'None':
        <dd>n/a</dd>
        % else:
        <dd>${c.move.power}</dd>
        % endif
        <dt>Accuracy</dt>
        <dd>
            ${c.move.accuracy}%
            % if c.move.accuracy != 100 and c.move.damage_class.name != 'None':
            ≈ ${"%.1f" % (c.move.power * c.move.accuracy / 100.0)} power
            % endif
        </dd>
        <dt>PP</dt>
        <dd>${c.move.pp}, up to ${c.move.pp * 8/5} with <a href="${url(controller='dex', action='items', name='pp up')}">PP Up</a></dd>
        <dt>Target</dt>
        <dd><abbr title="${c.move.target.description}">${c.move.target.name}</abbr></dd>
        <dt>Effect chance</dt>
        <dd>${c.move.effect_chance or 'n/a'}</dd>
        <dt>Priority</dt>
        % if c.move.priority > 0:
        <dd><span class="dex-priority-fast">${c.move.priority}</span> (fast)</dd>
        % elif c.move.priority < 0:
        <dd><span class="dex-priority-slow">${c.move.priority}</span> (slow)</dd>
        % else:
        <dd>${c.move.priority} (normal)</dd>
        % endif
    </dl>
</div>

<div class="dex-column">
    <h2>Flags</h2>
    <ul class="classic">
      % for flag, has_flag in c.flags:
        % if has_flag:
        <li>${flag.name}</li>
        <!-- XXX -->
        <!-- {h.literal(flag.description.as_html)} -->
        % else:
        <li class="disabled">${flag.name}</li>
        % endif
      % endfor
    </ul>
</div>

<div class="dex-column">
    <h2>Names</h2>
    <dl>
        % for foreign_name in c.move.foreign_names:
        <dt>${foreign_name.language.name}</dt>
        % if foreign_name.language.name == 'Japanese':
        <dd>${foreign_name.name} (${h.pokedex.romanize(foreign_name.name)})</dd>
        % else:
        <dd>${foreign_name.name}</dd>
        % endif
        % endfor
    </dl>

    <h2>Machines</h2>
    <dl>
    % for generation, version_numbers in sorted(c.machines.items(), \
                                                key=lambda (k, v): k.id):
        <dt>${h.pokedex.generation_icon(generation)}</dt>
        <dd>
          % for version_group, machine_number in version_numbers:
            % if version_group:
            ## Null version_group means this gen is all the same machine
            ${h.pokedex.version_icons(*version_group.versions)}
            % endif
            % if not machine_number:
            Not a TM
            % elif machine_number > 100:
            HM${"%02d" % (machine_number - 100)}
            % else:
            TM${"%02d" % machine_number}
            % endif
            <br>
          % endfor
        </dd>
    % endfor
    </dl>
</div>
</div>


<h1>Effect</h1>
<div class="dex-effect">
${h.literal(c.move.effect.as_html)}
</div>
<h2>Flavor Text</h2>
<dl>
    % for move_flavor_text in c.move.flavor_text:
    <dt>${h.pokedex.generation_icon(move_flavor_text.generation)}</dt>
    <dd>${move_flavor_text.flavor_text}</dd>
    % endfor
</dl>



<h1>Contests</h1>
<div class="dex-column-container">
<div class="dex-column">
    <h2>${h.pokedex.generation_icon(3)} Contest</h2>
    % if c.move.contest_effect:
    <dl>
        <dt>Type</dt>
        <dd>${h.pokedex.pokedex_img('chrome/contest/%s.png' % c.move.contest_type, alt=c.move.contest_type, title=c.move.contest_type)}</dd>
        <dt>Appeal</dt>
        <dd title="${c.move.contest_effect.appeal}">${u'♡' * c.move.contest_effect.appeal}</dd>
        <dt>Jam</dt>
        <dd title="${c.move.contest_effect.jam}">${u'♥' * c.move.contest_effect.jam}</dd>
        <dt>Flavor text</dt>
        <dd>${c.move.contest_effect.flavor_text}</dd>

        <dt>Use after</dt>
        <dd>
            % if c.move.contest_combo_prev:
            <ul class="inline-commas">
                % for move in c.move.contest_combo_prev:
                <li><a href="${url(controller='dex', action='moves', name=move.name.lower())}">${move.name}</a></li>
                % endfor
            </ul>
            % else:
            None
            % endif
        </dd>
        <dt>Use before</dt>
        <dd>
            % if c.move.contest_combo_next:
            <ul class="inline-commas">
                % for move in c.move.contest_combo_next:
                <li><a href="${url(controller='dex', action='moves', name=move.name.lower())}">${move.name}</a></li>
                % endfor
            </ul>
            % else:
            None
            % endif
        </dd>
    </dl>
    % else:
    <p>This move does not exist in games with Contests.</p>
    % endif
</div>

<div class="dex-column">
    <h2>${h.pokedex.generation_icon(4)} Super Contest</h2>
    % if c.move.super_contest_effect:
    <dl>
        <dt>Type</dt>
        <dd>${h.pokedex.pokedex_img('chrome/contest/%s.png' % c.move.contest_type, alt=c.move.contest_type, title=c.move.contest_type)}</dd>
        <dt>Appeal</dt>
        <dd title="${c.move.super_contest_effect.appeal}">${u'♡' * c.move.super_contest_effect.appeal}</dd>
        <dt>Flavor text</dt>
        <dd>${c.move.super_contest_effect.flavor_text}</dd>

        <dt>Use after</dt>
        <dd>
            % if c.move.super_contest_combo_prev:
            <ul class="inline-commas">
                % for move in c.move.super_contest_combo_prev:
                <li><a href="${url(controller='dex', action='moves', name=move.name.lower())}">${move.name}</a></li>
                % endfor
            </ul>
            % else:
            None
            % endif
        </dd>
        <dt>Use before</dt>
        <dd>
            % if c.move.super_contest_combo_next:
            <ul class="inline-commas">
                % for move in c.move.super_contest_combo_next:
                <li><a href="${url(controller='dex', action='moves', name=move.name.lower())}">${move.name}</a></li>
                % endfor
            </ul>
            % else:
            None
            % endif
        </dd>
    </dl>
    % else:
    <p>This move does not exist in games with Super Contests.</p>
    % endif
</div>
</div>

<h1>Pokémon</h1>
<table class="dex-pokemon-moves striped-rows">
## COLUMNS
% for i, column in enumerate(c.pokemon_columns):
% if i in c.pokemon_divider_columns:
<col class="dex-col-version dex-col-last-version">
% else:
<col class="dex-col-version">
% endif
% endfor
${lib.pokemon_table_columns()}
## HEADERS
% for method, method_list in c.pokemon:
<tr class="header-row">
    % for column in c.pokemon_columns:
    ${lib.pokemon_move_table_column_header(column)}
    % endfor
    ${lib.pokemon_table_header()}
</tr>
<tr class="subheader-row">
    <th colspan="${len(c.pokemon_columns) + 12}"><strong>${method.name}</strong>: ${method.description}</th>
</tr>
## DATA
% for pokemon, version_group_data in method_list:
<tr>
    % for column in c.pokemon_columns:
    ${lib.pokemon_move_table_method_cell(column, method, version_group_data)}
    % endfor
    ${lib.pokemon_table_row(pokemon)}
</tr>
% endfor
% endfor

</table>
