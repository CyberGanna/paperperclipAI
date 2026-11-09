# paperperclipAI

Piattaforma AI multi-agente per lo scalping.

Documentazione architetturale: [docs/ARCHITETTURA_SCALPING_AI.md](docs/ARCHITETTURA_SCALPING_AI.md)

## MVP di simulazione

Il primo MVP è in [scalping_mvp](scalping_mvp). Esegue analisi tecnica deterministica, Risk Gate fail-closed e paper execution locale.

Avvio:

    python -m scalping_mvp.demo

Il demo non usa credenziali, API esterne o broker reali.

Progetti di riferimento integrati:

- [TradingAgents](TradingAgents/README.md)
- [Market-Swarm-Agents](Market-Swarm-Agents/README.md)
