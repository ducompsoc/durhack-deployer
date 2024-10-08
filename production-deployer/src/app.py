from flask import Flask, request, make_response
from werkzeug.routing import Rule
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# in development, the app is behind https://smee.io
# in production, the app is behind nginx
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1,
)

@app.route("/")
def root_route():
    return make_response({
        "status": 200, 
        "message": "OK",
        "service": "durhack-nginx-deployer",
    })
app.url_map.add(Rule('/', endpoint='method-not-allowed'))

@app.route("/github-webhook", methods=["POST"])
def github_webhook():
    content = request.json
    print(request.headers)
    
    # a few things need to happen here, mainly validation. We need to validate that:
    #  - the webhook payload came from GitHub (https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)
    #  - the request origin IP address is one of GitHub's (https://api.github.com/meta)
    #  - the event described by the payload is an event from the https://github.com/ducompsoc/durhack-nginx repository
    # if any of the above conditions fail, respond immediately with a 4xx status code.

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
def catch_all(path):
    return make_response({"status": 404, "message": "Not Found"}, 404)

@app.endpoint('method-not-allowed')
def method_not_allowed():
    return make_response({
        "status": 405,
        "message": "Method Not Allowed",
    }, 405)

if __name__ == '__main__':
    app.run()
