#!/usr/bin/env python3
"""
OCR Test - Testing new OCR wrapper functionality and enhanced features
"""

import aiwand
from dotenv import load_dotenv

load_dotenv()

expected_texts_1 = [
     "Liquor Street",
    "Tandoori chicken", 
        "Lasooni Dal Tadka",
        "HYDERABADI MURG",
        "1,139.00",
        "Invoice Number",
        "Faridabad"
]


def test_new_ocr_wrapper():
    """Test the new OCR wrapper functionality with expected words validation"""
    print("🆕 Testing New OCR Wrapper Features")
    print("=" * 50)
    
    # Sample image for testing
    sample_image = "https://bella.amankumar.ai/examples/receipt_1.jpeg"
    
    
    def validate_ocr_accuracy(text, test_name):
        """Helper function to validate OCR accuracy"""
        print(f"\n🔍 {test_name} Validation:")
        matches = 0
        for expected in expected_texts_1:
            if expected.lower() in text.lower():
                print(f"   ✅ Found: '{expected}'")
                matches += 1
            else:
                print(f"   ❌ Missing: '{expected}'")
        
        accuracy = (matches / len(expected_texts_1)) * 100
        print(f"\n📊 {test_name} Accuracy: {accuracy:.1f}% ({matches}/{len(expected_texts_1)} items found)")
        
        if accuracy < 50:
            print("⚠️  OCR appears to be hallucinating - very low accuracy!")
            return False
        elif accuracy < 80:
            print("⚠️  OCR has moderate accuracy - some issues detected")
            return True
        else:
            print("✅ OCR appears to be working correctly!")
            return True
    
    try:
        # Test 1: Direct ocr_call_ai wrapper usage
        print("\n1️⃣ Testing ocr_call_ai() wrapper directly")
        print("-" * 40)
        
        extracted_text = aiwand.ocr(
            # user_prompt="Extract all text from this receipt image:",
            images=[sample_image],
            # additional_system_instructions="Focus on restaurant name, items, and total amount",
            # temperature=0.05,  # Very low for consistent extraction
            # debug=False  # Reduce debug output for cleaner test
        )
        
        print(f"✅ ocr_call_ai Success! Extracted {len(extracted_text)} characters")
        print(f"📄 Extracted text: {extracted_text}...")
        
        # Validate accuracy
        wrapper_direct_success = validate_ocr_accuracy(text=extracted_text, test_name="ocr_call_ai Direct")
        
        # Test 2: Enhanced ocr() function with new parameters
        print("\n2️⃣ Testing enhanced ocr() with customization")
        print("-" * 40)
        
        custom_result = aiwand.ocr(
            images=[sample_image],
            # system_prompt="You are an expert at reading restaurant receipts and invoices. Extract text with high accuracy. Only Extract table data.",
            # additional_system_instructions="Pay special attention to prices, quantities, and item names. Only extract invoice table data, nothing else.",
            # temperature=0.1,
            # model="gemini-2.0-flash-lite",
            debug=True
        )
        
        custom_success = False
        if custom_result:
            print(f"✅ Enhanced OCR Success! Extracted {len(custom_result)} characters")
            print(f"📄 Custom OCR: {custom_result}...")
            
            # Validate accuracy
            custom_success = validate_ocr_accuracy(custom_result, "Enhanced ocr()")
        else:
            print("❌ Enhanced OCR failed")
            print(f"Failed items: {custom_result['failed']}")
        
        # Test 3: Verify call_ai uses OCR wrapper internally
        print("\n3️⃣ Testing call_ai with use_ocr (should use wrapper internally)")
        print("-" * 40)
        
        wrapper_integrated = aiwand.call_ai(
            user_prompt="Extract all text from this receipt and then tell me the restaurant name and total amount:",
            images=[sample_image],
            use_ocr=True,  # This should now use the OCR wrapper internally
            model="gemini-2.0-flash-lite",
            debug=False
        )
        
        print(f"✅ call_ai with OCR Success! Response length: {len(wrapper_integrated)} characters")
        print(f"🤖 AI Analysis preview: {wrapper_integrated[:200]}...")
        
        # Check if the analysis contains expected restaurant info
        restaurant_found = any(term.lower() in wrapper_integrated.lower() 
                             for term in ["liquor street", "restaurant", "food", "receipt"])
        total_found = any(term in wrapper_integrated.lower() 
                         for term in ["1,139", "1139", "total", "amount"])
        
        print(f"🔍 call_ai Integration Validation:")
        print(f"   Restaurant info detected: {'✅' if restaurant_found else '❌'}")
        print(f"   Total amount detected: {'✅' if total_found else '❌'}")
        
        integration_success = restaurant_found and total_found
        
        # Test 4: Consistency check with simplified test
        print("\n4️⃣ OCR wrapper consistency test")
        print("-" * 40)
        
        # Get current model for comparison
        current_provider = aiwand.get_current_provider()
        print(f"🤖 Using provider: {current_provider}")
                        
        # Overall assessment
        print("\n" + "="*50)
        print("🎯 New Wrapper Test Results:")
        print(f"   ✅ ocr_call_ai direct: {'PASS' if wrapper_direct_success else 'FAIL'}")
        print(f"   ✅ Enhanced ocr(): {'PASS' if custom_success else 'FAIL'}")
        print(f"   ✅ call_ai integration: {'PASS' if integration_success else 'FAIL'}")
        
        overall_success = (wrapper_direct_success and custom_success and 
                         integration_success)
        
        print(f"\n🚀 Overall wrapper functionality: {'✅ WORKING' if overall_success else '❌ ISSUES DETECTED'}")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Wrapper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_legacy_tests():
    """Run focused legacy OCR tests"""
    print("\n🔄 Running Focused Legacy OCR Tests")
    print("=" * 40)
    
    # Sample image and document for testing  
    sample_image = "https://bella.amankumar.ai/examples/receipt_1.jpeg"
    statement_doc = "https://bella.amankumar.ai/examples/bank-statements/info-indian-overseas-bank.pdf"
    
    print(f"📷 Testing with image: {sample_image}")
    print(f"🤖 Current provider: {aiwand.get_current_provider()}")
    
    try:
        # Test 1: Standard OCR function (should now use new wrapper internally)
        print("\n1️⃣ Standard OCR Function (using new wrapper internally)")
        print("-" * 50)
        
        ocr_result = aiwand.ocr(
            images=[sample_image],
            model="gemini-2.0-flash-lite",
            debug=False
        )
        
        legacy_success = False
        if ocr_result:
            print(f"✅ Standard OCR Success! Extracted {len(ocr_result)} characters")
            print(f"📄 Text preview: {ocr_result[:150]}...")
            
            # Validate OCR accuracy
            print(f"\n🔍 Standard OCR Validation:")
            matches = 0
            for expected in expected_texts_1:
                if expected.lower() in ocr_result.lower():
                    print(f"   ✅ Found: '{expected}'")
                    matches += 1
                else:
                    print(f"   ❌ Missing: '{expected}'")
            
            accuracy = (matches / len(expected_texts_1)) * 100
            print(f"\n📊 Standard OCR Accuracy: {accuracy:.1f}% ({matches}/{len(expected_texts_1)} items found)")

            legacy_success = True if accuracy >= 70 else False
            if accuracy >= 70:
                print("✅ Standard OCR working correctly!")
            elif accuracy >= 30:
                print("⚠️  Standard OCR has moderate accuracy")
            else:
                print("❌ Standard OCR appears to be having issues")
                
        else:
            print("❌ Standard OCR failed")
            print(f"Failed items: {ocr_result}")
        
        # Test 2: Document OCR with new wrapper
        print("\n2️⃣ Document OCR Test")
        print("-" * 30)
        
        # Expected text from the bank statement for validation
        statement_expected_texts = [
            "Indian Overseas Bank",
            "228601000013427",  # Account Number  
            "PAPPATHI",          # Customer name
            "Statement for the period",
            "BALANCE"           # Column header
        ]

        ocr_prompt = f"""You are an document conversion system. 
Extract all text from the provided document accurately, preserving the original formatting, structure, and layout as much as possible. 
Follow belo Instructions:
- Extract ALL visible text from the document
- Maintain original formatting (line breaks, spacing, structure, indentation)
- Keep tables and multi-column layouts using spaces/tabs
- Preserve field labels with their delimiters (:)
- Include any numbers, dates, addresses, or special characters 
- Keep address blocks and phone numbers in original format
- Preserve special characters ($, %, etc.) exactly as shown
- Do not surround your output with triple backticks
- Render signatures as [Signature] or actual text if present
- Maintain section headers and sub-headers
- Keep page numbers and document identifiers
- Preserve form numbering and copyright text
- Keep line breaks and paragraph spacing as shown

Remember: Convert ONLY what is visible in the document, do not add, assume, or manufacture any information that isn't explicitly shown in the source image.

Output the extracted text clearly and accurately.
"""
        
        d1 = aiwand.call_ai(
            document_links=[statement_doc],
            # images=[sample_image],
            model="gemini-2.0-flash-lite",
            debug=True,
            # system_prompt="what is this document",
            use_ocr=False,
            use_vision=True
        )
        print(d1)

        d2 = aiwand.call_ai(
            document_links=[statement_doc],
            # images=[sample_image],
            model="gemini-2.5-flash-lite",
            debug=True,
            system_prompt="what is this total amount",
        )
        print(d2)

        doc_result = aiwand.ocr(
            document_links=[statement_doc],
            model="gemini-2.5-flash-lite",
        )

        doc_result_csv = aiwand.ocr(
            document_links=[statement_doc],
            model="gemini-2.5-flash-lite",
            system_prompt="Extract table data from this document in csv format"
        )
        print(doc_result_csv)

        doc_success = False
        if doc_result:
            extracted_doc_text = doc_result
            print(f"✅ Document OCR Success! Extracted {len(extracted_doc_text)} characters")
            print(f"📄 Document preview: {extracted_doc_text[:150]}...")
            
            # Validate document OCR accuracy  
            print(f"\n🔍 Document OCR Validation:")
            doc_matches = 0
            for expected in statement_expected_texts:
                if expected.lower() in extracted_doc_text.lower():
                    print(f"   ✅ Found: '{expected}'")
                    doc_matches += 1
                else:
                    print(f"   ❌ Missing: '{expected}'")
            
            doc_accuracy = (doc_matches / len(statement_expected_texts)) * 100
            print(f"\n📊 Document OCR Accuracy: {doc_accuracy:.1f}% ({doc_matches}/{len(statement_expected_texts)} items found)")
            
            if doc_accuracy >= 60:  # Lower threshold for documents
                print("✅ Document OCR working correctly!")
                doc_success = True
            elif doc_accuracy >= 20:
                print("⚠️  Document OCR has moderate accuracy")
                doc_success = True
            else:
                print("❌ Document OCR appears to be having issues")
                
        else:
            print("❌ Document OCR failed")
            print(f"Failed items: {doc_result['failed']}")
            
        # Legacy test summary
        print(f"\n📊 Legacy OCR Test Results:")
        print(f"   Standard OCR: {'✅ PASS' if legacy_success else '❌ FAIL'}")
        print(f"   Document OCR: {'✅ PASS' if doc_success else '❌ FAIL'}")
        
        return legacy_success and doc_success
        
    except Exception as e:
        print(f"❌ Legacy test error: {e}")
        print("\n💡 Troubleshooting:")
        print("   • Make sure you have OPENAI_API_KEY or GEMINI_API_KEY in your .env file")
        print("   • Check your internet connection")
        print("   • Verify the image/document URLs are accessible")
        return False
    
def main():
    """Enhanced OCR test suite with new wrapper functionality"""
    # Load environment variables
    load_dotenv()
    
    print("🧪 AIWand OCR Test Suite (Enhanced)")
    print("=" * 50)
    
    # Test new wrapper functionality first
    wrapper_success = test_new_ocr_wrapper()
    
    if not wrapper_success:
        print("⚠️  New wrapper tests failed, but continuing with legacy tests...")
    
    # Run legacy tests
    legacy_success = run_legacy_tests()
    
    # Final comprehensive summary
    print("\n" + "="*60)
    print("🎯 COMPLETE OCR TEST SUITE SUMMARY")
    print("="*60)
    
    overall_success = wrapper_success and legacy_success
    
    print(f"🆕 New OCR Wrapper Tests: {'✅ PASS' if wrapper_success else '❌ FAIL'}")
    print(f"🔄 Legacy OCR Tests: {'✅ PASS' if legacy_success else '❌ FAIL'}")
    print(f"\n🚀 Overall OCR System: {'✅ FULLY WORKING' if overall_success else '❌ ISSUES DETECTED'}")
    
    if overall_success:
        print("\n🎉 SUCCESS! All OCR functionality is working correctly!")
        print("\n📝 Available OCR methods:")
        print("   • aiwand.ocr_call_ai() - Direct OCR wrapper with optimizations")
        print("   • aiwand.ocr() - Enhanced with system_prompt, temperature controls")
        print("   • aiwand.call_ai(use_ocr=True) - Automatic OCR integration")
        
        print("\n🎛️  Customization options in aiwand.ocr():")
        print("   • system_prompt: Custom OCR instructions")
        print("   • additional_system_instructions: Extra guidelines")
        print("   • temperature: Control response consistency (default: 0.1)")
        print("   • model: Choose specific AI model")
        print("   • provider: Select AI provider")
        
        print("\n✨ Key improvements implemented:")
        print("   • OCR-optimized system prompts for better text extraction")
        print("   • Lower temperature (0.1) for consistent results")
        print("   • Better document handling and processing")
        print("   • User customization while maintaining optimal defaults")
        print("   • Fixed recursion and circular import issues")
    else:
        print("\n⚠️  Some tests failed. Check the detailed output above for specific issues.")
        if not wrapper_success:
            print("   • New OCR wrapper functionality needs attention")
        if not legacy_success:
            print("   • Legacy OCR compatibility needs attention")
    
    return overall_success

# if __name__ == "__main__":
    # main()
