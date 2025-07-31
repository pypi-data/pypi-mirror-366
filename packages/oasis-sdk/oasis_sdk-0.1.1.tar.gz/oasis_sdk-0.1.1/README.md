# OASIS-SDK

## 1. Concept

OASIS-LLM-PROXY-CLIENT는 OpenAI, Azure OpenAI 등 다양한 LLM Provider의 공식 SDK 및 LangChain을 얇게 wrapping하여, 사내 규칙에 맞는 필드 입력과 프록시 서버를 통한 키 주입을 지원하는 Python 라이브러리입니다. 원본 라이브러리의 모든 기능을 그대로 사용할 수 있도록 설계되어, 기존 SDK와 LangChain의 확장성과 호환성을 최대한 보장합니다.

## 2. Usage

### 2.1 install

```
pip install oasis-sdk
```

### 2.2 example

**client parameters**

[required]

- user_id: 사용자의 id
- workspace_code: 사용자의 workspace code
- tenant_code: 사용자의 tenant code
- proxy_url: Llm Proxy Server

[optional]

- user_ip: 사용자의 ip (defualt=127.0.0.1)
- plugin_name: 호출한 시스템 명 (ex, chatbot, mcp1, rag-mcp, ..., default=default-plugin)

[auto]

- root_id: 클라이언트 생성시 발급
- req_id: 요청시마다 발급

📍 **주의**

- 1번의 연속적인 수행에서 root_id는 고정되어야 함
- 연계되는 시스템에서는 클라이언트 생성시 초기 발급된 root_id를 주입하여 사용

#### 2.2.1 SDK

**1. openai**

```python
# 동기 클라이언트
client = OasisOpenAI(
    user_id="user_id",
    workspace_code="workspace_code",
    tenant_code="tenant_code",
    proxy_url="llm_proxy_server",
    user_ip="user_ip",
    plugin_name="your_system"
)

# 동기 호출
resp = client.chat.completions.create(
    model="model",
    messages=[{"role": "user", "content": "안녕?"}],
)

# 동기 스트림
stream = client.chat.completions.create(
    model="model",
    messages=[{"role": "user", "content": "안녕?"}],
    stream=True,
)

# 동기 임베딩
emb = client.embeddings.create(
    model="embedding_model",
    input="임베딩 테스트 문장",
)

# 비동기 클라이언트
aync_client = OasisAsyncOpenAI(
    user_id="user_id",
    workspace_code="workspace_code",
    tenant_code="tenant_code",
    proxy_url="llm_proxy_server",
    user_ip="user_ip",
    plugin_name="your_system"
)

# 비동기 호출
resp = await aync_client.chat.completions.create(
    model="model",
    messages=[{"role": "user", "content": "안녕?"}],
)

# 비동기 스트림
stream = await aync_client.chat.completions.create(
    model="model",
    messages=[{"role": "user", "content": "안녕?"}],
    stream=True,
)

# 비동기 임베딩
emb = await async_client.embeddings.create(
    model="embedding_model",
    input=["첫 문장", "둘째 문장"],
)
```

**2. azure openai**

```python
# 동기 클라이언트
client = OasisAzureOpenAI(
    user_id="user_id",
    workspace_code="workspace_code",
    tenant_code="tenant_code",
    proxy_url="llm_proxy_server",
    user_ip="user_ip",
    plugin_name="your_system",
    api_version="your_api_version"
)

# 동기 호출
resp = client.chat.completions.create(
    model="deployment",
    messages=[{"role": "user", "content": "안녕?"}],
)

# 동기 스트림
stream = client.chat.completions.create(
    model="deployment",
    messages=[{"role": "user", "content": "안녕?"}],
    stream=True,
)

# 동기 임베딩
emb = client.embeddings.create(
    model="embedding_deployment",
    input="Azure 임베딩 예시",
)

# 비동기 클라이언트
aync_client = OasisAsyncAzureOpenAI(
    user_id="user_id",
    workspace_code="workspace_code",
    tenant_code="tenant_code",
    proxy_url="llm_proxy_server",
    user_ip="user_ip",
    plugin_name="your_system",
    api_version="your_api_version"
)

# 비동기 호출
resp = await aync_client.chat.completions.create(
    model="deployment",
    messages=[{"role": "user", "content": "안녕?"}],
)

# 비동기 스트림
stream = await aync_client.chat.completions.create(
    model="deployment",
    messages=[{"role": "user", "content": "안녕?"}],
    stream=True,
)

# 비동기 임베딩
emb = await aclient.embeddings.create(
    model="embedding_deployment",
    input=["A 문장", "B 문장"],
)
```

#### 2.2.2 Langchain

- 기존 패키지와 동일하게 설계하였기 때문에 langchain은 클라이언트 생성시 모델도 같이 지정 필요

**1. openai**

```python
# chat
llm = OasisChatOpenAI(
    user_id="user_id",
    workspace_code="workspace_code",
    tenant_code="tenant_code",
    model="model"
    proxy_url="llm_proxy_server",
    user_ip="user_ip",
    plugin_name="your_system"
)

# 동기 호출
resp = llm.invoke("안녕 Azure LangChain!")

# 비동기 호출
resp = await llm.ainvoke("안녕 Azure LangChain!")

# 동기 스트림
resp = llm.stream("안녕 Azure LangChain!")

# 비동기 스트림
resp = await llm.astream("안녕 Azure LangChain!")

# embedding
embed = OasisOpenAIEmbedding(
    user_id="user_id",
    workspace_code="workspace_code",
    tenant_code="tenant_code",
    model="embed_model"
    proxy_url="llm_proxy_server",
    user_ip="user_ip",
    plugin_name="your_system"
)

# 동기 임베딩
vecs = embed.embed_documents(["LC 임베딩 테스트"])

# 비동기 임베딩
vecs = await embed.aembed_documents(["LC async 임베딩"])
```

**2. azure openai**

```python
# chat
llm = OasisAzureChatOpenAI(
    user_id="user_id",
    workspace_code="workspace_code",
    tenant_code="tenant_code",
    proxy_url="llm_proxy_server",
    model="deployment"
    api_version="your_api_version"
    user_ip="user_ip",
    plugin_name="your_system"
)

# 동기 호출
resp = llm.invoke("안녕 Azure LangChain!")

# 비동기 호출
resp = await llm.ainvoke("안녕 Azure LangChain!")

# 동기 스트림
resp = llm.stream("안녕 Azure LangChain!")

# 비동기 스트림
resp = await llm.astream("안녕 Azure LangChain!")

# embedding
embed = OasisAzureEmbedding(
    user_id="user_id",
    workspace_code="workspace_code",
    tenant_code="tenant_code",
    proxy_url="llm_proxy_server",
    model="deployment"
    api_version="your_api_version"
    user_ip="user_ip",
    plugin_name="your_system"
)

# 동기 임베딩
vecs = embed.embed_documents(["LC 임베딩 테스트"])

# 비동기 임베딩
vecs = await embed.aembed_documents(["LC async 임베딩"])
```

## 3. Dependency

- python 3.11.x
- openai 1.97.0
- langchain-openai 0.3.28
