"""
Unit tests for the main A3 API class.

This module tests the primary user interface for the AI Project Builder,
including error handling, configuration, and workflow orchestration.
"""

import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock