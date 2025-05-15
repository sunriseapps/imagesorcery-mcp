import inspect
import logging
import os
import re
import tempfile
import time
from datetime import datetime

import pytest


@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing."""
    fd, path = tempfile.mkstemp(suffix='.log')
    yield path
    os.close(fd)
    os.unlink(path)

def test_log_structure_and_components(temp_log_file):
    """
    Test that logs have the correct structure and all components are properly formatted
    using the actual logging configuration from the project.
    """
    # Import the logging configuration first to ensure it's initialized
    
    # Get the actual imagesorcery logger
    imagesorcery_logger = logging.getLogger("imagesorcery")
    
    # Create a temporary handler to capture logs
    handler = logging.FileHandler(temp_log_file)
    # Use the same formatter as the original logger
    original_formatter = imagesorcery_logger.handlers[0].formatter
    handler.setFormatter(original_formatter)
    imagesorcery_logger.addHandler(handler)
    
    # Generate a test log with a unique message
    test_message = f"Test message generated at {time.time()}"
    line_num = inspect.currentframe().f_lineno + 1
    imagesorcery_logger.info(test_message)
    
    # Remove the temporary handler
    imagesorcery_logger.removeHandler(handler)
    
    # Read the log file
    with open(temp_log_file, 'r') as f:
        log_content = f.read().strip()
    
    # Log format regex pattern to capture each component
    # This pattern should match the format defined in logging_config.py
    log_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - ([\w\.]+)\.(\w+):(\d+) - (\w+) - (.+)'
    match = re.match(log_pattern, log_content)
    
    # Verify we matched the pattern
    assert match, f"Log entry doesn't match expected pattern. Log content: {log_content}"
    
    # Extract components
    timestamp, logger_name, module_name, log_line_num, level, message = match.groups()
    
    # Verify each component
    
    # 1. Timestamp should be parseable
    try:
        datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f')
    except ValueError:
        pytest.fail(f"Invalid timestamp format: {timestamp}")
    
    # 2. Logger name should match what we set
    assert logger_name == "imagesorcery", f"Expected logger name 'imagesorcery', got '{logger_name}'"
    
    # 3. Module name should be this test module
    assert module_name == "test_logging", f"Expected module name 'test_logging', got '{module_name}'"
    
    # 4. Line number should match our recording
    assert int(log_line_num) == line_num, f"Expected line number {line_num}, got {log_line_num}"
    
    # 5. Level should be what we logged
    assert level == "INFO", f"Expected log level 'INFO', got '{level}'"
    
    # 6. Message should match what we logged
    assert message == test_message, f"Expected message '{test_message}', got '{message}'"

def test_different_modules_log_correctly(temp_log_file):
    """Test that logs from different modules include correct module names."""
    # Import the logging configuration first
    
    # Get the actual imagesorcery logger
    imagesorcery_logger = logging.getLogger("imagesorcery")
    
    # Setup a new handler for our test log file using the same formatter
    handler = logging.FileHandler(temp_log_file)
    original_formatter = imagesorcery_logger.handlers[0].formatter
    handler.setFormatter(original_formatter)
    
    # Add our handler to the logger
    imagesorcery_logger.addHandler(handler)
    
    # Log a message and get the current line number
    line_num = inspect.currentframe().f_lineno + 1
    imagesorcery_logger.info("Test message from test function")
    
    # Remove our handler
    imagesorcery_logger.removeHandler(handler)
    
    # Check the log file content
    with open(temp_log_file, 'r') as f:
        log_content = f.read()
    
    # Verify the module name and line number are in the log
    assert f'imagesorcery.test_logging:{line_num}' in log_content, "Log doesn't contain module info"
    assert 'Test message from test function' in log_content, "Log message not written correctly"

def test_different_log_levels(temp_log_file):
    """
    Test that different log levels are correctly formatted and filtered 
    according to the logger's level setting.
    """
    # Import the logging configuration first
    
    # Get the actual imagesorcery logger
    imagesorcery_logger = logging.getLogger("imagesorcery")
    
    # Store the original level to restore it later
    original_level = imagesorcery_logger.level
    
    # Create a temporary handler to capture logs
    handler = logging.FileHandler(temp_log_file)
    original_formatter = imagesorcery_logger.handlers[0].formatter
    handler.setFormatter(original_formatter)
    imagesorcery_logger.addHandler(handler)
    
    try:
        # Test with different log levels
        
        # 1. First test with DEBUG level (lower than default INFO)
        imagesorcery_logger.setLevel(logging.DEBUG)
        
        # Log messages at different levels
        debug_msg = "This is a DEBUG message"
        info_msg = "This is an INFO message"
        warning_msg = "This is a WARNING message"
        error_msg = "This is an ERROR message"
        critical_msg = "This is a CRITICAL message"
        
        imagesorcery_logger.debug(debug_msg)
        imagesorcery_logger.info(info_msg)
        imagesorcery_logger.warning(warning_msg)
        imagesorcery_logger.error(error_msg)
        imagesorcery_logger.critical(critical_msg)
        
        # Read the log file
        with open(temp_log_file, 'r') as f:
            debug_level_logs = f.readlines()
        
        # There should be 5 log entries (one for each level) when set to DEBUG
        assert len(debug_level_logs) == 5, f"Expected 5 log entries at DEBUG level, got {len(debug_level_logs)}"
        
        # Verify each log level appears in the correct entry
        assert "DEBUG" in debug_level_logs[0], f"First log should be DEBUG: {debug_level_logs[0]}"
        assert "INFO" in debug_level_logs[1], f"Second log should be INFO: {debug_level_logs[1]}"
        assert "WARNING" in debug_level_logs[2], f"Third log should be WARNING: {debug_level_logs[2]}"
        assert "ERROR" in debug_level_logs[3], f"Fourth log should be ERROR: {debug_level_logs[3]}"
        assert "CRITICAL" in debug_level_logs[4], f"Fifth log should be CRITICAL: {debug_level_logs[4]}"
        
        # Verify messages are correctly logged
        assert debug_msg in debug_level_logs[0], f"DEBUG message not correctly logged: {debug_level_logs[0]}"
        assert info_msg in debug_level_logs[1], f"INFO message not correctly logged: {debug_level_logs[1]}"
        assert warning_msg in debug_level_logs[2], f"WARNING message not correctly logged: {debug_level_logs[2]}"
        assert error_msg in debug_level_logs[3], f"ERROR message not correctly logged: {debug_level_logs[3]}"
        assert critical_msg in debug_level_logs[4], f"CRITICAL message not correctly logged: {debug_level_logs[4]}"
        
        # 2. Now test with INFO level (default level)
        # Clear the log file first
        open(temp_log_file, 'w').close()
        
        imagesorcery_logger.setLevel(logging.INFO)
        
        # Log messages at different levels again
        imagesorcery_logger.debug("This shouldn't appear in the log")
        imagesorcery_logger.info(info_msg)
        imagesorcery_logger.warning(warning_msg)
        imagesorcery_logger.error(error_msg)
        imagesorcery_logger.critical(critical_msg)
        
        # Read the log file again
        with open(temp_log_file, 'r') as f:
            info_level_logs = f.readlines()
        
        # There should be 4 log entries (DEBUG should be filtered out)
        assert len(info_level_logs) == 4, f"Expected 4 log entries at INFO level, got {len(info_level_logs)}"
        
        # Verify each log level appears in the correct entry
        assert "INFO" in info_level_logs[0], f"First log should be INFO: {info_level_logs[0]}"
        assert "WARNING" in info_level_logs[1], f"Second log should be WARNING: {info_level_logs[1]}"
        assert "ERROR" in info_level_logs[2], f"Third log should be ERROR: {info_level_logs[2]}"
        assert "CRITICAL" in info_level_logs[3], f"Fourth log should be CRITICAL: {info_level_logs[3]}"
        
        # 3. Test with WARNING level
        # Clear the log file first
        open(temp_log_file, 'w').close()
        
        imagesorcery_logger.setLevel(logging.WARNING)
        
        # Log messages at different levels again
        imagesorcery_logger.debug("This shouldn't appear in the log")
        imagesorcery_logger.info("This shouldn't appear in the log either")
        imagesorcery_logger.warning(warning_msg)
        imagesorcery_logger.error(error_msg)
        imagesorcery_logger.critical(critical_msg)
        
        # Read the log file again
        with open(temp_log_file, 'r') as f:
            warning_level_logs = f.readlines()
        
        # There should be 3 log entries (DEBUG and INFO should be filtered out)
        assert len(warning_level_logs) == 3, f"Expected 3 log entries at WARNING level, got {len(warning_level_logs)}"
        
        # Verify each log level appears in the correct entry
        assert "WARNING" in warning_level_logs[0], f"First log should be WARNING: {warning_level_logs[0]}"
        assert "ERROR" in warning_level_logs[1], f"Second log should be ERROR: {warning_level_logs[1]}"
        assert "CRITICAL" in warning_level_logs[2], f"Third log should be CRITICAL: {warning_level_logs[2]}"
        
        # 4. Test with ERROR level
        # Clear the log file first
        open(temp_log_file, 'w').close()
        
        imagesorcery_logger.setLevel(logging.ERROR)
        
        # Log messages at different levels again
        imagesorcery_logger.debug("This shouldn't appear in the log")
        imagesorcery_logger.info("This shouldn't appear in the log either")
        imagesorcery_logger.warning("This shouldn't appear in the log either")
        imagesorcery_logger.error(error_msg)
        imagesorcery_logger.critical(critical_msg)
        
        # Read the log file again
        with open(temp_log_file, 'r') as f:
            error_level_logs = f.readlines()
        
        # There should be 2 log entries (DEBUG, INFO, WARNING should be filtered out)
        assert len(error_level_logs) == 2, f"Expected 2 log entries at ERROR level, got {len(error_level_logs)}"
        
        # Verify each log level appears in the correct entry
        assert "ERROR" in error_level_logs[0], f"First log should be ERROR: {error_level_logs[0]}"
        assert "CRITICAL" in error_level_logs[1], f"Second log should be CRITICAL: {error_level_logs[1]}"
        
        # 5. Test with CRITICAL level
        # Clear the log file first
        open(temp_log_file, 'w').close()
        
        imagesorcery_logger.setLevel(logging.CRITICAL)
        
        # Log messages at different levels again
        imagesorcery_logger.debug("This shouldn't appear in the log")
        imagesorcery_logger.info("This shouldn't appear in the log either")
        imagesorcery_logger.warning("This shouldn't appear in the log either")
        imagesorcery_logger.error("This shouldn't appear in the log either")
        imagesorcery_logger.critical(critical_msg)
        
        # Read the log file again
        with open(temp_log_file, 'r') as f:
            critical_level_logs = f.readlines()
        
        # There should be 1 log entry (all others should be filtered out)
        assert len(critical_level_logs) == 1, f"Expected 1 log entry at CRITICAL level, got {len(critical_level_logs)}"
        
        # Verify the log level and message
        assert "CRITICAL" in critical_level_logs[0], f"Log should be CRITICAL: {critical_level_logs[0]}"
        assert critical_msg in critical_level_logs[0], f"CRITICAL message not correctly logged: {critical_level_logs[0]}"
        
        # Verify that the log format is still correct for each level
        for log_line in debug_level_logs:
            # Check that the log format includes module and line number
            assert re.match(r'.*imagesorcery\.test_logging:\d+ - \w+ -.*', log_line), f"Log format incorrect: {log_line}"
    
    finally:
        # Restore the original logger level and remove our handler
        imagesorcery_logger.setLevel(original_level)
        imagesorcery_logger.removeHandler(handler)
