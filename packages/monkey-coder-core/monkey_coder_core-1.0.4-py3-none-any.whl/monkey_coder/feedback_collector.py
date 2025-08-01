"""
Feedback collection system for Monkey Coder Core.

This module provides functionality for collecting user feedback and feature requests
to guide development of future versions, including v0.2 planning.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class FeedbackCollector:
    """
    Collects user feedback and feature requests for future planning.
    """

    def __init__(self):
        self.feedback_list = []
        print("FeedbackCollector initialized")

    def collect_feedback(self, user_id: str, feedback: str, feature_request: bool = False) -> None:
        """
        Collect feedback from users.

        Args:
            user_id: ID of the user providing feedback
            feedback: Feedback or feature request contents
            feature_request: Flag indicating if this is a feature request
        """
        self.feedback_list.append({
            "user_id": user_id,
            "feedback": feedback,
            "feature_request": feature_request,
            "timestamp": datetime.utcnow().isoformat()
        })
        print(f"Collected feedback from {user_id}: {feedback}")

    def summarize_feedback(self) -> Dict[str, Any]:
        """
        Summarize feedback collected so far.

        Returns:
            Summary of feedback and feature requests
        """
        total_feedback = len(self.feedback_list)
        feature_requests = sum(1 for entry in self.feedback_list if entry['feature_request'])

        return {
            "total_feedback": total_feedback,
            "feature_requests": feature_requests,
            "feedback_entries": self.feedback_list
        }

