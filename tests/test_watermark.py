"""
Unit tests for extract/watermark.py module using pytest and mock connection.
"""

import pytest
from unittest.mock import MagicMock
from extract.watermark import get_last_watermark, update_watermark, reset_watermark

def test_get_last_watermark_default():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None

    ts = get_last_watermark(mock_conn, 'test_key')
    assert ts == '1970-01-01T00:00:00+00:00'

def test_get_last_watermark_existing():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = ('2026-06-15T12:00:00+00:00',)

    ts = get_last_watermark(mock_conn, 'test_key')
    assert ts == '2026-06-15T12:00:00+00:00'

def test_update_watermark():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    update_watermark(mock_conn, 'test_key', '2026-07-01T00:00:00+00:00')
    assert mock_cursor.execute.called
    assert mock_conn.commit.called

def test_reset_watermark():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    reset_watermark(mock_conn, 'test_key')
    assert mock_cursor.execute.called
    assert mock_conn.commit.called
