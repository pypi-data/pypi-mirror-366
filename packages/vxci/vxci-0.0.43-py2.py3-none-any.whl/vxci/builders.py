from docker import from_env
from vxci.common import is_dev_repo, is_main_branch
from vxci.errors import DuplicateBuilderError, NotImplementedError
import subprocess
import shlex
import sys
import logging


_logger = logging.getLogger('vxci.' + __name__)
BUILDER_REGISTRY = {}


def factory(config):
    builder = 'orchestsh' if config.get('orchestsh') else 'deployv'
    return BUILDER_REGISTRY[builder](config)


class BaseBuilder():

    def __init__(self, config):
        self._cfg = config
        self._cli = from_env(timeout=7200).api

    def __init_subclass__(cls, **kwargs):
        super(BaseBuilder, cls).__init_subclass__(**kwargs)
        if cls.builder_name() in BUILDER_REGISTRY.keys():
            raise DuplicateBuilderError("The registry already has a builder named %s" % cls.builder_name())
        BUILDER_REGISTRY.update({cls.builder_name(): cls})

    @staticmethod
    def builder_name():
        return "base"

    def _format_build_cmd(self):
        raise NotImplementedError

    def build_image(self):
        cmd = self._format_build_cmd()
        _logger.info('Building image')
        try:
            subprocess.check_call(shlex.split(cmd))
        except subprocess.CalledProcessError:
            _logger.exception('Could not build the image, please read the log above')
            sys.exit(1)
        images = self._cli.images(self._cfg['instance_image'])
        if not images:
            _logger.error('Unable to find the recently built image. Expecting the image: %s', self._cfg['instance_image'])
            sys.exit(1)
        image_sha = images[0].get('Id')
        short_id = image_sha.split(':')[1][:10]
        tag = short_id
        git_sha = self._cfg["git_commit_sha"][:7]  # 7 is the default size "git rev-parse --short HEAD"
        if self._cfg.get('docker_image_repo'):
            tag = "%s-%s-%s" % (self._cfg['main_app'], self._cfg['version'], short_id)
            git_tag = "%s-%s-%s" % (self._cfg['main_app'], self._cfg['version'], git_sha)
            if is_dev_repo(self._cfg) and not is_main_branch(self._cfg):
                tag = "%s-%s-dev%s" % (self._cfg['main_app'], self._cfg['version'], short_id)
        self._cfg.update({'image_tag': tag, 'image_git_tag': git_tag})


class OrchestshBuilder(BaseBuilder):

    def __init__(self, config):
        super(OrchestshBuilder, self).__init__(config)

    @staticmethod
    def builder_name():
        return "orchestsh"

    def _format_build_cmd(self):
        cmd = (
            "orchestsh build -r %(url)s -b %(ref)s" % {
                "url": self._cfg['ci_repository_url'], "ref": self._cfg['ci_commit_ref_name']
            }
        )
        if self._cfg.get('push_image'):
            cmd += " --push"
        return cmd


class DeployvBuilder(BaseBuilder):

    def __init__(self, config):
        super(DeployvBuilder, self).__init__(config)

    @staticmethod
    def builder_name():
        return "deployv"

    def _format_build_cmd(self):
        cmd = (
            "deployvcmd build -b %(ref)s -u %(url)s -v %(version)s -i %(img)s -O %(repo)s#%(odoo_ref)s -T %(tag)s" % {
                "ref": self._cfg['ci_commit_ref_name'], "url": self._cfg['ci_repository_url'],
                "version": self._cfg['version'], "img": self._cfg['base_image'],
                "repo": self._cfg['odoo_repo'], "odoo_ref": self._cfg['odoo_branch'],
                "tag": self._cfg['instance_image']
            }
        )
        if not self._cfg.get('push_image'):
            cmd += " --skip-push"
        return cmd
