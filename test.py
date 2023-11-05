import unittest
from main2 import set_timezone  # Assuming the bot code is in a file named main.py
import datetime
import pytz
from mock import patch


class TestSetTimezone(unittest.TestCase):
    def test_timezone_parsing(self):
        context = type('', (), {})()  # Creating an empty class for context
        context.user_data = {'wakeup': '08:00'}
        timezone_str = "UTC+3"

        offset_minutes = int(timezone_str.split("UTC")[-1]) * 60
        self.assertEqual(offset_minutes, 180)

    def test_wakeup_time_adjustment(self):
        context = type('', (), {})()  # Creating an empty class for context
        context.user_data = {'wakeup': '08:00'}
        timezone_str = "UTC+3"
        user_timezone = pytz.FixedOffset(180)
        now = datetime.datetime.now(user_timezone).time()

# Assuming the current time is 09:00
        with patch('datetime.datetime') as mock_date:
            # Intended to be a naive datetime
            naive_datetime = datetime.datetime(2023, 1, 1, 9, 0)
            localized_datetime = naive_datetime.replace(tzinfo=user_timezone)
            mock_date.now.return_value = localized_datetime
            mock_date.time.return_value = now  # Corrected this line


# Only if being run as a script, not if imported
if __name__ == '__main__':
    unittest.main()
