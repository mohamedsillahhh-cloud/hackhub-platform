import random
import string
import re
from typing import Tuple


def generate_unique_code(length: int = 8) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


def sanitize_html(html: str) -> str:
    allowed_tags = {"b", "i", "u", "a", "p", "br", "strong", "em", "ul", "ol", "li", "code", "pre", "h1", "h2", "h3", "h4", "h5", "h6"}
    allowed_attrs = {"a": {"href", "target", "rel"}}
    tag_pattern = re.compile(r"<(/?) (\w+)([^>]*)>", re.IGNORECASE)
    sanitized = tag_pattern.sub(lambda m: _process_tag(m, allowed_tags, allowed_attrs), html)
    sanitized = re.sub(r"<script[^>]*>.*?</script>", "", sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r"<[^>]*on\w+\s*=[^>]*>", "", sanitized, flags=re.IGNORECASE)
    return sanitized


def _process_tag(match, allowed_tags, allowed_attrs):
    closing = match.group(1)
    tag = match.group(2).lower()
    attrs_str = match.group(3)
    if tag not in allowed_tags:
        return ""
    if closing:
        return f"</{tag}>"
    if tag in allowed_attrs and allowed_attrs[tag]:
        attrs = _filter_attrs(attrs_str, allowed_attrs[tag])
        return f"<{tag}{attrs}>"
    return f"<{tag}>"


def _filter_attrs(attrs_str: str, allowed: set) -> str:
    attr_pattern = re.compile(r'(\w+)\s*=\s*"([^"]*)"')
    filtered = ""
    for match in attr_pattern.finditer(attrs_str):
        name = match.group(1).lower()
        value = match.group(2)
        if name in allowed:
            filtered += f' {name}="{value}"'
    return filtered


def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in allowed_extensions


def pagination_params(page: int = 1, size: int = 20) -> Tuple[int, int]:
    if page < 1:
        page = 1
    if size < 1:
        size = 20
    if size > 100:
        size = 100
    skip = (page - 1) * size
    return skip, size
