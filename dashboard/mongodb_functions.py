import streamlit as st

from pymongo.mongo_client import MongoClient
from pprint import pprint


uri = "mongodb://localhost:27017/medical_app"

@st.cache_resource
def get_mongo_client():
    client = MongoClient(uri)
    try:
        client.admin.command('ping')
    except Exception as e:
        print(e)
    return client

@st.cache_resource
def get_analytics_collection():
    db_name = 'medical_app'
    collection_name = 'analytics'
    db = client[db_name]
    collection = db[collection_name]
    return collection

@st.cache_resource
def get_doctors_collection():
    db_name = 'medical_app'
    collection_name = 'doctors'
    db = client[db_name]
    collection = db[collection_name]
    return collection

client = get_mongo_client()
doctors_collection = get_doctors_collection()
analytics_collection = get_analytics_collection()


## DOCTORS
@st.cache_data
def get_distinct_locations():
    pipeline = [{
            '$group': {
                '_id': "$location",
                'Count': { '$sum': 1 }
                }
            },
            {
                '$project': {
                    "_id": 0,
                    "location": "$_id",
                    'Count': 1
                }
            }]
    location = doctors_collection.aggregate(pipeline)
    return list(location)

@st.cache_data
def get_distinct_specializations():
    specialization = doctors_collection.find({}).distinct("specialization")
    return list(specialization)

@st.cache_data
def get_doctors_count():
    pipeline = [
        {
            '$match': {
                'specialization': {
                    '$ne': None
                }
            }
        },
        {
            '$group': {
                '_id': "$specialization",
                'Count': { '$sum': 1 }
            }
        },
        {
            '$sort': { 'count': 1 }
        },
        {
            '$project': {
                "_id": 0,
                "Specialization": "$_id",
                'Count': 1
            }
        }
    ]
    dizionario = {"Specialization": [], "Count": []}
    result = list(doctors_collection.aggregate(pipeline))
    for element in result:
        dizionario['Specialization'].append(element['Specialization'])
        dizionario['Count'].append(element['Count'])
    return dizionario

@st.cache_data
def get_doctors_ranked(category):

    pipeline = [
        {
            '$match':
            {
                "$and" : [{"specialization": category}]
            } 
        },
        {
            '$addFields':
            {
                'score':
                {
                    '$multiply':[
                            { '$toInt': "$n_likes" }, {'$toInt': "$ranking"}
                        ]
                }
            }
        },
        {
            '$sort':
            {
                'score': -1
            }
        },
        {
            '$project': {
                '_id': 1,
                'name': 1,
                'location': 1,
                'specialization': 1,
                'n_replies': 1,
                'n_likes': 1,
                'ranking': 1,
                #'score': 1
                'picture': 1,
                'coordinates': 1
            }
        }
    ]
    result = doctors_collection.aggregate(pipeline)
    return list(result)


@st.cache_data
def get_doctors_coordinates(category):
    if(category == 'Tutte'):
        condition = [{"_id": { "$ne": None }}, {"coordinates": { "$ne": None }}]
    else:
        condition = [{"_id": { "$ne": None }},{"specialization": category}, {"coordinates": { "$ne": None }}]
        
    pipeline = [
        {
            '$match':
            {
                "$and" : condition
            } 
        },
        {
            '$project': {
                '_id': 1,
                'name': 1,
                'specialization': 1,
                'location': 1,
                #'score': 1
                'coordinates': 1
            }
        }
    ]
    result = doctors_collection.aggregate(pipeline)
    return list(result)




# ANALYTICS

@st.cache_data
def get_size_of_collection(source):
    if(source != 'Tutte'): 
        num = analytics_collection.count_documents({ "_id": { "$regex": source + '.it', "$options": "i" } })
    else:
        num = analytics_collection.count_documents({})
    return num


@st.cache_data
def get_distinct_categories():
    categories = analytics_collection.find({}).distinct("Category")
    return list(categories)

@st.cache_data
def get_avg_response_time(source):

    match = {
                "$and": [
                    {"Question Date": { "$ne": None }},
                    {"Answer Date": { "$ne": None }}
                ]
            }
    
    if source != 'Tutte':
        match = {
                    "$and": [
                        {"Question Date": { "$ne": None }},
                        {"Answer Date": { "$ne": None }},
                        { "_id": { "$regex": source + '.it', "$options": "i" } }
                    ]
                }

    avg_response_time = [
        {
            "$match": match
        },
        {
            "$addFields": {
                "Response Time (ms)": {
                    "$subtract": ["$Answer Date", "$Question Date"]
                }
            }
        },
        {
            "$group": {
                "_id": "$Category",
                "averageResponseTime": {
                    "$avg": "$Response Time (ms)"
                }
            }
        },
        {
            "$sort": {
                "averageResponseTime": 1
            }
        },
        {
            "$project": {
                "_id": 0,
                "Category": "$_id",
                "averageResponseTime": {
                    "$divide": ["$averageResponseTime", 3600000], # da ms in ore
                }
            }
        }
    ]
    dizionario = {'Categories': [], 'responseTimes': []}
    result = list(analytics_collection.aggregate(avg_response_time))
    for element in result:
        dizionario['Categories'].append(element['Category'])
        dizionario['responseTimes'].append(element['averageResponseTime'])
    return dizionario

@st.cache_data
def get_num_documents_by_category(source):
    match = {
            "_id": { "$ne": None }
            }
    
    if source != 'Tutte':
        match = {
                    "_id": { "$regex": source + '.it', "$options": "i" } 
                }
        
    pipeline = [
                {
                    "$match": match
                },
                {
                    "$group": {
                        "_id": "$Category",
                        "count": { "$sum": 1 }
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "URL": 1,
                        "Category": "$_id",
                        "count": 1
                    }
                }
            ]
    dizionario = {'Categories': [], 'Counts': []}
    result = list(analytics_collection.aggregate(pipeline))
    for element in result:
        dizionario['Categories'].append(element['Category'])
        dizionario['Counts'].append(element['count'])
    return dizionario

@st.cache_data
def get_category_minmax_dates(category):
    pipeline = [
        {
            "$match": {
                "Category": category
            }
        }, 
        {
            "$group": {
                "_id": None,
                "minYear": {"$min": { "$year": { "$toDate": "$Question Date" } }},
                "maxYear": {"$max": { "$year": { "$toDate": "$Question Date" } }}
            }
        }
    ]
    result = list(analytics_collection.aggregate(pipeline))[0]
    minYear = result['minYear']
    maxYear = result['maxYear']
    return minYear, maxYear

@st.cache_data
def get_category_questions_trend(category,source):

    # get min and max year for the given category
    minYear, maxYear = get_category_minmax_dates(category)

    all_months = []
    for year in range(minYear, maxYear + 1):
        for month in range(1, 13):
            all_months.append({"year": year, "month": month})

    match = {
                "Category": category
            }
    
    if source != 'Tutte':
        match = {   
                    "$and": [
                        {"Category": category},
                        {"_id": { "$regex": source + '.it', "$options": "i" }}]
                }

    pipeline = [
        {
            "$match": match
        },
        {
            "$group": {
                "_id": {
                    "year": { "$year": { "$toDate": "$Question Date" } },
                    "month": { "$month": { "$toDate": "$Question Date" } }
                },
                "count": { "$sum": 1 }
            }
        },
        {
            "$project": {
                "_id": 0,
                "year": "$_id.year",
                "month": "$_id.month",
                "count": 1
            }
        }
    ]
    data_result = list(analytics_collection.aggregate(pipeline))

    data_dict = {(doc["year"], doc["month"]): doc["count"] for doc in data_result}
    final_result = []
    for month in all_months:
        year_month = (month["year"], month["month"])
        count = data_dict.get(year_month, 0)
        final_result.append({"year": month["year"], "month": month["month"], "count": count})
    final_result.sort(key=lambda x: (x["year"], x["month"]))
    return final_result

