from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from fastapi_docshield import DocShield


class Author(BaseModel):
    name: str


class PublicPost(BaseModel):
    title: str
    author: Author


class AdminAuditLog(BaseModel):
    action: str
    secret_code: str


def _create_app(user_tags=None) -> FastAPI:
    app = FastAPI(
        title="Tag Filter Test API",
        openapi_tags=[
            {"name": "general", "description": "General routes"},
            {"name": "admin", "description": "Admin routes"},
        ],
    )

    @app.get("/", tags=["general"], response_model=PublicPost)
    def root():
        return {"title": "Hello", "author": {"name": "Alice"}}

    @app.post("/posts/{id}", tags=["admin"], response_model=AdminAuditLog)
    def create_post(id: int, payload: AdminAuditLog):
        return payload

    @app.get("/health")
    def health():
        return {"status": "ok"}

    DocShield(
        app=app,
        credentials={
            "admin": "admin_pass",
            "developer": "dev_pass",
            "ops": "ops_pass",
        },
        user_tags=user_tags,
    )
    return app


def test_default_behavior_without_user_tags():
    app = _create_app(user_tags=None)
    client = TestClient(app)

    res = client.get("/openapi.json", auth=("developer", "dev_pass"))
    assert res.status_code == 200
    data = res.json()

    assert "/" in data["paths"]
    assert "/posts/{id}" in data["paths"]
    assert "/health" in data["paths"]
    assert "AdminAuditLog" in data["components"]["schemas"]


def test_restricted_user_sees_only_allowed_paths_and_schemas():
    app = _create_app(
        user_tags={
            "admin": None,
            "developer": ["general"],
        }
    )
    client = TestClient(app)

    # Developer sees only "general" routes and their referenced schemas (including nested Author)
    dev_res = client.get("/openapi.json", auth=("developer", "dev_pass"))
    assert dev_res.status_code == 200
    dev_data = dev_res.json()

    assert list(dev_data["paths"].keys()) == ["/"]
    assert "/posts/{id}" not in dev_data["paths"]
    assert "/health" not in dev_data["paths"]

    dev_schemas = dev_data["components"]["schemas"]
    assert "PublicPost" in dev_schemas
    assert "Author" in dev_schemas
    assert "AdminAuditLog" not in dev_schemas

    dev_tags = [t["name"] for t in dev_data.get("tags", [])]
    assert dev_tags == ["general"]


def test_unrestricted_users_explicit_none_and_omitted():
    app = _create_app(
        user_tags={
            "admin": None,
            "developer": ["general"],
            # "ops" is intentionally omitted -> unrestricted by default
        }
    )
    client = TestClient(app)

    # Trigger restricted user first to ensure app.openapi() cache is not mutated
    dev_res = client.get("/openapi.json", auth=("developer", "dev_pass"))
    assert list(dev_res.json()["paths"].keys()) == ["/"]

    # Explicit None user sees everything
    admin_res = client.get("/openapi.json", auth=("admin", "admin_pass"))
    assert admin_res.status_code == 200
    admin_data = admin_res.json()
    assert {"/", "/posts/{id}", "/health"}.issubset(admin_data["paths"].keys())
    assert "AdminAuditLog" in admin_data["components"]["schemas"]

    # Omitted user also sees everything
    ops_res = client.get("/openapi.json", auth=("ops", "ops_pass"))
    assert ops_res.status_code == 200
    ops_data = ops_res.json()
    assert {"/", "/posts/{id}", "/health"}.issubset(ops_data["paths"].keys())
    assert "AdminAuditLog" in ops_data["components"]["schemas"]


def test_empty_tag_list_hides_all_routes_and_schemas():
    app = _create_app(user_tags={"developer": []})
    client = TestClient(app)

    res = client.get("/openapi.json", auth=("developer", "dev_pass"))
    assert res.status_code == 200
    data = res.json()

    assert data["paths"] == {}
    assert data["components"]["schemas"] == {}
