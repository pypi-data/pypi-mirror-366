from uprock_sdk.settings import GLOBAL_SETTINGS
from uprock_sdk.customers import CLIENT as CUSTOMERS_CLIENT
from uprock_sdk.terms import CLIENT as TERMS_CLIENT


def init(**kwargs):
    GLOBAL_SETTINGS.update(kwargs)

    CUSTOMERS_CLIENT.base_url = GLOBAL_SETTINGS.CORE_API_URL
    TERMS_CLIENT.base_url = GLOBAL_SETTINGS.TERMS_API_URL
