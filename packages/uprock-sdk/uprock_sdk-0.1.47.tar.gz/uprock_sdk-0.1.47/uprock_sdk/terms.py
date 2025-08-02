import datetime
from collections import defaultdict
from typing import DefaultDict, Dict, List, Optional, Tuple  # noqa: F401

import httpx
import jinja2
from html_sanitizer import Sanitizer

from uprock_sdk import GLOBAL_SETTINGS

CLIENT = httpx.AsyncClient(base_url=GLOBAL_SETTINGS.TERMS_API_URL)

_TERMS = defaultdict(dict)  # type: DefaultDict[str, Dict[Tuple[str, str], str]]
_TERMS_UPDATED_AT = {}


async def _load_terms(namespace: str):
    global _TERMS, _TERMS_UPDATED_AT

    response = await CLIENT.get(f"/v1/terms?namespaces[]={namespace}")
    response.raise_for_status()

    for raw_term in response.json():
        for translation in raw_term["translations"]:
            _TERMS[translation["language"]][(raw_term["name"], namespace)] = translation["content"]

    _TERMS_UPDATED_AT[namespace] = datetime.datetime.now(datetime.timezone.utc)


async def term(language: str, name: str, namespace: str) -> str:
    global _TERMS, _TERMS_UPDATED_AT

    if not _TERMS_UPDATED_AT or _TERMS_UPDATED_AT.get(
        namespace, datetime.datetime.fromtimestamp(0).replace(tzinfo=datetime.timezone.utc)
    ) + datetime.timedelta(seconds=GLOBAL_SETTINGS.TERMS_TTL_S) < datetime.datetime.now(datetime.timezone.utc):
        await _load_terms(namespace)

    if language in _TERMS:
        localized_terms = _TERMS[language]
    else:
        localized_terms = _TERMS[GLOBAL_SETTINGS.TERMS_DEFAULT_LANGUAGE]

    if (name, namespace) not in localized_terms:
        return name

    return localized_terms[(name, namespace)]


async def term_html(
    language: str,
    name: str,
    namespace: str,
    namespace_fallback: Optional[str] = None,
    strip_new_line: bool = True,
) -> str:
    content = await term(language, name, namespace)

    if content == name and namespace_fallback:
        content = await term(language, name, namespace_fallback)

    return sanitize(content=content, strip_new_line=strip_new_line)


async def term_jinja2(
    language: str,
    name: str,
    namespace: str,
    *args,
    namespace_fallback: Optional[str] = None,
    strip_new_line: bool = True,
    **kwargs,
) -> str:
    content = await term(language, name, namespace)

    if content == name and namespace_fallback:
        content = await term(language, name, namespace_fallback)

    template = jinja2.Template(source=content)

    return sanitize(content=template.render(*args, **kwargs), strip_new_line=strip_new_line)


def sanitize(content: str, strip_new_line: bool = True) -> str:
    sanitized_content = (
        Sanitizer(
            {
                "tags": {"a", "br", "b", "strong", "i", "em", "code", "s", "strike", "del", "u"},
                "attributes": {"a": ("href",)},
                "whitespace": set(),
                "empty": {"a", "br"},
                "separate": {"br"},
            }
        )
        .sanitize(content.replace("<p>", "").replace("</p>", "\n").replace("\n", "<br>"))
        .replace("<br>", "\n")
        .replace("<strong>", "<b>")
        .replace("</strong>", "</b>")
    )

    if strip_new_line:
        sanitized_content = sanitized_content.strip("\n")

    return sanitized_content


async def bulk_create(terms: List[Dict[str, str]]) -> None:
    response = await CLIENT.put("/v1/internal/terms", json=terms)
    response.raise_for_status()


async def bulk_remove(namespace: str) -> None:
    response = await CLIENT.delete(f"/v1/internal/terms?namespaces[]={namespace}")
    response.raise_for_status()


async def bulk_copy(source_namespace, target_namespace) -> None:
    response = await CLIENT.get(f"/v1/terms?namespaces[]={source_namespace}")
    response.raise_for_status()

    terms = [
        {
            "name": raw_term["name"],
            "namespace": target_namespace,
            "translations": [
                {"language": translation["language"], "content": translation["content"]}
                for translation in raw_term["translations"]
            ],
        }
        for raw_term in response.json()
    ]

    response = await CLIENT.put("/v1/internal/terms", json=terms)
    response.raise_for_status()
