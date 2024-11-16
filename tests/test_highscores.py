import json
from autokat.highscores import Highscore, Highscores


class DummyPath:
    def __init__(self, text=""):
        self._text = text

    def read_text(self):
        return self._text

    def write_text(self, text):
        self._text = text


def test_highscores_load():
    highscores = Highscores(
        DummyPath(
            json.dumps(
                [
                    {"team_name": "team1", "score": 100},
                    {"team_name": "team2", "score": 90},
                ]
            )
        )
    )
    assert highscores.top(5) == [
        Highscore(team_name="team1", score=100),
        Highscore(team_name="team2", score=90),
    ]

def test_highscores_insert():
    highscores = Highscores(
        DummyPath(
            json.dumps(
                [
                    {"team_name": "team1", "score": 100},
                    {"team_name": "team2", "score": 90},
                ]
            )
        )
    )
    highscores.add_score("team3", 95)
    assert highscores.top(5) == [
        Highscore(team_name="team1", score=100),
        Highscore(team_name="team3", score=95),
        Highscore(team_name="team2", score=90),
    ]

def test_highscores_insert_stable():
    highscores = Highscores(
        DummyPath(
            json.dumps(
                [
                    {"team_name": "team1", "score": 100},
                    {"team_name": "team2", "score": 90},
                ]
            )
        )
    )
    highscores.add_score("team3", 100)
    assert highscores.top(5) == [
        Highscore(team_name="team1", score=100),
        Highscore(team_name="team3", score=100),
        Highscore(team_name="team2", score=90),
    ]
