import argparse
import os
import re
from collections import defaultdict
from typing import List, Tuple, Optional, Pattern

import yaml
from perun.connector import AdaptersManager
from privacyidea.app import create_app
from privacyidea.models import db, TokenOwner, Token
from sqlalchemy import tuple_

# supplied as default values for arguments
PERUN_USER_ID_REGEX = r"perunUserId=(?P<perun_user_id>\d+),"
MFA_ACTIVE_TOKENS_ATTR_NAME = "urn:perun:user:attribute-def:def:mfaTokenTypes:mu"
PERUN_CONNECTOR_CONFIG_PATH = "/etc/perun-connector.yaml"

# create app to have access to Flask application context
app = create_app(config_name="development")


class ROLLOUTSTATE(object):
    CLIENTWAIT = "clientwait"
    PENDING = "pending"
    VERIFYPENDING = "verify"
    ENROLLED = "enrolled"
    BROKEN = "broken"
    FAILED = "failed"
    DENIED = "denied"


USABLE_ROLLOUT_STATES = {
    "webauthn": [""],
    "backupcode": [""],
    "totp": ["", ROLLOUTSTATE.ENROLLED],
}


def load_attrs_manager_config(config_filepath):
    if os.path.exists(config_filepath):
        with open(config_filepath, "r") as f:
            config = yaml.safe_load(f)
            return config
    else:
        raise FileNotFoundError(
            f"Attempted to load attributes manager config from '{config_filepath}' "
            f"but the file was not found."
        )


def get_adapters_manager(config_path: str) -> AdaptersManager:
    cfg = load_attrs_manager_config(config_path)
    if not cfg:
        raise ValueError("Was not able to load the attributes manager config.")
    adapters_manager = AdaptersManager(
        cfg["attributes_manager_config"], cfg["attributes_map"]
    )
    return adapters_manager


def get_args():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(
        description="Collects information about the usable token types of each privacyIDEA user and sends it to Perun."
    )
    parser._optionals.title = "Options"
    parser.add_argument(
        "--mfa-active-tokens-attr-name",
        "-a",
        default=MFA_ACTIVE_TOKENS_ATTR_NAME,
        help="name of Perun attribute containing user's active MFA tokens",
    )
    parser.add_argument(
        "--perun-user-id-regex",
        "-r",
        default=PERUN_USER_ID_REGEX,
        help="regex for parsing Perun user ID from privacyIDEA user ID",
    )
    parser.add_argument(
        "--perun-connector-config-path",
        "-c",
        default=PERUN_CONNECTOR_CONFIG_PATH,
        help="path to config for Perun Connector",
    )
    args = parser.parse_args()
    return args


def get_user_token_types() -> List[Tuple[str, str]]:
    usable_rollout_states_tuples = [
        (token_type, usable_state)
        for token_type, usable_states_lst in USABLE_ROLLOUT_STATES.items()
        for usable_state in usable_states_lst
    ]

    with app.app_context():
        user_token_types = (
            db.session.query(TokenOwner.user_id, Token.tokentype)
            .join(Token, Token.id == TokenOwner.token_id)
            .filter(Token.active.is_(True))
            .filter(Token.locked.is_(False))
            .filter(Token.revoked.is_(False))
            .filter(
                tuple_(Token.tokentype, Token.rollout_state).in_(
                    usable_rollout_states_tuples
                )
            )
            .distinct(TokenOwner.user_id, Token.tokentype)
            .order_by(TokenOwner.user_id)
            .all()
        )
        return user_token_types


def parse_perun_user_id(
    perun_user_id_regex: Pattern[str], privacyidea_user_id: str
) -> Optional[str]:
    match = re.search(perun_user_id_regex, privacyidea_user_id)
    if match:
        return match.group("perun_user_id")
    return None


def main():
    args = get_args()
    perun_user_id_regex = re.compile(args.perun_user_id_regex)
    mfa_active_tokens_attr_name = args.mfa_active_tokens_attr_name
    adapters_manager = get_adapters_manager(args.perun_connector_config_path)
    user_token_types = get_user_token_types()
    user_all_usable_tokens = defaultdict(list)

    for privacyidea_user_id, token_type in user_token_types:
        perun_user_id = parse_perun_user_id(perun_user_id_regex, privacyidea_user_id)
        user_all_usable_tokens[perun_user_id].append(token_type)

    for perun_user_id, token_types in user_all_usable_tokens.items():
        token_types.sort()
        attr_to_set = {mfa_active_tokens_attr_name: token_types}
        adapters_manager.set_user_attributes(int(perun_user_id), attr_to_set)


if __name__ == "__main__":
    main()
