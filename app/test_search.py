from app.search import SearchHit, Searcher


def test_hybrid_rrf_uses_one_based_rank(monkeypatch):
    searcher = Searcher()

    kw_hits = [
        SearchHit(doc_id="a", title="A", text="keyword first", score=10.0),
        SearchHit(doc_id="b", title="B", text="keyword second", score=9.0),
    ]
    sem_hits = [
        SearchHit(doc_id="b", title="B", text="semantic first", score=0.9),
        SearchHit(doc_id="c", title="C", text="semantic second", score=0.8),
    ]

    monkeypatch.setattr(searcher, "_search_keyword", lambda query, top_k: kw_hits)
    monkeypatch.setattr(searcher, "_search_semantic", lambda query, top_k: sem_hits)

    hits = searcher._search_hybrid("query", top_k=3, rrf_k=60)
    scores = {hit.doc_id: hit.score for hit in hits}

    assert [hit.doc_id for hit in hits] == ["b", "a", "c"]
    assert scores["a"] == 1.0 / 61.0
    assert scores["b"] == 1.0 / 62.0 + 1.0 / 61.0
    assert scores["c"] == 1.0 / 62.0
