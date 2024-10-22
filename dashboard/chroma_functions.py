import gc
import streamlit as st
import chromadb
import warnings
import torch
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from sentence_transformers import SentenceTransformer
from dashboard.llm_functions import query_sum_document, query_expansion
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever


################## Funzioni di utilità ##################
def clear_cache():
    gc.collect()
    torch.cuda.empty_cache()


@st.cache_resource
def get_chroma_client():
    client = st.session_state["chroma_client"] = chromadb.HttpClient(
            host="localhost",
            port=8000,
            ssl=False,
            headers=None,
            settings=Settings(),
            tenant=DEFAULT_TENANT,
            database=DEFAULT_DATABASE,
        )
    return client


def query_encode(query):
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=FutureWarning
        )
        model = SentenceTransformer('intfloat/multilingual-e5-large')
    embedding = model.encode('query: ' + query)
    del model
    clear_cache()
    return embedding


def chunks_concat(lista_chunks):
    full_question = ''
    lista_chunks = sorted(lista_chunks, key=lambda x: x['Chunk Number'])
    for chunk in lista_chunks:
        full_question += chunk['Question'] + '\n'
    return full_question


def question_answer_concat(questions, answers, rerank):
    documents = []
    urls = []

    if rerank == True:
        for r in questions:
            document = '\n\nDOCUMENTO:\nDomanda:' + r.page_content
            document += '\nRisposta: ' + r.metadata['Answer']

            documents.append(document)
            urls.append(r.metadata['URL'])      # URLs reordering

        return documents, urls

    else:
        # no rerank, just compose documents
        for question, answer in zip(questions, answers):
            document = '\n\nDOCUMENTO:\nDomanda:' + question
            document += '\nRisposta: ' + answer
            documents.append(document)

        return documents


def concat_documents(documents, summarize):
    documents_concat = ''
    for i, doc in enumerate(documents):
        if summarize == True:
            documents_concat += '\n\n' + query_sum_document(doc)
            print(f'DEBUG: Summarization {i+1}/{len(documents)}completata')
        else:
            documents_concat += doc
    return documents_concat


def get_new_prompt(query, documents, collection_name, summarize):
    documents_concat = ''

    # FORUMS
    if collection_name == 'RAG':
        # concat documents with or without summarizing and write new prompt
        documents_concat = concat_documents(documents, summarize)

        new_prompt = (
            'I miei sintomi sono i seguenti: ' + query + '.\n'
            'Si prega di formulare una diagnosi dettagliata, tenendo conto esclusivamente dei miei sintomi. '
            'Utilizza le informazioni contenute nei seguenti documenti come riferimento per possibili casi simili, '
            'senza confondere i sintomi dei documenti con i miei: ' + documents_concat + '\n'
            'La diagnosi dovrebbe essere espressa in modo formale e professionale, come se fossi un medico. '
            'Includi anche eventuali raccomandazioni o ulteriori indagini necessarie. (Max 250 words)'
        )

        # new_prompt = 'I miei sintomi sono: ' + query + '\n' \
        #              'Formula la mia diagnosi consultando le seguenti diagnosi date da medici ad altri pazienti ' \
        #              'se contengono informazioni rilevanti per il mio caso clinico: ' + documents_concat

    # HUMANITAS 
    elif collection_name == 'humanitas':
        # concat documents and write new prompt
        for doc in documents:
            documents_concat += 'DOCUMENTO: ' + doc + '\n\n'
        new_prompt = 'Query: ' + query + '\n\nData la precedente query, fornisci un tuo parere estraendo ' \
                     'informazioni dai seguenti documenti solo se rilevanti per la query: \n\n' + documents_concat
        
    # every other collection
    else: 
        # concat documents and write new prompt
        for doc in documents:
            documents_concat += 'DOCUMENTO: ' + doc + '\n\n'
        new_prompt = 'Query: ' + query + '\n\nDocumenti: \n\n' + documents_concat

    return new_prompt


################## Funzioni di retrieval ad hoc per le collection ####################
def documents_retrieval_humanitas(query, embedding, collection, rerank):
    documents = []

    limit = 3

    # retrieval
    if rerank == True:
        results = collection.query(query_embeddings=embedding.tolist(), n_results=15)
    else:
        results = collection.query(query_embeddings=embedding.tolist(), n_results=limit)

    documents = results['documents'][0]

    # rerank
    if rerank == True:
        docs = []
        for question in documents:
            docs.append(Document(
                    page_content = question,
                ))
        retriever = BM25Retriever.from_documents(docs, k=5)
        result = retriever.invoke(query)

        documents = result[:limit]

    return documents


def documents_retrieval_forums(query, embedding, collection, rerank):
    urls = []
    questions = []
    answers = []

    limit = 5

    # retrieval
    if rerank == True:
        results = collection.query(query_embeddings=embedding.tolist(), n_results=15)
    else:
        results = collection.query(query_embeddings=embedding.tolist(), n_results=limit)
    print('DEBUG: Retrieval completato')

    # controllo chunk provenienti dallo stesso URL (!)
    for r in results['metadatas'][0]:
        url = r['URL']
        if url not in urls:
            questions.append(r['Question'])
            answers.append(r['Answer'])
            urls.append(url)

    # rerank
    if rerank == True:
        docs = []
        for question, answer, url in zip(questions, answers, urls):
            docs.append(Document(
                    page_content = question,
                    metadata={'URL': url,
                              'Answer': answer}
                ))
        retriever = BM25Retriever.from_documents(docs, k=5)
        result = retriever.invoke(query)

        # lista degli URLs da riordinare in base al rank
        documents, urls = question_answer_concat(result, None, rerank)
        print('DEBUG: Reranking completato')

    # no rerank
    else:
        # lista degli URLs già ok
        documents = question_answer_concat(questions, answers, rerank)

    return documents, urls


################## Funzione finale per processare la query ####################
def process_query(query, collection_name, expansion=False, rerank=False, summarize=False):
    client = get_chroma_client()
    urls = []

    collection = client.get_collection(collection_name)

    print('DEBUG: Inizio processing')
    # Query expansion
    if expansion:
        query = query_expansion(query)
        print('DEBUG: Query expansion completata')
    embedding = query_encode(query)
    print('DEBUG: Query embedding completato')

    if collection_name == 'RAG':
        # Retrieval con/senza reranking
        documents, urls = documents_retrieval_forums(query, embedding, collection, rerank)

        # Creazione nuovo prompt con/senza summarization
        new_prompt = get_new_prompt(query, documents, collection_name, summarize)
        return new_prompt, urls

    elif collection_name == 'humanitas':
        # Retrieval con/senza reranking
        documents = documents_retrieval_humanitas(query, embedding, collection, rerank)

        # Creazione nuovo prompt senza summarization
        new_prompt = get_new_prompt(query, documents, collection_name, summarize=False)
        return new_prompt, urls

    else:
        return query, urls