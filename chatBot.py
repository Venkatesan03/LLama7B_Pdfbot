import os
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.vectorstores.elasticsearch import ElasticsearchStore
from langchain import PromptTemplate
from langchain.llms import CTransformers
from dataclasses import dataclass
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings

HUGFACE_MODEL = "thenlper/gte-large"
LLAMA_MODEL = "llama7B/llama-2-7b-chat.ggmlv3.q4_0.bin" # replace this with your path to the downloaded Llama model
LLAMA_TYPE = "llama"
MAX_TKN = 256
INPUT_PROMPT = """ Context : {context}
Question : {question}
Generate a helpful answer based on the provided information.
Ensure the answer is relevant and directly related to the context and question.
If you cannot find an answer or the information is insufficient, mention that you couldn't locate a relevant answer or state that you're unable to find an answer.

Answer : """

PROMPT_VARIABLES = ['context', 'question']


@dataclass
class ChatBot():
    embed_model = HUGFACE_MODEL
    llm_model = LLAMA_MODEL
    llm_type = LLAMA_TYPE
    token = MAX_TKN
    custom_prompt = INPUT_PROMPT
    prompt_var = PROMPT_VARIABLES
    index_name: None

    def custom_prompts(self):
        prompt = PromptTemplate(template=self.custom_prompt,
                            input_variables=self.prompt_var)
        return prompt
    
    # Langchain wrappers
    def lang_model(self):
        llm_wrapper = CTransformers(
                model = self.llm_model,
                model_type=self.llm_type,
                max_new_tokens = self.token,
                temperature = 0.9
            )
        return llm_wrapper
    

    def data_base(self):
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}
        hugfacembeddings = HuggingFaceEmbeddings(
            model_name=HUGFACE_MODEL,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )

        elastic_base = ElasticsearchStore(
        es_url="http://localhost:9200",
        index_name=self.index_name,
        embedding=  hugfacembeddings,
        strategy=ElasticsearchStore.ExactRetrievalStrategy()
        )
        # es_password=os.getenv("elastic_password"),
        return elastic_base
    
    
    # Pipeline for the Bot
    def bot_chain(self, prompt, llm_wrapper, database):
        bot_Chain = RetrievalQA.from_chain_type(
                                llm=llm_wrapper,
                                chain_type="stuff",
                                retriever=database.as_retriever(search_kwargs={'k': 1}),
                                chain_type_kwargs={"prompt": prompt},
                                return_source_documents=True
                            )
        return bot_Chain
    
    def pdf_bot(self):
        self.prompt = self.custom_prompts()
        self.llm_wrapper = self.lang_model()
        self.elastic_base = self.data_base()
        self.pdfbot = self.bot_chain(self.prompt, self.llm_wrapper, self.elastic_base)
        print("\nVenkat's PdfBot loaded with QnA Retreival Chain....\n")
        return self.pdfbot
