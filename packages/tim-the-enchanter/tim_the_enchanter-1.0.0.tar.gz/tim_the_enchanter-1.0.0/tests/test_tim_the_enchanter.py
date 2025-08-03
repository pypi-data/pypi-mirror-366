"""Tests for Tim The Enchanter package."""

import time
import unittest
from tim_the_enchanter import TimTheEnchanter, TimTheEnchanterReportFormat


class TestTimTheEnchanter(unittest.TestCase):
    """Test cases for the TimTheEnchanter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.tracker = TimTheEnchanter.create(enabled=True)
        self.session_id = self.tracker.start_session("test_session")

    def tearDown(self):
        """Tear down test fixtures."""
        if self.session_id:
            self.tracker.end_session(self.session_id)

    def test_record(self):
        """Test that recording events works correctly."""
        self.tracker.record(self.session_id, "test_process", 0.5)
        report = self.tracker.report(self.session_id, TimTheEnchanterReportFormat.CHRONOLOGICAL)
        self.assertEqual(report["format"], "chronological")
        self.assertEqual(report["session"], "test_session")
        self.assertEqual(len(report["events"]), 1)
        self.assertEqual(report["events"][0]["process_name"], "test_process")
        self.assertEqual(report["events"][0]["duration"], 0.5)

    def test_time_process(self):
        """Test the time_process context manager."""
        with self.tracker.time_process(self.session_id, "context_test"):
            time.sleep(0.01)  # Small sleep to ensure timing
        
        report = self.tracker.report(self.session_id, TimTheEnchanterReportFormat.BY_PROCESS)
        self.assertEqual(report["format"], "by_process")
        self.assertIn("context_test", report["processes"])
        self.assertEqual(len(report["processes"]["context_test"]), 1)
        self.assertGreater(report["processes"]["context_test"][0]["duration"], 0)

    def test_multiple_sessions(self):
        """Test that multiple sessions are isolated."""
        session1 = self.tracker.start_session("session1")
        session2 = self.tracker.start_session("session2")
        
        self.tracker.record(session1, "process1", 0.1)
        self.tracker.record(session2, "process2", 0.2)
        
        # Check that sessions are isolated
        report1 = self.tracker.report(session1, TimTheEnchanterReportFormat.CHRONOLOGICAL)
        report2 = self.tracker.report(session2, TimTheEnchanterReportFormat.CHRONOLOGICAL)
        
        self.assertEqual(len(report1["events"]), 1)
        self.assertEqual(len(report2["events"]), 1)
        self.assertEqual(report1["events"][0]["process_name"], "process1")
        self.assertEqual(report2["events"][0]["process_name"], "process2")
        
        self.tracker.end_session(session1)
        self.tracker.end_session(session2)

    def test_session_management(self):
        """Test session creation, listing, and deletion."""
        # Create multiple sessions
        session1 = self.tracker.start_session("session1")
        session2 = self.tracker.start_session("session2")
        
        # List sessions
        sessions = self.tracker.list_sessions()
        self.assertIn("session1", sessions)
        self.assertIn("session2", sessions)
        self.assertIn("test_session", sessions)
        
        # Delete a session
        self.tracker.delete_session(session1)
        sessions_after_delete = self.tracker.list_sessions()
        self.assertNotIn("session1", sessions_after_delete)
        self.assertIn("session2", sessions_after_delete)
        
        self.tracker.end_session(session2)

    def test_auto_generated_session_id(self):
        """Test that session IDs can be auto-generated."""
        session_id = self.tracker.start_session(None)  # Pass None to auto-generate
        self.assertIsInstance(session_id, str)
        self.assertGreater(len(session_id), 0)
        
        # Should be able to record in auto-generated session
        self.tracker.record(session_id, "test_process", 0.1)
        report = self.tracker.report(session_id, TimTheEnchanterReportFormat.CHRONOLOGICAL)
        self.assertEqual(len(report["events"]), 1)
        
        self.tracker.end_session(session_id)

    def test_disabled_tracking(self):
        """Test that tracking can be disabled."""
        disabled_tracker = TimTheEnchanter.create(enabled=False)
        session_id = disabled_tracker.start_session("disabled_session")
        
        # Should return empty string when disabled
        self.assertEqual(session_id, "")
        
        # Should not record anything when disabled
        disabled_tracker.record("", "test_process", 0.1)
        report = disabled_tracker.report("", TimTheEnchanterReportFormat.CHRONOLOGICAL)
        self.assertEqual(report["format"], "disabled")
        self.assertEqual(len(report["events"]), 0)


if __name__ == "__main__":
    unittest.main() 