import os
import unittest

from mbot.site.ptsitetest import PTSiteTest


class TestSiteHelper(unittest.TestCase):
    def test_mteam(self):
        test = PTSiteTest(os.path.join(os.path.abspath('../..'), 'app', 'sites/mteam.yml'),
                          '换上你自己的cookie')
        test.start_test()
