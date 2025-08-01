"""skillmat specific entities

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb import _
from cubicweb.predicates import is_instance
from cubicweb.entities import AnyEntity, adapters

from cubicweb_folder.entities import Folder


class Masters(AnyEntity):
    __regid__ = 'Masters'
    fetch_attrs = ('rate', 'foruser', 'skill')

    def dc_title(self):
        return u'%s: %s' % (self.skill[0].name, self.rate)

    def dc_long_title(self):
        return u'%s / %s' % (self.foruser[0].dc_title(), self.dc_title())


class Technology(AnyEntity):
    __regid__ = 'Technology'
    fetch_attrs = ('name',)

    def skill_categories(self):
        # XXX what if we have a skill tree with depth > 1
        return self.filed_under


class Skill(Folder):  # XXX

    def skill_categories(self):
        return [self]


class Talk(AnyEntity):
    __regid__ = 'Talk'
    fetch_attrs = ('subject', 'description', 'talktime')

    def dc_title(self):
        return u'%s' % (self.subject)


SKILLS = {0: _("I don't want to learn this technology"),
          1: _('I know nothing about this technology'),
          2: _('Just beginning whith this technology'),
          3: _('I start on this technology, and I can help'),
          4: _('I am doing well, selfworking'),
          5: _('I can conduct a training course')}


class TechnologyITreeAdapter(adapters.ITreeAdapter):
    __select__ = is_instance('Technology')
    tree_relation = 'filed_under'

    def children(self, entities=True, sametype=False):
        if entities:
            return ()
        return self._cw.empty_rset()
