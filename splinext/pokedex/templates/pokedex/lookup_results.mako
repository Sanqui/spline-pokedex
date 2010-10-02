<%inherit file="/base.mako"/>
<%! from splinext.pokedex import i18n %>\

<%def name="title()"><% _ = i18n.Translator(c) %>${_("Disambiguation")}</%def>

<%def name="title_in_page()">
<% _ = i18n.Translator(c) %>
<ul id="breadcrumbs">
    <li><a href="${url('/dex')}">${_(u"Pokédex")}</a></li>
    <li>${_("Disambiguation")}</li>
</ul>
</%def>

<h1>${c.input}</h1>
% if c.exact:
<p>${_("Hmmm, there are several things with that name.  Did you mean:")}</p>
% else:
<p>${_("It seems you don't know how to spell.  Did you mean one of these?")}</p>
% endif

<ul class="classic-list">
% for result in c.results:
<%
    object = result.object
%>\
<li>
    ${_(u"The %s") % c.table_labels[object.__class__]}
    <a href="${h.pokedex.make_thingy_url(object, subpage=c.subpage)}">
    % if object.__tablename__ == 'pokemon':
    ${h.pokedex.pokemon_sprite(object, prefix='icons')}
    % elif object.__tablename__ == 'items':
    ${h.pokedex.pokedex_img("items/%s.png" % h.pokedex.filename_from_name(object.name))}
    % elif object.__tablename__ == 'types':
    ${h.pokedex.type_icon(object)}
    % elif object.__tablename__ == 'moves':
    ${h.pokedex.type_icon(object.type)}
    ${h.pokedex.damage_class_icon(object.damage_class)}
    % endif
\
    % if object.__tablename__ == 'pokemon':
    ${object.full_name}
    % else:
    ${object.name}
    % endif
    </a>
    % if result.language:
    (<img src="${h.static_uri('spline', "flags/{0}.png".format(result.iso3166))}" alt="${result.language}" title="${result.language}"> ${result.name})
    % endif
</li>
% endfor
</ul>

% if c.exact and len(c.results) >= 20:
<p>${_(u'Boy, this is a lot of matches!  Maybe you want to use the full-blown <a href="{pokesearch}">Pokémon search</a> or <a href="{movesearch}">move search</a>, or check the various <a href="{dexurl}">lists of everything and lookup help</a>').format(pokesearch=url(controller='dex_search', action='pokemon_search'), movesearch=url(controller='dex_search', action='move_search'), dexurl=url('/dex')) | n}.</p>
% else:
<p><a href="${url('/dex')}">${_("Need help?")}</a></p>
% endif
