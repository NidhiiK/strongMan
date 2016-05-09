from ..models import Connection
from .. import forms
from django.shortcuts import render, redirect
from django.contrib import messages


class UpdateHandler:
    def __init__(self, request, id):
        self.request = request
        self.id = id

    @property
    def connection(self):
        return Connection.objects.get(pk=self.id).subclass()

    @property
    def parameter_dict(self):
        parameters = self.request.POST.copy()
        parameters['connection_id'] = self.id
        return parameters

    def _render(self, form=None):
        if form is None:
            form = forms.add_wizard.ConnectionForm().subclass(self.connection)
            form.fill(self.connection)
        return render(self.request, 'connections/Detail.html', {"form": form, "connection": self.connection})

    def _abstract_form(self):
        '''
        Intiates and validates the Abstract form
        :return Valid abstract form
        '''
        form = forms.AbstractConForm(self.parameter_dict)
        if not form.is_valid():
            raise Exception("No valid form detected." + str(form.errors))
        return form

    def handle(self):
        if self.request.method == "GET":
            return self._render()
        elif self.request.method == "POST":
            abstract_form = self._abstract_form()
            form_class = abstract_form.current_form_class

            form = form_class(self.parameter_dict)
            form.update_certificates()
            if not form.is_valid():
                return self._render(form)

            form.update_connection(self.id)
            messages.success(self.request,"Connection has been updated.")
            return self._render(form)


