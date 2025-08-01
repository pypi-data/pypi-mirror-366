"""template-specific forms/views/actions/components"""
import six
from cubicweb_web.view import EntityAdapter
from cubicweb.predicates import is_instance
from cubicweb_web.views import uicfg

from cubicweb_skillmat.entities import SKILLS

RATEVOCAB = [(l, six.text_type(v)) for v, l in sorted(SKILLS.items())]
uicfg.autoform_field_kwargs.tag_attribute(
    ('Masters', 'rate'),
    {'choices': RATEVOCAB,
     'internationalizable': True})

uicfg.autoform_section.tag_subject_of(('Talk', 'attended_by', '*'), 'main', 'attributes')
uicfg.autoform_section.tag_subject_of(('Talk', 'attended_by', '*'), 'muledit', 'attributes')


class TalkICalendarable(EntityAdapter):
    __regid__ = 'ICalendarable'
    __select__ = is_instance('Talk')

    @property
    def start(self):
        return self.entity.talktime

    @property
    def stop(self):
        return self.entity.talktime
