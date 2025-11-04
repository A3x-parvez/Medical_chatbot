from typing import Dict
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

import config

class MedicalRetriever:
    def __init__(self):
        """Initialize the medical retriever with Ollama models and FAISS."""
        # Initialize embeddings
        self.embeddings = OllamaEmbeddings(
            base_url=config.OLLAMA_BASE_URL,
            model=config.EMBED_MODEL_NAME
        )
        
        # Load FAISS index
        self.vectorstore = FAISS.load_local(
            config.FAISS_INDEX_PATH,
            self.embeddings,
            allow_dangerous_deserialization=True

        )
        
        # Initialize Ollama LLM
        self.llm = Ollama(
            base_url=config.OLLAMA_BASE_URL,
            model=config.LLM_MODEL_NAME
        )
        
        # Create prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            You are MedAI — a calm, professional, and medically knowledgeable assistant.

            Your role is to provide accurate, evidence-based answers to medical and healthcare-related questions.
            Use the provided medical context as your main reference, and if necessary, rely on your verified medical knowledge
            to clarify or complete the response. Always sound confident, concise, and factual.

            Rules:
            - If the question is about health, medicine, human biology, diseases, or treatment, answer it clearly and to the point.
            - If the question is unrelated to these topics (e.g., politics, history, general trivia), respond with:
            "I'm sorry, but I can only answer medical or health-related questions."
            - Never mention documents, retrieval systems, or any internal data sources.
            - Do not repeat the question, and avoid long or redundant explanations.
            - Maintain a calm, clinical, and trustworthy tone.

            Context:
            {context}

            Question:
            {question}

            Answer:
            """
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 3}
            ),
            chain_type_kwargs={
                "prompt": self.prompt_template
            }
        )
        
        print("Medical retriever initialized successfully")
    
    def get_answer(self, query: str, temperature: float = None) -> Dict:
        """
        Get answer for a medical query.
        
        Args:
            query (str): The medical question
            temperature (float, optional): Temperature for response generation
            
        Returns:
            Dict: Contains the response and metadata
        """
        try:
            # Update temperature if provided
            if temperature is not None:
                self.llm.temperature = temperature

            # 🧠 Add instruction to restrict model to PDF content
            # instruction = (
            #     "Answer ONLY using information from the provided document. "
            #     "If the document does not contain relevant details, respond with: "
            #     "'Not mentioned in the document.'\n\n"
            # )
            instruction = (
                "You are a trusted and knowledgeable medical assistant. "
                "give short, clear, and accurate answers based solely on medical knowledge. "
                "dont give answers outside the field of medical expertise."
                "Answer questions only about medicine, human health, diseases, diagnostics, or treatment. "
                "If the question is unrelated to medicine or health, politely decline to answer and guide the user back to health-related topics. "
                "Use accurate and verified medical information. "
                "Do not mention any documents or external data sources."
            )

            question = instruction + f"Question: {query}"

            
            # Get response from QA chain
            response = self.qa_chain.invoke(question)

            return {
                "response": response["result"],
                "success": True
            }
            
        except Exception as e:
            print(f"Error getting answer: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error. Please try again.",
                "success": False,
                "error": str(e)
            }