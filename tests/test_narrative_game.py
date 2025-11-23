import pytest

from narrative_game import NarrativeGame


def test_convoy_ending():
    game = NarrativeGame()
    result = game.simulate_path([1, 0, 0])
    assert result["ending"] == "The Convoy Forms"
    assert "Hands clasp" in result["summary"] or game.state.trust >= 2


def test_storm_ending_detach():
    game = NarrativeGame()
    result = game.simulate_path([0, 1, 1])
    assert result["ending"] == "Riding Out the Storm"
    assert game.state.trust < 0
    assert game.state.supplies <= 2


def test_invalid_scripted_choice_raises():
    game = NarrativeGame()
    with pytest.raises(IndexError):
        game.simulate_path([5])
