# TODO: migration period only, kept so that old imports do not break.
#  The client now lives in annetbox. Remove this module after the next major release.
from annetbox.base.client_sync import BaseNetboxClient, collect  # noqa: F401
from annetbox.base.models import PagingResponse  # noqa: F401
from requests import Session  # noqa: F401
