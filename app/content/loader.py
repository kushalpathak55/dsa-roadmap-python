"""Loads topics.yaml + per-topic markdown/frontmatter into structures the app uses for nav and topic pages."""

from __future__ import annotations

import functools
import re
from dataclasses import dataclass, field
from pathlib import Path

import frontmatter
import markdown as markdown_lib
import yaml

# codehilite always emits exactly `<div class="codehilite"><pre>...</pre></div>`
# with no nested divs inside, so a non-greedy match to the first following
# </div> reliably captures one block at a time even when a topic has several -
# wrapping each one with a header bar (dots + working copy button) here, once,
# is simpler than templating it per-block since explanation_html is a single
# blob of prose and code mixed together, not a list Jinja can iterate.
_CODEHILITE_RE = re.compile(r'<div class="codehilite">.*?</div>', re.DOTALL)
_CODE_CARD_HEADER = (
    '<div class="code-card"><div class="code-top">'
    '<div class="code-dots"><span></span><span></span><span></span></div>'
    '<button type="button" class="copy-btn">Copy</button>'
    '</div>'
)


def _wrap_code_blocks(html: str) -> str:
    return _CODEHILITE_RE.sub(lambda m: f"{_CODE_CARD_HEADER}{m.group(0)}</div>", html)

CONTENT_DIR = Path(__file__).parent
TOPICS_YAML = CONTENT_DIR / "topics.yaml"

# Category is a text label only now - color carries no category information
# (see style.css's design-tokens comment: complexity is the one consistent
# color language). Emoji is still used as a small icon next to the label.
CATEGORY_META: dict[str, dict[str, str]] = {
    "Foundations": {"emoji": "📐"},
    "Arrays & Searching": {"emoji": "🔍"},
    "Array Techniques": {"emoji": "↔️"},
    "Sorting": {"emoji": "🔀"},
    "Linked Lists": {"emoji": "🔗"},
    "Stacks & Queues": {"emoji": "🥞"},
    "Hashing": {"emoji": "🗂️"},
    "Trees": {"emoji": "🌳"},
    "Heaps": {"emoji": "⛰️"},
    "Graphs": {"emoji": "🕸️"},
    "Dynamic Programming": {"emoji": "🧩"},
    "Backtracking": {"emoji": "♛"},
}
DEFAULT_CATEGORY_META = {"emoji": "✨"}


def _path_slug(name: str) -> str:
    # e.g. "Arrays & Searching" -> "arrays_searching" - for the file-path-style
    # breadcrumb on a topic page (see topic.html).
    return "_".join(name.replace("&", "").split()).lower()


def complexity_bucket_for(raw: str) -> str:
    """Maps a single complexity string (e.g. "O(n log n)") to one of the 7
    buckets that drive this app's single color language (style.css's --c-*
    tokens). Used both for a topic's overall bucket (via time_avg) and,
    independently, for each cell of the per-topic complexity table - a
    O(1)-best/O(n)-worst row gets two different chip colors, not one color
    restated four times. Verified against every distinct complexity string
    actually used across app/content/*.md, not guessed."""
    s = (raw or "").strip()
    if s in ("", "-"):
        return "root"
    n = s.lower().replace(" ", "")
    if "!" in n or "2^" in n:
        return "exp"
    if "^2" in n or n in ("o(n*w)", "o(n*m)"):
        return "n2"
    if "log" in n and ("+e)" in n or "n*log" in n or "nlog" in n):
        return "nlogn"
    if "log" in n:
        return "logn"
    if n == "o(1)" or "α" in s.lower() or "alpha" in n:
        return "1"
    return "n"


def _complexity_bucket(status: str, complexity: "Complexity") -> str:
    """A topic's overall complexity bucket, from its typical (time_avg) cost -
    the one color that carries through its badge/nav/viz everywhere else on
    its page. content_only topics (a concept, not a complexity class, e.g.
    Big-O Notation itself) always bucket as "root"."""
    if status == "content_only":
        return "root"
    return complexity_bucket_for(complexity.time_avg)


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
    requires: list[str] = field(default_factory=list)
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
    def category_path(self) -> str:
        return _path_slug(self.category)

    @property
    def complexity_bucket(self) -> str:
        return _complexity_bucket(self.status, self.complexity)


@dataclass
class Category:
    name: str
    topics: list[Topic] = field(default_factory=list)

    @property
    def emoji(self) -> str:
        return CATEGORY_META.get(self.name, DEFAULT_CATEGORY_META)["emoji"]


def _load_topic_content(topic_meta: dict) -> Topic:
    md_path = CONTENT_DIR / topic_meta["markdown"]
    complexity = Complexity()
    body_html = "<p><em>Content coming soon.</em></p>"
    eli5_html = ""

    if md_path.exists():
        post = frontmatter.load(md_path)
        body_html = _wrap_code_blocks(
            markdown_lib.markdown(
                post.content,
                extensions=["fenced_code", "codehilite", "tables"],
                extension_configs={"codehilite": {"guess_lang": False}},
            )
        )
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
        requires=topic_meta.get("requires", []) or [],
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


def get_prev_next(topic: Topic) -> tuple[Topic | None, Topic | None]:
    """The mini-map strip and path-nav cards on a topic page show one step
    back and one step forward along the prerequisite DAG - not a flat
    previous/next by list order (that stopped meaning anything once the
    homepage became a graph, not a scrollable list). "prev" is the topic's
    own first prerequisite; "next" is the first topic (in category/order
    sequence) that lists this one as a prerequisite. Either can be None (the
    root has no prev, a leaf has no next)."""
    categories, by_slug = load_roadmap()
    prev_topic = by_slug.get(topic.requires[0]) if topic.requires else None
    next_topic = None
    for category in categories:
        for candidate in category.topics:
            if topic.slug in candidate.requires:
                next_topic = candidate
                break
        if next_topic:
            break
    return prev_topic, next_topic
