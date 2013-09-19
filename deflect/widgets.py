from __future__ import unicode_literals

from itertools import chain

from django.contrib.admin.widgets import AdminTextInputWidget
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class DataListInput(AdminTextInputWidget):
    """
    A form widget that displays a standard ``TextInput`` field, as well
    as an HTML5 datalist element. This provides a set of options that
    the user can select from, along with the ability to enter a custom
    value. Suggested options are matched as the user begins typing.
    """
    def __init__(self, attrs=None, choices=()):
        super(DataListInput, self).__init__(attrs)
        self.choices = list(chain.from_iterable(choices))

    def render(self, name, value, attrs={}, choices=()):
        attrs['list'] = 'id_%s_list' % name
        output = [super(DataListInput, self).render(name, value, attrs)]
        options = self.render_options(name, choices)
        if options:
            output.append(options)
        return mark_safe('\n'.join(output))

    def render_options(self, name, choices):
        output = []
        output.append('<datalist id="id_%s_list">' % name)
        output.append('<select style="display:none">')
        for option in chain(self.choices, choices):
            output.append(format_html('<option value="{0}" />', force_text(option)))
        output.append('</select>')
        output.append('</datalist>')
        return '\n'.join(output)
