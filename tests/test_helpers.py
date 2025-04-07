import unittest
import sqlite3
import os
from datetime import datetime
from app.utils import helpers

TEST_DB = "test_helpers.db"

class TestHelperFunctions(unittest.TestCase):
    def setUp(self):
        # Setup test DB
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        helpers.init_journal_db(TEST_DB)
        helpers.init_archetype_db(TEST_DB)

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_log_and_get_archetype_use(self):
        user_id = "tester"
        archetype = "Theo"
        is_custom = True
        module = "respond"
        mood = "hopeful"

        helpers.log_archetype_use(user_id, archetype, is_custom, module, mood, db_path=TEST_DB)
        usage_summary = helpers.get_archetype_usage_summary(user_id, db_path=TEST_DB)

        self.assertEqual(len(usage_summary), 1)
        self.assertEqual(usage_summary[0][0], "Theo")
        self.assertEqual(usage_summary[0][1], 1)

    def test_log_feedback_entry(self):
        user_id = "tester"
        archetype = "Fox"
        mood = "energetic"
        input_text = "I need help focusing"
        response_text = "Let's break it down."
        rating = 5
        comment = "Very helpful"

        helpers.log_feedback_entry(user_id, archetype, mood, input_text, response_text, rating, comment, db_path=TEST_DB)

        conn = sqlite3.connect(TEST_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feedback WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()

        self.assertEqual(len(rows), 1)
        # Assuming the table schema is: id, user_id, archetype, mood, input, response, rating, comment, timestamp
        self.assertEqual(rows[0][2], "Fox")       # archetype
        self.assertEqual(rows[0][6], 5)             # rating
        self.assertEqual(rows[0][7], "Very helpful")# comment

if __name__ == '__main__':
    unittest.main()
