#!/usr/bin/env python3
"""Fetch a narottam.com (WordPress) article and return clean title + body text."""
import sys, re, urllib.request
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"

def fetch_html(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", errors="replace")

def extract(url, html=None):
    if html is None:
        html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    # article title (prefer the post's <h1>, fall back to og:title / <title>)
    title = None
    h1 = soup.find(["h1"], class_=re.compile("entry-title|post-title", re.I)) or soup.find("h1")
    if h1:
        title = h1.get_text(" ", strip=True)
    if not title:
        og = soup.find("meta", property="og:title")
        if og and og.get("content"):
            title = og["content"].strip()

    # main body
    node = soup.find(class_=re.compile(r"\bentry-content\b"))
    if node is None:
        node = soup.find("article") or soup.body
    # drop scripts/styles/nav/share widgets
    for bad in node.find_all(["script", "style", "noscript", "form"]):
        bad.decompose()
    for bad in node.find_all(class_=re.compile("share|social|related|nav|sidebar|comment", re.I)):
        bad.decompose()

    # collect block-level text with blank lines between paragraphs
    parts = []
    for el in node.find_all(["p", "h2", "h3", "h4", "li", "blockquote"]):
        t = el.get_text(" ", strip=True)
        if t:
            parts.append(t)
    if not parts:
        parts = [node.get_text("\n", strip=True)]
    body = "\n\n".join(parts)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return title, body

if __name__ == "__main__":
    url = sys.argv[1]
    t, b = extract(url)
    print("TITLE:", t)
    print("WORDS:", len(b.split()))
    print("-----")
    print(b[:1500])
