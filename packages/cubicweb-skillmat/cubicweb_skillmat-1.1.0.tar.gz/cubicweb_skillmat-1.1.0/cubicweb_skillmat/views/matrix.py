from logilab.common.decorators import cached
from logilab.mtconverter import xml_escape

import pandas as pd
from cubicweb import _
from cubicweb_web.view import EntityView
from cubicweb.predicates import is_instance, match_view
from cubicweb.uilib import toggle_action
from cubicweb_web import action
from cubicweb_web.views.csvexport import CSVMixIn

from cubicweb_skillmat.entities import SKILLS


class SkillMatrixView(EntityView):
    __regid__ = 'matrix'
    __select__ = is_instance('CWUser')

    def call(self):
        skills = self.skills
        if not skills:
            self.w(self._cw._('no skill definition found'))
            return
        # prefetch every skill for users in the resultset
        self.masters_dict = self.prefetch_skills()
        self._cw.add_css('cubes.skillmat.css')
        divid = 'appMsg%s' % id(self)
        # FIXME: make the applmessages component flexible enough to use it
        msg = self._cw._('you can update your skill information by clicking on the corresponding cell')
        self.w(u'''<div class="appMsg" id="%s" onclick="%s">
        <div class="message">%s</div>
        </div>
        ''' % (divid, toggle_action(divid), xml_escape(msg)))
        self.w(u'<table class="matrix">')
        self.w(u'<tr>')
        self.w(u'<th style="width: 10%;">&nbsp;</th>')  # users column
        width = int(90 / len(skills))
        for skill in skills:
            self.w(u'<th style="width: %s%%;">%s</th>' %
                   (width, skill.view('oneline')))
        self.w(u'</tr>')
        for row in range(len(self.cw_rset)):
            self.cell_call(row, 0)
        self.w(u'</table>')
        self._build_help()

    def _build_help(self):
        """builds an HTML section explaining what each colour means"""
        self.w(u'<br />')
        self.w(u'<table class="matrixHelp">')
        celltemplatelabel = u'<td class="l%s rateInfo">&nbsp;</td>'
        matrix_label = dict(SKILLS)
        matrix_label[-1] = self._cw._(u'no information for this technology')
        for rate, label in sorted(matrix_label.items()):
            self.w(u'<tr>')
            self.w(celltemplatelabel % rate)
            self.w(u'<td>%s</td>' % self._cw._(label))
            self.w(u'</tr>')
        self.w(u'</table>')
        self.w(u'<br />')

    def cell_call(self, row, col):
        user = self.cw_rset.get_entity(row, col)
        ruser = self._cw.user
        relpath = self._cw.relative_path(includeparams=False)
        self.w(u'<tr>')
        self.w(u'<th style="width: 10%%;">%s</th>' % user.view('oneline'))
        skills = self.skills
        width = int(90 / len(skills))
        celltemplate1 = u'<td %%sstyle="width: %s%%%%">[<a href="%%s">+</a>]</td>' % width
        celltemplate2 = u'<td %%sstyle="width: %s%%%%">&nbsp;</td>' % width
        for skill in skills:
            user_can_update = (user.eid == ruser.eid) or ruser.is_in_group('managers')
            try:
                master = self.masters_dict[user.eid][skill.name]
            except KeyError:  # skill or even user might not be present
                master = None
            if master is None:
                if user_can_update:
                    url = self.add_masters_url(user, skill.eid, __redirectpath=relpath)
                    self.w(celltemplate1 % (u'', xml_escape(url)))
                else:
                    self.w(celltemplate2 % u'')
            else:
                attrs = u'class="l%s" ' % master.rate
                if user_can_update:
                    url = master.absolute_url(vid='edition', __redirectpath=relpath)
                    self.w(celltemplate1 % (attrs, xml_escape(url)))
                else:
                    self.w(celltemplate2 % attrs)
        self.w(u'</tr>')

    def add_masters_url(self, user, skilleid, **kwargs):
        linkto = ('foruser:%s:subject' % user.eid,
                  'skill:%s:subject' % skilleid)
        return self._cw.build_url('add/Masters', __linkto=linkto, **kwargs)

    @property
    @cached
    def skills(self):
        rset = self._cw.execute('Any F,N ORDERBY N WHERE F is Folder, F name N')
        return list(rset.entities())

    def prefetch_skills(self):
        """computes once and for all each skill rate for each user.

        :returns: a dict mapping user eid to a subdict mapping skillname
                  to masters object
        """
        rset = self._cw.execute('Any U,M,R,N WHERE M is Masters, M rate R, M foruser U, '
                                'M skill S, S is Folder, S name N, U eid IN (%s)'
                                % ','.join(str(row[0]) for row in self.cw_rset))
        masters_dict = {}
        for rowidx, (ueid, meid, rate, skillname) in enumerate(rset):
            masters = rset.get_entity(rowidx, 1)
            masters_dict.setdefault(ueid, {})[skillname] = masters
        return masters_dict


class SkillMatrixExport(CSVMixIn, EntityView):
    __regid__ = 'skillmat-export'
    __select__ = is_instance('CWUser')

    def call(self):
        users_skills = self._cw.execute(
            "Any L,R,N WHERE M is Masters, M rate R, M foruser U, "
            "M skill S, S is Folder, S name N, U login L, U eid IN (%s)"
            % ','.join(str(row[0]) for row in self.cw_rset)
        )
        dataframe = pd.DataFrame(
            users_skills,
            columns=["login", "rate", "skill_name"]
        )
        self.w(
            dataframe.pivot_table(
                index="login", columns="skill_name", values="rate",
            ).to_csv()
        )


class ExportMatrixAction(action.Action):
    __regid__ = 'skillmat-export-action'
    __select__ = (
        action.Action.__select__
        & is_instance("CWUser")
        & match_view("matrix")
    )

    category = "mainactions"
    title = _("export SkillMatrix")

    def url(self):
        return self._cw.build_url(rql=self.cw_rset.rql, vid="skillmat-export")
