import json
import os


class ScoreStore:
    def __init__(self, filename="high_score.json"):
        self.filename = filename
        self.high_score = 0
        self.load_high_score()

    def load_high_score(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as file:
                    data = json.load(file)
                    self.high_score = data.get('high_score', 0)
            else:
                self.high_score = 0
                self.save_high_score()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading high score: {e}")
            self.high_score = 0
            self.save_high_score()

    def save_high_score(self):
        try:
            data = {'high_score': self.high_score}
            with open(self.filename, 'w') as file:
                json.dump(data, file, indent=2)
        except IOError as e:
            print(f"Error saving high score: {e}")

    def update_high_score(self, new_score):
        if new_score > self.high_score:
            self.high_score = new_score
            self.save_high_score()
            return True
        return False

    def get_high_score(self):
        return self.high_score


score_store = ScoreStore()