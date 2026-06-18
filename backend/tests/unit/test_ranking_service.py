import pytest


class TestRankingTiebreaker:
    def test_tiebreaker_priority(self):
        entries = [
            {"team_name": "A", "innovation": 8, "impact": 9, "technical": 7, "design": 8, "total": 80},
            {"team_name": "B", "innovation": 7, "impact": 8, "technical": 9, "design": 7, "total": 80},
        ]
        sorted_entries = sorted(
            entries,
            key=lambda e: (e["total"], e["innovation"], e["impact"], e["technical"], e["design"]),
            reverse=True,
        )
        assert sorted_entries[0]["team_name"] == "A"

    def test_no_tie(self):
        entries = [
            {"team_name": "A", "total": 90},
            {"team_name": "B", "total": 80},
        ]
        sorted_entries = sorted(entries, key=lambda e: e["total"], reverse=True)
        assert sorted_entries[0]["team_name"] == "A"
        assert sorted_entries[1]["team_name"] == "B"
