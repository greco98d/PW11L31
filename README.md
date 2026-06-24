# Gestione Scorte — EOQ e ROP con Safety Stock
### Project Work 11 — L-31 Informatica per le Aziende Digitali

Software per il calcolo del Lotto Economico di Ordinazione (EOQ) e del Livello di Riordino (ROP), con supporto alla Scorta di Sicurezza (Safety Stock).

## Funzionalita'

- Calcolo EOQ tramite la formula di Wilson: `sqrt((2 * D * S) / H)`
- Calcolo della Scorta di Sicurezza: `Z * sigma * sqrt(L)`, con sigma derivata automaticamente dai dati storici
- Calcolo del Punto di Riordino: `ROP = d * L + SS`
- Confronto diretto tra modello classico (senza SS) e modello con Scorta di Sicurezza
- Checkbox per selezionare il modello di calcolo
- Validazione degli input con messaggi di errore specifici

## Esecuzione

Requisiti: Python 3.x — nessuna dipendenza esterna, solo librerie standard.

```bash
python pw11greco.py
```

## Struttura del codice

| Componente | Responsabilita' |
|---|---|
| `InventoryInputs` | Raccoglie i dati inseriti dall'utente |
| `InventoryResults` | Contiene tutti i risultati calcolati |
| `compute_results()` | Orchestra i calcoli in sequenza |
| `validate()` | Controlla la correttezza degli input |
| `format_classic_results()` | Formatta l'output del modello classico |
| `format_results_with_safety_stock()` | Formatta l'output con SS e tabella di confronto |
| `InventoryApp` | Gestisce l'interfaccia grafica |

## Documentazione

Vedere `relazione.md` per la descrizione completa delle formule, l'analisi dei risultati e il confronto tra i modelli.
