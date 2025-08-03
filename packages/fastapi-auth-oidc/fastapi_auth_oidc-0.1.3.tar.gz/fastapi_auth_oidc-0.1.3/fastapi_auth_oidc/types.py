from pydantic import BaseModel
from pydantic import ConfigDict


class IDToken(BaseModel):
    """Pydantic model representing an OIDC ID Token.

    ID Tokens are polymorphic and may have many attributes not defined in the spec thus this model accepts
    all addition fields. Only required fields are listed in the attributes section of this docstring or
    enforced by pydantic.

    See the specifications here. https://openid.net/specs/openid-connect-core-1_0.html#IDToken

    Attributes:
        iss (str): Issuer Identifier for the Issuer of the response.
        sub (str): Subject Identifier.
        aud (str): Audience(s) that this ID Token is intended for.
        exp (str): Expiration time on or after which the ID Token MUST NOT be accepted for processing.
        iat (iat): Time at which the JWT was issued.

    """

    model_config = ConfigDict(extra="allow")

    iss: str
    sub: str
    aud: str | list[str]
    exp: int
    iat: int
