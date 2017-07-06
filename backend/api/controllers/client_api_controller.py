"""This is the controller for all the clients API"""

import time
import endpoints
from protorpc import message_types

from api import eagle_api
from api.controllers import BaseApiController
from api.helpers import ClientApiHelper

from api.messages import ClientListResponse
from api.messages import ClientRequest
from api.messages import ID_resource

from core.models import Cliente
from core.helpers import ClientHelper


@eagle_api.api_class(resource_name='clientes', path='cliente')
class ClientEndpoint(BaseApiController):
    @endpoints.method(message_types.VoidMessage, ClientListResponse,
                      path='/cliente', http_method='GET',
                      name='get_all')
    def get_clients(self, request):
        clientes = Cliente.query().fetch()
        return ClientListResponse(clientes=[ClientApiHelper().to_message(cliente) for cliente in clientes if clientes])

    @endpoints.method(ClientRequest, ClientListResponse,
                      path='/cliente', http_method='POST',
                      name='create')
    def create_client(self, request):
        if not (request.documento and request.ruta and request.nombres and request.apellidos):
            raise endpoints.BadRequestException('Los datos: documento, ruta, nombres y apellidos, son obligatorios.')
        alert = ClientHelper.nuevo_registro(request.documento, request.ruta, request.nombres, request.apellidos,
                                            request.dir_casa, request.tel_casa, request.celular, request.nombre_est,
                                            request.dir_est)
        if alert[0] == "alert-danger":
            raise endpoints.BadRequestException(alert[1])
        time.sleep(1)
        clientes = Cliente.query().fetch()
        return ClientListResponse(clientes=[ClientApiHelper().to_message(cliente) for cliente in clientes if clientes])

    @endpoints.method(ID_resource, ClientListResponse,
                      path='{id}', http_method='PUT',
                      name='update')
    def update_client(self, request):
        cliente = Cliente.get_by_id(request.id)
        if not cliente:  # If the stock doesn't exist, raise an error
            raise endpoints.BadRequestException("El ID de ese cliente no existe")
        if not (request.documento and request.ruta and request.nombres and request.apellidos):
            raise endpoints.BadRequestException('Los datos: documento, ruta, nombres y apellidos, son obligatorios.')
        alert = ClientHelper.actualizar_registro(
            cliente.key, request.documento, request.ruta, request.nombres, request.apellidos, request.dir_casa,
            request.tel_casa, request.celular, request.nombre_est, request.dir_est)
        if alert[0] == "alert-danger":
            raise endpoints.BadRequestException(alert[1])
        time.sleep(1)
        clientes = Cliente.query().fetch()
        return ClientListResponse(clientes=[ClientApiHelper().to_message(cliente) for cliente in clientes if clientes])

    @endpoints.method(ID_resource, ClientListResponse,
                      path='{id}', http_method='DELETE',
                      name='delete')
    def delete_client(self, request):
        cliente = Cliente.get_by_id(request.id)
        if not cliente:  # If the stock doesn't exist, raise an error
            raise endpoints.BadRequestException("El ID de ese cliente no existe")
        cliente.key.delete()  # If the stock exists, it removes it from the database
        time.sleep(1)
        clientes = Cliente.query().fetch()
        return ClientListResponse(clientes=[ClientApiHelper().to_message(cliente) for cliente in clientes if clientes])
