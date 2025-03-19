import pytest
import string
from pathlib import Path

from src import GetNewsData, ArticleScorer

# Dummy implementations to bypass external dependencies

def dummy_nlp(text):
    # Mimic token attributes
    class DummyToken:
        def __init__(self, word):
            self.text = word
            self.is_stop = word in {"and", "the"}
            self.is_digit = word.isdigit()
            self.is_punct = False

    class DummyDoc:
        def __init__(self, text):
            # Assume text is already lowercased and punctuation removed by _clean_text
            self.text = text
            self.tokens = [DummyToken(word) for word in text.split()]
        def similarity(self, other):
            # return a value based on the length of the text
            return len(self.text) / 100.0
        def __iter__(self):
            return iter(self.tokens)
    return DummyDoc(text)

# Define a subclass to override make_request (so not call is made)
class DummyGetNewsData(GetNewsData):
    def make_request(self):
        # Instead of calling requests.get, simply return a dummy JSON.
        return {"status": "ok"}

###### GetNewsData Tests ####

def test_api_key():
    obj = GetNewsData()
    # Instead of triggering keyring directly set _api_key
    obj._api_key = "dummy_key"
    assert obj.api_key == "dummy_key"

def test_make_api_url():
    obj = GetNewsData()
    obj._api_key = "testkey"
    expected = ("https://newsapi.org/v2/top-headlines?country=us&"
                "category=politics&pageSize=60&apiKey=testkey")
    assert obj._make_api_url() == expected

def test_make_request():
    obj = DummyGetNewsData()
    obj._api_key = "dummy"
    assert obj.make_request() == {"status": "ok"}

def test_api_key_setter_type_error():
    obj = GetNewsData()
    with pytest.raises(TypeError):
        obj.api_key = "newkey"

# #### ArticleScorer Tests #####

def test_article_scorer_valid():
    articles = {"articles": [{"title": "T1", "description": "D1", "content": "C1"}]}
    scorer = ArticleScorer(articles, "comp text")
    assert scorer.articles == articles
    assert scorer.comp_txt == "comp text"

def test_article_scorer_invalid_articles():
    with pytest.raises(ValueError):
        ArticleScorer("not a dict", "comp text")

def test_article_scorer_invalid_comp_txt():
    articles = {"articles": [{"title": "T1", "description": "D1", "content": "C1"}]}
    with pytest.raises(ValueError):
        ArticleScorer(articles, 123)

def test_calc_scores():
    articles = {"articles": [
       {"title": "T1", "description": "D1", "content": "C1"},
       {"title": "T2", "description": "D2", "content": "C2"}
    ]}
    scorer = ArticleScorer(articles, "comp text")
    # setting dummy pipeline
    scorer._nlp = dummy_nlp
    # Override _score_article to always return 0.5
    scorer._score_article = lambda tup: 0.5
    scored = scorer.calc_scores(sort=False)
    for article in scored["articles"]:
        assert article.get("sim_score") == 0.5

def test_calc_scores_file_write(tmp_path):
    articles = {"articles": [{"title": "T1", "description": "D1", "content": "C1"}]}
    scorer = ArticleScorer(articles, "comp text")
    scorer._nlp = dummy_nlp
    scorer._score_article = lambda tup: 0.7
    file_path = tmp_path / "output.txt"
    scorer.calc_scores(write_file_path=str(file_path), sort=False)
    content = file_path.read_text()
    assert "'sim_score': 0.7" in content

def test_clean_text():
    articles = {"articles": [{"title": "T1", "description": "D1", "content": "C1"}]}
    scorer = ArticleScorer(articles, "comp text")
    # Use our dummy NLP to simulate token attributes
    scorer._nlp = dummy_nlp
    # _clean_text converts to lower, strips punctuation, then removes stop words and digits
    cleaned = scorer._clean_text("Hello, world! 123 and the Test.")
    
    assert cleaned == "hello world test"

def test_calc_sim_score():
    # Create two dummy doc objects with a fixed similarity
    class DummyDoc:
        def __init__(self, value):
            self.value = value
        def similarity(self, other):
            return self.value
    scorer = ArticleScorer({"articles": []}, "comp text")
    score = scorer._calc_sim_score(DummyDoc(0.75), DummyDoc(0.75))
    assert score == 0.75

def test_score_article():
    articles = {"articles": [{"title": "T1", "description": "D1", "content": "C1"}]}
    scorer = ArticleScorer(articles, "comp text")
    # Provide controlled similarity
    scores = [0.4, 0.6, 0.8]
    def fake_calc_sim_score(doc, comp_doc):
        return scores.pop(0)
    scorer._calc_sim_score = fake_calc_sim_score
    # Let _clean_text be an identity function
    scorer._clean_text = lambda text: text
    avg_score = scorer._score_article(("Title", "Description", "Content"))
    # Expected average: (0.4 + 0.6 + 0.8) / 3 = 0.6
    assert avg_score == 0.6