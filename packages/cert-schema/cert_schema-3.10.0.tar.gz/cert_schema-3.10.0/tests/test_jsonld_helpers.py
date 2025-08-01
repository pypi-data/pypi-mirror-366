import json
import unittest

from cert_schema import BlockcertValidationError
from cert_schema import normalize_jsonld, extend_preloaded_context, get_context_digests

class TestJsonldHelpers(unittest.TestCase):
    def test_v2_unmapped_fields(self):
        with self.assertRaises(BlockcertValidationError):
            with open('../examples/2.0-alpha/tampered_unmapped_fields.json') as data_f:
                certificate = json.load(data_f)
                normalize_jsonld(certificate, detect_unmapped_fields=True)

    def test_v2_preloaded_loader(self):
        with open('../examples/2.0-alpha/sample_valid.json') as data_f:
            certificate = json.load(data_f)
            normalize_jsonld(certificate, detect_unmapped_fields=True)

    def test_v2_unmapped_fields_with_vocab(self):
        with open('../examples/2.0-alpha/tampered_unmapped_fields_vocab.json') as data_f:
            certificate = json.load(data_f)
            normalize_jsonld(certificate, detect_unmapped_fields=True)

    def test_v2_1_unmapped_fields(self):
        with self.assertRaises(BlockcertValidationError):
            with open('../examples/2.1/tampered_unmapped_fields.json') as data_f:
                certificate = json.load(data_f)
                normalize_jsonld(certificate, detect_unmapped_fields=True)

    def test_v2_1_preloaded_loader(self):
        with open('../examples/2.1/sample_valid.json') as data_f:
            certificate = json.load(data_f)
            normalize_jsonld(certificate, detect_unmapped_fields=True)

    def test_v2_1_unmapped_fields_with_vocab(self):
        with open('../examples/2.1/tampered_unmapped_fields_vocab.json') as data_f:
            certificate = json.load(data_f)
            normalize_jsonld(certificate, detect_unmapped_fields=True)

    def test_v3_preloaded_loader(self):
        with open('../examples/3.0/bbba8553-8ec1-445f-82c9-a57251dd731c.json') as data_f:
            with open('./assertions/normalized-bbba8553-8ec1-445f-82c9-a57251dd731c.txt') as assertionFile:
                assertion = assertionFile.read()
                certificate = json.load(data_f)
                normalized = normalize_jsonld(certificate, detect_unmapped_fields=True)
                self.assertEqual(normalized, assertion)

    def test_v3_multisigned_preloaded_loader(self):
        with open('../examples/3.1/example.3.1.multisigned.json') as data_f:
            with open('./assertions/normalized-example.3.1.multisigned.txt') as assertionFile:
                with open('./fixtures/ed25519Context.json') as context_file:
                    cred_context = json.load(context_file)
                    assertion = assertionFile.read()
                    certificate = json.load(data_f)
                    extend_preloaded_context('https://w3id.org/security/suites/ed25519-2020/v1', cred_context)
                    normalized = normalize_jsonld(certificate, detect_unmapped_fields=True)
                    self.assertEqual(normalized,  assertion)

    def test_get_preloaded_digests(self):
        digests = get_context_digests('https://www.w3.org/ns/credentials/v2')
        expected = {
            'digestSRI': {
                'sha384': 'l/HrjlBCNWyAX91hr6LFV2Y3heB5Tcr6IeE4/Tje8YyzYBM8IhqjHWiWpr8+ZbYU'
            },
            'digestMultibase': {
                'sha256': 'uEiBZlVztZpfWHgPyslVv6-UwirFoQoRvW1htfx963sknNA'
            }
        }
        self.assertEqual(digests['digestSRI']['sha384'], expected['digestSRI']['sha384'])
        self.assertEqual(digests['digestMultibase']['sha256'], expected['digestMultibase']['sha256'])
