"""Minimal hybrid memory agent for the Lab 19 bonus challenge.

The production design would use Qdrant for episodic memory and Feast for user
features. This POC keeps the same boundaries but uses in-memory structures so
`python bonus/demo.py` runs without external services.
"""

import math
import re
import unicodedata
from collections import Counter, defaultdict, deque


class HybridMemoryAgent:
    def __init__(self, top_k: int = 3) -> None:
        self.top_k = top_k
        self.memories: list[dict[str, object]] = []
        self.recent_queries = defaultdict(lambda: deque(maxlen=12))
        self.default_profile = {
            "preferred_language": "vi",
            "reading_speed_wpm": 200,
            "topic_affinity": ["cloud"],
            "active_hours": "unknown",
        }
        self.user_profiles = {
            "u_001": {
                "preferred_language": "vi-en-mix",
                "reading_speed_wpm": 220,
                "topic_affinity": ["kubernetes", "cloud security", "terraform", "ai engineering"],
                "active_hours": "20:00-23:00",
            }
        }
        self.synonyms = {
            "autoscale": ["autoscaling", "auto scaling", "tu dong mo rong", "mo rong"],
            "autoscaling": ["autoscale", "tu dong mo rong", "horizontal pod autoscaler", "hpa"],
            "bao mat": ["security", "secure", "least privilege", "iam", "network policy"],
            "security": ["bao mat", "iam", "least privilege", "network policy", "secret"],
            "ha tang": ["infrastructure", "infra", "node", "cluster", "cloud"],
            "infrastructure": ["ha tang", "infra", "cloud", "cluster"],
            "dam may": ["cloud", "aws", "gcp", "azure"],
            "cloud": ["dam may", "aws", "gcp", "azure"],
            "kubernetes": ["k8s", "pod", "cluster", "hpa", "node pool"],
            "terraform": ["iac", "infrastructure as code"],
            "recommend": ["goi y", "doc gi tiep", "next"],
            "summary": ["tom tat", "tong ket"],
        }

    def remember(self, text: str, user_id: str = "u_001") -> None:
        """Add a new piece of episodic memory for this user."""
        for chunk in self._chunk(text):
            self.memories.append({"user_id": user_id, "text": chunk, "tokens": self._tokens(chunk)})

    def recall(self, query: str, user_id: str = "u_001") -> str:
        """Retrieve top-K memories + user profile features and assemble context."""
        self.recent_queries[user_id].append(query)
        profile = self.user_profiles.get(user_id, self.default_profile)
        query_tokens = self._tokens(query)
        ranked = self._search(query_tokens, user_id, profile)

        top_memories = "\n".join(
            f"{idx}. score={score:.2f} | {memory['text']}" for idx, (memory, score) in enumerate(ranked, 1)
        )
        if not top_memories:
            top_memories = "No matching memories found."

        recent = list(self.recent_queries[user_id])
        recent_topics = self._recent_topics(recent)
        fatigue_signal = self._fatigue_signal(recent)

        return (
            f"User profile:\n"
            f"- preferred_language: {profile['preferred_language']}\n"
            f"- reading_speed_wpm: {profile['reading_speed_wpm']}\n"
            f"- topic_affinity: {', '.join(profile['topic_affinity'])}\n"
            f"- active_hours: {profile['active_hours']}\n\n"
            f"Recent activity:\n"
            f"- queries_last_hour: {recent}\n"
            f"- recent_topics: {', '.join(recent_topics) or 'unknown'}\n"
            f"- fatigue_signal: {fatigue_signal}\n\n"
            f"Top memories:\n{top_memories}\n\n"
            f"Assembled instruction:\n"
            f"Answer in {profile['preferred_language']}. Prefer concise cloud-learning guidance, "
            f"boost topics matching {', '.join(profile['topic_affinity'])}, and cite memories above."
        )

    def _chunk(self, text: str) -> list[str]:
        return [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]

    def _search(
        self, query_tokens: Counter[str], user_id: str, profile: dict[str, object]
    ) -> list[tuple[dict[str, object], float]]:
        scored: list[tuple[dict[str, object], float]] = []
        for memory in self.memories:
            if memory["user_id"] != user_id:
                continue
            lexical = self._cosine(query_tokens, memory["tokens"])
            topic_boost = self._topic_boost(query_tokens, str(memory["text"]), profile)
            score = lexical + topic_boost
            if score > 0:
                scored.append((memory, score))
        return sorted(scored, key=lambda item: item[1], reverse=True)[: self.top_k]

    def _tokens(self, text: str) -> Counter[str]:
        normalized = self._normalize(text)
        expanded = [normalized]
        for term, variants in self.synonyms.items():
            if term in normalized or any(variant in normalized for variant in variants):
                expanded.extend([term, *variants])
        token_text = " ".join(expanded)
        return Counter(re.findall(r"[a-z0-9]+", token_text))

    def _normalize(self, text: str) -> str:
        without_accents = "".join(
            char for char in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(char) != "Mn"
        )
        return re.sub(r"\s+", " ", without_accents).strip()

    def _cosine(self, left: Counter[str], right: Counter[str]) -> float:
        common = set(left) & set(right)
        numerator = sum(left[token] * right[token] for token in common)
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

    def _topic_boost(self, query_tokens: Counter[str], memory_text: str, profile: dict[str, object]) -> float:
        memory_norm = self._normalize(memory_text)
        boost = 0.0
        for topic in profile["topic_affinity"]:
            topic_tokens = set(self._tokens(topic))
            if topic_tokens & set(query_tokens) and any(token in memory_norm for token in topic_tokens):
                boost += 0.08
        return boost

    def _recent_topics(self, queries: list[str]) -> list[str]:
        joined = " ".join(queries)
        tokens = self._tokens(joined)
        topics = []
        for topic in ["kubernetes", "autoscaling", "cloud security", "terraform", "ai engineering"]:
            if set(self._tokens(topic)) & set(tokens):
                topics.append(topic)
        return topics

    def _fatigue_signal(self, queries: list[str]) -> str:
        if not queries:
            return "unknown"
        avg_words = sum(len(query.split()) for query in queries) / len(queries)
        return "possible_late_night_deep_work" if avg_words >= 7 else "normal"
