[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![pt-br](https://img.shields.io/badge/lang-pt--br-green.svg)](README.pt-BR.md)

# Antropomorphic Writing

Uma ferramenta pra fazer texto parecer que foi escrito por uma pessoa. Você coloca o texto e ela traduz e reescreve até que o resultado soe natural.

A ideia é que texto gerado por IA deixa rastros. Passando por vários idiomas, esses padrões artificiais vão se perdendo pelo caminho.

## Como funciona

```
EN → Português → Chinês → Japonês → Finlandês → EN
```

| Passo | Motor | Descrição |
|:-----:|:------|:----------|
| 0 | DeepSeek | Escreve o texto original em **Português** com tom natural |
| 1 | DeepSeek | Traduz e reescreve de Português para **Chinês** |
| 2 | DeepSeek | Traduz de Chinês para **Japonês** com contexto do passo anterior |
| 3 | Google Tradutor | Traduz de Japonês para **Finlandês** |
| 4 | Niutrans / Google | Traduz de Finlandês de volta pra **Inglês** |

Cada passo vai removendo mais vestígios de IA. Por padrão, a pipeline roda em **double pass** — o texto passa pela corrente inteira duas vezes antes de voltar pro inglês. Dá pra desligar com `double_pass=False` se quiser apenas uma volta.

## Requisitos

- Python 3.10+
- Uma chave da DeepSeek (qualquer provedor compatível com OpenAI serve)

## Instalação

Crie um ambiente virtual e instale as dependências:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuração

Copie o arquivo de exemplo e insira sua chave:

```bash
cp config/config.example.toml config/config.toml
# Edite config/config.toml e defina deepseek_api_key
```

## Uso

```bash
# Pelo script
./humanize.sh "Texto pra humanizar"

# Como módulo Python
export LLM_API_KEY="sk-..."
python -m src.standard.pipeline --input "texto pra humanizar" --verbose  # double pass é padrão

# Direto no código Python
from standard.pipeline import run_standard_pipeline
import toml

config = toml.load("config/config.toml")
result = run_standard_pipeline("texto pra humanizar", config, double_pass=True)
print(result["result"])
```

## Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| `LLM_API_KEY` | Sua chave de API |
| `LLM_BASE_URL` | URL base da API (opcional) |
| `LLM_MODEL` | Nome do modelo (opcional) |

## Licença

MIT — use como quiser.
