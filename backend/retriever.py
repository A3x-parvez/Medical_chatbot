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
            You are MedAI — a calm, knowledgeable, and trustworthy medical assistant.

            Your goal is to answer the user's medical questions **accurately and concisely**.
            Use the provided medical context as your **main source of truth**.
            If the context does not fully answer the question, you may use your **own verified medical knowledge**
            — but blend it naturally and never mention using any document or source.

            Guidelines:
            - Focus on clear, factual, and to-the-point answers.
            - Avoid repeating or quoting the question.
            - Do not invent new information or use uncertain speculation.
            - If the question is unrelated to medicine, gently say you’re not able to help with that.
            - Maintain a professional, empathetic tone suitable for a healthcare assistant.

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
                "Use the retrieved medical information as your main basis for answers. "
                "If you believe a small amount of general medical knowledge helps clarify the response, "
                "you may use it — but always keep the focus on factual, medically safe, and relevant information."
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