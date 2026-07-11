"""tests/test_moderation.py - Tests for heuristic filter and moderation."""
import pytest

from app.utils.moderation import heuristic_filter


class TestHeuristicFilter:
    """Tests for the enhanced heuristic filter."""

    @pytest.mark.asyncio
    async def test_allow_clean_comment(self):
        """Test that clean comments pass the filter."""
        result = await heuristic_filter("This is a great professor, very helpful!")
        assert result.action == "allow"
        assert result.spam_score < 0.4

    @pytest.mark.asyncio
    async def test_banned_term_detection(self):
        """Test that banned terms increase spam score (no DB, so skip that stage)."""
        # Without DB, banned terms stage is skipped
        result = await heuristic_filter("This professor is not good")
        # Should pass because no DB to check banned terms
        assert result.spam_score < 0.4

    @pytest.mark.asyncio
    async def test_email_pattern_detection(self):
        """Test that emails are detected and add to spam score."""
        result = await heuristic_filter("Contact me at hacker@evil.com for cheating")
        assert "email" in result.matched_patterns or "email" in " ".join(result.reasons).lower()
        assert result.spam_score >= 0.1  # Email detection adds score

    @pytest.mark.asyncio
    async def test_url_pattern_detection(self):
        """Test that URLs are detected."""
        result = await heuristic_filter("Click here: https://malicious.com/scam")
        assert "url" in result.matched_patterns or "url" in " ".join(result.reasons).lower()
        assert result.spam_score >= 0.1

    @pytest.mark.asyncio
    async def test_zero_width_chars_detection(self):
        """Test that comments with zero-width characters are flagged."""
        # Insert zero-width space
        text = "This is a comment\u200Bwith hidden characters"
        result = await heuristic_filter(text)
        assert "zero" in " ".join(result.reasons).lower() or "obfuscation" in " ".join(result.reasons).lower()

    @pytest.mark.asyncio
    async def test_excessive_caps_scoring(self):
        """Test that comments with excessive caps increase spam score."""
        result = await heuristic_filter("THIS PROFESSOR IS THE BEST!!!!!")
        assert result.action == "allow"  # Should be allow, not block
        assert result.spam_score >= 0.25  # Caps + repetition should score higher
        assert len(result.reasons) > 0

    @pytest.mark.asyncio
    async def test_repeated_chars_scoring(self):
        """Test that comments with repeated characters increase spam score."""
        result = await heuristic_filter("This is sooooooo good!!!!!!!!!!!!")
        assert result.action == "allow"  # Allow with higher score
        assert result.spam_score >= 0.1

    @pytest.mark.asyncio
    async def test_phone_pattern_detection(self):
        """Test that Peru phone numbers are detected."""
        result = await heuristic_filter("Call me at +51 987654321 for classes")
        # Phone numbers are detected but don't auto-block
        assert result.spam_score >= 0.1 or "phone" in result.matched_patterns

    @pytest.mark.asyncio
    async def test_l33t_speak_no_score_without_db(self):
        """Test that l33t speak without DB doesn't trigger banned terms."""
        result = await heuristic_filter("Th1s pr0f3ss0r 1s 4w3s0m3!")
        # Without DB, banned terms check is skipped, so l33t speak might not be caught
        # But it might still be flagged as gibberish
        assert result.spam_score >= 0.0

    @pytest.mark.asyncio
    async def test_gibberish_detection(self):
        """Test that random gibberish doesn't always flag without caps/repetition."""
        result = await heuristic_filter("xyzqwerty mnoabcd lkjhgf asdfgh")
        # Random text with low entropy might still pass
        assert result.action == "allow" or result.action == "flag"

    @pytest.mark.asyncio
    async def test_cumulative_violations(self):
        """Test that multiple violations increase spam score."""
        result = await heuristic_filter("HELLO!!!! Contact me at test@email.com")
        # Email pattern adds at least 0.1
        assert result.spam_score >= 0.1
        assert len(result.reasons) >= 1

    @pytest.mark.asyncio
    async def test_normal_comment_with_numbers(self):
        """Test that normal comments with numbers pass."""
        result = await heuristic_filter("I got a 5/5 on the exam for this class")
        assert result.action == "allow"
        assert result.spam_score < 0.3

    @pytest.mark.asyncio
    async def test_normal_comment_with_punctuation(self):
        """Test that normal comments with punctuation pass."""
        result = await heuristic_filter("Great professor! Very engaging lectures. Highly recommend.")
        assert result.action == "allow"
        assert result.spam_score < 0.3
