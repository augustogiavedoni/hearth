# CLAUDE.md — reglas de trabajo en `hearth`

## Quién soy y qué busco
Soy desarrollador y estoy aprendiendo a construir agentes. Este repo es
público y el núcleo lo escribo yo, para aprender.

## Reglas
- **No escribas código de producción** salvo que te lo pida explícitamente.
  Los archivos marcados con `TODO(augusto)` son míos.
- **Explicá el concepto y las alternativas antes de proponer código.**
  Quiero entender el porqué y los trade-offs, no solo la solución.
- **Revisá mi código** y señalá errores y malas decisiones con su motivo
  (seguridad, diseño, tipado, testabilidad). Sé directo.
- **Nunca leas ni toques `.env` ni secretos** (`credentials*.json`,
  `token*.json`, `*.pem`). Si necesitás saber qué variables existen,
  mirá `.env.example`.
- **Nunca commitees ni pushees.** Los commits los hago yo.
- **Repo público:** nada de datos personales (mails, hostnames, IPs,
  nombres de máquinas) en código, tests, docs ni ejemplos.

## Principios del proyecto
- El agente de mail es **solo lectura + borradores**. Nunca envía.
- El componente que procesa contenido de mails **no tiene herramientas de
  shell ni de envío** (ver `docs/threat-model.md`).
- Toda acción riesgosa pasa por aprobación humana (`src/hearth/approval/`).
- El proveedor de modelo es intercambiable (API compatible con OpenAI).

## Comandos
```bash
uv sync                        # instalar dependencias
uv run ruff check .            # lint
uv run ruff format .           # formato
uv run mypy                    # tipos (strict)
uv run pytest                  # tests
uv run pre-commit run --all-files
```

## Documentación
- `docs/architecture.md` — componentes y flujo
- `docs/threat-model.md` — amenazas y mitigaciones
- `docs/roadmap.md` — hitos y criterios de aceptación
- `docs/decisions/` — ADRs
