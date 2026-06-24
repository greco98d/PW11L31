# Relazione - Project Work 11
## Lotto Economico di Ordinazione (EOQ) e Livello di Riordino con Scorta di Sicurezza

**Corso di Laurea L-31 - Informatica per le Aziende Digitali**
**Settori: INF/01, ING-INF/05, ING-IND/17**

---

## 1. Descrizione del Problema

Le aziende che gestiscono materiali a domanda indipendente devono rispondere a due domande operative:

- **Quanto ordinare?** — ordinare troppo costa in magazzino, ordinare troppo poco genera rotture di stock.
- **Quando ordinare?** — anticipare l'ordine ha un costo, ritardarlo un rischio.

Il progetto implementa due modelli che rispondono a queste domande:

- **Modello EOQ classico**: assume domanda costante e prevedibile. Serve come riferimento teorico.
- **Modello con Scorta di Sicurezza**: estende il classico tenendo conto della variabilita' reale della domanda, calcolata automaticamente dai dati storici inseriti.

Il software consente di scegliere tra i due modelli tramite una checkbox e ne mostra il confronto diretto.

---

## 2. Dati di Esempio

Per verificare il funzionamento del software e' stata simulata un'azienda che distribuisce componenti meccanici con i seguenti dati:

| Parametro              | Valore              |
|------------------------|---------------------|
| Domanda Anno 1         | 1.200 unita'        |
| Domanda Anno 2         | 1.450 unita'        |
| Domanda Anno 3         | 1.310 unita'        |
| Costo Setup (S)        | 80 euro/ordine      |
| Costo Mantenimento (H) | 5 euro/unita'/anno  |
| Lead Time (L)          | 15 giorni           |
| Livello di Servizio    | 95% — Z = 1,645     |

---

## 3. Formule Implementate

### Formula 1 — Lotto Economico di Wilson (EOQ)

```
EOQ = sqrt( (2 * D * S) / H )
```

**Parametri:** D = domanda media annua, S = costo fisso per ordine, H = costo di mantenimento per unita'/anno.

**Cosa fa:** trova la quantita' da ordinare che minimizza la somma di costi di setup e costi di magazzino. Aumentare D o S sposta l'EOQ verso lotti piu' grandi; aumentare H lo riduce.

**Impatto:** con i dati di esempio, D = 1.320, S = 80, H = 5 → EOQ = 206 pezzi per ordine.

---

### Formula 2 — Punto di Riordino Classico

```
ROP_classico = (D / 365) * L
```

**Parametri:** D / 365 = domanda giornaliera media, L = lead time in giorni.

**Cosa fa:** calcola a quale livello di scorte lanciare un nuovo ordine, assumendo che la domanda durante il lead time sia esattamente uguale alla media.

**Impatto:** con i dati di esempio, domanda giornaliera = 3,6 unita', L = 15 → ROP classico = 54 pezzi. Se la domanda scende sotto 54 pezzi in magazzino, si ordina. Il rischio e' che qualsiasi picco di domanda durante i 15 giorni di attesa porta a rottura di stock.

---

### Formula 3 — Scorta di Sicurezza (Safety Stock)

```
SS = Z * sigma * sqrt(L)
```

**Parametri:** Z = coefficiente del livello di servizio, sigma = deviazione standard della domanda (calcolata automaticamente dai 3 anni inseriti), L = lead time in giorni.

**Cosa fa:** quantifica il buffer necessario per coprire la variabilita' della domanda durante il lead time. Sigma viene derivata direttamente dai dati storici con la deviazione standard campionaria — non richiede input manuale.

**Impatto:** con i dati di esempio, sigma = 125,3 (la domanda varia di circa ±125 unita'/anno tra gli anni), Z = 1,645, L = 15 → SS = 798 pezzi.

Leggere Z come una manopola del rischio: Z = 1,28 copre il 90% degli scenari, Z = 1,645 il 95%, Z = 2,33 il 99%. Piu' alto il livello di servizio, piu' costoso il buffer.

---

### Formula 4 — Punto di Riordino con Scorta di Sicurezza

```
ROP = (D / 365) * L + SS
```

**Cosa fa:** aggiunge il buffer SS al ROP classico. E' il livello di scorte al quale va emesso l'ordine nella pratica.

**Impatto:** ROP = 54 + 798 = 852 pezzi.

---

## 4. Risultati e Confronto

Con i dati di esempio, il software produce il seguente confronto tra i due modelli:

| Indicatore                  | Modello Classico | Modello con SS |
|-----------------------------|-----------------|----------------|
| Domanda media annua         | 1.320 unita'    | 1.320 unita'   |
| Sigma (dai dati storici)    | —               | 125,3 unita'   |
| Lotto Economico (EOQ)       | 206 pezzi       | 206 pezzi      |
| Scorta di Sicurezza (SS)    | 0 pezzi         | 798 pezzi      |
| Livello di Riordino (ROP)   | 54 pezzi        | 852 pezzi      |

**Cosa ci dicono questi risultati:**

- **L'EOQ e' identico** nei due modelli. La variabilita' della domanda non cambia quanto ordinare, ma quando.
- **Il ROP passa da 54 a 852 pezzi**: la scorta di sicurezza impone di riordinare molto prima, per avere un buffer che assorba i picchi durante i 15 giorni di lead time.
- **La differenza (+798 pezzi) e' elevata** perche' la domanda storica varia significativamente (da 1.200 a 1.450, sigma = 125,3). Con una domanda piu' stabile, la SS sarebbe proporzionalmente minore.
- **Senza SS**, se nel mese di punta la domanda giornaliera supera la media di anche solo il 10%, le scorte si esauriscono prima dell'arrivo dell'ordine.
- **Con SS al 95%**, solo in 1 ciclo su 20 si rischia una rottura di stock — un compromesso accettabile per la maggior parte delle aziende.

---

## 5. Architettura del Codice

Il software e' sviluppato in Python 3 con sole librerie standard (`math`, `statistics`, `tkinter`, `dataclasses`).

### Modelli dati

Due `dataclass` separano nettamente gli input dagli output:

```python
@dataclass
class InventoryInputs:
    year1_demand, year2_demand, year3_demand  # dati storici
    setup_cost, holding_cost, lead_time_days  # parametri economici
    service_level_z                           # livello di servizio

@dataclass
class InventoryResults:
    average_demand, demand_std_dev            # statistiche derivate
    economic_order_qty                        # EOQ
    classic_reorder_point                     # ROP senza SS
    safety_stock, safe_reorder_point          # SS e ROP con SS
```

### Funzioni di calcolo (pure, senza effetti collaterali)

Ogni funzione implementa esattamente una formula:

```python
def wilson_eoq(average_demand, setup_cost, holding_cost):
    return math.sqrt((2 * average_demand * setup_cost) / holding_cost)

def safety_stock(service_level_z, demand_std_dev, lead_time_days):
    return service_level_z * demand_std_dev * math.sqrt(lead_time_days)

def reorder_point(daily_demand, lead_time_days, safety_stock=0.0):
    return daily_demand * lead_time_days + safety_stock
```

La sigma non viene chiesta all'utente ma calcolata automaticamente:

```python
def sample_std_dev_of_three(a, b, c):
    return statistics.stdev([a, b, c])
```

### Validazione

La funzione `validate()` controlla tutti i vincoli prima del calcolo e solleva `ValueError` con messaggi in italiano. Quando la checkbox e' disattivata, il coefficiente Z non viene ne' letto ne' validato.

### Interfaccia grafica

La classe `InventoryApp` costruisce la UI in metodi separati (`_build_*`), ognuno responsabile di una sola sezione. Una checkbox "Includi Scorta di Sicurezza" commuta tra i due modelli: se disattivata, il campo Z viene disabilitato e il calcolo usa `format_classic_results`; se attivata, usa `format_results_with_safety_stock` che include la tabella di confronto.

---

## 6. Processo di Sviluppo

1. **Analisi della traccia**: identificazione delle formule (EOQ, SS, ROP) e dei requisiti di interfaccia e documentazione.
2. **Modellazione del dominio**: definizione di `InventoryInputs` e `InventoryResults` come punto di partenza, separando dati da logica fin dall'inizio.
3. **Implementazione delle formule**: ogni formula tradotta in una funzione pura, verificata manualmente con i dati di esempio.
4. **Calcolo automatico di sigma**: invece di richiedere la deviazione standard come input, il software la deriva dai 3 anni storici tramite `statistics.stdev`.
5. **Interfaccia grafica**: costruzione per sezioni logiche con `LabelFrame`, aggiunta della checkbox per la selezione del modello.
6. **Validazione e gestione errori**: controlli espliciti per ogni vincolo (H > 0, domande positive, Z > 0 quando necessario).
7. **Verifica risultati**: calcolo manuale con i dati di esempio e confronto con l'output del software.

---

## 7. Esecuzione

Requisiti: Python 3.x (librerie `math`, `statistics`, `tkinter`, `dataclasses` — tutte standard).

```bash
python pw11greco.py
```

Verifica disponibilita' di Tkinter: `python -m tkinter`
