import re
from bs4 import BeautifulSoup, SoupStrainer, Tag, NavigableString, Doctype
from typing import Generator
from urllib.parse import urljoin,urlparse


def langchain_docs_extractor(html: str,
                             include_output_cells: bool,
                             path_url: str | None = None) -> str:
    """
    Receives HTML and returns formatted text (Markdown) 
    after cleaning and extracting main content.
    """
    try:
        # Definimos las etiquetas 'grandes' de contenedor
        tags = ['article', 'div', 'section', 'body', 'main']

        soup = BeautifulSoup(html, "html.parser", parse_only=SoupStrainer(tags))

        # Removemos elementos no deseados
        SCAPE_TAGS = ["nav", "footer", "aside", "script", "style"]
        [tag.decompose() for tag in soup.find_all(SCAPE_TAGS)]

        def get_text(tag: Tag) -> Generator[str, None, None]:
            for child in tag.children:
                if isinstance(child, Doctype):
                    continue

                if isinstance(child, NavigableString):
                    yield child.get_text()
                elif isinstance(child, Tag):
                    # Encabezados
                    if child.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                        text = child.get_text(strip=False)
                        if text == "API Reference:":
                            yield f"> **{text}**\n"
                            ul = child.find_next_sibling("ul")
                            if ul is not None and isinstance(ul, Tag):
                                ul.attrs["api_reference"] = "true"
                        else:
                            yield f"{'#' * int(child.name[1:])} "
                            yield from child.get_text(strip=False)
                            if path_url is not None:
                                link = child.find("a")
                                if link is not None:
                                    yield f" [](/{path_url}/{link.get('href')})"
                            yield "\n\n"

                    elif child.name == "a":
                        yield f"[{child.get_text(strip=False)}]({child.get('href')})"

                    elif child.name == "img":
                        yield f"![{child.get('alt', '')}]({child.get('src')})"

                    elif child.name in ["strong", "b"]:
                        yield f"**{child.get_text(strip=False)}**"

                    elif child.name in ["em", "i"]:
                        yield f"_{child.get_text(strip=False)}_"

                    elif child.name == "br":
                        yield "\n"

                    elif child.name == "code":
                        parent = child.find_parent()
                        if parent is not None and parent.name == "pre":
                            classes = parent.attrs.get("class", "")
                            language = next(
                                filter(lambda x: re.match(r"language-\w+", x), classes),
                                None,
                            )
                            if language is None:
                                language = ""
                            else:
                                language = language.split("-")[1]

                            # Si el contenido es pycon / text y no se quieren output cells, saltar
                            if language in ["pycon", "text"] and not include_output_cells:
                                continue

                            lines = []
                            for span in child.find_all("span", class_="token-line"):
                                line_content = "".join(
                                    token.get_text() for token in span.find_all("span")
                                )
                                lines.append(line_content)

                            code_content = "\n".join(lines)
                            yield f"```{language}\n{code_content}\n```\n\n"
                        else:
                            yield f"`{child.get_text(strip=False)}`"

                    elif child.name == "p":
                        yield from get_text(child)
                        yield "\n\n"

                    elif child.name == "ul":
                        if "api_reference" in child.attrs:
                            for li in child.find_all("li", recursive=False):
                                yield "> - "
                                yield from get_text(li)
                                yield "\n"
                        else:
                            for li in child.find_all("li", recursive=False):
                                yield "- "
                                yield from get_text(li)
                                yield "\n"
                        yield "\n\n"

                    elif child.name == "ol":
                        for i, li in enumerate(child.find_all("li", recursive=False)):
                            yield f"{i + 1}. "
                            yield from get_text(li)
                            yield "\n\n"

                    elif child.name == "div" and "tabs-container" in child.attrs.get("class", []):
                        tabs = child.find_all("li", {"role": "tab"})
                        tab_panels = child.find_all("div", {"role": "tabpanel"})
                        for tab, tab_panel in zip(tabs, tab_panels):
                            tab_name = tab.get_text(strip=True)
                            yield f"{tab_name}\n"
                            yield from get_text(tab_panel)

                    elif child.name == "table":
                        thead = child.find("thead")
                        header_exists = isinstance(thead, Tag)
                        if header_exists:
                            headers = thead.find_all("th")
                            if headers:
                                yield "| "
                                yield " | ".join(header.get_text() for header in headers)
                                yield " |\n"
                                yield "| "
                                yield " | ".join("----" for _ in headers)
                                yield " |\n"

                        tbody = child.find("tbody")
                        tbody_exists = isinstance(tbody, Tag)
                        if tbody_exists:
                            for row in tbody.find_all("tr"):
                                yield "| "
                                yield " | ".join(
                                    cell.get_text(strip=True) for cell in row.find_all("td")
                                )
                                yield " |\n"
                        yield "\n\n"

                    elif child.name in ["button"]:
                        # Omite botones
                        continue

                    else:
                        yield from get_text(child)

        joined = "".join(get_text(soup))
        return re.sub(r"\n\n+", "\n\n", joined).strip()

    except Exception as e:
        print(f"Error in langchain_docs_extractor: {e}")
        return ""


def extract_links_from_markdown(url: str, text: str) -> list[str]:
    # Extraer el dominio base de la URL original (ej: "gpcustomersupportfcwc2025.tickets.fifa.com")
    base_netloc = urlparse(url).netloc

    # Patrón regex mejorado (excluye imágenes y captura solo enlaces)
    pattern = r'(?<!\!)\[[^\]]+\]\(([^)]+)\)'
    raw_urls = re.findall(pattern, text)

    final_urls = []
    
    for raw_url in raw_urls:
        # Convertir a URL absoluta usando la base
        absolute_url = urljoin(url, raw_url)
        
        # Obtener el dominio del enlace absoluto
        parsed_url = urlparse(absolute_url)
        url_netloc = parsed_url.netloc

        # Filtrar solo URLs del mismo dominio y evitar archivos (opcional)
        if url_netloc == base_netloc and not parsed_url.path.endswith(('.png', '.jpg', '.pdf')):
            final_urls.append(absolute_url)

    return final_urls