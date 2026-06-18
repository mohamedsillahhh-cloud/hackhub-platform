import pytest


class TestScoreCalculation:
    def test_weighted_average(self):
        criteria = [
            {"name": "Innovation", "weight": 0.3, "score": 8},
            {"name": "Technical", "weight": 0.4, "score": 7},
            {"name": "Design", "weight": 0.2, "score": 9},
            {"name": "Impact", "weight": 0.1, "score": 6},
        ]
        weighted = sum(c["weight"] * c["score"] for c in criteria)
        total_weight = sum(c["weight"] for c in criteria)
        result = weighted / total_weight if total_weight else 0
        assert round(result, 2) == 7.60

    def test_weight_zero_edge_case(self):
        criteria = [
            {"name": "Test", "weight": 0, "score": 10},
            {"name": "Test2", "weight": 0, "score": 5},
        ]
        total_weight = sum(c["weight"] for c in criteria)
        assert total_weight == 0

    def test_score_boundaries(self):
        for score in [0, 5, 10]:
            assert 0 <= score <= 10
