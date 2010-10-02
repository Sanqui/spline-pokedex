<%inherit file="/base.mako"/>
<%namespace name="dexlib" file="lib.mako"/>
<%! from splinext.pokedex import i18n %>\

<%def name="title()"><% _ = i18n.Translator(c) %>${_("Items")}</%def>

<%def name="title_in_page()">
<% _ = i18n.Translator(c) %>
<ul id="breadcrumbs">
    <li><a href="${url('/dex')}">${_(u"Pokédex")}</a></li>
    <li>${_("Items")}</li>
</ul>
</%def>
<% dex_translate = i18n.DexTranslator(c) %>
<% _ = i18n.Translator(c) %>

<h1>${_("Items")}</h1>

<p>${_("Pick your pocket:")}</p>

<ul class="classic-list">
    % for pocket in c.item_pockets:
    <li>
        <a href="${url(controller='dex', action='item_pockets', pocket=pocket.identifier)}">
            ${h.pokedex.pokedex_img(u"chrome/bag/{0}.png".format(pocket.identifier))}
            ${dex_translate(pocket.name)}
        </a>
    </li>
    % endfor
</ul>


