"""
Example: Using AIWand Classifier

This example demonstrates how to use the new AIWand classifier functionality
for text classification and grading tasks.
"""

import aiwand
from dotenv import load_dotenv

def main():
    load_dotenv()
    print("🔍 AIWand Classifier Examples\n")
    
    # Example 1: Simple binary classification
    print("=== Example 1: Binary Classification ===")
    
    result = aiwand.classify_text(
        question="What is 2 + 2?",
        answer="4",
        expected="4",
        choice_scores={"CORRECT": 1.0, "INCORRECT": 0.0}
    )
    
    print(f"Score: {result.score}")
    print(f"Choice: {result.choice}")
    print(f"Reasoning: {result.reasoning}")
    print()
    
    # Example 2: Custom grading with evaluation criteria (FIXED - no grades in prompt_template)
    print("=== Example 2: Custom Grading Scale ===")
    
    result = aiwand.classify_text(
        question="Write a haiku about spring",
        answer="Cherry blossoms bloom\nGentle breeze through ancient trees\nSpring awakens all",
        prompt_template="Evaluate this haiku based on structure (5-7-5 syllables) and imagery quality",
        choice_scores={"A": 1.0, "B": 0.75, "C": 0.5, "D": 0.25}
    )
    
    print(f"Score: {result.score}")
    print(f"Choice: {result.choice}")
    print(f"Reasoning: {result.reasoning}")
    print()
    
    # Example 3: Using system_msg parameter for context
    print("=== Example 3: Custom System Message ===")
    
    result = aiwand.classify_text(
        question="What causes rain?",
        answer="Rain is caused by water evaporation and condensation in clouds.",
        expected="Rain is caused by the water cycle - evaporation, condensation, and precipitation.",
        system_msg="You are a science teacher grading student responses. Be encouraging but accurate.",
        prompt_template="Check if the student understands the basic water cycle concepts",
        choice_scores={"EXCELLENT": 1.0, "GOOD": 0.8, "NEEDS_WORK": 0.4}
    )
    
    print(f"Score: {result.score}")
    print(f"Choice: {result.choice}")
    print(f"Reasoning: {result.reasoning}")
    print()
    
    # Example 4: Creating a reusable classifier
    print("=== Example 4: Reusable Classifier ===")
    
    # Create a math grader with specific evaluation criteria
    math_grader = aiwand.create_classifier(
        prompt_template="Compare the math answer to the expected result. Check for mathematical accuracy and method",
        choice_scores={"CORRECT": 1.0, "PARTIAL": 0.5, "INCORRECT": 0.0},
        system_msg="You are a math teacher. Focus on correctness and show your work",
        use_reasoning=True
    )
    
    # Use it multiple times
    questions = [
        ("What is 5 + 3?", "8", "8"),
        ("What is 10 / 2?", "5", "5"),
        ("What is 7 * 6?", "43", "42"),  # Wrong answer
    ]
    
    for question, answer, expected in questions:
        result = math_grader(question=question, answer=answer, expected=expected)
        print(f"Q: {question}")
        print(f"A: {answer} -> Score: {result.score} ({result.choice})")
        if result.reasoning:
            print(f"Reasoning: {result.reasoning[:100]}...")
        print()
    
    # Example 5: Predefined binary classifier
    print("=== Example 5: Predefined Binary Classifier ===")
    
    relevance_checker = aiwand.create_binary_classifier(criteria="relevance")
    
    result = relevance_checker(
        question="What is the capital of France?",
        answer="Paris is the capital of France.",
        expected="Paris"
    )
    
    print(f"Relevance Score: {result.score}")
    print(f"Choice: {result.choice}")
    print()
    
    # Example 6: Quality classifier
    print("=== Example 6: Quality Classifier ===")
    
    quality_grader = aiwand.create_quality_classifier()
    
    result = quality_grader(
        question="Explain photosynthesis",
        answer="Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to produce oxygen and energy in the form of sugar.",
        expected=""  # No specific expected answer
    )
    
    print(f"Quality Score: {result.score}")
    print(f"Grade: {result.choice}")
    print(f"Reasoning: {result.reasoning}")
    print()
    
    # Example 7: Advanced usage showing clean separation
    print("=== Example 7: Advanced Usage - Clean Logic Separation ===")
    
    # The evaluation logic goes in prompt_template (becomes part of system prompt)
    # The grading scale goes ONLY in choice_scores (not repeated in prompt)
    result = aiwand.classify_text(
        question="Describe the water cycle",
        answer="Water evaporates from oceans, forms clouds, then falls as rain",
        expected="The water cycle includes evaporation, condensation, precipitation, and collection",
        system_msg="You are an environmental science educator",
        prompt_template="Assess completeness of water cycle explanation, covering key stages and processes",
        choice_scores={
            "COMPLETE": 1.0,
            "MOSTLY_COMPLETE": 0.75, 
            "PARTIAL": 0.5,
            "INCOMPLETE": 0.25
        }
    )
    
    print(f"Water cycle explanation score: {result.score} ({result.choice})")
    print(f"Reasoning: {result.reasoning}")
    print()
    
    # Example 8: Comparison with improved logic
    print("=== Example 8: Before vs After Improvements ===")
    print("❌ BEFORE (redundant, confusing):")
    print("   prompt_template = 'Grade as: A (1.0), B (0.75), C (0.5)' # Scores repeated!")
    print("   choice_scores = {'A': 1.0, 'B': 0.75, 'C': 0.5}        # Scores again!")
    print()
    print("✅ AFTER (clean, logical):")
    print("   prompt_template = 'Evaluate based on accuracy and clarity'  # Just criteria")
    print("   choice_scores = {'A': 1.0, 'B': 0.75, 'C': 0.5}            # Scores once")
    print("   system_msg = 'You are an expert evaluator'                  # Context")
    print()
    
    # Show the clean version in action
    clean_result = aiwand.classify_text(
        question="What color is the sky?",
        answer="Blue",
        expected="Blue", 
        system_msg="You are an expert evaluator",
        prompt_template="Evaluate based on accuracy and clarity",
        choice_scores={"A": 1.0, "B": 0.75, "C": 0.5}
    )
    
    print(f"Clean result: Score={clean_result.score}, Choice={clean_result.choice}")


if __name__ == "__main__":
    try:
        main()
    except aiwand.AIError as e:
        print(f"AI Error: {e}")
        print("Make sure you have set up your API keys with 'aiwand setup' or environment variables.")
    except Exception as e:
        print(f"Error: {e}") 