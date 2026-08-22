from app import LegalRAGPipeline

def run_tests():
    pipeline = LegalRAGPipeline()
    
    test_queries = [
        # Query 1: The original "Zero FIR" test (Let's see if the new prompt fixed the CrPC hallucination)
        "What is the procedure for a Zero FIR under the BNSS?",
        
        # Query 2: The Pure Hallucination Trap (Cryptocurrency isn't explicitly defined in these laws. Will it guess or refuse?)
        "What is the punishment for cryptocurrency laundering under the BNS?",
        
        # Query 3: The Old Slang Trap (Can the expander translate "eve-teasing" to "sexual harassment" / "outraging modesty" without failing?)
        "What is the punishment for eve-teasing?",
        
        # Query 4: The Procedural Edge Case (A very specific rule. Can the dense vector find the "sunset/sunrise" clause?)
        "Can a police officer arrest a woman after sunset under the BNSS?",
        
        #query 5:
        "What is the punishment for rape?",
        
        # Query 6: The Synthesis Trap (Combines electronic evidence from BSA with snatching from BNS. Very hard for standard RAG to fuse).
        "Is an electronic confession recorded on a smartwatch admissible for proving a snatching case?"
    ]
    
    for i, query in enumerate(test_queries, start=1):
        print("\n" + "=" * 80)
        print(f"TEST QUERY {i}: {query}")
        print("=" * 80)
        
        result = pipeline.query(query)
        
        print(f"\nANSWER:\n{result['answer']}")
        print(f"\nCONFIDENCE: {result['confidence_tier']} ({result['confidence_score']}%)")
        print("CITATIONS:")
        
        unique_citations = {f"Act: {c.get('act')} | Sec: {c.get('section')} | Page: {c.get('pages')}" for c in result['citations']}
        for citation in unique_citations:
            print(f" - {citation}")

if __name__ == "__main__":
    run_tests()