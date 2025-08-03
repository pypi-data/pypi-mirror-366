# noinspection PyProtectedMember
# from dagster._core.libraries import DagsterLibraryRegistry
# from dagster_dingtalk.version import __version__

from dagster_qcloud_cos.resources import QcloudCosResource
from dagster_qcloud_cos.operations import InitCosOperations , cos_op

# DagsterLibraryRegistry.register("dagster-dingtalk", __version__)
