try:
    from hanifx import greet, version, safe_hash, help_menu

    print("✅ hanifx module imported successfully!\n")

    print("🧪 greet():")
    print(greet())

    print("\n🧪 version():")
    print(version())

    print("\n🧪 safe_hash('HelloWorld'):")
    print(safe_hash("HelloWorld"))

    print("\n🧪 help_menu():")
    print(help_menu())

except ImportError as ie:
    print("❌ ImportError: hanifx module is not installed or has issues.")
    print("Details:", ie)

except Exception as e:
    print("❌ Unexpected error occurred while testing hanifx module.")
    print("Details:", e)
