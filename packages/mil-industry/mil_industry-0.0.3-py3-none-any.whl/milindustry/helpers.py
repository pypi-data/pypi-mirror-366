from typing import List

from esi.models import Token
from esi.errors import TokenError

from app_utils.allianceauth import notify_throttled

from allianceauth.eveonline.models import EveCharacter
from allianceauth.framework.api.user import get_all_characters_from_user

from allianceauth.services.hooks import get_extension_logger
logger = get_extension_logger(__name__)

def fetch_tokens_for_user(user, scopes) -> List[Token]:
    """returns valid token for a user

    Args:
    - user: User for the token retrieval
    - scopes: Provide the required scopes.

    Exceptions:
    - TokenError: If no valid token can be found
    """
    characters_for_user = get_all_characters_from_user(user=user)

    tokens: List[Token] = []
    for character in characters_for_user:
        token = (
            Token.objects.prefetch_related("scopes")
            .filter(user=user, character_id=character.character_id)
            .require_scopes(scopes)
            .require_valid()
            .first()
        )

        if token:
            tokens.append(token)
        else:
            logger.info(f"No valid token for {character.character_name}")

    return tokens
