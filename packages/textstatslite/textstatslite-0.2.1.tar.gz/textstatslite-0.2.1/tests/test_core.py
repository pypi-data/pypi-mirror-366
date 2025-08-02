import unittest
from textstatslite import core

class TestTextStats(unittest.TestCase):
    def setUp(self):
        self.text = "Python is simple. Python is powerful and fun."

    def test_word_count(self):
        self.assertEqual(core.count_words(self.text), 8)

    def test_word_count_exclude_stopwords(self):
        self.assertEqual(core.count_words(self.text, exclude_stopwords=True), 5)

    def test_sentence_count(self):
        self.assertEqual(core.count_sentences(self.text), 2)

    def test_character_count(self):
        self.assertEqual(core.count_characters(self.text), len(self.text))

    def test_character_count_no_spaces(self):
        self.assertEqual(core.count_characters(self.text, include_spaces=False), len(self.text.replace(" ", "")))

    def test_average_word_length(self):
        self.assertAlmostEqual(core.average_word_length(self.text), 4.5, places=2)

    def test_average_word_length_exclude_stopwords(self):
        avg = core.average_word_length(self.text, exclude_stopwords=True)
        self.assertTrue(4.5 < avg < 6.5)

    def test_most_frequent_words(self):
        result = core.most_frequent_words(self.text, n=2)
        self.assertIn(('python', 2), result)

    def test_readability_score(self):
        score = core.flesch_reading_ease(self.text)
        self.assertIsInstance(score, float)

    def test_get_text_statistics(self):
        stats = core.get_text_statistics(self.text)
        self.assertIn("word_count", stats)
        self.assertIn("flesch_reading_ease", stats)

if __name__ == "__main__":
    unittest.main()