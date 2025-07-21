from SPARQLWrapper import JSON, SPARQLWrapper
from multiprocessing import Process, Queue

import re

def replace_comma_in_res(text):
    def replace_match(match):
        return match.group(1) + match.group(2).replace(',', '\\,')

    pattern = r'(res:)([^,\s]*(?:,[^,\s]*)*)'
    return re.sub(pattern, replace_match, text)

def execute_one_query(query, endpoint):
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(10 * 60)
    results = sparql.query().convert()
    return results["results"]["bindings"]


def execute_query(question, endpoint, sparql_key_name, limit_number, prefix):
    try:
        # 特定の質問からSPARQLクエリを取得
        sparql = SPARQLWrapper(endpoint) 

        query_text = prefix + question[sparql_key_name]

        query_text = query_text.replace("LIMIT", "#LIMIT")
        if limit_number >= 1:
            query_text = query_text + "\nLIMIT " + str(limit_number)

        query_text = replace_comma_in_res(query_text)

        # コメントを削除
        query_text = re.sub(r'(?m)^#.*$', '', query_text)

        sparql.setQuery(query_text)
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(10 * 60)
        results = sparql.query().convert()

       
        return results["results"]["bindings"], question["id"]
    except Exception as e:
        print(f"Execute Error: {e}")
        print(question["id"])
        return [], question


def execute_query_for_error(question, endpoint, sparql_key_name, limit_number, prefix):
    timeout_seconds = 600  # タイムアウト時間を設定
    try:
        # SPARQLクエリを準備
        sparql = SPARQLWrapper(endpoint)

        query_text = prefix + question[sparql_key_name]

        query_text = query_text.replace("LIMIT", "#LIMIT")
        if limit_number >= 1:
            query_text += "\nLIMIT " + str(limit_number)

        query_text = replace_comma_in_res(query_text)

        # コメントを削除
        query_text = re.sub(r'(?m)^#.*$', '', query_text)

        sparql.setQuery(query_text)
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(10 * 60)

        results = sparql.query().convert()
        return "no error"
    except Exception as e:
        # エラー内容を返す
        return str(e)
