"""Tests for FakeEmbedder."""

from rag_system.embeddings.fake import FakeEmbedder


def test_n_inputs_produce_n_vectors():
    embedder = FakeEmbedder(dimension=8)
    vectors = embedder.embed_documents(["a", "b", "c"])
    assert len(vectors) == 3


def test_consistent_dimension():
    embedder = FakeEmbedder(dimension=16)
    vectors = embedder.embed_documents(["hello", "world"])
    assert all(len(v) == 16 for v in vectors)


def test_same_input_is_stable():
    embedder = FakeEmbedder(dimension=8)
    v1 = embedder.embed_documents(["same text"])
    v2 = embedder.embed_documents(["same text"])
    assert v1 == v2
