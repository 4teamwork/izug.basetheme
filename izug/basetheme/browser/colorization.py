from plone.app.layout.viewlets.common import ViewletBase
import os


COLORS = {
    'red': '#C3375A',
    'yellow': '#EBD21E',
    'green': '#37C35A'}

ENVIRONMENT_KEY = 'izug_basetheme_colorization'


class ColorizationViewlet(ViewletBase):

    def update(self):
        color = self._get_color()
        if color is not None:
            self.css = self._generate_css(color)
        else:
            self.css = ''

    def _get_color(self):
        colorname = os.environ.get(ENVIRONMENT_KEY, None)
        if colorname is not None:
            return COLORS[colorname]
        else:
            return None

    def _generate_css(self, color):
        return '\n'.join((
                '#portal-top {',
                '  background-color: %s !important;' % color,
                '}',
                ))
