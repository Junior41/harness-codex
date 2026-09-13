# Arquivos instalados do Harness Codex

Esta pasta contém o bootstrap, as regras do fluxo, três agentes personalizados, um diagnóstico opcional e o modelo do histórico.

## Instalação em projeto com configuração existente

Faça merge de `.codex/config.toml` em vez de sobrescrevê-lo:

1. `developer_instructions` é uma única chave de nível superior. Preserve o texto existente e acrescente, dentro da mesma string, o trecho entre `BEGIN CODEX_PORTABLE_WORKFLOW_V1` e `END CODEX_PORTABLE_WORKFLOW_V1`.
2. Se já houver `[agents]`, preserve a tabela e acrescente ou ajuste apenas `enabled = true`.
3. Não declare duas chaves `developer_instructions` nem duas tabelas `[agents]`.
4. Preserve agentes preexistentes e copie apenas `planejamento.toml`, `execucao.toml` e `validacao.toml`, resolvendo nomes conflitantes antes da cópia.

O projeto deve ser confiável. Inicie uma conversa nova após instalar ou alterar o bootstrap.

## Diagnóstico

```bash
python3 -B .codex/scripts/check_workflow.py --codex-dir .codex
```

Consulte o `README.md` da raiz do repositório do harness para modelos, níveis de raciocínio, uso, validação e limitações.
