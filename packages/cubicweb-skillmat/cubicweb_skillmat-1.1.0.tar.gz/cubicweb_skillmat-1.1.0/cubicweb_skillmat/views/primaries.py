"""skillmat primary views

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance
from cubicweb_web.views import primary

from cubicweb_folder.views import FolderPrimaryView


class SkillPrimaryView(FolderPrimaryView):

    def cell_call(self, row, col):
        super(SkillPrimaryView, self).cell_call(row, col)
        skill = self.cw_rset.get_entity(row, col)
        rql = ('Any U,L,R ORDERBY L WITH U,L,R BEING ( '
               # get username and skill for those who specified it
               '   (Any U,L,R WHERE U login L, M foruser U, M rate R, '
               '    M skill S, S eid %(s)s) '
               ' UNION '  # union users for who the skill is unknown
               '   (Any U,L,-1 WHERE U login L, U is CWUser, '
               '    NOT EXISTS(M skill S, S eid %(s)s, M foruser U))  )')
        rset = self._cw.execute(rql, {'s': skill.eid})
        if not rset:
            self.warning('no skill information found for %s', skill.dc_title())
            return
        self._cw.add_css('cubes.skillmat.css')
        self.w(u'<table class="matrix">')
        self.w(u'<tr>')
        for row in range(len(rset)):
            self.w(u'<th>%s</th>' % self._cw.view('oneline', rset, row=row, col=0))
        self.w(u'</tr>\n<tr>')
        width = 100 / len(rset)
        for ueid, _, rate in rset:
            if rate == -1:
                linkto = ('foruser:%s:subject' % ueid,
                          'skill:%s:subject' % skill.eid)
                url = xml_escape(self._cw.build_url('add/Masters', __linkto=linkto))
                self.w(u'<td style="width: %s%%"><a href="%s">%s</a></td>' % (
                    width, url, self._cw._('???')))
            else:
                linkto = ('foruser:%s:subject' % ueid,
                          'skill:%s:subject' % skill.eid)
                url = xml_escape(self._cw.build_url('change/Masters', __linkto=linkto))
                self.w(u'<td style="width: %s%%"><a href="%s">%s</a></td>' % (
                    width, url, self._cw._('???')))

                self.w(u'<td style="width: %s%%" class="l%s">&nbsp;</td>' % (width, rate))
        self.w(u'</tr>')
        self.w(u'</table>')


class TalkPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Talk',)

    def render_entity_title(self, entity):
        self.w(u'<h1>%s</h1>' % xml_escape(entity.dc_title()))

    def render_entity_relations(self, entity):
        if entity.related('interested_in', 'object'):
            self.w(self._cw._('interested people :'))
            self.wview('list', entity.related('interested_in', 'object'), 'null')
        if entity.related('presented_by'):
            self.w(self._cw._('presented by :'))
            self.wview('list', entity.related('presented_by'), 'null')


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (SkillPrimaryView,))
    vreg.register_and_replace(SkillPrimaryView, FolderPrimaryView)
