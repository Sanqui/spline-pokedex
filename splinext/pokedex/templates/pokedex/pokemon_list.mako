<%inherit file="/base.mako"/>
<%namespace name="lib" file="/lib.mako"/>
<%! from splinext.pokedex import i18n %>\

<%def name="title()"><% _ = i18n.Translator(c) %>${_(u"Pokémon")}</%def>

<%def name="title_in_page()">
<% _ = i18n.Translator(c) %>
<ul id="breadcrumbs">
    <li><a href="${url('/dex')}">${_(u"Pokédex")}</a></li>
    <li>${_(u"Pokémon")}</li>
</ul>
</%def>

<% _ = i18n.Translator(c) %>

<h1>${_(u"Pokémon lists")}</h1>
<p>${_(u'The following are all links to the <a href="{url}">Pokémon search</a>, so you can filter and sort however you want.').format(url=url(controller='dex_search', action='pokemon_search')) | n}</p>

<h2>${_(u"By generation")}</h2>
<ul class="classic-list">
    <li><a href="${url(controller='dex_search', action='pokemon_search', introduced_in=['1','2','3','4'], sort='evolution-chain')}">${_(u"EVERY POKéMON EVER")}</a></li>
    <li><a href="${url(controller='dex_search', action='pokemon_search', introduced_in='1', sort='evolution-chain')}">${h.pokedex.generation_icon(1)} ${_(u"Red/Blue/Yellow")}</a></li>
    <li><a href="${url(controller='dex_search', action='pokemon_search', introduced_in='2', sort='evolution-chain')}">${h.pokedex.generation_icon(2)} ${_(u"Gold/Silver/Crystal")}</a></li>
    <li><a href="${url(controller='dex_search', action='pokemon_search', introduced_in='3', sort='evolution-chain')}">${h.pokedex.generation_icon(3)} ${_(u"Ruby/Sapphire/Emerald")}</a></li>
    <li><a href="${url(controller='dex_search', action='pokemon_search', introduced_in='4', sort='evolution-chain')}">${h.pokedex.generation_icon(4)} ${_(u"Diamond/Pearl/Platinum")}</a></li>
    <li><a href="${url(controller='dex_search', action='pokemon_search', introduced_in='5', sort='evolution-chain')}">${h.pokedex.generation_icon(5)} ${_(u"Black/White")}</a></li>
</ul>

<h2>${_(u"By regional Pokédex")}</h2>
<ul class="classic-list">
    <li><a href="${url(controller='dex_search', action='pokemon_search', in_pokedex='7', sort='evolution-chain')}">${h.pokedex.generation_icon(2)} ${_(u"Johto")}</a></li>
    <li><a href="${url(controller='dex_search', action='pokemon_search', in_pokedex='4', sort='evolution-chain')}">${h.pokedex.generation_icon(3)} ${_(u"Hoenn")}</a></li>
    <li><a href="${url(controller='dex_search', action='pokemon_search', in_pokedex='6', sort='evolution-chain')}">${h.pokedex.generation_icon(4)} ${_(u"Sinnoh")}</a></li>
</ul>

<h2>${_(u"Miscellaneous interesting lists")}</h2>
<ul class="classic-list">
    <li><a href="${url(controller='dex_search', action='pokemon_search', evolution_stage='basic')}">${_(u"Basic Pokémon")}</a></li>
    <li><a href="${url(controller='dex_search', action='pokemon_search', evolution_position='last')}">${_(u"Fully-evolved Pokémon")}</a></li>
    <li><a href="${url(controller='dex_search', action='pokemon_search', evolution_position='only')}">${_(u"Non-evolving Pokémon")}</a></li>
</ul>
