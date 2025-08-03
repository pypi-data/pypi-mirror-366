def evaluate_test_cases(func, test_cases):
    total = len(test_cases)
    passed = 0

    for i, case in enumerate(test_cases, start=1):
        inputs = case.get("input", ())
        expected = case.get("expected_output")

        try:
            result = func(*inputs)
            is_pass = result == expected
        except Exception as e:
            result = f"Error: {e}"
            is_pass = False

        print(f"Test {i}: {'✅ Passed' if is_pass else '❌ Failed'}")
        print(f"  Input: {inputs}")
        print(f"  Expected: {expected}, Got: {result}\n")

        if is_pass:
            passed += 1

    print(f"Summary: {passed}/{total} tests passed.")
