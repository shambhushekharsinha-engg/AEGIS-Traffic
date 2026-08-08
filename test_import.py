import traceback
try:
    import dashboard.app
    print("Success")
except Exception as e:
    traceback.print_exc()
