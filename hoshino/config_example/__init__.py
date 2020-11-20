import importlib
import os
from hoshino import log
from nonebot.default_config import *
from .__bot__ import *

# check correctness
RES_DIR = os.path.expanduser(RES_DIR)
assert RES_PROTOCOL in ('http', 'file', 'base64')

# load module configs
logger = log.new_logger('config', DEBUG)
for module in MODULES_ON:
    try:
        new_module = module.replace(os.sep,'.')
        importlib.import_module('hoshino.config.' + new_module)
        logger.info(f'Succeeded to load config of "{new_module}"')
    except ModuleNotFoundError:
        logger.warning(f'Not found config of "{new_module}"')
