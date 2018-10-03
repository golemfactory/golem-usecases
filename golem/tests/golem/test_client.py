# pylint: disable=protected-access,too-many-lines
import datetime
import json
import os
import time
import uuid
from random import Random
from types import MethodType
from unittest import mock
from unittest import TestCase
from unittest.mock import (
    MagicMock,
    Mock,
    patch,
)

from ethereum.utils import denoms
from freezegun import freeze_time
from pydispatch import dispatcher
from twisted.internet.defer import Deferred

from apps.dummy.task.dummytask import DummyTask
from apps.dummy.task.dummytaskstate import DummyTaskDefinition
import golem
from golem import model
from golem import testutils
from golem.client import Client, ClientTaskComputerEventListener, \
    DoWorkService, MonitoringPublisherService, \
    NetworkConnectionPublisherService, \
    ResourceCleanerService, TaskArchiverService, \
    TaskCleanerService
from golem.clientconfigdescriptor import ClientConfigDescriptor
from golem.core.common import timeout_to_string
from golem.core.deferred import sync_wait
from golem.core.simpleserializer import DictSerializer
from golem.environments.environment import Environment as DefaultEnvironment
from golem.manager.nodestatesnapshot import ComputingSubtaskStateSnapshot
from golem.network.p2p.node import Node
from golem.network.p2p.p2pservice import P2PService
from golem.network.p2p.peersession import PeerSessionInfo
from golem.report import StatusPublisher
from golem.resource.dirmanager import DirManager
from golem.rpc.mapping.rpceventnames import UI, Environment
from golem.task.acl import Acl
from golem.task.taskbase import Task
from golem.task.taskserver import TaskServer
from golem.task.taskstate import TaskState, TaskStatus, SubtaskStatus, \
    TaskTestStatus
from golem.task.tasktester import TaskTester
from golem.tools import testwithreactor
from golem.tools.assertlogs import LogTestCase

from .ethereum.test_fundslocker import make_mock_task as \
    make_fundslocker_mock_task

random = Random(__name__)


@patch('signal.signal')  # pylint: disable=too-many-ancestors
@patch('golem.network.p2p.node.Node.collect_network_info')
class TestClientRPCMethods(TestClientBase, LogTestCase):
    def test_run_benchmark(self, *_):
        from apps.blender.blenderenvironment import BlenderEnvironment
        from apps.blender.benchmark.benchmark import BlenderBenchmark
        from apps.lux.luxenvironment import LuxRenderEnvironment            #deleted
        from apps.lux.benchmark.benchmark import LuxBenchmark               #deleted

        benchmark_manager = self.client.task_server.benchmark_manager
        benchmark_manager.run_benchmark = Mock()
        benchmark_manager.run_benchmark.side_effect = lambda b, tb, e, c, ec: \
            c(True)

        with self.assertRaisesRegex(Exception, "Unknown environment"):
            sync_wait(self.client.run_benchmark(str(uuid.uuid4())))

        sync_wait(self.client.run_benchmark(BlenderEnvironment.get_id()))

        assert benchmark_manager.run_benchmark.call_count == 1
        assert isinstance(benchmark_manager.run_benchmark.call_args[0][0],
                          BlenderBenchmark)

        sync_wait(self.client.run_benchmark(LuxRenderEnvironment.get_id())) #deleted

        assert benchmark_manager.run_benchmark.call_count == 2              #deleted
        assert isinstance(benchmark_manager.run_benchmark.call_args[0][0],  #deleted
                          LuxBenchmark)                                     #deleted

        result = sync_wait(self.client.run_benchmark(                       #deleted
            DefaultEnvironment.get_id()))                                   #deleted
        assert result > 100.0                                               #deleted
        assert benchmark_manager.run_benchmark.call_count == 2

 