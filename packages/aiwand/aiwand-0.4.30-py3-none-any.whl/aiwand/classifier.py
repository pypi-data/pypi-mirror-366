"""
AIWand Classifier - Simple text classification and grading functionality.

This module provides a simplified classifier that can be used to grade or classify
text responses based on custom criteria and choice scores.
"""

from typing import Dict, Optional, Any, Union
from pydantic import BaseModel, Field

from .config import call_ai, AIError, ModelType
from .models import AIProvider


class ClassifierResponse(BaseModel):
    """Response from the classifier with score, choice, and optional reasoning."""
    
    score: float = Field(description="The numerical score for the response")
    choice: str = Field(description="The choice/grade selected")
    reasoning: str = Field(default="", description="Reasoning behind the choice")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Add reasoning to metadata for compatibility
        if self.reasoning and "rationale" not in self.metadata:
            self.metadata["rationale"] = self.reasoning


def classify_text(
    question: str,
    answer: str,
    expected: str = "",
    prompt_template: str = "",
    choice_scores: Optional[Dict[str, float]] = None,
    system_msg: str = "",
    use_reasoning: bool = True,
    model: Optional[ModelType] = None,
    provider: Optional[Union[AIProvider, str]] = None
) -> ClassifierResponse:
    """
    Classify or grade text based on custom criteria.
    
    This function provides a simple interface for text classification and grading
    that's inspired by autoevals but integrated with AIWand's provider system.
    
    Args:
        question: The question, prompt, or context
        answer: The response to be evaluated
        expected: The expected or reference response (optional)
        prompt_template: Custom evaluation logic/criteria (goes into system prompt)
        choice_scores: Mapping of choices to scores (e.g., {"A": 1.0, "B": 0.5, "C": 0.0})
        system_msg: Custom system message for evaluation context
        use_reasoning: Whether to include step-by-step reasoning
        model: Specific model to use
        provider: Specific provider to use
        
    Returns:
        ClassifierResponse with score, choice, reasoning, and metadata
        
    Raises:
        ValueError: If required parameters are missing
        AIError: If the classification fails
        
    Examples:
        # Simple grading
        result = classify_text(
            question="What is 2+2?",
            answer="4", 
            expected="4",
            choice_scores={"CORRECT": 1.0, "INCORRECT": 0.0}
        )
        
        # Custom evaluation with specific criteria
        result = classify_text(
            question="Write a haiku about spring",
            answer="Cherry blossoms bloom\\nGentle breeze through ancient trees\\nSpring awakens all",
            prompt_template="Evaluate this haiku based on structure (5-7-5 syllables) and imagery quality.",
            choice_scores={"A": 1.0, "B": 0.75, "C": 0.5, "D": 0.25},
            use_reasoning=True
        )
    """
    # Validate inputs
    if not question.strip():
        raise ValueError("question cannot be empty")
    if not answer.strip():
        raise ValueError("answer cannot be empty")
    
    # Default choice scores if not provided
    if choice_scores is None:
        choice_scores = {"CORRECT": 1.0, "INCORRECT": 0.0}
    
    if not choice_scores:
        raise ValueError("choice_scores cannot be empty")
    
    # Build system prompt components
    base_system_msg = system_msg if system_msg.strip() else "You are an AI classifier and grader. Evaluate responses according to the given criteria."
    
    # Add evaluation logic from prompt_template to system prompt
    evaluation_logic = ""
    if prompt_template.strip():
        evaluation_logic = f"\nEvaluation Criteria: {prompt_template.strip()}"
    else:
        # Default evaluation logic
        if expected.strip():
            evaluation_logic = "\nEvaluation Criteria: Compare the given answer to the expected answer and evaluate how well they match."
        else:
            evaluation_logic = "\nEvaluation Criteria: Evaluate the quality and appropriateness of the answer to the question."
    
    # Available choices (only names, not scores)
    available_choices = ", ".join(choice_scores.keys())
    
    # Complete system prompt
    system_prompt = f"""{base_system_msg}

{evaluation_logic}

Available grades: {available_choices}

{"Provide your step-by-step reasoning in the 'reasoning' field, then your final grade in the 'grade' field." if use_reasoning else "Provide your final grade in the 'grade' field."}

Your grade must be exactly one of the specified options."""
    
    # Create user prompt (clean, without choice scores)
    user_prompt_parts = [f"Question: {question}", f"Answer: {answer}"]
    if expected.strip():
        user_prompt_parts.append(f"Expected: {expected}")
    
    user_prompt = "\n".join(user_prompt_parts)
    
    # Create dynamic response model
    if use_reasoning:
        class DynamicClassifierModel(BaseModel):
            reasoning: str = Field(description="Step-by-step analysis and reasoning")
            grade: str = Field(description=f"Final grade, must be one of: {available_choices}")
    else:
        class DynamicClassifierModel(BaseModel):
            grade: str = Field(description=f"Final grade, must be one of: {available_choices}")
    
    try:
        # Use structured output
        result = call_ai(
            system_prompt=system_prompt,
            response_format=DynamicClassifierModel,
            model=model,
            provider=provider,
            user_prompt=user_prompt
        )
        
        # Validate grade
        grade = result.grade.upper()
        if grade not in choice_scores:
            # Try case-insensitive match
            grade_lower = result.grade.lower()
            matched_key = None
            for key in choice_scores.keys():
                if key.lower() == grade_lower:
                    matched_key = key
                    break
            
            if matched_key:
                grade = matched_key
            else:
                raise AIError(f"Invalid grade '{result.grade}' received. Expected one of: {available_choices}")
        
        score = choice_scores[grade]
        reasoning = getattr(result, 'reasoning', '') if use_reasoning else ''
        
        return ClassifierResponse(
            score=score,
            choice=grade,
            reasoning=reasoning,
            metadata={
                "model": str(model) if model else None,
                "provider": str(provider) if provider else None,
                "choices_available": list(choice_scores.keys()),
                "choice_scores": choice_scores
            }
        )
        
    except AIError:
        raise
    except Exception as e:
        raise AIError(f"Classification failed: {str(e)}")


def create_classifier(
    prompt_template: str,
    choice_scores: Dict[str, float],
    system_msg: str = "",
    use_reasoning: bool = True,
    model: Optional[ModelType] = None,
    provider: Optional[Union[AIProvider, str]] = None
) -> callable:
    """
    Create a reusable classifier function with predefined settings.
    
    This is useful when you want to create a classifier with specific settings
    that you'll use multiple times.
    
    Args:
        prompt_template: Evaluation criteria and logic (goes into system prompt)
        choice_scores: Mapping of choices to scores
        system_msg: Custom system message for evaluation context
        use_reasoning: Whether to include reasoning
        model: Default model to use
        provider: Default provider to use
        
    Returns:
        A callable classifier function
        
    Example:
        # Create a reusable grader
        grader = create_classifier(
            prompt_template="Compare the math answer to the expected result. Check for mathematical accuracy.",
            choice_scores={"CORRECT": 1.0, "PARTIAL": 0.5, "INCORRECT": 0.0},
            use_reasoning=True
        )
        
        # Use it multiple times with clear keyword arguments
        result1 = grader(question="2+2", answer="4", expected="4")
        result2 = grader(question="3+3", answer="6", expected="6")
    """
    def classifier(
        question: str,
        answer: str,
        expected: str = "",
        **kwargs
    ) -> ClassifierResponse:
        """Classify text using the predefined settings.
        
        Args:
            question: The question, prompt, or context
            answer: The response to evaluate
            expected: Expected response (optional)
        """
        # Allow overriding settings via kwargs
        return classify_text(
            question=question,
            answer=answer,
            expected=expected,
            prompt_template=prompt_template,
            choice_scores=choice_scores,
            system_msg=system_msg,
            use_reasoning=use_reasoning,
            model=kwargs.get('model', model),
            provider=kwargs.get('provider', provider)
        )
    
    return classifier


# Predefined common classifiers
def create_binary_classifier(
    criteria: str = "correctness",
    model: Optional[ModelType] = None,
    provider: Optional[Union[AIProvider, str]] = None
) -> callable:
    """
    Create a simple binary (correct/incorrect) classifier.
    
    Args:
        criteria: What to evaluate (e.g., "correctness", "relevance", "quality")
        model: Model to use
        provider: Provider to use
        
    Returns:
        Binary classifier function
    """
    prompt_template = f"Evaluate the {criteria} of the answer. Is the answer correct and appropriate for the given question?"
    
    return create_classifier(
        prompt_template=prompt_template,
        choice_scores={"CORRECT": 1.0, "INCORRECT": 0.0},
        use_reasoning=True,
        model=model,
        provider=provider
    )


def create_quality_classifier(
    model: Optional[ModelType] = None,
    provider: Optional[Union[AIProvider, str]] = None
) -> callable:
    """
    Create a quality classifier with grades A through F.
    
    Args:
        model: Model to use
        provider: Provider to use
        
    Returns:
        Quality classifier function
    """
    prompt_template = "Evaluate the overall quality of the answer considering factors like accuracy, completeness, clarity, and appropriateness."
    
    return create_classifier(
        prompt_template=prompt_template,
        choice_scores={"A": 1.0, "B": 0.8, "C": 0.6, "D": 0.4, "F": 0.0},
        use_reasoning=True,
        model=model,
        provider=provider
    ) 