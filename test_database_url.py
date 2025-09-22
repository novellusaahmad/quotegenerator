#!/usr/bin/env python3
"""Simple test script to validate ``DATABASE_URL`` format."""

import os
import sys

import pytest

sqlalchemy = pytest.importorskip("sqlalchemy")
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url

def test_database_url():
    """Test DATABASE_URL format and connection"""
    
    # Get DATABASE_URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable is not set")
        return False
    
    print(f"🔍 Testing DATABASE_URL: {database_url}")
    
    try:
        # Test URL parsing
        url = make_url(database_url)
        print(f"✅ URL parsing successful")
        print(f"   - Database type: {url.drivername}")
        print(f"   - Host: {url.host or 'local file'}")
        print(f"   - Database: {url.database}")
        
        # Test engine creation
        engine = create_engine(database_url)
        print(f"✅ Engine creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ DATABASE_URL validation failed: {e}")
        return False

if __name__ == "__main__":
    if test_database_url():
        print("\n🚀 DATABASE_URL is valid and ready for use")
        sys.exit(0)
    else:
        print("\n💥 DATABASE_URL validation failed")
        sys.exit(1)