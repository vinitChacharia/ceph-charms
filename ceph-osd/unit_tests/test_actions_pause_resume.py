import mock

import sys

from test_utils import CharmTestCase

sys.path.append('hooks')

import pause_resume as actions


class PauseTestCase(CharmTestCase):

    def setUp(self):
        super(PauseTestCase, self).setUp(
            actions, ["check_call",
                      "get_local_osd_ids",
                      "set_unit_paused",
                      "assess_status"])

    def test_pauses_services(self):
        self.get_local_osd_ids.return_value = [5]
        actions.pause([])
        cmd = ['ceph', 'osd', 'out', '5']
        self.check_call.assert_called_once_with(cmd)
        self.set_unit_paused.assert_called_once_with()
        self.assess_status.assert_called_once_with()


class ResumeTestCase(CharmTestCase):

    def setUp(self):
        super(ResumeTestCase, self).setUp(
            actions, ["check_call",
                      "get_local_osd_ids",
                      "clear_unit_paused",
                      "assess_status"])

    def test_pauses_services(self):
        self.get_local_osd_ids.return_value = [5]
        actions.resume([])
        cmd = ['ceph', 'osd', 'in', '5']
        self.check_call.assert_called_once_with(cmd)
        self.clear_unit_paused.assert_called_once_with()
        self.assess_status.assert_called_once_with()


class MainTestCase(CharmTestCase):

    def setUp(self):
        super(MainTestCase, self).setUp(actions, ["action_fail"])

    def test_invokes_action(self):
        dummy_calls = []

        def dummy_action(args):
            dummy_calls.append(True)

        with mock.patch.dict(actions.ACTIONS, {"foo": dummy_action}):
            actions.main(["foo"])
        self.assertEqual(dummy_calls, [True])

    def test_unknown_action(self):
        """Unknown actions aren't a traceback."""
        exit_string = actions.main(["foo"])
        self.assertEqual("Action foo undefined", exit_string)

    def test_failing_action(self):
        """Actions which traceback trigger action_fail() calls."""
        dummy_calls = []

        self.action_fail.side_effect = dummy_calls.append

        def dummy_action(args):
            raise ValueError("uh oh")

        with mock.patch.dict(actions.ACTIONS, {"foo": dummy_action}):
            actions.main(["foo"])
        self.assertEqual(dummy_calls, ["Action foo failed: uh oh"])
