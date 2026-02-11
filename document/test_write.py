try:
    with open('test_log.txt', 'w') as f:
        f.write("Hello from test_write.py")
    print("Write successful")
except Exception as e:
    print(f"Write failed: {e}")
