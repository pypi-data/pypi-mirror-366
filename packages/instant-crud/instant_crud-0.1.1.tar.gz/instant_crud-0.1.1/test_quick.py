#!/usr/bin/env python3
"""Quick test to verify instant-crud is working."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_imports():
    """Test basic imports."""
    try:
        import instant_crud

        print("✅ instant_crud imported successfully")

        from instant_crud import auto_crud_api, setup

        print("✅ Main functions imported")

        from instant_crud.config.settings import get_settings

        print("✅ Settings imported")

        from instant_crud.response.pagination import create_pagination_builder

        print("✅ Pagination imported")

        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality."""
    try:
        from typing import Optional

        from sqlmodel import Field, SQLModel

        from instant_crud import auto_crud_api

        @auto_crud_api(prefix="/test", tags=["Test"])
        class TestModel(SQLModel, table=True):
            id: Optional[int] = Field(primary_key=True)
            name: str

        print("✅ Model with decorator created (no session required)")

        # Test che il modello sia registrato
        from instant_crud.core.factory import get_default_factory

        factory = get_default_factory()
        if len(factory._registered_models) > 0:
            print("✅ Model registered in factory")

        return True
    except Exception as e:
        print(f"❌ Basic functionality failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing instant-crud library...")

    success = True
    success &= test_imports()
    success &= test_basic_functionality()

    if success:
        print("\n🎉 All quick tests passed!")
        print("💡 Try running: uv run python examples/basic_usage.py")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1)
