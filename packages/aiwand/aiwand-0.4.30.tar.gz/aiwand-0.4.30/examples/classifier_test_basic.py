"""
Basic Classifier Test - No API calls required

This example shows how to create classifiers and inspect their structure
without making actual AI API calls.
"""

import aiwand

def main():
    print("🧪 AIWand Classifier Basic Test (No API calls)\n")
    
    # Test 1: Check imports and types
    print("=== Test 1: Imports and Types ===")
    print(f"ClassifierResponse type: {aiwand.ClassifierResponse}")
    print(f"classify_text function: {aiwand.classify_text}")
    print()
    
    # Test 2: Create reusable classifiers (no API calls yet)
    print("=== Test 2: Creating Reusable Classifiers ===")
    
    # Create a binary classifier
    binary_classifier = aiwand.create_binary_classifier(criteria="accuracy")
    print(f"✅ Binary classifier created: {binary_classifier}")
    
    # Create a quality classifier
    quality_classifier = aiwand.create_quality_classifier()
    print(f"✅ Quality classifier created: {quality_classifier}")
    
    # Create a custom classifier
    custom_classifier = aiwand.create_classifier(
        prompt_template="Grade this response: {input} -> {output}",
        choice_scores={"EXCELLENT": 1.0, "GOOD": 0.7, "FAIR": 0.4, "POOR": 0.0},
        use_reasoning=True
    )
    print(f"✅ Custom classifier created: {custom_classifier}")
    print()
    
    # Test 3: Show how to create ClassifierResponse manually
    print("=== Test 3: ClassifierResponse Structure ===")
    
    # Create a sample response manually (like what would come from AI)
    response = aiwand.ClassifierResponse(
        score=0.8,
        choice="GOOD",
        reasoning="The response is accurate and well-structured.",
        metadata={"test": True}
    )
    
    print(f"Score: {response.score}")
    print(f"Choice: {response.choice}")
    print(f"Reasoning: {response.reasoning}")
    print(f"Metadata: {response.metadata}")
    print()
    
    # Test 4: Show the simplification compared to complex setup
    print("=== Test 4: Simplification Demo ===")
    print("🔥 Instead of complex setup like:")
    print("""
    choice_scores = {"A": 1.0, "B": 0.0, "C": 0.5}
    grader = KayLLMClassifier(
        name="SimpleGrader",
        prompt_template=simple_classifier_prompt,
        choice_scores=choice_scores,
        use_cot=True,
        model=model_value,
    )
    response = await grader(
        input="question",
        output="predicted", 
        expected="expected",
    )
    """)
    
    print("✨ Now you can simply call:")
    print("result = aiwand.classify_text(question, answer, expected, choice_scores={'A': 1.0, 'B': 0.0, 'C': 0.5})")
    print()
    
    print("📋 Ready to use! Set up your API keys with 'aiwand setup' to start classifying.")
    print("💡 Run 'python examples/classifier_usage.py' for full examples with real AI calls.")


if __name__ == "__main__":
    main() 