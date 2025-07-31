"""
AIC Utils - AIC API wrapper and GitLab integration framework for pipeline management
"""

from .aic import AIC
from .gitlabmanager import GitLabManager
from .gitlab_init import GitLabRepositoryInitializer
from .dataset_converter import DatasetConverter
from .slack_logger import SlackLogger

__version__ = '2.0.0'
__author__ = 'Dylan D'

__all__ = [
    'AIC',
    'GitLabManager', 
    'GitLabRepositoryInitializer',
    'DatasetConverter',
    'SlackLogger'
]
