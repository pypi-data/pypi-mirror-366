import unittest

from cubicweb.devtools.testlib import CubicWebTC


class HookTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            self.skill = cnx.create_entity('Folder', name=u'python')
            self.u = self.create_user(cnx, u'joe', password=u'joe')
            cnx.commit()

    def test_owned_by_auto_set(self):
        """test owned_by insertion when all is inserted in 1 query"""
        with self.admin_access.cnx() as cnx:
            skilleid = self.skill.eid
            meid = cnx.execute('INSERT Masters M: M rate 3, M foruser U, M skill S WHERE '
                               'U eid %(u)s, S eid %(s)s', {'u': self.u.eid, 's': skilleid})[0][0]
            owners = cnx.execute('Any L WHERE U login L, M owned_by U, M eid %s' % meid)
            cnx.commit()
            self.assertSetEqual(set(row[0] for row in owners), set(('admin', 'joe')))

    def test_owned_by_auto_set_2(self):
        """test owned_by insertion when all is inserted in separate queries"""
        with self.admin_access.cnx() as cnx:
            skilleid = self.skill.eid
            meid = cnx.execute('INSERT Masters M: M rate 3, M foruser U, M skill S WHERE '
                               'S eid %(s)s', {'s': skilleid})[0][0]
            # should only owned by admin at this point
            owners = cnx.execute('Any L WHERE U login L, M owned_by U, M eid %s' % meid)
            cnx.commit()
            self.assertSetEqual(set(row[0] for row in owners), set(('admin',)))
            cnx.execute('SET M foruser U WHERE M eid %s, U eid %s' % (meid, self.u.eid))
            # should now be owned by admin and targeted user
            owners = cnx.execute('Any L WHERE U login L, M owned_by U, M eid %s' % meid)
            cnx.commit()
            self.assertSetEqual(set(row[0] for row in owners), set(('admin', 'joe')))

    def test_owned_by_auto_set_3(self):
        """test owned_by insertion when targeted user is the creator
        (all in one query)
        """
        with self.new_access(u'joe').cnx() as cnx:
            skilleid = self.skill.eid
            meid = cnx.execute('INSERT Masters M: M rate 3, M foruser U, M skill S WHERE '
                               'U eid %(u)s, S eid %(s)s', {'u': self.u.eid, 's': skilleid})[0][0]
            owners = cnx.execute('Any L WHERE U login L, M owned_by U, M eid %s' % meid)
            cnx.commit()
            self.assertSetEqual(set(row[0] for row in owners), set((u'joe',)))

    def test_owned_by_auto_set_4(self):
        """test owned_by insertion when targeted user is the creator"""
        with self.new_access(u'joe').cnx() as cnx:
            skilleid = self.skill.eid
            meid = cnx.execute('INSERT Masters M: M rate 3, M skill S WHERE '
                               'S eid %(s)s', {'s': skilleid})[0][0]
            # should only owned by admin at this point
            owners = cnx.execute('Any L WHERE U login L, M owned_by U, M eid %s' % meid)
            self.assertSetEqual(set(row[0] for row in owners), set(('joe',)))
            cnx.execute('SET M foruser U WHERE M eid %s, U eid %s' % (meid, self.u.eid))
            # should now be owned by admin and targeted user
            owners = cnx.execute('Any L WHERE U login L, M owned_by U, M eid %s' % meid)
            self.assertSetEqual(set(row[0] for row in owners), set(('joe',)))


if __name__ == '__main__':
    unittest.main()
