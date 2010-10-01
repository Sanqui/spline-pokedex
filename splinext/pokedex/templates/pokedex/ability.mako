<%inherit file="/base.mako"/>
<%namespace name="lib" file="/lib.mako"/>
<%namespace name='dexlib' file='lib.mako'/>
<%! from splinext.pokedex import i18n %>\

<%def name="title()"><% _ = i18n.Translator(c) %>${_("%s - Abilities") % c.ability.name}</%def>

<%def name="title_in_page()">
<% _ = i18n.Translator(c) %>
<ul id="breadcrumbs">
    <li><a href="${url('/dex')}">${_(u"Pokédex")}</a></li>
    <li><a href="${url(controller='dex', action='abilities_list')}">${_("Abilities")}</a></li>
    <li>${c.ability.name}</li>
</ul>
</%def>

<div id="dex-header">
    <a href="${url.current(name=c.prev_ability.name.lower(), form=None)}" id="dex-header-prev" class="dex-box-link">
        <img src="${h.static_uri('spline', 'icons/control-180.png')}" alt="«">
        ${c.prev_ability.id}: ${c.prev_ability.name}
    </a>
    <a href="${url.current(name=c.next_ability.name.lower(), form=None)}" id="dex-header-next" class="dex-box-link">
        ${c.next_ability.id}: ${c.next_ability.name}
        <img src="${h.static_uri('spline', 'icons/control.png')}" alt="»">
    </a>
    ${c.ability.id}: ${c.ability.name}
</div>


<%lib:cache_content>
<% dex_translate = i18n.DexTranslator(c) %>
<% _ = i18n.Translator(c) %>


${h.h1(_('Essentials'))}
<div class="dex-page-portrait">
    <p id="dex-page-name">${c.ability.name}</p>
    <p>${h.pokedex.generation_icon(c.ability.generation)}</p>
</div>

<div class="dex-page-beside-portrait">
    <h2>${_("Summary")}</h2>
    <div class="markdown">
        ${dex_translate(c.ability.short_effect).as_html | n}
    </div>
</div>


${h.h1(_('Effect'))}
<div class="markdown">
    ${dex_translate(c.ability.effect).as_html | n}
</div>


${h.h1(_('Flavor'))}
<div class="dex-column-container">
<div class="dex-column-2x">
    <h2>${_("Flavor Text")}</h2>
    ${dexlib.flavor_text_list(c.ability.flavor_text)}
</div>

<div class="dex-column">
    <h2>${_("Foreign Names")}</h2>
    <dl>
        % for foreign_name in c.ability.foreign_names:
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


${h.h1(_(u'Pokémon', context='plural'), id='pokemon')}
<table class="dex-pokemon-moves striped-rows">
    ${dexlib.pokemon_table_columns()}
    <thead>
        <tr class="header-row">
            ${dexlib.pokemon_table_header()}
        </tr>
    </thead>
    <tbody>
        % for pokemon in c.pokemon:
        <tr>
            ${dexlib.pokemon_table_row(pokemon)}
        </tr>
        % endfor
    </tbody>
</table>


${h.h1(_('External Links'), id='links')}
<ul class="classic-list">
    <li><a href="http://bulbapedia.bulbagarden.net/wiki/${c.ability.name.replace(' ', '_')}_%28ability%29">${_("Bulbapedia")}</a></li>
    <li><a href="http://legendarypokemon.net/dp/abilities#${c.ability.name.lower().replace(' ', '+')}">${_(u"Legendary Pokémon")}</a></li>
    <li><a href="http://serebii.net/abilitydex/${c.ability.name.lower().replace(' ', '')}.shtml">${_("Serebii.net")}</a></li>
    <li><a href="http://smogon.com/dp/abilities/${c.ability.name.lower().replace(' ', '_')}">${_("Smogon")}</a></li>
</ul>
</%lib:cache_content>
