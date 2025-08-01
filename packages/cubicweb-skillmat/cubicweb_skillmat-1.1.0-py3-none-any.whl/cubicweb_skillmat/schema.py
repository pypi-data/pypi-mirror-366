from yams.buildobjs import (EntityType, SubjectRelation, RelationDefinition,
                            String, Datetime, Int)
from yams.constraints import IntervalBoundConstraint

from cubicweb.schema import ERQLExpression

from cubicweb_folder.schema import Folder

from cubicweb import _


class Masters(EntityType):  # XXX find a suitable name
    """relation promoted to EntityType to store the `rate` attribute
    """
    __permissions__ = {'read': ('managers', 'users'),
                       'add': ('managers', ERQLExpression('X foruser U')),
                       'update': ('managers', 'owners'),
                       'delete': ('managers',),
                       }
    rate = Int(required=True, constraints=[IntervalBoundConstraint(minvalue=0, maxvalue=5)])
    foruser = SubjectRelation('CWUser', cardinality='1*')
    skill = SubjectRelation(('Technology', 'Folder'), cardinality='1*')


class Technology(Folder):
    pass


class Talk(EntityType):
    """relation promoted to EntityType to store the `subject' attribute
    """
    subject = String(required=True, fulltextindexed=True, indexed=True, maxsize=32)
    description = String(fulltextindexed=True,
                         description=_('more detailed subject description'))
    talktime = Datetime(description=_('estimated presentation date'))
    presented_by = SubjectRelation('CWUser', cardinality='?*')
    attended_by = SubjectRelation('CWUser', cardinality='**')
    talks_about = SubjectRelation(('Technology', 'Folder'), cardinality='+*')


class comments(RelationDefinition):
    subject = 'Comment'
    object = 'Talk'
    cardinality = '1*'
    composite = 'object'

# extend CWUser


class wishes_to_learn(RelationDefinition):
    subject = 'CWUser'
    object = ('Technology', 'Folder')


class interested_in(RelationDefinition):
    subject = 'CWUser'
    object = 'Talk'
