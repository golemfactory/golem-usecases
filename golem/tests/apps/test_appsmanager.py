from apps.lux.luxenvironment import LuxRenderEnvironment


class TestAppsManager(TestCase):

    def test_get_env_list(self):
            assert any(isinstance(app, LuxRenderEnvironment) for app in apps)
