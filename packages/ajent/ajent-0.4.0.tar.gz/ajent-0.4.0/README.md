# Ajent

**ajent** é uma biblioteca open source para implementar agentes de IA em JavaScript, com suporte a comunicação com modelos de linguagem (LLMs) através de uma API centralizada. O objetivo do projeto é facilitar a integração de LLMs em aplicações frontend e backend, suportando ferramentas customizadas (tools) e serialização de respostas.

---

## 📚 Funcionalidades

- Suporte para múltiplos provedores de LLMs (atualmente OpenAI).
- Envio de mensagens com ferramentas customizadas (tools).
- Serialização robusta de respostas em formato JSON.
- Estrutura modular e extensível para suporte a outros provedores de LLMs no futuro.

---

## 🚀 Começando

### Requisitos

- Python 3.8 ou superior.
- Biblioteca `openai` instalada (para integração com OpenAI).

### Instalação

Para utilizar essa biblioteca é necessário um pip install.
```bash
pip install ajent
```

## 🛠️ Como Usar
### Configurando um cliente LLM  
Use a classe LLMFactory para criar o cliente LLM com base no provedor escolhido.   
O nome do LLM (e.g., "openai") e o token de autenticação (opcional) devem ser fornecidos.

``` python
from ajent import LLMFactory

llm_name = "openai"
llm_token = "sua-chave-de-api"
llm_client = LLMFactory.create_client(llm_name, llm_token)
response = llm_client.send(messages, tools, model="gpt-4o-mini")
```