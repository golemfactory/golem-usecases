# pylint: disable=protected-access
import os
import unittest.mock as mock

from tests.test_utils.assertlogs import LogTestCase
from golem_verificator.verifier import SubtaskVerificationState
from golem_verificator.lux_verifier import LuxRenderVerifier, logger
from golem_verificator.common.rendering_task_utils import AdvanceRenderingVerificationOptions
from tests.test_utils.pep8_conformance_test import Pep8ConformanceTest
from tests.test_utils.temp_dir_fixture import TempDirFixture


class TestLuxRenderVerifier(TempDirFixture, LogTestCase, Pep8ConformanceTest):

    PEP8_FILES = ['lux_verifier.py']

    def test_merge_flm_files_failure(self):
        subtask_info = {"tmp_dir": self.path,
                        'merge_ctd': {'extra_data': {'flm_files': []}},
                        'root_path': self.path}

        verification_data = dict()
        verification_data["subtask_info"] = subtask_info
        verification_data["results"] = []
        verification_data["reference_data"] = []
        verification_data["resources"] = []

        computer_cls = mock.Mock()
        computer_cls.return_value = computer_cls

        lux_render_verifier = LuxRenderVerifier(verification_data, computer_cls)
        lux_render_verifier.computer = None
        lux_render_verifier.test_flm = "test_flm"
        assert not lux_render_verifier.merge_flm_files("flm_file", subtask_info, "flm_output")
        assert lux_render_verifier.state == SubtaskVerificationState.NOT_SURE
        lux_render_verifier.computer = computer_cls()
        lux_render_verifier.computer.wait.return_value = None
        assert not lux_render_verifier.merge_flm_files("flm_file", subtask_info, "flm_output")
        lux_render_verifier.computer.wait.return_value = mock.Mock()
        lux_render_verifier.verification_error = True
        assert not lux_render_verifier.merge_flm_files("flm_file", subtask_info, "flm_output")
        lux_render_verifier.verification_error = False
        lux_render_verifier.computer.get_result.return_value = {
            'data': self.additional_dir_content([3])}
        assert not lux_render_verifier.merge_flm_files("flm_file", subtask_info, "flm_output")

        flm_file = os.path.join(self.path, "bla.flm")
        open(flm_file, 'w').close()
        lux_render_verifier.computer.get_result.return_value = {
            'data': self.additional_dir_content([1]) + [flm_file]}
        assert not lux_render_verifier.merge_flm_files("flm_file", subtask_info, "flm_output")
        stderr_file = os.path.join(self.path, "stderr.log")
        lux_render_verifier.computer.get_result.return_value = {'data': [flm_file, stderr_file]}
        assert not lux_render_verifier.merge_flm_files("flm_file", subtask_info, "flm_output")
        open(stderr_file, 'w').close()
        assert lux_render_verifier.merge_flm_files("flm_file", subtask_info, "flm_output")

        with open(stderr_file, 'w') as f:
            f.write("ERROR at merging files")

        assert not lux_render_verifier.merge_flm_files("flm_file", subtask_info, "flm_output")

    def test_flm_verify_failure(self):
        verification_data = dict()
        verification_data["subtask_info"] = {}
        verification_data["results"] = []
        verification_data["reference_data"] = []
        verification_data["resources"] = []
        computer_cls = mock.Mock()
        computer_cls.return_value = computer_cls

        lux_render_verifier = LuxRenderVerifier(verification_data, computer_cls)
        with self.assertLogs(logger, level="INFO"):
            lux_render_verifier._verify_flm_failure("Error in something")
        assert lux_render_verifier.verification_error
