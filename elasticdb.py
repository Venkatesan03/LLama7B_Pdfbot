import os
import tempfile
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import TextLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores.elasticsearch import ElasticsearchStore

QUERY_DB = "how long is the amazon river ?"
def process_pdf_and_create_vector_store(file_content: bytes, index: str):
    index_name = index  # give the name of the index for the uploading documents...
    # Create a temporary directory to store the uploaded PDF
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_pdf_path = os.path.join(temp_dir, "uploaded.pdf")

        # Save the uploaded file to the temporary location
        with open(temp_pdf_path, "wb") as temp_pdf_file:
            temp_pdf_file.write(file_content)

        # Initialize PyPDFLoader and load the PDF
        pdf_loader = PyPDFLoader(temp_pdf_path)
        texts = pdf_loader.load()
    
    list_of_text = [doc.page_content for doc in texts]

    output_file_path = "output.txt"  
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to "output.txt" within the "database_pdf" directory
    output_file_path = os.path.join(script_directory, 'output.txt')
    # print(f"\n File stored in : {output_file_path}\n")

    # Open the file in 'w' (write) mode
    with open(output_file_path, 'w') as output_file:
        content = "".join(list_of_text)
        # Write the content to the file
        output_file.write(content)

    #Initialize embeddings
    model_name = "thenlper/gte-large"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    hugfacembeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    # Load the document, split it into chunks, embed each chunk and load it into the vector store.
    raw_documents = TextLoader(output_file_path).load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 300,
        chunk_overlap  = 20,
        length_function = len,
        is_separator_regex = False,
        )
    documents = text_splitter.split_documents(raw_documents)
    print(f"\nNo of chunked documents : {len(documents)}")

    elas_d_base = ElasticsearchStore.from_documents(
        documents,
        embedding=hugfacembeddings,
        index_name=index_name,
        es_url="http://localhost:9200"
        )
    #  os.getenv("elastic_password")
    print("\nDocuments Updated Successfully to ElasticSearch...\n")
    # elas_d_base.client.indices.refresh(index=index_name)
    # query = QUERY_DB
    # results = elas_d_base.similarity_search(query)

    
