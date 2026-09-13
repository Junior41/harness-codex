# Harness Codex

Harness portátil para organizar tarefas do Codex em três fases sequenciais:

1. **Planejamento** — entende o pedido, inspeciona o projeto e define critérios de aceitação.
2. **Execução** — implementa a mudança ou produz a resposta solicitada.
3. **Validação** — revisa o resultado de forma independente e executa verificações pertinentes.

O harness usa configuração local do Codex e agentes personalizados. Não é uma aplicação separada, não exige servidor e não armazena credenciais.

## Estrutura

```text
.codex/
├── config.toml
├── WORKFLOW.md
├── README.md
├── agents/
│   ├── planejamento.toml
│   ├── execucao.toml
│   └── validacao.toml
├── scripts/
│   └── check_workflow.py
└── templates/
    └── HISTORY.md
```

Ao ser instalado, o harness mantém o histórico do projeto em `CODEX_HISTORY.md`, fora de `.codex`.

## Requisitos

- Uma versão atual do Codex CLI, aplicativo desktop ou extensão de IDE com suporte a subagentes.
- O projeto precisa estar marcado como confiável para que o Codex carregue `.codex/config.toml`.
- A conta precisa ter acesso aos modelos configurados.
- Python 3.11 ou superior é opcional e usado apenas pelo diagnóstico local.

## Instalação

Clone este repositório e copie somente a pasta `.codex` para a raiz do projeto onde deseja usar o fluxo:

```bash
git clone URL_DO_REPOSITORIO harness-codex
cp -a harness-codex/.codex /caminho/do/seu-projeto/
```

Também é possível baixar o repositório como ZIP e copiar a pasta oculta `.codex` pelo gerenciador de arquivos.

Depois da cópia:

1. Abra a raiz do projeto no Codex.
2. Marque o projeto como confiável.
3. Inicie uma conversa nova. A configuração é descoberta no início da sessão.
4. Faça um pedido normalmente. O coordenador deve conduzir planejamento, execução e validação.

Se o projeto já possui `.codex/config.toml`, não sobrescreva o arquivo. Consulte [as instruções de merge](.codex/README.md#instalação-em-projeto-com-configuração-existente).

## Configuração padrão

| Fase | Modelo | Esforço |
| --- | --- | --- |
| Planejamento | `gpt-6-astra` | `ultra` |
| Execução | `gpt-5.6-terra` | `high` |
| Validação | `gpt-6-astra` | `high` |

Edite os arquivos em `.codex/agents/` para trocar o modelo ou o esforço. Por exemplo:

```toml
model = "gpt-5.6-sol"
model_reasoning_effort = "high"
```

Inicie uma conversa nova depois de alterar configurações carregadas no início da sessão.

## Modelos que podem ser usados

Os modelos recomendados atualmente para Codex são:

| Modelo | Identificador | Uso típico |
| --- | --- | --- |
| Astra | `gpt-6-astra` | Fluxos complexos de ponta a ponta, planejamento profundo e decisões difíceis. |
| 5.6 Sol | `gpt-5.6-sol` | Trabalho complexo, aberto e que exige profundidade ou acabamento. |
| 5.6 Terra | `gpt-5.6-terra` | Trabalho cotidiano, implementação e análise com bom equilíbrio entre capacidade e custo. |
| 5.6 Luna | `gpt-5.6-luna` | Tarefas rápidas, claras, repetíveis ou de grande volume. |

Outros modelos compatíveis com o cliente podem funcionar, como `gpt-5.5` ou modelos fornecidos por outro provedor. Modelos disponíveis variam conforme plano, rollout, autenticação, cliente e provedor. Confirme a disponibilidade no seletor do Codex ou no catálogo local antes de fixar um identificador.

Referências: [modelos do Codex](https://learn.chatgpt.com/docs/models) e [subagentes](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## Níveis de raciocínio

Use `model_reasoning_effort` no TOML do agente:

| Valor | Quando usar |
| --- | --- |
| `low` | Tarefa simples e bem delimitada, com prioridade para velocidade. |
| `medium` | Equilíbrio entre velocidade e profundidade; bom padrão geral. |
| `high` | Lógica complexa, casos extremos, implementação ou revisão cuidadosa. |
| `xhigh` | Problemas especialmente difíceis que justificam mais tempo e tokens. |
| `max` | Profundidade máxima em uma tarefa muito difícil, quando suportado. |
| `ultra` | Raciocínio profundo e delegação proativa, quando disponível para a conta e o modelo. |

Na interface, `low` pode aparecer como **Light** e `xhigh` como **Extra High**. Nem todo modelo oferece todos os níveis. Um esforço maior normalmente aumenta latência e consumo de tokens.

Configurações alternativas úteis:

```text
Mais econômico: Terra/medium nas três fases
Equilibrado:     Sol/high → Terra/high → Sol/high
Mais profundo:   Astra/ultra → Sol/high → Astra/high
Mais rápido:     Terra/medium → Luna/medium → Terra/high
```

Valide cada combinação na conta que executará o harness. O script local consegue comparar os perfis com um cache de modelos, mas um cache não prova acesso em runtime.

## Como usar

Depois de instalar e iniciar uma conversa nova, basta pedir uma tarefa:

```text
Implemente validação de e-mail no formulário de cadastro e execute os testes relacionados.
```

O chat deve mostrar eventos das três fases. Em clientes interativos, use `/agent` para visualizar as threads dos subagentes.

Para continuar uma tarefa interrompida, peça para continuar. O fluxo usa o estado conhecido e o histórico, sem recomeçar deliberadamente todas as fases.

## Verificação

### 1. Verificação estrutural

Na raiz do projeto que recebeu `.codex`:

```bash
python3 -B .codex/scripts/check_workflow.py --codex-dir .codex
```

Se existir um catálogo local do Codex:

```bash
python3 -B .codex/scripts/check_workflow.py \
  --codex-dir .codex \
  --models-cache "$HOME/.codex/models_cache.json"
```

O resultado `"ok": true` confirma a estrutura e, quando fornecido, a presença das combinações no catálogo. `"execution_verified": false` é esperado: essa inspeção não chama modelos.

### 2. Verificação de carregamento

Em uma sessão nova, peça:

```text
Informe quais instruções de projeto e agentes personalizados foram carregados, sem executar alterações.
```

O Codex deve identificar o fluxo e os agentes. Se não identificar, confira se o projeto está confiável, se `.codex` está na raiz correta e se a sessão foi iniciada depois da instalação.

### 3. Verificação comportamental

Faça uma mudança pequena e reproduzível. Confirme que:

- planejamento, execução e validação aparecem no chat;
- os subagentes aparecem na atividade ou em `/agent`;
- a execução altera somente os arquivos esperados;
- a validação relata evidências reais;
- `CODEX_HISTORY.md` registra mudanças, testes e pendências sem apagar entradas anteriores.

Esse é o teste que demonstra o fluxo completo. A inspeção estrutural, sozinha, não comprova obediência do modelo.

## Limitações

- A coordenação é orientada por instruções, não por um controlador determinístico.
- Instruções de sistema, permissões, modo de colaboração e disponibilidade de modelos têm precedência.
- Cada subagente consome tokens próprios; aplicar três fases a pedidos muito simples pode custar mais do que uma execução única.
- O modelo principal continua sendo o escolhido pelo usuário; os TOMLs configuram os agentes iniciados pelo fluxo.
- O harness não copia nem modifica autenticação, configuração pessoal ou credenciais.

## Desinstalação

Se `.codex` era exclusivo deste harness, remova a pasta e inicie uma conversa nova. Se o projeto já tinha configuração própria, remova apenas o trecho delimitado por `BEGIN CODEX_PORTABLE_WORKFLOW_V1` e `END CODEX_PORTABLE_WORKFLOW_V1`, além dos três agentes do harness.

O `CODEX_HISTORY.md` pertence ao projeto e pode ser preservado.
