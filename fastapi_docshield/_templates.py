"""
HTML for the pages DocShield serves.

Placeholders look like __NAME__ and are filled in by render().
"""

import re
from typing import Dict

_PLACEHOLDER = re.compile(r"__([A-Z0-9_]+)__")


def render(template: str, values: Dict[str, str]) -> str:
    """
    Fill the placeholders of a template in one pass.

    One pass matters: text that was put in is never scanned again, so custom
    CSS or JavaScript that happens to contain a placeholder name stays as it is.
    """
    return _PLACEHOLDER.sub(
        lambda match: values.get(match.group(1), match.group(0)), template
    )


# Loads a script or stylesheet from the first URL that works. With the CDN
# fallback there are two URLs: the CDN one and the copy bundled in the package.
# Stylesheets go in front of the custom CSS, so the custom rules win.
LOADER_SCRIPT = """
function docshieldLoad(kind, urls) {
    return new Promise(function (resolve, reject) {
        var index = 0;
        function attempt() {
            var url = urls[index];
            var element = document.createElement(kind);
            if (kind === 'link') {
                element.rel = 'stylesheet';
                element.href = url;
            } else {
                element.src = url;
            }
            element.onload = resolve;
            element.onerror = function () {
                element.remove();
                index += 1;
                if (index < urls.length) {
                    console.warn('DocShield: could not load ' + url + ', trying ' + urls[index]);
                    attempt();
                } else {
                    reject(new Error('Could not load ' + url));
                }
            };
            document.head.insertBefore(element, document.getElementById('docshield-custom-css'));
        }
        attempt();
    });
}
"""

SWAGGER_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
<style>
    body { margin: 0; }
    #swagger-ui { display: flex; flex-direction: column; height: 100vh; }
</style>
__CUSTOM_STYLE__
</head>
<body>
__LOGOUT_LINK__
<div id="swagger-ui"></div>
<script>
__LOADER__
Promise.all([
    docshieldLoad('link', __CSS_URLS__),
    docshieldLoad('script', __JS_URLS__)
]).then(function () {
    var config = __CONFIG__;
    config.presets = [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
    ];
    var oauth2RedirectUrl = __OAUTH2_REDIRECT_URL__;
    if (oauth2RedirectUrl) {
        config.oauth2RedirectUrl = window.location.origin + oauth2RedirectUrl;
    }
    var ui = SwaggerUIBundle(config);
    window.ui = ui;
    var initOAuth = __INIT_OAUTH__;
    if (initOAuth) {
        ui.initOAuth(initOAuth);
    }
    return ui;
}, function (error) {
    console.error('Failed to load Swagger UI:', error);
    document.getElementById('swagger-ui').innerHTML = '<h2>Failed to load documentation</h2>';
    return null;
}).then(function (ui) {
    if (!ui) {
        return;
    }
    // Custom JavaScript
    __CUSTOM_JS__
});
</script>
</body>
</html>
"""

REDOC_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
<link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
<style>
    body { margin: 0; padding: 0; }
</style>
__CUSTOM_STYLE__
</head>
<body>
__LOGOUT_LINK__
<noscript>ReDoc requires Javascript to function. Please enable it to browse the documentation.</noscript>
<div id="redoc-container"><redoc spec-url="__OPENAPI_URL__"></redoc></div>
<script>
__LOADER__
docshieldLoad('script', __JS_URLS__).then(function () {
    return true;
}, function (error) {
    console.error('Failed to load ReDoc:', error);
    document.getElementById('redoc-container').innerHTML = '<h2>Failed to load documentation</h2>';
    return false;
}).then(function (loaded) {
    if (!loaded) {
        return;
    }
    // Custom JavaScript
    __CUSTOM_JS__
});
</script>
</body>
</html>
"""

LOGOUT_LINK = (
    '<a class="docshield-logout" href="__LOGOUT_URL__" style="position: fixed; '
    "right: 14px; bottom: 14px; z-index: 10000; padding: 6px 12px; border-radius: 6px; "
    "background: #1f2937; color: #fff; font: 13px/1.4 system-ui, sans-serif; "
    'text-decoration: none; opacity: 0.9;">Log out</a>'
)

LOGIN_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>__TITLE__</title>
<style>
    :root { color-scheme: light dark; }
    body {
        margin: 0; min-height: 100vh; display: flex; align-items: center;
        justify-content: center; font: 16px/1.5 system-ui, sans-serif;
        background: #f3f4f6; color: #111827;
    }
    form {
        width: 100%; max-width: 320px; margin: 16px; padding: 28px;
        border-radius: 10px; background: #fff; box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
    }
    h1 { margin: 0 0 20px; font-size: 20px; }
    label { display: block; margin-bottom: 14px; font-size: 14px; }
    input {
        display: block; width: 100%; box-sizing: border-box; margin-top: 4px;
        padding: 9px 10px; border: 1px solid #d1d5db; border-radius: 6px;
        font: inherit; background: transparent; color: inherit;
    }
    button {
        width: 100%; padding: 10px; border: 0; border-radius: 6px;
        background: #059669; color: #fff; font: inherit; font-weight: 600; cursor: pointer;
    }
    .error { margin: 0 0 14px; color: #dc2626; font-size: 14px; }
    @media (prefers-color-scheme: dark) {
        body { background: #111827; color: #f9fafb; }
        form { background: #1f2937; box-shadow: none; }
        input { border-color: #4b5563; }
        .error { color: #f87171; }
    }
</style>
</head>
<body>
<form method="post" action="__ACTION__">
<h1>__HEADING__</h1>
__ERROR__
<input type="hidden" name="next" value="__NEXT__">
<label>Username<input name="username" autocomplete="username" required autofocus></label>
<label>Password<input name="password" type="password" autocomplete="current-password" required></label>
<button type="submit">Log in</button>
</form>
</body>
</html>
"""
