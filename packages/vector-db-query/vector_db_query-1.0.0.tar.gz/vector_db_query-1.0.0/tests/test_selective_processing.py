"""Tests for selective processing filters."""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

from vector_db_query.data_sources.filters import (
    SelectiveProcessor, FilterRule, FilterType, FilterAction,
    has_attachments_filter, is_automated_email_filter, meeting_duration_filter
)


class TestFilterRule:
    """Test FilterRule model."""
    
    def test_rule_creation(self):
        """Test creating filter rule."""
        rule = FilterRule(
            name="Test Rule",
            type=FilterType.PATTERN,
            action=FilterAction.EXCLUDE,
            pattern="*spam*",
            priority=10,
            enabled=True
        )
        
        assert rule.name == "Test Rule"
        assert rule.type == FilterType.PATTERN
        assert rule.action == FilterAction.EXCLUDE
        assert rule.pattern == "*spam*"
        assert rule.priority == 10
        assert rule.enabled is True
    
    def test_rule_with_value(self):
        """Test rule with value parameter."""
        rule = FilterRule(
            name="Size Filter",
            type=FilterType.SIZE,
            action=FilterAction.EXCLUDE,
            value={'min': 0, 'max': 1024 * 1024}  # 1MB
        )
        
        assert rule.value['max'] == 1024 * 1024
        assert rule.pattern is None
    
    def test_rule_with_metadata(self):
        """Test rule with metadata."""
        rule = FilterRule(
            name="Custom Filter",
            type=FilterType.CUSTOM,
            action=FilterAction.INCLUDE,
            metadata={'filter_name': 'has_attachments', 'param': 'value'}
        )
        
        assert rule.metadata['filter_name'] == 'has_attachments'
        assert 'param' in rule.metadata


class TestSelectiveProcessor:
    """Test SelectiveProcessor functionality."""
    
    @pytest.fixture
    def processor(self):
        """Create processor instance."""
        config = {
            'filter_rules': [],
            'manual_exclusions': {
                'gmail': [],
                'fireflies': [],
                'google_drive': []
            }
        }
        return SelectiveProcessor(config)
    
    @pytest.fixture
    def sample_email(self):
        """Create sample email item."""
        return {
            'id': 'email_123',
            'headers': {
                'subject': 'Important Meeting Notes',
                'from': 'boss@company.com'
            },
            'date': datetime.utcnow().isoformat(),
            'body_text': 'Please find the meeting notes attached',
            'attachments': [{'filename': 'notes.pdf'}],
            'size': 2048
        }
    
    @pytest.fixture
    def sample_transcript(self):
        """Create sample transcript item."""
        return {
            'id': 'trans_123',
            'title': 'Team Sync Meeting',
            'date': datetime.utcnow().isoformat(),
            'duration': 1800,  # 30 minutes
            'participants': ['user1@company.com', 'user2@company.com'],
            'content': 'Meeting transcript content...'
        }
    
    def test_pattern_filter(self, processor, sample_email):
        """Test pattern-based filtering."""
        # Add exclude pattern
        rule = FilterRule(
            name="Spam Filter",
            type=FilterType.PATTERN,
            action=FilterAction.EXCLUDE,
            pattern="*spam*"
        )
        processor.add_rule(rule)
        
        # Test non-matching email
        assert processor.should_process(sample_email, 'gmail') is True
        
        # Test matching email
        spam_email = sample_email.copy()
        spam_email['headers']['subject'] = 'Amazing spam offer!'
        assert processor.should_process(spam_email, 'gmail') is False
    
    def test_date_range_filter(self, processor, sample_email):
        """Test date range filtering."""
        # Add date range filter (last 7 days only)
        rule = FilterRule(
            name="Recent Only",
            type=FilterType.DATE_RANGE,
            action=FilterAction.INCLUDE,
            value={
                'start': (datetime.utcnow() - timedelta(days=7)).isoformat()
            }
        )
        processor.add_rule(rule)
        
        # Test recent email
        assert processor.should_process(sample_email, 'gmail') is True
        
        # Test old email
        old_email = sample_email.copy()
        old_email['date'] = (datetime.utcnow() - timedelta(days=30)).isoformat()
        assert processor.should_process(old_email, 'gmail') is False
    
    def test_size_filter(self, processor, sample_email):
        """Test size-based filtering."""
        # Add size filter (exclude files > 1MB)
        rule = FilterRule(
            name="Large Files",
            type=FilterType.SIZE,
            action=FilterAction.EXCLUDE,
            value=1024 * 1024  # 1MB
        )
        processor.add_rule(rule)
        
        # Test small file
        assert processor.should_process(sample_email, 'gmail') is True
        
        # Test large file
        large_email = sample_email.copy()
        large_email['size'] = 2 * 1024 * 1024  # 2MB
        assert processor.should_process(large_email, 'gmail') is False
    
    def test_sender_filter(self, processor, sample_email):
        """Test sender filtering."""
        # Add sender filter
        rule = FilterRule(
            name="No-reply Filter",
            type=FilterType.SENDER,
            action=FilterAction.EXCLUDE,
            pattern="noreply@*"
        )
        processor.add_rule(rule)
        
        # Test regular sender
        assert processor.should_process(sample_email, 'gmail') is True
        
        # Test no-reply sender
        noreply_email = sample_email.copy()
        noreply_email['headers']['from'] = 'noreply@company.com'
        assert processor.should_process(noreply_email, 'gmail') is False
        
        # Also test with metadata for non-email sources
        noreply_email['metadata'] = {'sender_email': 'noreply@service.com'}
        assert processor.should_process(noreply_email, 'fireflies') is False
    
    def test_subject_filter(self, processor, sample_email):
        """Test subject filtering with regex."""
        # Add subject filter
        rule = FilterRule(
            name="Newsletter Filter",
            type=FilterType.SUBJECT,
            action=FilterAction.EXCLUDE,
            pattern=r"newsletter|weekly.*digest|subscription"
        )
        processor.add_rule(rule)
        
        # Test regular subject
        assert processor.should_process(sample_email, 'gmail') is True
        
        # Test newsletter subject
        newsletter = sample_email.copy()
        newsletter['headers']['subject'] = 'Weekly Newsletter - Issue 42'
        assert processor.should_process(newsletter, 'gmail') is False
        
        # Test digest subject
        digest = sample_email.copy()
        digest['headers']['subject'] = 'Your weekly news digest'
        assert processor.should_process(digest, 'gmail') is False
    
    def test_content_filter(self, processor, sample_email):
        """Test content filtering."""
        # Add content filter
        rule = FilterRule(
            name="Unsubscribe Filter",
            type=FilterType.CONTENT,
            action=FilterAction.EXCLUDE,
            pattern=r"unsubscribe|opt.?out"
        )
        processor.add_rule(rule)
        
        # Test regular content
        assert processor.should_process(sample_email, 'gmail') is True
        
        # Test with unsubscribe content
        unsub_email = sample_email.copy()
        unsub_email['body_text'] = 'Newsletter content... Click here to unsubscribe'
        assert processor.should_process(unsub_email, 'gmail') is False
    
    def test_custom_filter_attachments(self, processor, sample_email):
        """Test custom filter for attachments."""
        # Register custom filter
        processor.register_custom_filter('has_attachments', has_attachments_filter)
        
        # Add rule to exclude emails with attachments
        rule = FilterRule(
            name="No Attachments",
            type=FilterType.CUSTOM,
            action=FilterAction.EXCLUDE,
            metadata={'filter_name': 'has_attachments'}
        )
        processor.add_rule(rule)
        
        # Test email with attachments
        assert processor.should_process(sample_email, 'gmail') is False
        
        # Test email without attachments
        no_attach = sample_email.copy()
        no_attach['attachments'] = []
        assert processor.should_process(no_attach, 'gmail') is True
    
    def test_custom_filter_automated(self, processor, sample_email):
        """Test custom filter for automated emails."""
        # Register custom filter
        processor.register_custom_filter('is_automated', is_automated_email_filter)
        
        # Add rule
        rule = FilterRule(
            name="No Automated",
            type=FilterType.CUSTOM,
            action=FilterAction.EXCLUDE,
            metadata={'filter_name': 'is_automated'}
        )
        processor.add_rule(rule)
        
        # Test regular email
        assert processor.should_process(sample_email, 'gmail') is True
        
        # Test automated email patterns
        automated_patterns = [
            'noreply@company.com',
            'no-reply@service.com',
            'notifications@app.com',
            'system@automated.com',
            'donotreply@website.com'
        ]
        
        for sender in automated_patterns:
            auto_email = sample_email.copy()
            auto_email['headers']['from'] = sender
            assert processor.should_process(auto_email, 'gmail') is False
    
    def test_custom_filter_meeting_duration(self, processor, sample_transcript):
        """Test custom filter for meeting duration."""
        # Register custom filter
        processor.register_custom_filter('meeting_duration', meeting_duration_filter)
        
        # Add rule to exclude short meetings
        rule = FilterRule(
            name="Long Meetings Only",
            type=FilterType.CUSTOM,
            action=FilterAction.EXCLUDE,
            metadata={
                'filter_name': 'meeting_duration',
                'max_duration': 600  # 10 minutes
            }
        )
        processor.add_rule(rule)
        
        # Test long meeting (30 minutes)
        assert processor.should_process(sample_transcript, 'fireflies') is True
        
        # Test short meeting (5 minutes)
        short_meeting = sample_transcript.copy()
        short_meeting['duration'] = 300
        assert processor.should_process(short_meeting, 'fireflies') is False
    
    def test_priority_ordering(self, processor, sample_email):
        """Test filter priority ordering."""
        # Add conflicting rules with different priorities
        exclude_rule = FilterRule(
            name="Exclude All",
            type=FilterType.PATTERN,
            action=FilterAction.EXCLUDE,
            pattern="*",
            priority=5
        )
        
        include_rule = FilterRule(
            name="Include Important",
            type=FilterType.SUBJECT,
            action=FilterAction.INCLUDE,
            pattern="Important",
            priority=10  # Higher priority
        )
        
        processor.add_rule(exclude_rule)
        processor.add_rule(include_rule)
        
        # Should be included due to higher priority rule
        assert processor.should_process(sample_email, 'gmail') is True
    
    def test_manual_exclusions(self, processor, sample_email):
        """Test manual exclusion lists."""
        # Add email ID to exclusion list
        processor.add_manual_exclusion('gmail', 'email_123')
        
        # Should be excluded
        assert processor.should_process(sample_email, 'gmail') is False
        
        # Different ID should not be excluded
        other_email = sample_email.copy()
        other_email['id'] = 'email_456'
        assert processor.should_process(other_email, 'gmail') is True
        
        # Remove exclusion
        processor.remove_manual_exclusion('gmail', 'email_123')
        assert processor.should_process(sample_email, 'gmail') is True
    
    def test_rule_management(self, processor):
        """Test rule management operations."""
        # Add rules
        rule1 = FilterRule(name="Rule 1", type=FilterType.PATTERN, action=FilterAction.EXCLUDE, pattern="test1")
        rule2 = FilterRule(name="Rule 2", type=FilterType.PATTERN, action=FilterAction.EXCLUDE, pattern="test2")
        
        assert processor.add_rule(rule1) is True
        assert processor.add_rule(rule2) is True
        
        # Get active rules
        active = processor.get_active_rules()
        assert len(active) == 2
        
        # Toggle rule
        processor.toggle_rule("Rule 1", False)
        active = processor.get_active_rules()
        assert len(active) == 1
        
        # Remove rule
        assert processor.remove_rule("Rule 2") is True
        assert len(processor.rules) == 1
    
    def test_statistics(self, processor, sample_email):
        """Test exclusion statistics."""
        # Add some rules
        rule1 = FilterRule(name="Pattern", type=FilterType.PATTERN, action=FilterAction.EXCLUDE, pattern="test")
        rule2 = FilterRule(name="Size", type=FilterType.SIZE, action=FilterAction.EXCLUDE, value=1000)
        
        processor.add_rule(rule1)
        processor.add_rule(rule2)
        
        # Add manual exclusions
        processor.add_manual_exclusion('gmail', 'id1')
        processor.add_manual_exclusion('gmail', 'id2')
        processor.add_manual_exclusion('fireflies', 'id3')
        
        stats = processor.get_exclusion_stats()
        
        assert stats['total_rules'] == 2
        assert stats['active_rules'] == 2
        assert stats['rule_types'][FilterType.PATTERN] == 1
        assert stats['rule_types'][FilterType.SIZE] == 1
        assert stats['manual_exclusions']['gmail'] == 2
        assert stats['manual_exclusions']['fireflies'] == 1
        assert stats['manual_exclusions']['google_drive'] == 0
    
    def test_import_export_rules(self, processor):
        """Test importing and exporting rules."""
        # Add some rules
        rule1 = FilterRule(name="Rule 1", type=FilterType.PATTERN, action=FilterAction.EXCLUDE, pattern="test1")
        rule2 = FilterRule(name="Rule 2", type=FilterType.SIZE, action=FilterAction.INCLUDE, value=1000)
        
        processor.add_rule(rule1)
        processor.add_rule(rule2)
        
        # Export rules
        exported = processor.export_rules()
        assert len(exported) == 2
        
        # Create new processor and import
        new_processor = SelectiveProcessor({})
        imported_count = new_processor.import_rules(exported)
        
        assert imported_count == 2
        assert len(new_processor.rules) == 2
        assert new_processor.rules[0].name == "Rule 1"
        assert new_processor.rules[1].name == "Rule 2"
    
    def test_tag_action(self, processor, sample_email):
        """Test TAG action (should include but mark)."""
        # Add tag rule
        rule = FilterRule(
            name="Tag Important",
            type=FilterType.SUBJECT,
            action=FilterAction.TAG,
            pattern="Important"
        )
        processor.add_rule(rule)
        
        # Should still be processed
        assert processor.should_process(sample_email, 'gmail') is True
        
        # In real implementation, would add metadata tag


class TestCustomFilters:
    """Test custom filter functions."""
    
    def test_has_attachments_filter(self):
        """Test attachment detection filter."""
        # With attachments
        item_with = {'attachments': [{'name': 'file.pdf'}]}
        assert has_attachments_filter(item_with, 'gmail') is True
        
        # Without attachments
        item_without = {'attachments': []}
        assert has_attachments_filter(item_without, 'gmail') is False
        
        # No attachments field
        item_none = {}
        assert has_attachments_filter(item_none, 'gmail') is False
    
    def test_is_automated_email_filter(self):
        """Test automated email detection."""
        # Automated senders
        automated_items = [
            {'headers': {'from': 'noreply@company.com'}},
            {'headers': {'from': 'notifications@app.com'}},
            {'headers': {'from': 'system@service.com'}},
            {'metadata': {'sender_email': 'donotreply@website.com'}}
        ]
        
        for item in automated_items:
            assert is_automated_email_filter(item, 'gmail') is True
        
        # Regular sender
        regular = {'headers': {'from': 'john@company.com'}}
        assert is_automated_email_filter(regular, 'gmail') is False
    
    def test_meeting_duration_filter(self):
        """Test meeting duration filter."""
        # Without parameters (default behavior)
        short_meeting = {'duration': 300}  # 5 minutes
        long_meeting = {'duration': 3600}  # 1 hour
        
        assert meeting_duration_filter(short_meeting, 'fireflies') is True
        assert meeting_duration_filter(long_meeting, 'fireflies') is True
        
        # With min duration
        params = {'min_duration': 600}  # 10 minutes
        assert meeting_duration_filter(short_meeting, 'fireflies', params) is False
        assert meeting_duration_filter(long_meeting, 'fireflies', params) is True
        
        # With max duration
        params = {'max_duration': 1800}  # 30 minutes
        assert meeting_duration_filter(short_meeting, 'fireflies', params) is True
        assert meeting_duration_filter(long_meeting, 'fireflies', params) is False
        
        # With both
        params = {'min_duration': 600, 'max_duration': 1800}
        medium_meeting = {'duration': 1200}  # 20 minutes
        assert meeting_duration_filter(short_meeting, 'fireflies', params) is False
        assert meeting_duration_filter(medium_meeting, 'fireflies', params) is True
        assert meeting_duration_filter(long_meeting, 'fireflies', params) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])