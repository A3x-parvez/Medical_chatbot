from typing import Dict
import os
import json
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

import config


class MedicalRetriever:
    def __init__(self, llm_model: str = None):
        """Initialize the medical retriever with Ollama models and FAISS.

        Uses a single, fixed embedding model (configured in `config.EMBED_MODEL_NAME`).
        llm_model: model to use for generation
        """
        # Single embedding model (no dynamic embedding switching)
        self.embed_model = config.EMBED_MODEL_NAME
        self.llm_model = llm_model or config.LLM_MODEL_NAME

        # Initialize embeddings using the single configured embedding model
        self.embeddings = OllamaEmbeddings(
            base_url=config.OLLAMA_BASE_URL,
            model=self.embed_model
        )

        # Load FAISS index
        self.vectorstore = FAISS.load_local(
            config.FAISS_INDEX_PATH,
            self.embeddings,
            allow_dangerous_deserialization=True
        )

        # Initialize LLM
        self.llm = Ollama(
            base_url=config.OLLAMA_BASE_URL,
            model=self.llm_model
        )

        # ---- Persona and Behavior Template ----
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            You are MedAI — a calm, professional, and medically intelligent assistant.

            Your role is to give accurate, concise, and trustworthy answers about:
            - Medicine, diseases, diagnosis, treatment, human biology, and wellness.
            - Reproductive and sexual health (including menstruation, pregnancy, first-time sex, hygiene, contraception, etc.).
            Always answer these topics with clarity, empathy, and professionalism.

            Guidelines:
            - If the question is medical or health-related, give a short and direct answer (3–6 sentences).
            - If the question is unrelated to medicine (e.g., politics, sports, entertainment, etc.), 
              respond only with: “I’m sorry, but I can only answer medical or health-related questions.”
            - Do not combine that message with a valid medical answer.
            - Never mention any documents, retrieval systems, or external data.
            - Keep a confident, compassionate tone suitable for a trusted medical advisor.

            Context:
            {context}

            Question:
            {question}

            Answer:
            """
        )

        # ---- Retrieval QA Chain ----
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": self.prompt_template}
        )

        print("✅ Medical retriever initialized successfully")

    def update_llm(self, new_llm_model: str):
        """Switch the LLM model used for generation at runtime."""
        if not new_llm_model:
            return
        print(f"🔧 Updating LLM model to: {new_llm_model}")
        self.llm_model = new_llm_model
        self.llm = Ollama(base_url=config.OLLAMA_BASE_URL, model=self.llm_model)
        # Recreate the chain to pick up new llm
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": self.prompt_template}
        )

    def get_state(self) -> Dict:
        """Return current model state for API/UI."""
        return {
            "embed_model": self.embed_model,
            "llm_model": self.llm_model,
            "llm_models": config.SELECTED_LLM_MODELS
        }

    def get_answer(self, query: str, temperature: float = None) -> Dict:
        """
        Get an answer for a medical query.
        """
        try:
            if temperature is not None:
                self.llm.temperature = temperature

            # Clean, merged instruction (no redundancy)
            instruction = (
                "You are a trusted and knowledgeable medical assistant. "
                "Provide short, clear, and medically accurate answers based primarily on medical knowledge. "
                "Focus strictly on topics like human health, diseases, treatment, diagnosis, wellness, or reproductive health. "
                "Do not answer unrelated topics. "
                "Do not mention sources or internal systems."
            )

            question = instruction + f"\n\nQuestion: {query}"

            # Invoke QA chain
            response = self.qa_chain.invoke(question)

            return {
                "response": response.get("result", str(response)),
                "success": True
            }

        except Exception as e:
            print(f"Error getting answer: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error. Please try again.",
                "success": False,
                "error": str(e)
            }
