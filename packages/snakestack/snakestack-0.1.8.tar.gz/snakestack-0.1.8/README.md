# 🐍 SnakeStack

![Python](https://img.shields.io/badge/python-^3.13-blue)
![Poetry](https://img.shields.io/badge/poetry-2.1.3+-blueviolet)
![Pipeline](https://github.com/BrunoSegato/snakestack/actions/workflows/ci.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/snakestack.svg)](https://pypi.org/project/snakestack/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Uma coleção de utilitários para acelerar o desenvolvimento backend em Python com padrões reutilizáveis e produtivos.

---

## 🎓 Visão Geral

O SnakeStack é uma biblioteca modular que fornece recursos para estruturar projetos Python com boas práticas, extensibilidade e produtividade. Seu primeiro módulo disponibiliza uma stack de **logging configurável e extensível**, ideal para projetos FastAPI, Flask ou scripts.

---

## 🚀 Principais Recursos (v0.1.0)

* Configuração declarativa de `logging` com suporte a `dictConfig`
* Classe `LoggerConfigurator` para aplicação e customização dinâmica
* `JsonFormatter` pronto para produção (com `request_id`, `trace_id`, etc.)
* Suporte a filtros customizados com `ContextVars`
* Extensibilidade: adicione formatters, handlers ou filters personalizados

---

## 👀 Exemplo Rápido

```python
import logging
from snakestack.logging import LoggerConfigurator

configurator = LoggerConfigurator()
configurator.apply()

logger = logging.getLogger("my.module")
logger.info("Logging simples funcionando.")
```

---

## 🔧 Instalação

### Padrão:

```bash
pip install snakestack
```

Isso instala a lib com suporte a Redis assíncrono (redis>=4.2.0).
```bash
pip install snakestack[redis]
```

### Via Poetry:

```bash
poetry add snakestack
```

---

## 🌐 Roadmap

| Versão | Feature                                       |
| ------ |-----------------------------------------------|
| 0.1.0  | Stack de logging configurável                 |
| 0.2.0  | Decoradores de cache                          |
| 0.3.0  | Consumer com Pull                             |
| 0.4.0  | Consumer com Streaming Pull                   |
| 0.5.0  | Middleware e instrumentação com OpenTelemetry |
| 0.6.0  | Handler para exceções padronizadas            |
| 0.7.0  | Publisher para Google Pub/Sub                 |
| 0.8.0  | Decoradores de Circuit Break                  |

---

## 📚 Como contribuir

1. Faça fork do projeto
2. Crie uma branch: `git checkout -b minha-feature`
3. Instale dependências com `poetry install --with dev`
4. Rode os testes: `make test`
5. Crie um PR ✨

---

## 🪜 Testes e Qualidade

```bash
make check     # mypy + ruff
make test      # pytest
make test-ci   # cobertura
```

---

## ✅ Licença

Este projeto é licenciado sob os termos da licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
