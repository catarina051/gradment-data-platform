"""
Unit tests for extract/partition_manager.py module.
"""

import pytest
from unittest.mock import MagicMock
from extract.partition_manager import ensure_partitions_for_timestamps

def test_ensure_partitions_empty_timestamps():
    mock_conn = MagicMock()
    ensure_partitions_for_timestamps(mock_conn, [])
    assert not mock_conn.cursor.called

def test_ensure_partitions_with_timestamps():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None # Simulates partition does not exist yet

    count = ensure_partitions_for_timestamps(mock_conn, ['2026-06-15T12:00:00Z', '2026-07-20T10:00:00Z'])
    assert mock_cursor.execute.called
    assert mock_conn.commit.called
    assert count == 2
