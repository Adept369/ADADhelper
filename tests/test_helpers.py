import os
import sqlite3
import unittest
import tempfile
from datetime import datetime
from app.utils import helpers

class TestHelperFunctions(unittest.TestCase):
    def setUp(self):
        # Create a temporary file to be used as the test database.
        temp_db = tempfile.NamedTemporaryFile(delete=False)
        temp_db.close()  # Close it so SQLite can use it.
        self.TEST_DB = temp_db.name

        # Initialize the test database tables.
        helpers.init_journal_db(self.TEST_DB)
        helpers.init_archetype_db(self.TEST_DB)

    def tearDown(self):
        # Remove the temporary database file after tests.
        if os.path.exists(self.TEST_DB):
            os.remove(self.TEST_DB)

    def test_log_and_get_archetype_use(self):
        user_id = "tester"
        archetype = "Theo"
        is_custom = True
        module = "respond"
        mood = "hopeful"

        helpers.log_archetype_use(user_id, archetype, is_custom, module, mood, db_path=self.TEST_DB)
        usage_summary = helpers.get_archetype_usage_summary(user_id, db_path=self.TEST_DB)

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

        helpers.log_feedback_entry(user_id, archetype, mood, input_text, response_text, rating, comment, db_path=self.TEST_DB)

        conn = sqlite3.connect(self.TEST_DB)
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
