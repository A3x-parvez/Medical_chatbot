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
            template="""You are a helpful medical assistant. Use the following medical context to answer the question. 
            If you cannot find a relevant answer in the context, say so - do not make up information.
            
            Context: {context}
            
            Question: {question}
            
            Answer:"""
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
            
            # Get response from QA chain
            response = self.qa_chain.invoke(query)
            
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