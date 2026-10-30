# TODO: migration period only, kept so that old imports do not break.
#  The status client now lives in annetbox, it takes ssl_context in place of insecure.
#  Remove this module after the next major release.
from annetbox.base.client_sync import NetboxStatusClient  # noqa: F401
from annetbox.base.models import Status  # noqa: F401
