#!/usr/bin/env python3
"""
Local test script for the knowledge management system.
Run this to test the system before deploying to Vercel.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from knowledge_processor import KnowledgeProcessor


def test_system_health():
    """Test system health and configuration."""
    print("🔍 Testing system health...")
    
    try:
        processor = KnowledgeProcessor()
        health_status = processor.test_system_health()
        
        print(f"Overall Status: {health_status['overall_status']}")
        print("\nComponent Status:")
        
        for component, status in health_status['components'].items():
            status_emoji = "✅" if status['status'] == 'healthy' else "❌"
            print(f"  {status_emoji} {component}: {status['details']}")
        
        return health_status['overall_status'] == 'healthy'
        
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False


def test_hardcoded_flow():
    """Test the hardcoded knowledge processing flow."""
    print("\n🧠 Testing hardcoded knowledge processing flow...")
    
    try:
        processor = KnowledgeProcessor()
        result = processor.process_hardcoded_flow()
        
        if result.success:
            print("✅ Knowledge processing completed successfully!")
            print(f"📊 Updated knowledge base has {len(result.updated_knowledge_base.facts)} facts")
            
            # Show a sample of the updated knowledge base
            print("\n📋 Updated Knowledge Base (first 3 facts):")
            for i, fact in enumerate(result.updated_knowledge_base.facts[:3]):
                print(f"  {fact.number}. {fact.description[:80]}...")
            
            print(f"\n📝 Processing Log Summary:")
            print(result.processing_log)
            
        else:
            print("❌ Knowledge processing failed!")
            print(f"Error: {result.error_message}")
            print(f"\n📝 Processing Log:")
            print(result.processing_log)
        
        return result.success
        
    except Exception as e:
        print(f"❌ Hardcoded flow test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Knowledge Management System Tests")
    print("=" * 50)
    
    # Check environment variables
    print("🔑 Checking environment variables...")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found!")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    else:
        print("✅ OPENAI_API_KEY found and configured")
    
    # Run health check
    health_ok = test_system_health()
    
    if not health_ok:
        print("\n❌ System health check failed. Please fix the issues above before proceeding.")
        return False
    
    # Run hardcoded flow test
    flow_ok = test_hardcoded_flow()
    
    if flow_ok:
        print("\n🎉 All tests passed! Your system is ready for deployment.")
        print("\nNext steps:")
        print("1. Deploy to Vercel: `vercel deploy`")
        print("2. Test the live endpoint: POST to your-domain.vercel.app/api/process/hardcoded")
        print("3. Check logs via the health endpoint: GET your-domain.vercel.app/api/process/health")
    else:
        print("\n❌ Tests failed. Please check the logs above and fix any issues.")
    
    return flow_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 