"""Deterministic OpenAPI 2.x / 3.x parsing into ApiContract rows."""

from __future__ import annotations

import re
from typing import Any

from contractlens.contracts.models import ApiContract

HTTP_OPS = frozenset({"get", "post", "put", "delete", "patch", "options", "head", "trace"})


def _leading_slash(path: str) -> str:
    p = path.strip()
    if not p.startswith("/"):
        return "/" + p
    return p


def _ref_name(ref: str) -> str | None:
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return None
    tail = ref.split("/")[-1]
    return tail or None


_MAX_SCHEMA_REF_CHAIN = 32


def set_max_schema_ref_chain(n: int | None) -> None:
    """Tune recursive `$ref` walk depth inside local components/schemas (4–96)."""
    global _MAX_SCHEMA_REF_CHAIN
    if n is None:
        _MAX_SCHEMA_REF_CHAIN = 32
        return
    try:
        v = int(n)
    except (TypeError, ValueError):
        return
    _MAX_SCHEMA_REF_CHAIN = max(4, min(v, 96))


def _resolve_schema(doc: dict[str, Any], schema: dict[str, Any] | None) -> dict[str, Any] | None:
    if not schema:
        return None
    seen = 0
    cur: dict[str, Any] | None = schema
    while cur and "$ref" in cur and seen < _MAX_SCHEMA_REF_CHAIN:
        seen += 1
        ref = cur["$ref"]
        name = _ref_name(ref)
        if not name:
            break
        comps = doc.get("components") if isinstance(doc.get("components"), dict) else {}
        schemas = comps.get("schemas") if isinstance(comps.get("schemas"), dict) else {}
        if isinstance(schemas.get(name), dict):
            cur = schemas[name]
            continue
        defs = doc.get("definitions") if isinstance(doc.get("definitions"), dict) else {}
        if isinstance(defs.get(name), dict):
            cur = defs[name]
            continue
        break
    return cur


def _property_keys_from_schema(doc: dict[str, Any], schema: dict[str, Any] | None) -> list[str]:
    resolved = _resolve_schema(doc, schema)
    if not resolved:
        return []
    props = resolved.get("properties")
    if isinstance(props, dict):
        return [str(k) for k in props.keys()]
    return []


def _schema_from_swagger_body(doc: dict[str, Any], op: dict[str, Any]) -> dict[str, Any] | None:
    responses = op.get("responses")
    if not isinstance(responses, dict):
        return None
    for code in ("200", "201", "default"):
        block = responses.get(code)
        if not isinstance(block, dict):
            continue
        sch = block.get("schema")
        if isinstance(sch, dict):
            return sch
    return None


def _schema_from_oas3_body(doc: dict[str, Any], op: dict[str, Any]) -> dict[str, Any] | None:
    responses = op.get("responses")
    if not isinstance(responses, dict):
        return None
    for code in ("200", "201", "default"):
        block = responses.get(code)
        if not isinstance(block, dict):
            continue
        content = block.get("content")
        if not isinstance(content, dict):
            continue
        for mt in (
            "application/json",
            "application/problem+json",
            "*/*",
        ):
            piece = content.get(mt)
            if isinstance(piece, dict):
                sch = piece.get("schema")
                if isinstance(sch, dict):
                    return sch
        # first content entry
        for piece in content.values():
            if isinstance(piece, dict):
                sch = piece.get("schema")
                if isinstance(sch, dict):
                    return sch
    return None


def _request_schema_swagger(doc: dict[str, Any], op: dict[str, Any]) -> dict[str, Any] | None:
    params = op.get("parameters")
    if not isinstance(params, list):
        return None
    body_param: dict[str, Any] | None = None
    for p in params:
        if isinstance(p, dict) and p.get("in") == "body":
            body_param = p
            break
    if not body_param:
        return None
    sch = body_param.get("schema")
    return sch if isinstance(sch, dict) else None


def _request_schema_oas3(doc: dict[str, Any], op: dict[str, Any]) -> dict[str, Any] | None:
    rb = op.get("requestBody")
    if not isinstance(rb, dict):
        return None
    content = rb.get("content")
    if not isinstance(content, dict):
        return None
    for mt in (
        "application/json",
        "application/x-www-form-urlencoded",
        "multipart/form-data",
    ):
        piece = content.get(mt)
        if isinstance(piece, dict):
            sch = piece.get("schema")
            if isinstance(sch, dict):
                return sch
    for piece in content.values():
        if isinstance(piece, dict):
            sch = piece.get("schema")
            if isinstance(sch, dict):
                return sch
    return None


def _parameter_names(op: dict[str, Any]) -> list[str]:
    params = op.get("parameters")
    if not isinstance(params, list):
        return []
    names: list[str] = []
    for p in params:
        if isinstance(p, dict) and p.get("name"):
            names.append(str(p["name"]))
    return names


def _openapi_or_swagger_version(doc: dict[str, Any]) -> str:
    if isinstance(doc.get("openapi"), str):
        return "openapi3"
    if doc.get("swagger") == "2.0":
        return "swagger2"
    if isinstance(doc.get("swagger"), str):
        return "swagger2"
    return "unknown"


def _auth_hint(doc: dict[str, Any], op: dict[str, Any]) -> str | None:
    if isinstance(op.get("security"), list) and len(op.get("security")) > 0:
        return "security_scheme"
    if isinstance(doc.get("security"), list) and len(doc.get("security")) > 0:
        return "security_scheme"
    return None


def _dto_hint(schema: dict[str, Any] | None) -> str | None:
    if not schema:
        return None
    ref = schema.get("$ref")
    if isinstance(ref, str):
        name = _ref_name(ref)
        if name:
            return name
    title = schema.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    return None


def parse_spec_document(doc: dict[str, Any], source_display: str) -> list[ApiContract]:
    """Extract ``ApiContract`` rows from a loaded OpenAPI/Swagger dict."""
    paths = doc.get("paths")
    if not isinstance(paths, dict):
        return []

    version_kind = _openapi_or_swagger_version(doc)
    out: list[ApiContract] = []
    line_hint = 1

    for raw_path, path_item in sorted(paths.items()):
        if not isinstance(path_item, dict):
            continue
        path_str = _leading_slash(str(raw_path))
        for method, op in path_item.items():
            mlower = str(method).lower()
            if mlower not in HTTP_OPS:
                continue
            if not isinstance(op, dict):
                continue

            if version_kind == "swagger2":
                res_schema = _schema_from_swagger_body(doc, op)
                req_schema = _request_schema_swagger(doc, op)
            else:
                res_schema = _schema_from_oas3_body(doc, op)
                req_schema = _request_schema_oas3(doc, op)

            req_fields = _property_keys_from_schema(doc, req_schema)
            req_fields.extend(_parameter_names(op))
            # de-dupe preserving order
            seen: set[str] = set()
            dedup_req: list[str] = []
            for x in req_fields:
                k = x.lower()
                if k in seen:
                    continue
                seen.add(k)
                dedup_req.append(x)

            resp_fields = _property_keys_from_schema(doc, res_schema)

            req_dto = _dto_hint(req_schema)
            resp_dto = _dto_hint(res_schema)

            auth = _auth_hint(doc, op)

            summary_bits = []
            if isinstance(op.get("operationId"), str):
                summary_bits.append(op["operationId"])
            if isinstance(op.get("summary"), str):
                summary_bits.append(op["summary"])
            summary = ", ".join(summary_bits) if summary_bits else None

            dto_extra = f" ({summary})" if summary else ""

            out.append(
                ApiContract(
                    method=mlower.upper(),
                    path=path_str,
                    source=source_display,
                    line=line_hint,
                    request_fields=dedup_req,
                    response_fields=resp_fields,
                    request_dto=(req_dto + dto_extra) if req_dto else None,
                    response_dto=(resp_dto + dto_extra) if resp_dto else None,
                    auth=auth,
                )
            )
            line_hint += 1

    return out


def backend_implementation_field_names(be: ApiContract) -> set[str]:
    """Approximate JSON field names implied by backend scanner output."""
    names = set(be.response_fields or [])
    dto = be.response_dto or ""
    m = re.search(r"anonymous\s*\{([^}]*)\}", dto)
    if m:
        inner = m.group(1).strip()
        if "=" in inner:
            for key in re.findall(r"(\w+)\s*=", inner):
                names.add(key)
        else:
            for part in inner.split(","):
                p = part.strip()
                if p:
                    names.add(p)
    return names


def openapi_documented_field_names(oas: ApiContract) -> set[str]:
    return set(oas.response_fields or [])


def openapi_documented_request_fields(oas: ApiContract) -> set[str]:
    return set(oas.request_fields or [])


def backend_request_field_names(be: ApiContract) -> set[str]:
    names = {x.lower() for x in (be.request_fields or [])}
    rdto = (be.request_dto or "").lower()
    if "iformfile" in rdto:
        names.add("file")
    return names
