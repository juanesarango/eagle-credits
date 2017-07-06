"""This controller is the base parent. Here all common API members are defined."""

from protorpc import remote

class BaseApiController(remote.Service):  # pylint: disable=too-few-public-methods
    """base for the remote service API"""
    pass
