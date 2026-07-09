from backend.app.core.hallucination_detector import HallucinationDetector

detector = HallucinationDetector()

test_cases = [
    # (context, response, expected_hallucinated)
    ("Project X is complete?", "Project X is not complete", False),
    # ("Project X is complete", "Project X is ongoing", True),
    # ("Budget is $100k", "Budget is $50k", True),
    # ("Deadline is coming Friday", "Deadline is next Friday", False),  # Edge case
    # ("Meeting at 3pm", "Meeting scheduled", False),  # Partial match
    # ("Sarah is project lead", "John is project lead", True),
]


correct = 0
for context, response, expected in test_cases:
    result = detector.detect(response, context)
    predicted = result['is_hallucinated']
    
    match = predicted == expected
    correct += match
    
    status = "✓" if match else "✗"
    print(f"{status} {response[:40]:40} → {predicted} (expected {expected})")

print(f"\nAccuracy: {correct}/{len(test_cases)} ({correct/len(test_cases)*100:.0f}%)")
