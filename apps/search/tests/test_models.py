import pytest
from apps.search.models import SearchIndex


class TestSearchIndex:
    def test_search_index_creation(self):
        index = SearchIndex(content_type="user", object_id="42", content="John Doe")
        assert index.content_type == "user"
        assert index.object_id == "42"

    def test_search_index_str(self):
        index = SearchIndex(content_type="doc", object_id="1")
        assert "doc:1" in str(index)
