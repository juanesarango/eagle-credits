import endpoints

from api.controllers import ClientEndpoint

APPLICATION = endpoints.api_server([ClientEndpoint])
