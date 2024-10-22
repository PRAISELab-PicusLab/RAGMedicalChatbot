from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from geopy.geocoders import Nominatim
import random

def load_dataframe(spark, path):
    df = spark.read \
                        .option("inferSchema", "true") \
                        .option("header", "true") \
                        .option("multiline", "true")\
                        .option('escape', "\"") \
                        .csv(path)
    print(path, 'loaded')
    df.printSchema()
    return df


def chunking(passage, min_chunk_size=300, aggregate = True):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
        separators=[
            "\n",
            ".",
            "\uff0e",  # Fullwidth full stop
            "\u3002",  # Ideographic full stop
            " ",
        ],
        chunk_size=1000,
        chunk_overlap=0,
        length_function=len,
        is_separator_regex=False
        )
        
        text_chunks = text_splitter.split_text(passage)
        if aggregate:
            if (len(text_chunks) > 1):
                index = 0
                length = len(text_chunks)
                while index < length:
                    if len(text_chunks[index]) < min_chunk_size:
                        if 0 < index < length-1:
                            if len(text_chunks[index-1]) < len(text_chunks[index+1]):
                                text_chunks[index-1] = text_chunks[index-1] + '\n' + text_chunks[index]
                                text_chunks.pop(index)
                            else:
                                text_chunks[index] = text_chunks[index] + '\n' + text_chunks[index+1]
                                text_chunks.pop(index+1)
                            length -= 1

                        elif index == 0:
                            text_chunks[index] = text_chunks[index] + '\n' + text_chunks[index+1]
                            text_chunks.pop(index+1)
                            length -= 1
                        elif index == length-1:
                            text_chunks[index-1] = text_chunks[index-1] + '\n' + text_chunks[index]
                            text_chunks.pop(index)
                            length -= 1
                    else:
                        index += 1
        
        return text_chunks
    except:
        return []


def embed(question): 
    try:
        model = SentenceTransformer('intfloat/multilingual-e5-large', device='cuda')
        embedding = model.encode(question)#, show_progress_bar=True)
        embedding_as_np = embedding.tolist()
        return embedding_as_np
    except:
        return [0.0]


def get_coordinates(location, country):
    try:
        #loc = Nominatim(user_agent="spark_application")
        loc = Nominatim(domain='127.0.0.1:8080', scheme='http', timeout=3)
        getLoc = loc.geocode(location, country_codes=country)
        #time.sleep(1)
        return [getLoc.latitude, getLoc.longitude]
    except:
        return [0.0,0.0]
    

def map_category(category, category_mapping):
    try:
        c = category_mapping[category]
        return c
    except:
        return "MISSING"

