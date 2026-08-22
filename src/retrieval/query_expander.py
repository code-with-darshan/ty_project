from openai import OpenAI
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL


class QueryExpander:
    """Translates colloquial legal terms into formal statutory language for better retrieval across all Indian law domains."""

    def __init__(self, model_name: str = OLLAMA_MODEL, base_url: str = OLLAMA_BASE_URL):
        self.model_name = model_name
        self.client = OpenAI(
            base_url=base_url,
            api_key="ollama",
        )

    def expand_query(self, query: str) -> str:
        # We use Few-Shot Prompting to completely prevent the model from answering the question
        system_prompt = (
            "You are a legal terminology translator specialising in Indian law across all domains "
            "(criminal, civil, family, property, labour, corporate, intellectual property, consumer, "
            "constitutional, and digital law).\n\n"
            "Your task: take the user's colloquial or informal query and rewrite it using the formal "
            "legal concepts and terminology found in the relevant Indian statute(s).\n\n"
            "STRICT RULES:\n"
            "1. Use precise statutory language — the exact words a lawyer or court would use.\n"
            "2. If the Act is known, include it (e.g., 'Hindu Marriage Act 1955', 'IT Act 2000').\n"
            "3. DO NOT answer the user's question. DO NOT explain the law. DO NOT provide penalties or lists.\n"
            "4. OUTPUT ONLY THE EXPANDED QUERY STRING — nothing else.\n\n"
            "EXAMPLES:\n"
            "User: What is the procedure for a Zero FIR?\n"
            "Output: information relating to a cognizable offence irrespective of jurisdiction Bharatiya Nagarik Suraksha Sanhita BNSS\n\n"
            "User: What is the punishment for eve-teasing?\n"
            "Output: punishment for outraging the modesty of a woman sexual harassment words gestures acts intended to insult modesty BNS\n\n"
            "User: How do I get a divorce under Hindu law?\n"
            "Output: grounds for dissolution of marriage divorce Hindu Marriage Act 1955\n\n"
            "User: Can I break a contract if the other party lied to me?\n"
            "Output: voidability of contract induced by misrepresentation fraud Indian Contract Act 1872\n\n"
            "User: What is my right to get government documents?\n"
            "Output: right to information public authority disclosure records Right to Information Act 2005\n\n"
            "User: What is software copyright protection in India?\n"
            "Output: copyright protection computer programme literary work author rights Copyright Act 1957\n\n"
            "User: What are the rights of a consumer who bought a defective product?\n"
            "Output: defect in goods liability of manufacturer seller consumer rights redressal Consumer Protection Act 2019\n\n"
            "User: Hit and run case punishment?\n"
            "Output: causing death by rash and negligent driving and escaping without reporting to police or magistrate Motor Vehicles Act BNS\n\n"
            "User: What is the penalty for hacking a website?\n"
            "Output: unauthorised access to computer resource data tampering cyber offence Information Technology Act 2000\n"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
                temperature=0.0,
            )
            expanded_query = response.choices[0].message.content.strip()
            return expanded_query.strip('"').strip("'")
        except Exception as e:
            print(f"Query expansion failed: {e}")
            return query