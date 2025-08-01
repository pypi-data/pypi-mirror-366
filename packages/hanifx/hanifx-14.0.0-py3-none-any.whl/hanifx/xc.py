try:
    from hanifx import greet

    print("Module imported successfully!")
    result = greet()
    print("Function Output:", result)

except ImportError:
    print("hanifx module is not installed.")
except Exception as e:
    print("Something went wrong:", e)
