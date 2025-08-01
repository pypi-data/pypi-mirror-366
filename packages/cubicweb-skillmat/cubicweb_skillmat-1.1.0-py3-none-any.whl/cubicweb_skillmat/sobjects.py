"""this contains the server-side objects"""

from cubicweb.server.hook import Hook, match_rtype


class OnNewMastersHook(Hook):
    """adds owned_by relation betweem the Masters and the targeted user
    """
    __regid__ = 'skillmat_set_owner_when_set_foruser'
    __select__ = Hook.__select__ & match_rtype('foruser')
    events = ('after_add_relation',)

    def __call__(self):
        self._cw.execute('SET M owned_by U WHERE M eid %(m)s, U eid %(u)s, NOT M owned_by U',
                         {'m': self.eidfrom, 'u': self.eidto})
