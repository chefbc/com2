# Copyright (c) 2016-2024 Martin Donath <martin.donath@squidfunk.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import os
import re

from glob import iglob
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from urllib.parse import urlencode, urlparse

from rich import inspect
# from mkdocs.utils import log

# def write_to_mkdocs_log(message: str, level: str = "info"):
#     if level == "info":
#         log.info(message)
#     elif level == "warning":
#         log.warning(message)
#     elif level == "error":
#         log.error(message)
#     else:
#         log.debug(message)

# Example usage:
# write_to_mkdocs_log("This is an informational message")
# write_to_mkdocs_log("This is a warning message", "warning")

# -----------------------------------------------------------------------------
# Hooks
# -----------------------------------------------------------------------------

# def on_page_markdown(markdown: str, *, page: Page, config: MkDocsConfig, files):
#     global timeline_html
#     if page.file.src_uri == "articles/index.md":
#         markdown += "\n" + timeline_html
    
#     timeline_html = "<div class=\"timeline\">\n"
#     for article_title, article_details in articles.items():
#         timeline_html += "  <div class=\"entry\">\n"
#         timeline_html += f"    <div class=\"title\">{article_details['title']}</div>\n"
#         timeline_html += f"    <div class=\"content\">{article_details['content']}</div>\n"
#         timeline_html += "  </div>\n"
#     timeline_html += "</div>"
    
#     return timeline_html

def on_page_markdown(markdown: str, *, page: Page, config: MkDocsConfig, files):
    global timeline_html
    timeline_html = ""  # Initialize timeline_html as an empty string
    if page.file.src_uri == "articles/index.md":
        markdown += "\n" + timeline_html

    timeline_html += "<div class=\"rightbox\">\n"
    timeline_html += "  <div class=\"rb-container\">\n"
    timeline_html += "    <ul class=\"rb\">\n"
    
    for article in articles:
        timeline_html += "      <li class=\"rb-item\">\n"
        timeline_html += f"        <div class=\"timestamp\">\n          {article['timestamp']}\n        </div>\n"
        timeline_html += f"        <div class=\"item-title\">{article['title']}</div>\n"
        timeline_html += "      </li>\n"
    
    timeline_html += "    </ul>\n"
    timeline_html += "  </div>\n"
    timeline_html += "</div>\n"
    
    # Append timeline_html to markdown regardless of the condition
    markdown += "\n" + timeline_html
    
    return markdown


# Determine missing translations and render language overview in the setup
# guide, including links to provide missing translations.
# def on_page_markdown(markdown: str, *, page: Page, config: MkDocsConfig, files):
#     if page.file.src_uri != "test/index.md":
#         return markdown
    
#     language_links = []
#     for code, country in countries.items():
#         language_link = f"https://translate.squidfunk.com/{code}"
#         language_links.append(f"- [{code.upper()}]({language_link}) for {country.upper()}\n")
#     markdown += "\n## Available Translations\n"
#     markdown += "".join(language_links)

#     #text_to_append = "\n## Available Translations\n"  # Your text here
#     #append_to_markdown("docs/test/index.md", text_to_append)
    
#     return markdown


# def append_to_markdown(file_path, text):
#     with open(file_path, "a") as file:
#         file.write(text)



# -----------------------------------------------------------------------------
# Data
# -----------------------------------------------------------------------------

# articles = {
#     "Introduction to Python": {"title": "Introduction to Python", "content": "Python is a high-level, interpreted, and general-purpose programming language that emphasizes code readability."},
#     "Understanding AI": {"title": "Understanding AI", "content": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and learn."},
#     "Web Development Basics": {"title": "Web Development Basics", "content": "Web development is the work involved in developing a website for the Internet or an intranet."},
#     "Data Science Explained": {"title": "Data Science Explained", "content": "Data Science is a multidisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from structured and unstructured data."},
#     "The Future of Technology": {"title": "The Future of Technology", "content": "Emerging technologies such as AI, blockchain, and quantum computing are set to redefine the future of technology."}
# }


articles = [
    {
        "title": "Chris Serrano posted a photo on your wall.",
        "timestamp": "3rd May 2020<br> 7:00 PM",
        "message": "Chris Serrano posted a photo on your wall."
    },
    {
        "title": "Chris Serrano posted a photo on your wall.",
        "timestamp": "3rd May 2020<br> 7:00 PM",
        "message": "Chris Serrano posted a photo on your wall."
    },
    {
        "title": "Chris Serrano posted a photo on your wall.",
        "timestamp": "3rd May 2020<br> 7:00 PM",
        "message": "Chris Serrano posted a photo on your wall."
    },
    # Add more entries as needed
]



