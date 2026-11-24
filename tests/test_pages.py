"""The documentation pages, their assets and the OpenAPI schema."""

import inspect

import pytest
from fastapi import FastAPI

from .helpers import ADMIN, make_client

SWAGGER_CDN = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/"
REDOC_CDN = "https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js"
STATIC_URLS = {
    "/docshield/static/swagger-ui-bundle.js": "javascript",
    "/docshield/static/swagger-ui.css": "text/css",
    "/docshield/static/redoc.standalone.js": "javascript",
}


def test_default_pages_use_the_cdn_with_a_local_fallback():
    client = make_client()

    docs = client.get("/docs", auth=ADMIN).text
    redoc = client.get("/redoc", auth=ADMIN).text

    assert SWAGGER_CDN + "swagger-ui-bundle.js" in docs
    assert SWAGGER_CDN + "swagger-ui.css" in docs
    assert "/docshield/static/swagger-ui-bundle.js" in docs
    assert "/docshield/static/swagger-ui.css" in docs
    assert REDOC_CDN in redoc
    assert "/docshield/static/redoc.standalone.js" in redoc
    assert 'spec-url="/openapi.json"' in redoc


def test_prefer_local_never_loads_from_the_cdn():
    client = make_client(prefer_local=True)

    docs = client.get("/docs", auth=ADMIN).text
    redoc = client.get("/redoc", auth=ADMIN).text

    assert "/docshield/static/swagger-ui-bundle.js" in docs
    assert "cdn.jsdelivr.net" not in docs
    assert "/docshield/static/redoc.standalone.js" in redoc
    assert "cdn.jsdelivr.net" not in redoc


def test_cdn_only_mode_has_no_local_files():
    client = make_client(use_cdn_fallback=False)

    docs = client.get("/docs", auth=ADMIN).text

    assert SWAGGER_CDN + "swagger-ui-bundle.js" in docs
    assert "/docshield/static/" not in docs
    assert "/docshield/static/" not in client.get("/redoc", auth=ADMIN).text
    for url in STATIC_URLS:
        assert client.get(url).status_code == 404


def test_custom_asset_urls_are_used():
    client = make_client(
        swagger_js_url="https://assets.example.com/swagger.js",
        swagger_css_url="https://assets.example.com/swagger.css",
        redoc_js_url="https://assets.example.com/redoc.js",
    )

    docs = client.get("/docs", auth=ADMIN).text
    redoc = client.get("/redoc", auth=ADMIN).text

    assert "https://assets.example.com/swagger.js" in docs
    assert "https://assets.example.com/swagger.css" in docs
    assert "cdn.jsdelivr.net" not in docs
    assert "https://assets.example.com/redoc.js" in redoc
    assert "cdn.jsdelivr.net" not in redoc


def test_one_custom_asset_url_keeps_the_default_for_the_other():
    client = make_client(swagger_js_url="https://assets.example.com/swagger.js")

    docs = client.get("/docs", auth=ADMIN).text

    assert "https://assets.example.com/swagger.js" in docs
    assert SWAGGER_CDN + "swagger-ui.css" in docs


@pytest.mark.parametrize("url, media_type", sorted(STATIC_URLS.items()))
def test_bundled_files_are_served(url, media_type):
    response = make_client().get(url)

    assert response.status_code == 200
    assert media_type in response.headers["content-type"]
    assert len(response.content) > 10000
    assert "max-age" in response.headers["Cache-Control"]


def test_missing_bundled_file_is_a_404(tmp_path):
    from fastapi.testclient import TestClient

    from .helpers import make_app

    app, shield = make_app(prefer_local=True)
    shield.static_handler.static_dir = tmp_path
    client = TestClient(app)

    assert client.get("/docshield/static/swagger-ui.css").status_code == 404
    # Without the bundled files the pages go back to the CDN
    assert SWAGGER_CDN in client.get("/docs", auth=ADMIN).text
    assert REDOC_CDN in client.get("/redoc", auth=ADMIN).text


def test_custom_css_and_js_are_added_to_both_pages():
    client = make_client(
        custom_css=".swagger-ui { background: red; }",
        custom_js="console.log('custom js ran');",
    )

    for url in ("/docs", "/redoc"):
        page = client.get(url, auth=ADMIN).text
        assert ".swagger-ui { background: red; }" in page
        assert "console.log('custom js ran');" in page


def test_pages_without_custom_code_have_no_custom_style():
    page = make_client().get("/docs", auth=ADMIN).text

    assert '<style id="docshield-custom-css">' not in page
    assert "// No custom JS" in page


def test_custom_code_that_looks_like_a_placeholder_is_left_alone():
    client = make_client(
        custom_css="/* __CONFIG__ */", custom_js="var name = '__JS_URLS__';"
    )

    page = client.get("/docs", auth=ADMIN).text

    assert "/* __CONFIG__ */" in page
    assert "var name = '__JS_URLS__';" in page


def test_app_title_is_escaped():
    client = make_client(app_kwargs={"title": "<script>alert(1)</script>"})

    for url in ("/docs", "/redoc"):
        page = client.get(url, auth=ADMIN).text
        assert "<script>alert(1)</script>" not in page
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page


def test_swagger_ui_settings_of_the_app_are_passed_on():
    parameters = inspect.signature(FastAPI.__init__).parameters
    if "swagger_ui_parameters" not in parameters:
        pytest.skip("This FastAPI version has no swagger_ui_parameters")
    client = make_client(
        app_kwargs={
            "swagger_ui_parameters": {
                "persistAuthorization": True,
                "deepLinking": False,
            },
            "swagger_ui_init_oauth": {"clientId": "my-client"},
        }
    )

    page = client.get("/docs", auth=ADMIN).text

    assert '"persistAuthorization": true' in page
    assert '"deepLinking": false' in page
    assert '"showExtensions": true' in page
    assert '{"clientId": "my-client"}' in page


def test_script_end_tags_in_settings_cannot_break_out_of_the_script():
    parameters = inspect.signature(FastAPI.__init__).parameters
    if "swagger_ui_parameters" not in parameters:
        pytest.skip("This FastAPI version has no swagger_ui_parameters")
    client = make_client(
        app_kwargs={"swagger_ui_parameters": {"filter": "</script><b>x</b>"}}
    )

    page = client.get("/docs", auth=ADMIN).text

    assert "</script><b>x</b>" not in page


def test_root_path_is_put_in_front_of_every_url():
    client = make_client(root_path="/api")

    docs = client.get("/docs", auth=ADMIN).text
    redoc = client.get("/redoc", auth=ADMIN).text
    schema = client.get("/openapi.json", auth=ADMIN).json()

    assert '"url": "/api/openapi.json"' in docs
    assert '"/api/docshield/static/swagger-ui-bundle.js"' in docs
    assert '"/api/docs/oauth2-redirect"' in docs
    assert 'spec-url="/api/openapi.json"' in redoc
    assert '"/api/docshield/static/redoc.standalone.js"' in redoc
    assert {"url": "/api"} in schema["servers"]


def test_root_path_is_not_added_to_the_servers_twice():
    client = make_client(app_kwargs={"servers": [{"url": "/api"}]}, root_path="/api")

    servers = client.get("/openapi.json", auth=ADMIN).json()["servers"]

    assert servers.count({"url": "/api"}) == 1


def test_openapi_schema_lists_the_app_routes():
    schema = make_client().get("/openapi.json", auth=ADMIN).json()

    assert schema["info"]["title"] == "Test API"
    assert "/" in schema["paths"]
    assert "servers" not in schema


def test_root_path_set_on_the_app_works_too():
    import warnings

    with warnings.catch_warnings():
        # Newer FastAPI versions prefer the server's --root-path over this argument
        warnings.simplefilter("ignore")
        client = make_client(app_kwargs={"root_path": "/api"})

    assert '"url": "/api/openapi.json"' in client.get("/docs", auth=ADMIN).text
    assert {"url": "/api"} in client.get("/openapi.json", auth=ADMIN).json()["servers"]


def test_root_path_can_be_left_out_of_the_servers():
    client = make_client(app_kwargs={"root_path_in_servers": False}, root_path="/api")

    assert "servers" not in client.get("/openapi.json", auth=ADMIN).json()
