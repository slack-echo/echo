from logging import Logger
from typing import Callable, Optional

from slack_bolt.authorization import AuthorizeResult
from slack_bolt.middleware import RequestVerification
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse

from utils.loader import read_yaml


def authorize(enterprise_id: str, team_id: str, logger: Logger) -> AuthorizeResult:
    secrets = read_yaml(".env.yaml")
    installations = secrets.get("INSTALLATIONS")
    for team in installations:
        # enterprise_id doesn't exist for some teams
        is_valid_enterprise = (
            True
            if "enterprise_id" not in team or enterprise_id == team["enterprise_id"]
            else False
        )
        if is_valid_enterprise and (team["team_id"] == team_id):
            # Return an instance of AuthorizeResult
            # If you don't store bot_id and bot_user_id, could also call `from_auth_test_response` with your bot_token to automatically fetch them
            return AuthorizeResult(
                enterprise_id=enterprise_id,
                team_id=team_id,
                bot_token=team.get("bot_token"),
                bot_user_id=team.get("bot_user_id"),
            )

    logger.error("No authorization information was found")


def verify(req: BoltRequest, resp: BoltResponse, next: Callable[[], BoltResponse], logger: Optional[Logger] = None) -> BoltResponse:  # type: ignore
    enterprise_id = req.context.enterprise_id
    team_id = req.context.team_id
    secrets = read_yaml(".env.yaml")
    installations = secrets.get("INSTALLATIONS")
    for team in installations:
        # enterprise_id doesn't exist for some teams
        is_valid_enterprise = (
            True
            if "enterprise_id" not in team or enterprise_id == team["enterprise_id"]
            else False
        )
        if is_valid_enterprise and (team["team_id"] == team_id):
            # Return an instance of BoltResponse
            return RequestVerification(
                signing_secret=team.get("signing_secret"), base_logger=logger
            ).process(req=req, resp=resp, next=next)

    logger.error("No verification information was found")
