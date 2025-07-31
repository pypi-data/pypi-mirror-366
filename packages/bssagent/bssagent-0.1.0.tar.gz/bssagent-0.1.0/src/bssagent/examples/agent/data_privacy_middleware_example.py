"""
Example demonstrating how to use DataPrivacyMiddleware with the Server class.
"""

from bssagent.infrastructure import Server
from bssagent.security import DataPrivacyMiddleware, DataPrivacyMiddlewareFactory

def example_basic_usage():
    """Example 1: Basic usage with default settings."""
    print("=== Example 1: Basic Usage ===")
    
    # Create server
    server = Server(title="Privacy Test Server")
    server.create_app()
    
    # Add data privacy middleware with default settings
    server.add_custom_middleware(DataPrivacyMiddleware)
    
    print("✓ Added DataPrivacyMiddleware with default settings")
    return server

def example_custom_configuration():
    """Example 2: Custom configuration using factory."""
    print("\n=== Example 2: Custom Configuration ===")
    
    # Create server
    server = Server(title="Privacy Test Server")
    server.create_app()
    
    # Create custom middleware with specific settings
    CustomPrivacyMiddleware = DataPrivacyMiddlewareFactory.create(
        enable_logging=True,
        enable_masking=True,  # This will mask sensitive data in logs
        log_level="INFO"
    )
    
    # Add the custom middleware
    server.add_custom_middleware(CustomPrivacyMiddleware)
    
    print("✓ Added DataPrivacyMiddleware with custom configuration:")
    print("  - enable_logging: True")
    print("  - enable_masking: True")
    print("  - log_level: INFO")
    return server

def example_multiple_middleware():
    """Example 3: Using multiple middleware instances with different configs."""
    print("\n=== Example 3: Multiple Middleware ===")
    
    # Create server
    server = Server(title="Privacy Test Server")
    server.create_app()
    
    # Create different middleware configurations
    LoggingOnlyMiddleware = DataPrivacyMiddlewareFactory.create(
        enable_logging=True,
        enable_masking=False,
        log_level="WARNING"
    )
    
    MaskingMiddleware = DataPrivacyMiddlewareFactory.create(
        enable_logging=False,
        enable_masking=True,
        log_level="DEBUG"
    )
    
    # Add both middleware (order matters - first added is outermost)
    server.add_custom_middleware(LoggingOnlyMiddleware)
    server.add_custom_middleware(MaskingMiddleware)
    
    print("✓ Added multiple DataPrivacyMiddleware instances:")
    print("  1. LoggingOnlyMiddleware (WARNING level, no masking)")
    print("  2. MaskingMiddleware (DEBUG level, with masking)")
    return server

def test_sensitive_data_detection():
    """Test the sensitive data detection functionality."""
    print("\n=== Testing Sensitive Data Detection ===")
    
    from bssagent.security.data_privacy_manager import DataPrivacyManager
    
    privacy_manager = DataPrivacyManager()
    
    # Test data with sensitive information
    test_data = {
        "user_info": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "555-123-4567",
            "ssn": "123-45-6789"
        },
        "payment": {
            "credit_card": "1234-5678-9012-3456",
            "api_key": "sk-1234567890abcdef1234567890abcdef12345678"
        }
    }
    
    import json
    test_json = json.dumps(test_data)
    
    # Detect sensitive data
    findings = privacy_manager.detect_sensitive_data(test_json)
    
    print("Test data contains:")
    for data_type, matches in findings.items():
        print(f"  - {data_type}: {len(matches)} matches")
    
    # Test masking
    masked_data = privacy_manager.mask_sensitive_data(test_json)
    print(f"\nMasked data preview: {masked_data[:100]}...")
    
    return findings

if __name__ == "__main__":
    print("DataPrivacyMiddleware Usage Examples")
    print("=" * 50)
    
    # Run examples
    server1 = example_basic_usage()
    server2 = example_custom_configuration()
    server3 = example_multiple_middleware()
    
    # Test detection
    findings = test_sensitive_data_detection()
    
    print("\n" + "=" * 50)
    print("All examples completed successfully!")
    print("\nTo run a server with privacy middleware:")
    print("1. Choose one of the example configurations above")
    print("2. Add your endpoints using server.add_endpoint()")
    print("3. Run with server.run()")
    print("\nExample:")
    print("  server = example_basic_usage()")
    print("  server.add_endpoint('/test', 'POST', your_handler)")
    print("  server.run(host='0.0.0.0', port=8000)") 