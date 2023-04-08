from azure.functions import HttpRequest, HttpResponse

from slack_bolt.app import App
from slack_bolt.oauth import OAuthFlow
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse


def to_bolt_request(req: HttpRequest) -> BoltRequest:
    HttpRequest
    return BoltRequest(  # type: ignore
        body=req.get_body().decode("utf-8"),
        query=req.params,
        headers=req.headers,  # type: ignore
    )  # type: ignore


def to_azure_response(bolt_resp: BoltResponse) -> HttpResponse:
    resp: HttpResponse = HttpResponse(bolt_resp.body, bolt_resp.status)
    for k, values in bolt_resp.headers.items():
        if k.lower() == "content-type" and resp.headers.get("content-type") is not None:
            # Remove the one set by Azure Functions
            resp.headers.pop("content-type")
        for v in values:
            resp.headers.add_header(k, v)
    return resp


class SlackRequestHandler:
    def __init__(self, app: App):  # type: ignore
        self.app = app

    def handle(self, req: HttpRequest) -> HttpResponse:
        if req.method == "GET":
            if self.app.oauth_flow is not None:
                oauth_flow: OAuthFlow = self.app.oauth_flow
                if req.url == oauth_flow.install_path:
                    bolt_resp = oauth_flow.handle_installation(to_bolt_request(req))
                    return to_azure_response(bolt_resp)
                elif req.url == oauth_flow.redirect_uri_path:
                    bolt_resp = oauth_flow.handle_callback(to_bolt_request(req))
                    return to_azure_response(bolt_resp)
        elif req.method == "POST":
            bolt_resp: BoltResponse = self.app.dispatch(to_bolt_request(req))
            return to_azure_response(bolt_resp)

        return HttpResponse("Not Found", 404)
