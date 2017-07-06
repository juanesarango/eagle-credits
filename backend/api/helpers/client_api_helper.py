"""This helper contains the methods use in the clients messages"""

from api.helpers import BaseApiHelper
from api.messages import ClientResponse

from core.models import Cliente


class ClientApiHelper(BaseApiHelper):
    """This helper contains the methods use in the clients messages"""

    _model = Cliente

    @staticmethod
    def to_message(entity):
        """Method to format the message sent."""
        return ClientResponse(
            id=entity.key.id(),
            documento=entity.documento,
            ruta=entity.ruta.urlsafe(),
            nombres=entity.nombres,
            apellidos=entity.apellidos,
            dir_casa=entity.dir_casa,
            tel_casa=entity.tel_casa,
            celular=entity.celular,
            nombre_est=entity.nombre_est,
            dir_est=entity.dir_est,
            creditos=[credito.key.urlsafe() for credito in entity.creditos if entity.creditos],
            consecutivo=entity.consecutivo,
            )
