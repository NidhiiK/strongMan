from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from ..forms import HeaderForm
from ..models import Proposal, Connection, Child

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

        hash_options = [
            "SHA1",
            "SHA224",
            "SHA256",
            "SHA384",
            "SHA512"
        ]

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

        options = {
            'encryption_algorithms': encryption_algorithms,
            'key_lengths': key_lengths,
            'hash_options': hash_options,
            'dh_groups': dh_groups,
        }

        return JsonResponse(options)