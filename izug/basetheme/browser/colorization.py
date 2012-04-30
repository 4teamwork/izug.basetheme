from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize import ram
import os


COLORS = {
    'red': '#C3375A',
    'yellow': '#EBD21E',
    'green': '#37C35A'}

ENVIRONMENT_KEY = 'izug_basetheme_colorization'


class ColorizationViewlet(ViewletBase):

    @ram.cache(lambda *a, **kw: 'cache for ever')
    def available(self):
        return self._get_color() is not None

    def update(self):
        color = self._get_color()
        if color is not None:
            self.css = self._generate_css(color)

    def _get_color(self):
        colorname = os.environ.get(ENVIRONMENT_KEY, None)
        if colorname is not None:
            return COLORS[colorname]
        else:
            return None

    @ram.cache(lambda *a, **kw: 'cache for ever')
    def _generate_css(self, color):
        return '\n'.join((
                '#portal-top {',
                '  background-color: %s !important;' % color,
                '}',
                ))
