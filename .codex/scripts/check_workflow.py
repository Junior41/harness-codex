#!/usr/bin/env python3
"""Inspeciona o harness sem alterar arquivos nem iniciar solicitações a modelos."""

import argparse
import json
from pathlib import Path
import sys
import tomllib


STAGES = ("planejamento", "execucao", "validacao")
REQUIRED = ("name", "description", "developer_instructions", "model", "model_reasoning_effort")


def read_toml(path):
    with path.open("rb") as source:
        return tomllib.load(source)


def inspect(codex_dir, models_cache=None):
    """Retorna a configuração solicitada e os erros sem alegar execução."""
    errors = []
    result = {
        "codex_dir": str(codex_dir.resolve()),
        "stages": [],
        "catalog_checked": False,
    }

    try:
        config = read_toml(codex_dir / "config.toml")
        instructions = config.get("developer_instructions", "")
        if not isinstance(instructions, str) or "CODEX_PORTABLE_WORKFLOW_V1" not in instructions:
            errors.append("Bootstrap CODEX_PORTABLE_WORKFLOW_V1 ausente em developer_instructions.")
        agents = config.get("agents", {})
        if not isinstance(agents, dict) or agents.get("enabled") is not True:
            errors.append("A configuração [agents] enabled = true é necessária para este fluxo.")
    except (OSError, ValueError) as exc:
        errors.append(f"config.toml: {exc}")

    catalog = None
    if models_cache is not None:
        try:
            data = json.loads(models_cache.read_text(encoding="utf-8"))
            models = data.get("models") if isinstance(data, dict) else data
            if not isinstance(models, list) or not models:
                raise ValueError("catálogo sem lista de modelos")
            catalog = {}
            for model in models:
                if not isinstance(model, dict) or not isinstance(model.get("slug"), str):
                    raise ValueError("entrada de modelo sem slug")
                levels = model.get("supported_reasoning_levels")
                if not isinstance(levels, list):
                    raise ValueError(f"níveis de raciocínio ausentes para {model['slug']}")
                if any(
                    not isinstance(level, dict) or not isinstance(level.get("effort"), str)
                    for level in levels
                ):
                    raise ValueError(f"níveis de raciocínio inválidos para {model['slug']}")
                catalog[model["slug"]] = {level["effort"] for level in levels}
            result["catalog_checked"] = True
        except (OSError, ValueError) as exc:
            errors.append(f"Catálogo: {exc}")

    names = set()
    for stage in STAGES:
        try:
            profile = read_toml(codex_dir / "agents" / f"{stage}.toml")
            missing = [
                key
                for key in REQUIRED
                if not isinstance(profile.get(key), str) or not profile[key].strip()
            ]
            if missing:
                errors.append(
                    f"{stage}: campos textuais obrigatórios inválidos: {', '.join(missing)}."
                )
                continue
            if profile["name"] in names:
                errors.append(f"{stage}: nome de agente duplicado: {profile['name']}.")
            names.add(profile["name"])
            model = profile["model"]
            effort = profile["model_reasoning_effort"]
            result["stages"].append(
                {
                    "stage": stage,
                    "name": profile["name"],
                    "model_requested": model,
                    "reasoning_requested": effort,
                }
            )
            if catalog is not None:
                if model not in catalog:
                    errors.append(
                        f"{stage}: {model!r} não consta no catálogo consultado; "
                        "atualize ou confira o catálogo antes de delegar."
                    )
                elif effort not in catalog[model]:
                    available = ", ".join(sorted(catalog[model]))
                    errors.append(
                        f"{stage}: raciocínio {effort!r} não anunciado para {model}; "
                        f"disponíveis: {available}."
                    )
        except (OSError, ValueError) as exc:
            errors.append(f"{stage}: {exc}")

    for relative in ("WORKFLOW.md", "README.md", "templates/HISTORY.md"):
        try:
            if not (codex_dir / relative).read_text(encoding="utf-8").strip():
                errors.append(f"Arquivo vazio: {relative}.")
        except (OSError, ValueError) as exc:
            errors.append(f"{relative}: {exc}")

    result["errors"] = errors
    result["ok"] = not errors
    result["execution_verified"] = False
    result["note"] = (
        "Inspeção local; não comprova carregamento no chat, acesso atual à conta "
        "ou execução das etapas."
    )
    if models_cache is None:
        result["note"] += " Compatibilidade de modelos não verificada: forneça --models-cache."
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--codex-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--models-cache",
        type=Path,
        help="Catálogo local do Codex (models_cache.json); somente leitura.",
    )
    args = parser.parse_args()
    result = inspect(args.codex_dir, args.models_cache)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
