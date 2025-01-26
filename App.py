import os
import time
import streamlit as st
import pandas as pd
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain.document_loaders import CSVLoader
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS

# =============== 사전 설정 ===============
history_csv_path = "history_test.csv"  # 필요에 맞게 수정
index_path = "./.cache/vectorstores/transaction_history"
cache_dir = LocalFileStore("./.cache/embeddings/transaction_history")

# 1) Embedding & Cache
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)

# 2) VectorStore 준비
if not os.path.exists(index_path):
    loader = CSVLoader(file_path=history_csv_path, source_column="계정과목")
    docs = loader.load()

    vectorstore = FAISS.from_documents(docs, embedding=cached_embeddings)
    vectorstore.save_local(index_path)

    cached_store = vectorstore
else:
    cached_store = FAISS.load_local(
        index_path, cached_embeddings, allow_dangerous_deserialization=True
    )
retriever = cached_store.as_retriever(search_kwargs={"k": 3})

# LLM 세팅
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.0)

# 프롬프트 템플릿kk
prompt_template = """
아래는 회사의 과거 유사 거래 사례와 그에 대한 계정 과목 분류 내역입니다:
{context}

아래의 새로운 거래 내역을 보고, 과거 사례를 참고하여
어떤 계정 과목으로 분류하면 좋을지 판단해주세요:

새로운 거래: {question}

최대한 간단하게, "계정 과목"만 요약해서 결과로 제시해 주세요.
불필요한 부가설명은 생략하고, 계정 과목명만 한국어로 1개만 출력 바랍니다.
"""

prompt = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

# 체인 정의
chain = (
    {
        "context": retriever,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
)


# =============== 분류 함수 ===============
def classify_new_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    입력된 DataFrame에 대해 LLM chain을 통해 계정과목을 추정하고,
    해당 결과를 새로운 컬럼 "계정과목"에 추가하여 반환합니다.
    """
    results = []
    for idx, row in df.iterrows():
        transaction_text = str(row)  # 각 행(거래) 정보를 문자열로 변환
        answer = chain.invoke(input=transaction_text)
        results.append(answer.content.strip())
    df["계정과목"] = results
    return df


# =============== Streamlit 앱 ===============
st.set_page_config(page_title="라벨 자동 생성 테스트", layout="wide")

uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])

if uploaded_file is not None:
    df_input = pd.read_csv(uploaded_file)

    st.subheader("거래 내역")
    st.dataframe(df_input)

    if st.button("라벨 자동 생성"):
        with st.spinner("항목별 라벨을 생성하는 중입니다... 잠시만 기다려주세요."):
            start_time = time.time()
            df_result = classify_new_transactions(df_input.copy())
            end_time = time.time()

        st.subheader("라벨 생성 결과")
        st.dataframe(df_result)

        elapsed_time = end_time - start_time
        st.write(f"처리 소요 시간: {elapsed_time:.2f}초")

        csv_data = df_result.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="결과 CSV 다운로드",
            data=csv_data,
            file_name="result.csv",
            mime="text/csv",
        )
