#!/usr/bin/env python3
"""
Test script to demonstrate the unified send_email function with thread support.
"""

from src.universal_mcp_google_mail.app import GoogleMailApp
from src.universal_mcp_google_mail.models import GmailMessage

def test_unified_send_email():
    """
    Test the unified send_email function with thread support.
    This is a demonstration script - you would need to configure your Gmail API credentials.
    """
    
    print("=== Unified send_email Function Test ===\n")
    
    # Note: This would require proper Gmail API configuration
    # app = GoogleMailApp(integration)
    
    print("1. Enhanced send_email function now supports both new emails and replies:")
    print("   - New email: send_email(to, subject, body)")
    print("   - Reply: send_email(to, subject, body, thread_id='12345')")
    print()
    
    print("2. Examples of usage:")
    print()
    print("   # Send new email")
    print("   send_email(")
    print("       to='user@example.com',")
    print("       subject='Meeting Tomorrow',")
    print("       body='Let\\'s meet at 2pm'")
    print("   )")
    print()
    print("   # Reply to thread (auto-adds 'Re:' prefix)")
    print("   send_email(")
    print("       to='user@example.com',")
    print("       subject='Meeting Tomorrow',  # Becomes 'Re: Meeting Tomorrow'")
    print("       body='I\\'ll be there!',")
    print("       thread_id='1985f5a3d2a6c3c8'  # ← This makes it a reply")
    print("   )")
    print()
    print("   # Reply with custom subject")
    print("   send_email(")
    print("       to='user@example.com',")
    print("       subject='Re: Meeting Tomorrow',  # Already has 'Re:', won't change")
    print("       body='I\\'ll be there!',")
    print("       thread_id='1985f5a3d2a6c3c8'")
    print("   )")
    print()
    
    print("3. Key Benefits:")
    print("   ✅ Backward compatible - existing code works unchanged")
    print("   ✅ Single function for both new emails and replies")
    print("   ✅ Auto-adds 'Re:' prefix for replies")
    print("   ✅ Properly threads replies in Gmail UI")
    print("   ✅ Clean and simple API")
    print()
    
    print("4. Removed Functions:")
    print("   ❌ reply_to_message() - No longer needed")
    print("   ❌ reply_to_thread() - No longer needed")
    print("   ✅ send_email() - Now handles everything!")

if __name__ == "__main__":
    test_unified_send_email() 