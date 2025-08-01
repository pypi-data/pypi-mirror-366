import unittest

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb import Unauthorized


class SecurityTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            self.skill = cnx.create_entity("Folder", name=u'python')
            self.u1 = self.create_user(cnx, u'joe', password=u'joe')
            self.u2 = self.create_user(cnx, u'jack', password=u'jack')
            self.master = cnx.create_entity('Masters', rate=3, foruser=self.u1,
                                            skill=self.skill)
            cnx.commit()

    def test_admin_can_update(self):
        with self.admin_access.cnx() as cnx:
            eid = self.master.eid
            cnx.execute('SET M rate 4 WHERE M eid %s' % eid)
            cnx.commit()
            self.assertEqual(cnx.execute('Any R WHERE M eid %s, M rate R' % eid)[0][0], 4)

    def test_owner_can_update(self):
        with self.new_access(u'joe').cnx() as cnx:
            eid = self.master.eid
            cnx.execute('SET M rate 4 WHERE M eid %s' % eid)
            cnx.commit()
            self.assertEqual(cnx.execute('Any R WHERE M eid %s, M rate R' % eid)[0][0], 4)

    def test_others_cannot_update(self):
        with self.new_access(u'jack').cnx() as cnx:
            eid = self.master.eid
            cnx.execute('SET M rate 4 WHERE M eid %s' % eid)
            self.assertRaises(Unauthorized, cnx.commit)
            self.assertEqual(cnx.execute('Any R WHERE M eid %s, M rate R' % eid)[0][0], 3)


if __name__ == '__main__':
    unittest.main()
