# encoding: utf8

from spline.lib.i18n import BaseTranslator
from pokedex.db import markdown

class Translator(BaseTranslator):
    package = 'splinext.pokedex'
    domain = 'spline-pokedex'

class DexTranslator(BaseTranslator):
    package = 'pokedex'
    domain = 'pokedex'

    def __call__(self, message, *args, **kwargs):
        if isinstance(message, markdown.MarkdownString):
            return markdown.MarkdownString(self(unicode(message)))
        else:
            return super(DexTranslator, self).__call__(message, *args, **kwargs)
