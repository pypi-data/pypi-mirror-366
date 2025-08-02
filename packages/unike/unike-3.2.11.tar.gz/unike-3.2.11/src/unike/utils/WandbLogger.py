# coding:utf-8
#
# unike/utils/WandbLogger.py
#
# created by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on Jan 1, 2024
# updated by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on Feb 24, 2024
#
# 该脚本定义了 WandbLogger 类.

"""
WandbLogger - 使用 Weights and Biases 记录实验结果。
"""

import wandb
import swanlab
from typing import Literal, Any, Optional
from accelerate import Accelerator
from types import SimpleNamespace


class WandbLogger:
    """使用 `Weights and Biases <https://docs.wandb.ai/>`_ 记录实验结果。"""

    def __init__(self, endpoint: Literal['wandb', 'swanlab'] = 'wandb'):

        """创建 WandbLogger 对象。
        
        :param endpoint: 使用 wandb 还是 swanlab 记录实验结果
        :type endpoint: Literal['wandb', 'swanlab']
        """
        self.config: SimpleNamespace = SimpleNamespace()
        self.endpoint = endpoint
        self.logger: Any = None

        self.project: str = 'UniKE'
        self.name: str = ''
        self.offline = False

    def set_config(self, project: str, name: str, config: dict[str, Any] | None = None, offline: bool = False) -> 'WandbLogger':
        """设置项目名称和配置。
        
        :param project: wandb 的项目名称
        :type project: str
        :param name: wandb 的 run name
        :type name: str
        :param config: wandb 的项目配置如超参数。
        :type config: dict[str, Any] | None
        :param offline: 是否离线模式
        :type offline: bool
        """
        self.project = project
        self.name = name
        self.offline = offline
        if config:
            self.config: SimpleNamespace = SimpleNamespace(**config)
        return self

    def _init(self):
        if self.logger is not None:
            return
        if self.endpoint == 'wandb':
            if not self.offline:
                wandb.login()
            wandb.init(project=self.project, name=self.name, config=self.config.__dict__, mode='offline' if self.offline else 'online')
            self.logger = wandb
        elif self.endpoint == 'swanlab':
            if not self.offline:
                swanlab.login()
            swanlab.init(project=self.project, name=self.name, config=self.config.__dict__, mode='offline' if self.offline else 'online')
            self.logger = swanlab

    def log(self, *args, **kwargs):
        """记录日志"""
        self.logger.log(*args, **kwargs)

    def finish(self):
        """关闭日志"""
        if isinstance(self.logger, Accelerator):
            self.logger.end_training()
        else:
            self.logger.finish()
