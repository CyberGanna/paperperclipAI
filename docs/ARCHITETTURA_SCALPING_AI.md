# Piattaforma AI multi-agente per lo scalping

## Decisione architetturale

Il progetto è fattibile come piattaforma di ricerca, simulazione e paper trading. Lo scalping a bassa latenza richiede una separazione netta: i modelli AI possono occuparsi di ricerca, notizie, classificazione del regime, confronto tra ipotesi e spiegazioni; dati, indicatori, rischio, idempotenza, invio ordini e arresto devono essere deterministici.

L'implementazione procede per livelli: analisi senza ordini, paper trading con costi e slippage, operatività supervisionata e infine automazione limitata. L'MVP produce segnali riproducibili, motivazioni, controlli di rischio e simulazioni. Non deve collegarsi a un conto reale.

## Architettura

Componenti principali:

- Market Data Gateway per tick, order book, candele e volumi.
- Normalizer e Data Quality per timestamp, duplicati, buchi, ritardi e dati fuori sequenza.
- Feature Engine per VWAP, RSI, MACD, ATR, volatilità, spread, volume profile, CVD e microstruttura.
- Regime Classifier per trend, range, alta volatilità, bassa liquidità ed eventi.
- Agent Runtime per eseguire agenti con input e output strutturati.
- Orchestrator per coordinare il ciclo e creare proposte.
- Policy e Risk Gate deterministico, obbligatorio e fail-closed.
- Paper Execution Engine per fill parziali, commissioni, latenza e slippage.
- Broker Adapter isolato per Interactive Brokers e broker futuri.
- Portfolio, Position Service e Performance Analyst.
- Audit Ledger append-only per dati, versioni, output, controlli e fill.
- API FastAPI, dashboard React/Next.js e osservabilità.

Nessun agente linguistico può chiamare direttamente un broker. Solo l'Execution Service può inviare un ordine, dopo un RiskApprovedOrder emesso dal Policy Gate. L'Orchestrator non può modificare un rifiuto.

## Agenti, input, output e permessi

| Agente | Input | Output | Permessi |
|---|---|---|---|
| Market Scanner | prezzi, spread, volumi, liquidità, volatilità | strumenti candidati, confidenza, scadenza | sola lettura |
| News & Sentiment Analyst | notizie, calendario, fonti autorizzate | eventi, sentiment, impatto e scadenza | sola lettura |
| Technical Analysis | candele, order book, feature | segnali, livelli e invalidazione | sola lettura |
| Strategy Engine | segnali, regime e storico | setup con entry, stop, target e motivazione | sola lettura |
| Risk Manager | proposta, portafoglio e limiti | APPROVE, REJECT o REDUCE con motivazione | può bloccare |
| Execution Agent | ordini già approvati | stato ordine e fill | solo gateway |
| Performance Analyst | fill, PnL, costi, drawdown | metriche e report | sola lettura |
| Orchestrator | risultati e stato sessione | proposta e transizioni | non può elevare permessi |

Ogni output deve essere un contratto Pydantic/JSON versionato con timestamp, confidenza, dati usati, versione del modello e condizioni di invalidazione.

## Flusso operativo

1. Ingestione di un aggiornamento di mercato.
2. Normalizzazione, controllo qualità e verifica anti look-ahead.
3. Calcolo delle feature.
4. Scanner, analisi tecnica, news e regime in parallelo.
5. Strategy Engine crea una proposta oppure NO_TRADE.
6. Orchestrator crea TradeProposal con correlation_id e scadenza.
7. Policy Gate verifica sessione, spread, liquidità, esposizione, perdita giornaliera, rischio, duplicati, latenza e slippage.
8. Se un controllo fallisce, il ciclo termina come RISK_REJECTED e viene registrato.
9. In Fase 1/2 si usa il Paper Execution Engine.
10. In Fase 3 è richiesta conferma umana.
11. Solo in Fase 4 un Broker Adapter può operare entro limiti predefiniti.
12. Performance Analyst aggiorna PnL, costi e qualità dell'esecuzione.

Stati minimi: CANDIDATE, ANALYZING, PROPOSED, RISK_REJECTED, AWAITING_APPROVAL, PAPER_SUBMITTED, FILLED, PARTIALLY_FILLED, CLOSED, CANCELLED, ERROR.

## Controlli di rischio

Perdita massima giornaliera e settimanale, rischio per trade, esposizione per strumento e portafoglio, limite ordini, spread e slippage massimi, controllo liquidità, stop protettivo, timeout, blocco dopo errori o perdita connessione, idempotency key, doppia verifica, kill switch e audit completo.

Le credenziali devono stare in un secret manager o in variabili d'ambiente escluse dal repository. Nessuna chiave API o wallet private key deve essere committata.

## Tecnologie consigliate

Python 3.12, Pydantic v2, FastAPI, PostgreSQL/TimescaleDB, Redis Streams o NATS JetStream, Polars/pandas, NumPy, ta-lib, vectorbt o Backtrader, LangGraph o un orchestratore equivalente, Interactive Brokers Gateway/TWS in adapter isolato, React/Next.js, WebSocket/SSE, OpenTelemetry, Prometheus, Grafana e Docker Compose.

TradingAgents è un riferimento per analisti, ricerca, dibattito e gestione del portafoglio. Market-Swarm-Agents è un riferimento per strategie, agenti specializzati e backtesting. I due moduli restano isolati finché dipendenze, licenze e costi sono verificati.

## Roadmap

### Fase 0 — Fondazioni

Definire mercati, timeframe, sorgenti dati, sessioni, limiti, eventi, contratti e criteri di successo.

### Fase 1 — MVP di analisi

Implementare Scanner, Technical Analysis, Strategy Engine, Risk Manager, Orchestrator e dashboard read-only. Nessun ordine.

### Fase 2 — Paper trading

Aggiungere simulazione realistica, commissioni, slippage, latenza, fill, stop, audit e report.

### Fase 3 — Supervisione umana

Aggiungere login, ruoli, approvazione manuale, sessioni e Interactive Brokers in modalità paper.

### Fase 4 — Automazione controllata

Abilitare singoli strumenti e strategie con limiti stretti, canary release, shadow mode e arresto automatico.

### Fase 5 — Estensione

Aggiungere broker, mercati e agenti mantenendo compatibilità degli schemi, audit e rollback.

## Criteri di accettazione dell'MVP

- Segnali riproducibili dai dati e dalla configurazione salvati.
- Nessun agente invia ordini direttamente.
- Ogni proposta contiene stop, target, size e motivazione.
- Un rifiuto del Risk Gate è definitivo per quel ciclo.
- Il paper engine applica costi, slippage e latenza.
- Il kill switch impedisce nuovi ordini.
- Dashboard e audit mostrano il percorso completo.
- Verifiche su idempotenza, dati mancanti, riconnessione e look-ahead bias.
- Nessun segreto nel repository.

## Chiarimenti necessari

1. Mercati: azioni, futures, forex, crypto o più asset.
2. Strumenti e timeframe del primo MVP.
3. Sorgente dati e budget mensile.
4. Interactive Brokers come primo broker.
5. Modalità iniziale: analisi, paper trading o conferma manuale.
6. Perdita massima, rischio per trade ed esposizione.
7. Modelli AI disponibili, budget e privacy.
8. Esecuzione locale, server o cloud.
9. Utenti, ruoli e autenticazione.
10. Criteri quantitativi per passare da una fase alla successiva.
