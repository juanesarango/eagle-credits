"""These messages are called when it initialises for accessing them more easily."""

import endpoints
from protorpc import messages
from protorpc import message_types

from api.messages.client_api_messages import ClientRequest
from api.messages.client_api_messages import ClientResponse
from api.messages.client_api_messages import ClientListResponse


# This Resource container is created for reading parameters from the URL request
ID_resource = endpoints.ResourceContainer(
    ClientRequest,
    id=messages.IntegerField(1, variant=messages.Variant.INT64, required=True)
)
