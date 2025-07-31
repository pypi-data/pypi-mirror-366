from skt.vault_utils import get_secrets

ALL_BQ_USER_GROUP_KEY = "04d34og8115a68n"
SKB_USER_GROUP_KEY = "02et92p00zva9qe"
CREDENTIALS_SECRET_PATH = "gcp/skt-datahub/dataflow"
SKB_CREDENTIALS_SECRET_PATH = "gcp/skt-datahub/aidp-skb"


def _get_jupyterhub_user_id():
    import os

    return os.environ["JUPYTERHUB_USER"] if "JUPYTERHUB_USER" in os.environ else None


def _get_proxy():
    import httplib2

    proxy_ip, proxy_port = get_secrets("proxies")["http"].replace("http://", "").split(":")
    proxy_http = httplib2.Http(proxy_info=httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_HTTP, proxy_ip, int(proxy_port)))
    return proxy_http


def _get_directory_credentials():
    import json
    from google.oauth2 import service_account

    key = get_secrets("gcp/skt-datahub/dataflow")["config"]
    json_acct_info = json.loads(key)
    credentials = service_account.Credentials.from_service_account_info(
        json_acct_info,
        scopes=[
            "https://www.googleapis.com/auth/admin.directory.user",
            "https://www.googleapis.com/auth/admin.directory.group",
            "https://www.googleapis.com/auth/admin.directory.group.member",
        ],
        subject="admin@sktml.io",
    )
    return credentials


def _check_jupyterhub_user_membership_for_group(user_id, group_key):
    import google_auth_httplib2
    import googleapiclient.discovery

    credentials = _get_directory_credentials()
    authorized_http = google_auth_httplib2.AuthorizedHttp(credentials, http=_get_proxy())
    service = googleapiclient.discovery.build("admin", "directory_v1", http=authorized_http, cache_discovery=False)
    results = service.members().hasMember(groupKey=group_key, memberKey=f"{user_id}@sktml.io").execute()
    return results["isMember"]


def _get_user_credentials():
    import pydata_google_auth

    credentials = pydata_google_auth.get_user_credentials(
        ["https://www.googleapis.com/auth/cloud-platform"],
        client_id="496763979626-ia7imnkjnq54edv4a1ni9lbco7fmtvii.apps.googleusercontent.com",
        client_secret="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",
        use_local_webserver=False,
        redirect_uri="https://sdk.cloud.google.com/authcode.html",
    )
    return credentials


def _get_service_account_credentials():
    import json
    from google.oauth2 import service_account

    key = get_secrets(CREDENTIALS_SECRET_PATH)["config"]
    json_acct_info = json.loads(key)
    credentials = service_account.Credentials.from_service_account_info(json_acct_info)
    scoped_credentials = credentials.with_scopes(["https://www.googleapis.com/auth/cloud-platform"])

    return scoped_credentials


def _get_skb_service_account_credentials():
    import json
    from google.oauth2 import service_account

    key = get_secrets(SKB_CREDENTIALS_SECRET_PATH)["config"]
    json_acct_info = json.loads(key)
    credentials = service_account.Credentials.from_service_account_info(json_acct_info)
    scoped_credentials = credentials.with_scopes(["https://www.googleapis.com/auth/cloud-platform"])

    return scoped_credentials


def get_gcp_credentials():
    jupyterhub_user_id = _get_jupyterhub_user_id()
    if jupyterhub_user_id:
        if _check_jupyterhub_user_membership_for_group(jupyterhub_user_id, ALL_BQ_USER_GROUP_KEY):
            # return _get_user_credentials()
            return _get_service_account_credentials()
        elif _check_jupyterhub_user_membership_for_group(jupyterhub_user_id, SKB_USER_GROUP_KEY):
            return _get_skb_service_account_credentials()
    return _get_service_account_credentials()


def get_gcp_credentials_json_string():
    jupyterhub_user_id = _get_jupyterhub_user_id()
    if jupyterhub_user_id:
        if _check_jupyterhub_user_membership_for_group(jupyterhub_user_id, ALL_BQ_USER_GROUP_KEY):
            return get_secrets(CREDENTIALS_SECRET_PATH)["config"]
        elif _check_jupyterhub_user_membership_for_group(jupyterhub_user_id, SKB_USER_GROUP_KEY):
            return get_secrets(SKB_CREDENTIALS_SECRET_PATH)["config"]
    return get_secrets(CREDENTIALS_SECRET_PATH)["config"]
