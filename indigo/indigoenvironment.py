from golem.docker.image import DockerImage
from golem.docker.environment import DockerEnvironment


class IndigoRendererEnvironment(DockerEnvironment):
    INDIGO_RENDERER_DOCKER_IMAGE = "golemfactory/indigorenderer"

    @classmethod
    def get_id(cls):
        return "INDIGO_RENDERER"

    def __init__(self, tag="0.1", image_id=None):
        image = DockerImage(image_id=image_id) if image_id \
            else DockerImage(self.INDIGO_RENDERER_DOCKER_IMAGE, tag=tag)
        DockerEnvironment.__init__(self, [image])

        self.short_description = "Indigo Renderer(https://www.indigorenderer.com/)"

    def get_performance(self, cfg_desc):
        return cfg_desc.estimated_lux_performance