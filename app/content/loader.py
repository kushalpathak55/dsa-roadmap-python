"""Loads topics.yaml + per-topic markdown/frontmatter into structures the app uses for nav and topic pages."""

from __future__ import annotations

import functools
from dataclasses import dataclass, field
from pathlib import Path

import frontmatter
import markdown as markdown_lib
import yaml

CONTENT_DIR = Path(__file__).parent
TOPICS_YAML = CONTENT_DIR / "topics.yaml"

# Bright, playful accent per category. `slot` selects a CSS custom property
# (--cat-1..--cat-8, defined in style.css) rather than a raw hex, so light/dark
# mode and future palette tweaks stay in one place. Only 8 slots exist for 12
# categories, so the lowest-collision-risk categories (farthest apart in the
# nav) reuse a slot - identity is always carried by the label + emoji too,
# never by color alone.
CATEGORY_META: dict[str, dict[str, str]] = {
    "Foundations": {"emoji": "📐", "slot": "1"},
    "Arrays & Searching": {"emoji": "🔍", "slot": "2"},
    "Array Techniques": {"emoji": "↔️", "slot": "6"},
    "Sorting": {"emoji": "🔀", "slot": "3"},
    "Linked Lists": {"emoji": "🔗", "slot": "4"},
    "Stacks & Queues": {"emoji": "🥞", "slot": "5"},
    "Hashing": {"emoji": "🗂️", "slot": "6"},
    "Trees": {"emoji": "🌳", "slot": "7"},
    "Heaps": {"emoji": "⛰️", "slot": "8"},
    "Graphs": {"emoji": "🕸️", "slot": "1"},
    "Dynamic Programming": {"emoji": "🧩", "slot": "2"},
    "Backtracking": {"emoji": "♛", "slot": "4"},
}
DEFAULT_CATEGORY_META = {"emoji": "✨", "slot": "1"}


def _path_slug(name: str) -> str:
    # e.g. "Arrays & Searching" -> "arrays_searching" - for the file-path-style
    # breadcrumb on a topic page (see topic.html).
    return "_".join(name.replace("&", "").split()).lower()


@dataclass
class Complexity:
    time_best: str = "-"
    time_avg: str = "-"
    time_worst: str = "-"
    space: str = "-"
    stable: bool | None = None
    in_place: bool | None = None


@dataclass
class Topic:
    slug: str
    category: str
    title: str
    order: int
    status: str  # "built" | "content_only" | "coming_soon"
    markdown: str
    why: str = ""
    algo_key: str | None = None
    family: str | None = None
    motion: str | None = None
    explanation_html: str = ""
    eli5_html: str = ""
    complexity: Complexity = field(default_factory=Complexity)

    @property
    def is_built(self) -> bool:
        return self.status == "built"

    @property
    def is_coming_soon(self) -> bool:
        return self.status == "coming_soon"

    @property
    def is_content_only(self) -> bool:
        """A topic that's fully written but has no algorithm to visualize
        (e.g. Big-O Notation is a concept, not a procedure) - gets neither
        the live-view visualizer nor the "coming soon" banner."""
        return self.status == "content_only"

    @property
    def has_complexity(self) -> bool:
        """False when no `complexity:` frontmatter was set at all - lets a
        content_only topic skip a Complexity table that wouldn't mean anything
        for it, without needing to special-case it by slug anywhere."""
        c = self.complexity
        return any(v not in (None, "-") for v in (c.time_best, c.time_avg, c.time_worst, c.space))

    @property
    def category_emoji(self) -> str:
        return CATEGORY_META.get(self.category, DEFAULT_CATEGORY_META)["emoji"]

    @property
    def category_slot(self) -> str:
        return CATEGORY_META.get(self.category, DEFAULT_CATEGORY_META)["slot"]

    @property
    def category_path(self) -> str:
        return _path_slug(self.category)


@dataclass
class Category:
    name: str
    topics: list[Topic] = field(default_factory=list)

    @property
    def emoji(self) -> str:
        return CATEGORY_META.get(self.name, DEFAULT_CATEGORY_META)["emoji"]

    @property
    def slot(self) -> str:
        return CATEGORY_META.get(self.name, DEFAULT_CATEGORY_META)["slot"]


def _load_topic_content(topic_meta: dict) -> Topic:
    md_path = CONTENT_DIR / topic_meta["markdown"]
    complexity = Complexity()
    body_html = "<p><em>Content coming soon.</em></p>"
    eli5_html = ""

    if md_path.exists():
        post = frontmatter.load(md_path)
        body_html = markdown_lib.markdown(post.content, extensions=["fenced_code", "tables"])
        complexity_data = post.metadata.get("complexity", {})
        complexity = Complexity(**complexity_data)
        eli5_source = post.metadata.get("eli5", "")
        if eli5_source:
            eli5_html = markdown_lib.markdown(eli5_source)

    return Topic(
        slug=topic_meta["slug"],
        category=topic_meta["category"],
        title=topic_meta["title"],
        order=topic_meta.get("order", 0),
        status=topic_meta.get("status", "coming_soon"),
        markdown=topic_meta["markdown"],
        why=topic_meta.get("why", ""),
        algo_key=topic_meta.get("algo_key"),
        family=topic_meta.get("family"),
        motion=topic_meta.get("motion"),
        explanation_html=body_html,
        eli5_html=eli5_html,
        complexity=complexity,
    )


@functools.lru_cache(maxsize=1)
def load_roadmap() -> tuple[list[Category], dict[str, Topic]]:
    """Parses topics.yaml once per process. Returns (ordered categories, slug -> Topic lookup)."""
    raw = yaml.safe_load(TOPICS_YAML.read_text(encoding="utf-8")) or []

    categories: dict[str, Category] = {}
    by_slug: dict[str, Topic] = {}

    for entry in raw:
        topic = _load_topic_content(entry)
        by_slug[topic.slug] = topic
        categories.setdefault(topic.category, Category(name=topic.category)).topics.append(topic)

    for category in categories.values():
        category.topics.sort(key=lambda t: t.order)

    return list(categories.values()), by_slug


def get_topic(slug: str) -> Topic | None:
    _, by_slug = load_roadmap()
    return by_slug.get(slug)
