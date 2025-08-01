"""skillmat boxes

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.predicates import is_instance, match_user_groups
from cubicweb_web import component


class EditWishesBox(component.EditRelationCtxComponent):
    __regid__ = 'edit-wishes'
    __select__ = (component.EditRelationCtxComponent.__select__
                  & is_instance('CWUser') & match_user_groups('owners'))

    rtype = 'wishes_to_learn'
    target = 'object'

    def mastered_skills(self, user, threshold=5):
        """return the list of mastered skills
        """
        rql = 'Any S,N WHERE M skill S, S name N, M rate >= %(r)s, M foruser U, U eid %(u)s'
        rset = self._cw.execute(rql, {'r': threshold, 'u': user.eid})
        return rset.entities()

    def unrelated_entities(self, euser):
        """filter skills for which the user already knows"""
        entities = super(EditWishesBox, self).unrelated_entities(euser)
        mastered = set(entity.eid for entity in self.mastered_skills(euser))
        return [entity for entity in entities if entity.eid not in mastered]


class EditAttendedByBox(component.EditRelationCtxComponent):
    __regid__ = 'edit-attended-by'
    __select__ = component.EditRelationCtxComponent.__select__ & is_instance('Talk')

    rtype = 'attended_by'
    target = 'object'

    # Todo : replace + et - in this box by a comprehensive label

    # def w_related(self, box, entity):
    #     """appends existing relations to the `box`"""
    #     rql = 'DELETE S %s O WHERE S eid %%(s)s, O eid %%(o)s' % self.rtype
    #     related = self.related_entities(entity)
    #     for etarget in related:
    #         box.append(self.box_item(entity, etarget, rql, u'assiste'))
    #     return len(related)

    # def w_unrelated(self, box, entity):
    #     """appends unrelated entities to the `box`"""
    #     rql = 'SET S %s O WHERE S eid %%(s)s, O eid %%(o)s' % self.rtype
    #     for etarget in self.unrelated_entities(entity):
    #         box.append(self.box_item(entity, etarget, rql, u'n\'assite pas'))
