from protorpc import messages


class ClientResponse(messages.Message):
    id = messages.IntegerField(1)
    documento = messages.IntegerField(2)
    ruta = messages.StringField(3)
    nombres = messages.StringField(4)
    apellidos = messages.StringField(5)
    dir_casa = messages.StringField(6)
    tel_casa = messages.IntegerField(7)
    celular = messages.IntegerField(8)
    nombre_est = messages.StringField(9)
    dir_est = messages.StringField(10)
    creditos = messages.StringField(11, repeated=True)
    consecutivo = messages.IntegerField(12)


class ClientListResponse(messages.Message):
    clientes = messages.MessageField(ClientResponse, 1, repeated=True)
    count = messages.IntegerField(2)


class ClientRequest(messages.Message):
    documento = messages.IntegerField(1)
    ruta = messages.StringField(2)
    nombres = messages.StringField(3)
    apellidos = messages.StringField(4)
    dir_casa = messages.StringField(5)
    tel_casa = messages.IntegerField(6)
    celular = messages.IntegerField(7)
    nombre_est = messages.StringField(8)
    dir_est = messages.StringField(9)
