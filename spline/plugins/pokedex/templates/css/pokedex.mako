/*** General ***/

/* Pokémon sprite link grid */
a.dex-icon-link { display: inline-block; border: 1px solid transparent; }
a.dex-icon-link:hover { border: 1px solid #bfd3f1; background: #e6eefa; }
a.dex-icon-link.selected { border: 1px solid #95b7ea; background: #bfd4f2; }
a.dex-box-link { display: inline-block; margin: 0.25em; border: 1px solid transparent; }
a.dex-box-link:hover { border: 1px solid #bfd3f1; background: #e6eefa; }
a.dex-box-link.selected { border: 1px solid #95b7ea; background: #bfd4f2; }

/* Header */
ul.inline-menu { text-align: middle; }
ul.inline-menu > li { display: inline; }
ul.inline-menu > li:after { content: ' | '; }
ul.inline-menu > li:last-child:after { content: none; }

#dex-header { overflow: hidden; /* new float context */ text-align: center; line-height: 24px; /* keep buttons at least 24px tall */ }
#dex-header-prev { float: left;  text-align: left; }
#dex-header-next { float: right; text-align: right; }
#dex-header-prev, #dex-header-next { width: 15em; min-height: 24px; margin: 0; }
#dex-header-prev img, #dex-header-next img { vertical-align: middle; }
#dex-header ul.inline-menu {  line-height: 1.2; }
#dex-header + h1 { margin-top: 0.25em; }

/* Table columns */
col.dex-col-stat        { width: 3em; }
col.dex-col-stat-name   { width: 10em; }
col.dex-col-stat-bar    { width: auto; }
col.dex-col-stat-pctile { width: 5em; }
col.dex-col-stat-result { width: 5em; }
col.dex-col-version     { width: 3.5em; }  /* two versions (32px < 33px == 3em) plus 0.17em padding < 3.5em */
col.dex-col-last-version{ border-right: 1px solid #b4c7e6; }

/* Cool three-column layout */
.dex-column-container { clear: both; overflow: hidden /* float context */; margin-top: 1em; }
.dex-column { float: left; width: 32.666%; margin-left: 1%; }
.dex-column:first-child { margin-left: 0; }
.dex-column-2x { float: left; width: 66.333%; margin-left: 1%; }
.dex-column-2x:first-child { margin-left: 0; }

/* Type damage */
.dex-damage-taken-0   { font-weight: bold; color: #44c; }
.dex-damage-taken-25  { font-weight: bold; color: #4cc; }
.dex-damage-taken-50  { font-weight: bold; color: #4c4; }
.dex-damage-taken-100 { font-weight: bold; color: #999; }
.dex-damage-taken-200 { font-weight: bold; color: #c44; }
.dex-damage-taken-400 { font-weight: bold; color: #c4c; }

.dex-damage-dealt-0   { font-weight: bold; color: #44c; }
.dex-damage-dealt-25  { font-weight: bold; color: #c4c; }
.dex-damage-dealt-50  { font-weight: bold; color: #c44; }
.dex-damage-dealt-100 { font-weight: bold; color: #999; }
.dex-damage-dealt-200 { font-weight: bold; color: #4c4; }
.dex-damage-dealt-400 { font-weight: bold; color: #4cc; }

/* Size comparison */
.dex-size { height: 120px; padding-bottom: 2.5em /* for -value */; overflow: hidden /* new float context */}
.dex-size img { clip: 8px; position: absolute; bottom: 0; image-rendering: -moz-crisp-edges; }
.dex-size input[type='text'] { text-align: right; }
.dex-size .dex-size-trainer,
.dex-size .dex-size-pokemon { display: block; position: relative; float: left; height: 100%; width: 50%; text-align: left; }
.dex-size .dex-size-trainer { text-align: right; }
.dex-size .dex-size-pokemon { text-align: left; }
.dex-size .dex-size-trainer img { right: 0.25em; }
.dex-size .dex-size-pokemon img { left: 0.25em; }
.dex-size .js-dex-size-raw { display: none; }
.dex-size .dex-size-value { position: absolute; height: 2em; margin: 0; line-height: 1; padding: 0.25em; bottom: -2.5em; }
.dex-size .dex-size-trainer .dex-size-value { right: 0.25em; }
.dex-size .dex-size-pokemon .dex-size-value { left: 0.25em; }

/*** Individual pages ***/
.dex-page-portrait { float: left; width: 15em; min-height: 10em; padding-bottom: 1em; text-align: center; }
.dex-page-portrait p { margin: 0.25em 0; line-height: 1; }
.dex-page-beside-portrait:after { display: block; clear: both; content: ""; }
p#dex-page-name { font-size: 2em; margin: 0.12em 0; }
#dex-pokemon-forme { font-size: 1.25em; font-weight: bold; }
#dex-pokemon-portrait-sprite { margin: 0.33em; padding: 7px; background: url(/dex/media/chrome/sprite-frame.png) center center no-repeat; }

ul.dex-page-damage { overflow: hidden /* new float context */; margin-bottom: 2em; }
ul.dex-page-damage li { display: inline-block; text-align: center; padding: 0.125em; }
ul.dex-page-damage li img { display: block; margin-bottom: 0.25em; }

ul.dex-pokemon-compatibility { max-height: 136px /* four rows of icons plus borders */; overflow: auto; }

.dex-pokemon-item-rarity { display: inline-block; width: 3em; text-align: right; }

table.dex-evolution-chain { width: 100%; table-layout: fixed; border-collapse: separate; border-spacing: 0.5em; empty-cells: hide; }
table.dex-evolution-chain td { padding: 0.5em; vertical-align: middle; border: 1px solid #d8d8d8; background: #f0f0f0; }
table.dex-evolution-chain td:hover { border: 1px solid #bfd3f1; background: #e6eefa; }
table.dex-evolution-chain td.selected { border: 1px solid #95b7ea; background: #bfd4f2; }
.dex-evolution-chain-method { display: block; overflow: hidden; font-size: 0.8em; line-height: 1.25em; }
.dex-evolution-chain-pokemon { padding-top: 8px /* bump icon up a bit */; display: block; font-weight: bold; }
.dex-evolution-chain-pokemon img { float: left; margin-top: -8px /* fills link's top padding */; padding-right: 0.33em; }

table.dex-pokemon-stats { width: 100%; }
table.dex-pokemon-stats th label { display: block; text-align: right; font-weight: normal; color: #2457a0; }
table.dex-pokemon-stats th input { text-align: left; }
table.dex-pokemon-stats .dex-pokemon-stats-bar-container { background: #f8f8f8; }
table.dex-pokemon-stats .dex-pokemon-stats-bar { padding: 0.33em; border: 1px solid #d8d8d8; background: #f0f0f0; }
table.dex-pokemon-stats td.dex-pokemon-stats-pctile { text-align: right; }
table.dex-pokemon-stats td.dex-pokemon-stats-result { text-align: right; }

.dex-simple-encounters-terrain { margin-bottom: 0.5em; }
dl.dex-simple-encounters dd img { vertical-align: bottom; }
dl.dex-simple-encounters ul { display: inline; }
dl.dex-simple-encounters ul li { display: inline; }
dl.dex-simple-encounters ul li:after { content: '; '; }
dl.dex-simple-encounters ul li:last-child:after { content: ''; }

/* This is actually the pokemon-locations page */
table.dex-encounters th.version { width: 8em; }
table.dex-encounters td { width: 10em; vertical-align: top; }
table.dex-encounters td.location { vertical-align: top; }
table.dex-encounters th.location { vertical-align: top; text-align: left; }
.dex-location-area { font-size: 0.8em; font-style: italic; color: black; }
.dex-encounter-condition-group { padding: 0.5em 0; }
.dex-encounter-condition-group + .dex-encounter-condition-group { border-top: 1px solid #404040; }
.dex-encounter-conditions + .dex-encounter-conditions { margin-top: 0.5em; }
.dex-encounter-conditions .dex-encounter-icon { float: left; width: 24px; height: 24px; line-height: 24px; text-align: center; overflow: hidden;}
.dex-encounter-conditions .dex-encounter-icon img { vertical-align: middle; }
.dex-encounter-conditions .dex-encounter-rarity { float: right; }
.dex-encounter-conditions .dex-rarity-bar { position: relative; overflow: auto; font-size: 0.75em; height: 1em; line-height: 1; margin-top: 0.25em; background: #e8e8e8; border: 1px solid #96bbf2; }
.dex-encounter-conditions .dex-rarity-bar-fill { height: 100%; background: #96bbf2; }
.dex-encounter-conditions .dex-rarity-bar-fills { float: left; height: 100%; background: #96bbf2; }
.dex-encounter-conditions .dex-rarity-bar-fills + .dex-rarity-bar-fills { margin-left: -1px; border-left: 1px solid #b3cef6; }
.dex-encounter-conditions .dex-rarity-bar-value { position: absolute; height: 100%; top: 0; right: 0; color: #808080; vertical-align: bottom; }

table.dex-pokemon-moves {;}
table.dex-pokemon-pokemon-moves { width: 100%; }
table.dex-pokemon-moves td { padding: 0.33em; vertical-align: middle; text-align: center; }
table.dex-pokemon-moves th { padding: 0.33em 0.17em; text-align: center; }
table.dex-pokemon-moves tr.subheader-row th { padding: 0.17em 0.33em; text-align: left; }
table.dex-pokemon-moves td.egg { padding: 0 /* egg sprite consumes a lot of space, so let it extend into padding */; }
table.dex-pokemon-moves td.effect { font-size: 0.8em; text-align: left; }
table.dex-pokemon-moves td.effect p { margin: 0; }
table.dex-pokemon-moves td.tutored { white-space: nowrap; }
table.dex-pokemon-moves .no-tutor { visibility: hidden; }
table.dex-pokemon-moves td.type2 { text-align: left; }
table.dex-pokemon-moves td.ability { font-size: 0.75em; }
table.dex-pokemon-moves td.egg-group { font-size: 0.75em; }
table.dex-pokemon-moves td.stat { text-align: right; }
/* javascript filtering/sorting */
table.dex-pokemon-moves tr.js-dex-pokemon-moves-controls .js-label { font-size: 0.67em; }
table.dex-pokemon-moves tr.js-dex-pokemon-moves-controls:hover { background: transparent; outline: none; }
table.dex-pokemon-moves tr.js-dex-pokemon-moves-controls td:hover { cursor: pointer; outline: 1px solid #bfd3f1; outline-offset: -1px; background: #e6eefa; }
table.dex-pokemon-moves tr.js-dex-pokemon-moves-controls td.js-not-a-button:hover { cursor: default; outline: none; background: transparent; }
table.dex-pokemon-moves tr.js-dex-pokemon-moves-controls td.js-sorted-by { background: #f0efe6; }
table.dex-pokemon-moves tr:nth-child(2n) td.js-sorted-by { background: #f0efe6; }
table.dex-pokemon-moves tr:nth-child(2n+1) td.js-sorted-by { background: #f6f4ea; }
table.dex-pokemon-moves tr:nth-child(2n) td.better-move-reason { background: #afcfaf; }
table.dex-pokemon-moves tr:nth-child(2n+1) td.better-move-reason { background: #c0d8c0; }

.dex-pokemon-flavor-generation { position: absolute; line-height: 1.5; }
dl.dex-pokemon-flavor-text + .dex-pokemon-flavor-generation { padding-top: 1.5em; }
dl.dex-pokemon-flavor-text + .dex-pokemon-flavor-generation + dl.dex-pokemon-flavor-text { padding-top: 1.5em; }
dl.dex-pokemon-flavor-text dt { width: 7em /* enough for gen, two versions, and space */; }
dl.dex-pokemon-flavor-text dd { padding-left: 7.5em; }

th { vertical-align: middle; }
.vertical-text { -moz-transform: rotate(-90deg); }

.dex-priority-fast { font-weight: bold; color: green; }
.dex-priority-slow { font-weight: bold; color: red; }

/* Move effects, etc */
.dex-effect a { font-weight: normal; }


#dex-cheat-unlocked { overflow: hidden /* float containment */; width: 60%; margin: auto; margin-top: 10em; }
#dex-cheat-unlocked .dex-cheat-unlocked-left { float: left; }
#dex-cheat-unlocked .dex-cheat-unlocked-right { float: right; }
#dex-cheat-unlocked .dex-cheat-unlocked-line1 { font-size: 48px; font-weight: bold; text-align: center; text-transform: uppercase; }
#dex-cheat-unlocked .dex-cheat-unlocked-line2 { font-size: 34px; font-weight: bold; text-align: center; text-transform: uppercase; }
#dex-cheat-list { margin-top: 1em; margin-bottom: 5em; text-align: center; }
#dex-cheat-list li { display: inline; padding: 0.5em 1em; }
#dex-cheat-list li.this-cheat { font-weight: bold; }

.dex-obdurate-word { white-space: nowrap; }
