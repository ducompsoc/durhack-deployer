from ipaddress import ip_address

from flask import Flask, Response, request, make_response
from werkzeug.routing import Rule
from werkzeug.middleware.proxy_fix import ProxyFix

from config import config
from github_meta import ensure_ip_is_github_hooks_ip
from payload_signature_verifier import PayloadSignatureVerifier

app = Flask(__name__)
signature_verifier = PayloadSignatureVerifier(config.webhook_secret_token)

app.wsgi_app = ProxyFix(
    app.wsgi_app, **vars(config.proxy_fix)
)


@app.route("/")
def root_route() -> Response:
    return make_response({
        "status": 200,
        "message": "OK",
        "service": "durhack-nginx-deployer",
    })


app.url_map.add(Rule('/', endpoint='method-not-allowed'))


@app.route("/github-webhook", methods=["POST"])
async def github_webhook() -> Response:
    # ensure the request origin IP address is one of GitHub's (https://api.github.com/meta)
    remote_ip = ip_address(request.remote_addr)
    await ensure_ip_is_github_hooks_ip(remote_ip)

    # verify the webhook payload came from GitHub (https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)
    payload_body = request.get_data()
    signature_from_requester = request.headers.get("X-Hub-Signature-256")
    signature_verifier.verify(payload_body, signature_from_requester)

    payload = request.get_json()

    # Then, add the event to a queue for processing (this ensures we can always send a 2xx response to GitHub in a timely manner)
    # the event metadata needs to include
    # - the `X-GitHub-Event` request header (which contains the event type)
    # - the `X-GitHub-Delivery` request header (which contains a unique ID for the event represented by the payload)
    # - the request body

    # Finally, respond with a 2xx status code
    return make_response("", 204)


app.url_map.add(Rule('/github-webhook', endpoint='method-not-allowed'))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path) -> Response:
    return make_response({"status": 404, "message": "Not Found"}, 404)


@app.endpoint('method-not-allowed')
def method_not_allowed() -> Response:
    return make_response({
        "status": 405,
        "message": "Method Not Allowed",
    }, 405)


if __name__ == '__main__':
    app.run(host=config.listen.host, port=config.listen.port)
