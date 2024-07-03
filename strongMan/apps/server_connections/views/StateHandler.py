from django.http import JsonResponse

from strongMan.apps.server_connections.models.connections import Connection


class StateHandler(object):
    def __init__(self, request, id):
        self.request = request
        self.id = id

    @property
    def connection(self):
        return Connection.objects.get(pk=self.id).subclass()

    def handle(self):
        response = dict(id=self.connection.id, success=True)
        response['state'] = self.connection.state

   
       # Include PSK information 
        if hasattr(self.connection, 'psk'):
            response['psk'] = self.connection.psk.psk_value


        return JsonResponse(response)
