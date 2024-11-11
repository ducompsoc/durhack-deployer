import hashlib
import hmac
import unittest

from flask import make_response
from werkzeug.exceptions import Forbidden, BadRequest, HTTPException


class PayloadSignatureVerifier:
    def __init__(self, secret_token: str) -> None:
        self.encoded_secret_token = secret_token.encode('utf-8')

    # https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries#python-example
    def verify(self, payload_body: bytes, signature_header: str | None) -> None:
        """Verify that the payload was sent from GitHub by validating SHA256.

        Raise and return 403 if not authorized.

        Args:
            payload_body: original request body to verify (request.body())
            signature_header: header received from GitHub (x-hub-signature-256)
        """
        if signature_header is None:
            raise BadRequest(response=make_response({
                "status": 400,
                "message": "Bad Request",
                "description": "X-Hub-Signature-256 header is missing",
            }, 400))
        hash_object = hmac.new(self.encoded_secret_token, msg=payload_body, digestmod=hashlib.sha256)
        expected_signature = "sha256=" + hash_object.hexdigest()
        if not hmac.compare_digest(expected_signature, signature_header):
            raise Forbidden(response=make_response({
                "status": 403,
                "message": "Forbidden",
                "description": "X-Hub-Signature-256 header didn't match expected signature",
            }, 403))


class VerifySignatureTest(unittest.TestCase):
    # https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries#testing-the-webhook-payload-validation
    def test_example(self):
        verifier = PayloadSignatureVerifier("It's a Secret to Everybody")
        try:
            verifier.verify(
                "Hello, World!".encode('utf-8'),
                "sha256=757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46f4379c8b043e17"
            )
        except HTTPException:
            self.fail("verify_signature should not raise any errors using the GitHub-provided example")

    def test_missing_signature_header(self):
        verifier = PayloadSignatureVerifier("It's a Secret to Everybody")
        self.assertRaises(
            HTTPException,
            verifier.verify,
            "Hello, World!".encode('utf-8'),
            None,
        )


if __name__ == "__main__":
    unittest.main()
