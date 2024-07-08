import sys

from django import forms
from strongMan.apps.server_connections.forms.SubForms import HeaderForm, RemoteCertificateForm, \
    RemoteIdentityForm, ServerCertificateForm, EapForm, EapCertificateForm, EapTlsForm, PoolForm
from strongMan.apps.server_connections.models.connections import IKEv2Certificate, IKEv2EAP, \
    IKEv2CertificateEAP, IKEv2EapTls, Ike2Psk, Connection


# from django import forms

class ProposalForm(forms.Form):
    encryption_algorithm_choices = [
        ("AES128", "AES128"),
        ("AES192", "AES192"),
        ("AES256", "AES256"),
        ("AES16-GCM", "AES16-GCM"),
        ("AES12-GCM", "AES12-GCM"),
        ("AES8-GCM", "AES8-GCM"),
        ("AES16-CCM", "AES16-CCM"),
        ("AES12-CCM", "AES12-CCM"),
        ("AES8-CCM", "AES8-CCM"),
        ("CHACHA20_POLY1305", "CHACHA20_POLY1305"),
    ]

    hash_option_choices = [
        ("SHA1", "SHA1"),
        ("SHA224", "SHA224"),
        ("SHA256", "SHA256"),
        ("SHA384", "SHA384"),
        ("SHA512", "SHA512"),
        ("md5"),("md5"),
    ]

    dh_group_choices = [
        ("MODP3072", "MODP3072"),
        ("MODP4096", "MODP4096"),
        ("MODP6144", "MODP6144"),
        ("MODP8192", "MODP8192"),
        ("MODP2048", "MODP2048"),
        ("MODP1024", "MODP1024"),
        ("MODP768", "MODP768"),
        ("CURVE25519", "CURVE25519"),
        ("CURVE448", "CURVE448"),
        ("ECP_256", "ECP_256"),
        ("ECP_384", "ECP_384"),
        ("ECP_521", "ECP_521"),
        ("ECP_224", "ECP_224"),
        ("ECP_192", "ECP_192"),
    ]

    encryption_algorithm = forms.ChoiceField(choices=encryption_algorithm_choices)
    hash_option = forms.ChoiceField(choices=hash_option_choices)
    dh_group = forms.ChoiceField(choices=dh_group_choices)




class AbstractDynamicForm(forms.Form):
    refresh_choices = forms.CharField(max_length=10, required=False)
    current_form = forms.CharField(max_length=100, required=True)

    @property
    def current_form_class(self):
        current_form_name = self.cleaned_data["current_form"]
        return getattr(sys.modules[__name__], current_form_name)

    @property
    def template(self):
        raise NotImplementedError

    def update_certs(self):
        pass


class ChooseTypeForm(AbstractDynamicForm):
    form_name = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(ChooseTypeForm, self).__init__(*args, **kwargs)
        if 'remote_access' in args:
            self.fields['form_name'].choices = ChooseTypeForm.get_choices_remote_access()
        if 'site_to_site' in args:
            self.fields['form_name'].choices = ChooseTypeForm.get_choices_site_to_site()

    @property
    def selected_form_class(self):
        name = self.cleaned_data["form_name"]
        return getattr(sys.modules[__name__], name)

    @property
    def template(self):
        return "server_connections/forms/ChooseType.html"

    @classmethod
    def get_choices_remote_access(cls):
        return tuple(
                tuple((type(subclass()).__name__, subclass().model.choice_name)) for subclass in
                AbstractConnectionForm.__subclasses__())

    @classmethod
    def get_choices_site_to_site(cls):
        return tuple((
            tuple((type(Ike2CertificateForm()).__name__, Ike2CertificateForm().model.choice_name)),
            tuple((type(Ike2EapTlsForm()).__name__, Ike2EapTlsForm().model.choice_name)),
            ######### adding psk option #######
            tuple((type(Ike2PskForm()).__name__, Ike2PskForm().model.choice_name))
        ))


class AbstractConnectionForm(AbstractDynamicForm):

    def is_valid(self):
        valid = True
        # Call is_valid method for every base class
        for base in self.__class__.__bases__:
            if base == AbstractConnectionForm:
                continue
            if hasattr(base, "is_valid"):
                valid = base.is_valid(self)
                if not valid:
                    valid = False
        return valid

    def create_connection(self, connection_type):
        connection = self.model(profile=self.cleaned_data['profile'], version=self.cleaned_data['version'],
                                pool=self.cleaned_data['pool'], connection_type=connection_type,
                                send_certreq=self.cleaned_data["send_certreq"],
                                initiate=self.cleaned_data["initiate"])
        connection.save()
        # Call create_connection method for every base class
        for base in self.__class__.__bases__:
            if base == AbstractConnectionForm:
                continue
            if hasattr(base, "create_connection"):
                base.create_connection(self, connection)
        return connection

    def update_connection(self, pk):
        connection = self.model.objects.get(id=pk)
        for base in self.__class__.__bases__:
            if base == AbstractConnectionForm:
                continue
            if hasattr(base, "update_connection"):
                base.update_connection(self, connection)
        return connection

    def fill(self, connection):
        # Call fill method for every base class
        for base in self.__class__.__bases__:
            if base == AbstractConnectionForm:
                continue
            if hasattr(base, "fill"):
                base.fill(self, connection)

    @classmethod
    def get_models(cls):
        return tuple(
                tuple((subclass().model(), type(subclass()).__name__)) for subclass in cls.__subclasses__())

    @classmethod
    def subclass(self, connection):
        typ = type(connection)
        for model, form_name in self.get_models():
            if type(model) is typ:
                form_class = getattr(sys.modules[__name__], form_name)
                return form_class()
        return self


class Ike2CertificateForm(AbstractConnectionForm, HeaderForm, ServerCertificateForm, RemoteCertificateForm,
                          RemoteIdentityForm, PoolForm):

    @property
    def model(self):
        return IKEv2Certificate

    @property
    def template(self):
        return "server_connections/forms/Ike2Certificate.html"

    def update_certs(self):
        self.update_certificates()


class Ike2EapForm(AbstractConnectionForm, HeaderForm, RemoteCertificateForm, RemoteIdentityForm, EapForm,
                  PoolForm):
    @property
    def model(self):
        return IKEv2EAP

    @property
    def template(self):
        return "server_connections/forms/Ike2EAP.html"

    def update_certs(self):
        self.update_certificates()


class Ike2EapCertificateForm(AbstractConnectionForm, HeaderForm, ServerCertificateForm,
                             RemoteCertificateForm, RemoteIdentityForm, EapCertificateForm, PoolForm):
    @property
    def model(self):
        return IKEv2CertificateEAP

    @property
    def template(self):
        return "server_connections/forms/Ike2EapCertificate.html"

    def update_certs(self):
        self.update_certificates()


class Ike2EapTlsForm(AbstractConnectionForm, HeaderForm, RemoteCertificateForm, RemoteIdentityForm,
                     EapTlsForm, PoolForm):
    @property
    def model(self):
        return IKEv2EapTls

    @property
    def template(self):
        return "server_connections/forms/Ike2EapTls.html"

    def update_certs(self):
        self.update_certificates()


from ..utils import generate_psk

class Ike2PskForm(AbstractConnectionForm, HeaderForm, RemoteCertificateForm, RemoteIdentityForm,
                     EapTlsForm, PoolForm):
    @property
    def model(self):
        return Ike2Psk

    @property
    def template(self):
        return "server_connections/forms/psk.html"

    # def update_certs(self):
    #     self.update_certificates()

    psk = forms.CharField(label="Pre-Shared Key", required=True, widget=forms.PasswordInput)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.psk:
            instance.psk = generate_psk()
        if commit:
            instance.save()
        return instance

    def save_psk(self):
        psk = self.cleaned_data.get('psk')
        if not psk:
            psk = generate_psk()
        connection = Connection.objects.create(
            profile=self.cleaned_data['profile'],
            psk=psk,
            # other fields
        )
        connection.save()
        return connection

