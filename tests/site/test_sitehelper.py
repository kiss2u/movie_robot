import asyncio
import os
import unittest

from mbot.site.ptsitetest import PTSiteTest


class TestSiteHelper(unittest.TestCase):
    def test_mteam(self):
        test = PTSiteTest(os.path.join(os.path.abspath('../..'), 'app', 'sites/mteam.yml'),
                          '换你自己的ck')
        asyncio.run(test.start_test())
