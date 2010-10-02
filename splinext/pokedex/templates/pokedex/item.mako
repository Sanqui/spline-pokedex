<%inherit file="/base.mako"/>
<%namespace name="dexlib" file="lib.mako"/>
<%! from splinext.pokedex import i18n %>\

<%def name="title()"><% _ = i18n.Translator(c) %>${_("%s - Items") % c.item.name}</%def>

<%def name="title_in_page()">
<% _ = i18n.Translator(c) %>
<ul id="breadcrumbs">
    <li><a href="${url('/dex')}">${_(u"Pokédex")}</a></li>
    <li><a href="${url(controller='dex', action='items_list')}">${_("Items")}</a></li>
    <li><a href="${url(controller='dex', action='item_pockets', pocket=c.item.pocket.identifier)}">${_("%s pocket") % c.item.pocket.name}</a></li>
    <li>${c.item.name}</li>
</ul>
</%def>

<% dex_translate = i18n.DexTranslator(c) %>
<% _ = i18n.Translator(c) %>

${h.h1(_('Essentials'))}

## Portrait block
<div class="dex-page-portrait">
    <p id="dex-page-name">${c.item.name}</p>
    <%
        if c.item.appears_underground or c.item.berry:
            sprite_path = 'items/big'
        else:
            sprite_path = 'items'
    %>\
    <div id="dex-pokemon-portrait-sprite">
        ${h.pokedex.pokedex_img(u"{0}/{1}.png".format(sprite_path, h.pokedex.filename_from_name(c.item.name)))}
    </div>
    <p id="dex-page-types">
        <a href="${url(controller='dex', action='item_pockets', pocket=c.item.pocket.identifier)}">
            ${h.pokedex.pokedex_img(u"chrome/bag/{0}.png".format(c.item.pocket.identifier))}
            ${c.item.pocket.name}
        </a> ${_("pocket")}
    </p>
</div>

<div class="dex-page-beside-portrait">
<dl>
    <dt>${_("Cost")}</dt>
    <dd>
        % if c.item.cost:
        ${_(u"%s Pokédollars") % c.item.cost}
        % else:
        ${_(u"Can't be bought or sold")}
        % endif
    </dd>
    <dt>${_(u"Flags")}</dt>
    <dd>
        <ul class="classic-list">
            % for flag in c.item.flags:
            <li>${dex_translate(flag.name)}</li>
            % endfor
        </ul>
    </dd>
</dl>
</div>


${h.h1(_('Effect'))}
<div class="markdown">
${dex_translate(c.item.effect).as_html | n}
</div>

% if c.item.fling_effect or c.item.berry:
<h2>${_("Special move effects")}</h2>
<dl>
    % if c.item.fling_effect:
    <dt><a href="${url(controller='dex', action='moves', name='fling')}">${_("Fling")}</a></dt>
    <dd>${dex_translate(c.item.fling_effect.effect)}</dd>
    % endif
    % if c.item.berry:
    <dt><a href="${url(controller='dex', action='moves', name='natural gift')}">${_("Natural Gift")}</a></dt>
    <dd>${_("Inflicts regular {type} damage with {power} power").format(type=h.pokedex.type_link(c.item.berry.natural_gift_type), power=c.item.berry.natural_gift_power) | n}.</dd>
    % endif
</dl>
% endif


${h.h1(_('Flavor'))}
<div class="dex-column-container">
<div class="dex-column-2x">
    <h2>${_("Flavor text")}</h2>
    ${dexlib.flavor_text_list(c.item.flavor_text)}
</div>

<div class="dex-column">
    <h2>${_("Foreign names")}</h2>
    <dl>
        % for foreign_name in c.item.foreign_names:
        <dt>${foreign_name.language.name}
        <img src="${h.static_uri('spline', "flags/{0}.png".format(foreign_name.language.iso3166))}" alt=""></dt>
        % if foreign_name.language.name == 'Japanese':
        <dd>${foreign_name.name} (${h.pokedex.romanize(foreign_name.name)})</dd>
        % else:
        <dd>${foreign_name.name}</dd>
        % endif
        % endfor
    </dl>
</div>
</div>


% if c.item.berry:
${h.h1(_('Berry tag'))}
<div class="dex-column-container">
<div class="dex-column">
    <h2>${_("Growth")}</h2>
    <dl>
        <dt>${_("Maximum harvest")}</dt>
        <dd>${_("%s berries") % c.item.berry.max_harvest}</dd>
        <dt>${_("Time to grow")}</dt>
        <dd>
            ${_("%s hours per stage") % c.item.berry.growth_time}<br>
            ${_("%s hours total") % (c.item.berry.growth_time * 4)}<br>
            <%! from splinext.pokedex.db import get_by_name %>
            ${h.pokedex.item_link(c.growth_mulch)}:
                ${_("%s/%s hours") % (c.item.berry.growth_time * 3 / 4, c.item.berry.growth_time * 3)}<br>
            ${h.pokedex.item_link(c.damp_mulch)}:
                ${_("%s/%s hours") % (c.item.berry.growth_time * 5 / 4, c.item.berry.growth_time * 5)}
        </dd>
        <dt>${_("Soil drying rate")}</dt>
        <dd>${c.item.berry.soil_dryness}</dd>
    </dl>
</div>
<div class="dex-column">
    <h2>${_("Taste")}</h2>
    <dl>
        % for berry_flavor in c.item.berry.flavors:
        <dt>${dex_translate(berry_flavor.contest_type.flavor).title()}</dt>
        <dd>
            % if berry_flavor.flavor:
            ${berry_flavor.flavor}
            ${_("(raises %s)") % h.pokedex.pokedex_img("chrome/contest/{0}.png".format(berry_flavor.contest_type.name), alt=dex_translate(berry_flavor.contest_type.name)) | n}
            % else:
            ${_(u"—")}
            % endif
        </dd>
        % endfor
        <dt>${_("Smoothness")}</dt>
        <dd>${c.item.berry.smoothness}</dd>
    </dl>
</div>
<div class="dex-column">
    <h2>${_("Flavor")}</h2>
    <dl>
        <dt>${_("Size")}</dt>
        <dd>${"{0:.1f}".format(c.item.berry.size / 25.4)}" or ${"{0:.1f}".format(c.item.berry.size / 10.0)} cm</dd>
        <dt>${_("Firmness")}</dt>
        <dd>${c.item.berry.firmness}</dd>
</div>
</div>
% endif


% if c.holding_pokemon:
${h.h1(_(u'Held by wild Pokémon'), id='pokemon')}
<table class="dex-pokemon-moves striped-rows">
## Columns
% for column_group in c.held_version_columns:
<colgroup class="dex-colgroup-versions">
    % for column in column_group:
    <col class="dex-col-version">
    % endfor
</colgroup>
% endfor
<colgroup>${dexlib.pokemon_table_columns()}</colgroup>

## Headers
<thead>
  <tr class="header-row">
    <% from itertools import groupby %>
    % for column_group in c.held_version_columns:
      ## Only print a generation icon if the whole gen is one column
      % if len(column_group) == 1:
        <th>${h.pokedex.generation_icon(column_group[0][0].generation)}</th>
      % else:
        % for column in column_group:
        <th>
          % for _, version_group in groupby(column, lambda version: version.version_group):
          ${h.pokedex.version_icons(*version_group)}<br />
          % endfor
        </th>
        % endfor
      % endif
    % endfor

    ${dexlib.pokemon_table_header()}
  </tr>
</thead>

## Rows
<tbody>
% for pokemon, version_rarities in sorted(c.holding_pokemon.items(), \
                                          key=lambda (k, v): k.id):
    <tr>
        % for column in sum(c.held_version_columns, []):
            % if version_rarities[column[0]]:
            <td>${version_rarities[column[0]]}%</td>
            % else:
            <td></td>
            % endif
        % endfor

        ${dexlib.pokemon_table_row(pokemon)}
    </tr>
% endfor
</tbody>
</table>
% endif
