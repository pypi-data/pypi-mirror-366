import html
from html.parser import HTMLParser
from pathlib import Path
from typing import override

from zona.config import ZonaConfig
from zona.layout import Layout
from zona.links import resolve_link
from zona.models import Item


class HTMLProcessor(HTMLParser):
    """
    HTMLProcessor applies Zona's link resolution logic to an HTML document.
    """

    def __init__(
        self,
        source: Path,
        config: ZonaConfig | None,
        layout: Layout,
        item_map: dict[Path, Item],
        convert_charrefs: bool = True,
    ) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self._chunks: list[str] = []
        self.source: Path = source
        self.config: ZonaConfig | None = config
        self.layout: Layout = layout
        self.item_map: dict[Path, Item] = item_map

    @override
    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ):
        if tag == "a":
            attr_dict: dict[str, str] = {
                k: v for k, v in attrs if v is not None
            }
            href_val = attr_dict.get("href")
            if href_val is not None:
                resolved = resolve_link(
                    href_val,
                    self.source,
                    self.config,
                    self.layout,
                    self.item_map,
                )
                attr_dict["href"] = resolved.href
                if resolved.target is not None:
                    attr_dict["target"] = resolved.target
            attrs_str = " ".join(
                f'{k}="{v}"' for k, v in attr_dict.items()
            )
            self._chunks.append(f"<a {attrs_str}>")
        else:
            attrs_str = " ".join(
                f'{k}="{v}"' for k, v in attrs if v is not None
            )
            self._chunks.append(
                f"<{tag}{' ' + attrs_str if attrs_str else ''}>"
            )

    @override
    def handle_endtag(self, tag: str):
        self._chunks.append(f"</{tag}>")

    @override
    def handle_data(self, data: str):
        self._chunks.append(html.escape(data))

    @override
    def handle_entityref(self, name: str):
        self._chunks.append(f"&{name};")

    @override
    def handle_charref(self, name: str):
        self._chunks.append(f"&#{name};")

    def get_html(self) -> str:
        return "".join(self._chunks)
