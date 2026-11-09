# Scalping MVP

Questo modulo implementa la prima fase del progetto: analisi tecnica deterministica, controllo di rischio fail-closed e paper execution locale.

## Avvio

Dalla radice del repository:

    python -m scalping_mvp.demo

Il demo produce una proposta e un ordine `PAPER_FILLED`. Non usa credenziali, API esterne o broker reali.

## Dashboard

Avvia la dashboard locale:

    python -m scalping_mvp.dashboard

Apri poi http://127.0.0.1:8877 nel browser. Mostra gli agenti, il diario delle decisioni, le operazioni paper e il grafico dell'equity. I pulsanti Avvia e Pausa controllano il ciclo locale.
