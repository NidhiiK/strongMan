from django.shortcuts import render, redirect
from django.views import View
from ..forms import ProposalForm  # Import your ProposalForm from forms.py
from ..models import Proposal, Connection, Child  # Import necessary models

class IpsecOptionsHandler(View):
    
    def get(self, request, *args, **kwargs):
        encryption_algorithms = [
            "AES128",
            "AES192",
            "AES256",
            "AES16-GCM",
            "AES12-GCM",
            "AES8-GCM",
            "AES16-CCM",
            "AES12-CCM",
            "AES8-CCM",
            "CHACHA20_POLY1305"
        ]
        
        # Key lengths for the specified encryption algorithms
        key_lengths = {
            "AES128": [128, 96, 64],
            "AES192": [128, 96, 64],
            "AES256": [128, 96, 64],
            "AES16-GCM": [256, 192, 128],
            "AES12-GCM": [256, 192, 128],
            "AES8-GCM": [256, 192, 128],
            "AES16-CCM": [256, 192, 128],
            "AES12-CCM": [256, 192, 128],
            "AES8-CCM": [256, 192, 128],
            "CHACHA20_POLY1305": [256]
        }
    
        # Hash options
        hash_options = [
            "SHA1",
            "SHA224",
            "SHA256",
            "SHA384",
            "SHA512"
        ]
    
        # DH group options
        dh_groups = [
            "MODP3072",
            "MODP4096",
            "MODP6144",
            "MODP8192",
            "MODP2048",
            "MODP1024",
            "MODP768",
            "CURVE25519",
            "CURVE448",
            "ECP_256",
            "ECP_384",
            "ECP_521",
            "ECP_224",
            "ECP_192"
        ]
    
        form = ProposalForm()
    
        context = {
            'encryption_algorithms': encryption_algorithms,
            'key_lengths': key_lengths,
            'hash_options': hash_options,
            'dh_groups': dh_groups,
            'form': form
        }
    
        return render(request, 'Ike2Certificate.html', context)
    
    def post(self, request, *args, **kwargs):
        form = ProposalForm(request.POST)
    
        if form.is_valid():
            encryption_algorithm = form.cleaned_data['encryption_algorithm']
            hash_option = form.cleaned_data['hash_option']
            dh_group = form.cleaned_data['dh_group']
    
            proposal_type = f"{encryption_algorithm}-{hash_option}-{dh_group}"
    
            # Save the proposal to the database or process it as needed
            connection_id = request.POST.get('connection_id')
            child_id = request.POST.get('child_id')
    
            if connection_id:
                connection = Connection.objects.get(id=connection_id)
                Proposal(type=proposal_type, connection=connection).save()
    
            if child_id:
                child = Child.objects.get(id=child_id)
                Proposal(type=proposal_type, child=child).save()
    
            # Redirect to the page where the form was originally loaded
            return redirect('server_connections:ike2_certificate')
    
        # If form is not valid, re-render the form with errors
        context = {
            'form': form
        }
    
        return render(request, 'Ike2Certificate.html', context)
