<%inherit file="/base.mako"/>
<%namespace name="dexlib" file="lib.mako"/>
<%! from splinext.pokedex import i18n %>\

<%def name="title()">
<% dex_translate = i18n.DexTranslator(c) %>
<% _ = i18n.Translator(c) %>
${_("%s pocket - Items") % dex_translate(c.item_pocket.name)}
</%def>

<%def name="title_in_page()">
<% dex_translate = i18n.DexTranslator(c) %>
<% _ = i18n.Translator(c) %>
<ul id="breadcrumbs">
    <li><a href="${url('/dex')}">${_(u"Pokédex")}</a></li>
    <li><a href="${url(controller='dex', action='items_list')}">${_("Items")}</a></li>
    <li>${_("%s pocket") % dex_translate(c.item_pocket.name)}</li>
</ul>
</%def>

<% dex_translate = i18n.DexTranslator(c) %>
<% _ = i18n.Translator(c) %>

## Menu sort of thing
<ul id="dex-item-pockets">
    % for pocket in c.item_pockets:
    <li>
        <a href="${url(controller='dex', action='item_pockets', pocket=pocket.identifier)}">
            ${h.pokedex.pokedex_img("chrome/bag/{0}{1}.png".format(pocket.identifier, '-selected' if pocket == c.item_pocket else ''))}
        </a>
    </li>
    % endfor
</ul>

<h1>${dex_translate(c.item_pocket.name)}</h1>

<table class="striped-rows">
<tr class="header-row">
    % if c.item_pocket.identifier == u'berries':
    <th>${_("Num")}</th>
    % endif
    <th>${_("Item")}</th>
</tr>
% for category in c.item_pocket.categories:
% if category.name:
<tr class="subheader-row">
    <th colspan="999">${dex_translate(category.name)}</th>
</tr>
% endif
% for item in category.items:
<tr>
    % if c.item_pocket.identifier == u'berries':
    <td>${item.berry.id}</td>
    % endif
    <td>${h.pokedex.item_link(item)}</td>
</tr>
% endfor
% endfor
</table>
