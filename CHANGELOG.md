# Changelog

## Version 0.3.0 (2026-11-24)

Everything that worked in 0.2.1 keeps working: the same arguments, the same URLs and the same default behavior.

### Added

- **Form login** with `auth_method="form"`: a login page, a signed session cookie and a "Log out" link on the documentation pages (#4). HTTP Basic credentials are still accepted in this mode, so scripts keep working.
- **`user_tags`**: show each user only the routes, schemas and tag descriptions that match their tags (#5, #10, thanks @lokhandeganesh). Webhooks are filtered the same way.
- The app's Swagger UI settings are used: `swagger_ui_parameters` and `swagger_ui_init_oauth`.
- Apps behind a proxy with a root path work: the root path is put in front of the schema URL, the bundled files, the login redirects and the OpenAPI `servers` list.
- Python 3.8 and 3.9 are supported again, and the package is tested with FastAPI 0.68 up to the current release.
- Type information is shipped with the package (`py.typed`).

### Fixed

- A user whose password or username has non-ASCII characters could never log in, and the attempt ended in a server error. Credentials are now read as UTF-8.
- Routes of the app that live under the docs path, like `/docs/guide`, were removed together with the default documentation routes. Now only the documentation routes themselves are removed.
- Swagger UI's OAuth2 redirect page (`/docs/oauth2-redirect`) was removed and never added back, which broke the "Authorize" flow for OAuth2. It works again.
- Custom CSS was loaded before the Swagger UI stylesheet in the default mode, so rules with the same weight lost. It now always comes last.
- An error in custom JavaScript replaced the whole page with "Failed to load documentation". The page now stays, and the error goes to the console.
- The app title is escaped in the pages.
- The ReDoc CDN URL pointed at `redoc@next`, which is a release candidate of ReDoc 3. It now points at `redoc@2`, the version FastAPI uses.
- A login attempt for a user that doesn't exist takes as long as one for a user that does.

### Changed

- `requests` and `uvicorn` are no longer installed with the package, because it never used them. If your app imports them, add them to your own requirements.
- The documentation pages and the schema are sent with `Cache-Control: no-store`.
- The bundled Swagger UI and ReDoc files are served from memory, which also works on old FastAPI versions without `aiofiles`.

### Removed

- `StaticHandler.get_fallback_html()`, which nothing used.
- The loose demo and manual test scripts in the repository root. The `examples` folder has a short example for each feature.

## Version 0.2.1 (2025-08-17)

- **Fixed**: Blank page issue after authentication for some users
  - Improved handling of custom URL parameters by storing them as instance variables
  - Simplified `_setup_routes()` method for better maintainability
  - Applied fix from PR #2 for more robust URL parameter handling
- **Fixed**: Route removal logic now correctly removes all default documentation routes
  - Properly removes `/docs`, `/redoc`, and `/openapi.json` endpoints
  - Prevents 500 errors when accessing old endpoints
- **Improved**: Example files and documentation
  - Fixed `custom_styling.py` to work with uvicorn by adding default app variable
  - Standardized credentials across all custom styling examples
  - Added `python-multipart` to dev dependencies for form data handling
  - Added clear run instructions in example files

## Version 0.2.0 (2025-08-17)

- **Added**: Custom CSS and JavaScript injection support
  - New `custom_css` parameter to inject custom styles into documentation pages
  - New `custom_js` parameter to inject custom JavaScript for enhanced functionality
  - Complete customization examples for dark theme, minimal theme, corporate branding, and analytics
  - Support for both Swagger UI and ReDoc customization
- **Added**: Automatic CDN fallback to local files for better reliability
  - Documentation now automatically falls back to bundled static files if CDN is unavailable
  - New `prefer_local` option to always serve from local files
  - New `use_cdn_fallback` option to control fallback behavior
  - Bundled Swagger UI and ReDoc static files for offline capability
- **Fixed**: Static file URL bug that caused blank documentation pages
  - Previously, when no custom CDN URLs were provided, the package would pass `None` values to FastAPI's documentation functions
  - This resulted in HTML with `href="None"` and `src="None"`, causing white/blank pages
  - Now properly handles default CDN URLs when custom URLs are not specified

## Version 0.1.0 (2025-01-15)

- Initial release
- Basic HTTP authentication for FastAPI documentation endpoints
- Support for multiple users
