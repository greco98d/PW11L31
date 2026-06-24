import math
import statistics
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox


# ---------------------------------------------------------------------------
# Modelli di dominio
# ---------------------------------------------------------------------------

@dataclass
class InventoryInputs:
    """Classe per rappresentare gli input dell'inventario."""
    year1_demand:    float
    year2_demand:    float
    year3_demand:    float
    setup_cost:      float
    holding_cost:    float
    lead_time_days:  float
    service_level_z: float


@dataclass
class InventoryResults:
    """Classe per rappresentare i risultati dei calcoli dell'inventario."""
    average_demand:        float
    demand_std_dev:        float
    economic_order_qty:    float
    classic_reorder_point: float
    safety_stock:          float
    safe_reorder_point:    float


# ---------------------------------------------------------------------------
# Funzioni di calcolo puro — ciascuna fa esattamente una cosa
# ---------------------------------------------------------------------------

def average_of_three(a: float, b: float, c: float) -> float:
    """Calcola la media di tre valori."""
    return (a + b + c) / 3


def sample_std_dev_of_three(a: float, b: float, c: float) -> float:
    """Calcola la deviazione standard campionaria di tre valori."""
    return statistics.stdev([a, b, c])


def wilson_eoq(average_demand: float, setup_cost: float, holding_cost: float) -> float:
    """Formula di Wilson: la quantità di ordine che minimizza il costo totale dell'inventario.
    EOQ = sqrt((2 * D * S) / H)
    """
    return math.sqrt((2 * average_demand * setup_cost) / holding_cost)


def daily_demand(annual_demand: float) -> float:
    """Converte la domanda annuale in domanda giornaliera."""
    return annual_demand / 365


def safety_stock(service_level_z: float, demand_std_dev: float, lead_time_days: float) -> float:
    """Stock di sicurezza extra per assorbire la variabilità della domanda durante il lead time.
    SS = Z * sigma * sqrt(L)
    """
    return service_level_z * demand_std_dev * math.sqrt(lead_time_days)


def reorder_point(daily_demand: float, lead_time_days: float, safety_stock: float = 0.0) -> float:
    """Livello di stock al quale deve essere piazzato un nuovo ordine.
    ROP = d * L + SS
    """
    return daily_demand * lead_time_days + safety_stock


def compute_results(inputs: InventoryInputs) -> InventoryResults:
    """Esegue tutti i calcoli in ordine e restituisce il set completo di risultati."""
    # Calcola la domanda media
    avg_demand  = average_of_three(inputs.year1_demand, inputs.year2_demand, inputs.year3_demand)
    # Calcola la deviazione standard
    std_dev     = sample_std_dev_of_three(inputs.year1_demand, inputs.year2_demand, inputs.year3_demand)
    # Calcola la quantità economica di ordine
    eoq         = wilson_eoq(avg_demand, inputs.setup_cost, inputs.holding_cost)
    # Calcola la domanda giornaliera
    d_daily     = daily_demand(avg_demand)
    # Calcola lo stock di sicurezza
    ss          = safety_stock(inputs.service_level_z, std_dev, inputs.lead_time_days)
    # Calcola il punto di riordino classico (senza stock di sicurezza)
    classic_rop = reorder_point(d_daily, inputs.lead_time_days)
    # Calcola il punto di riordino sicuro (con stock di sicurezza)
    safe_rop    = reorder_point(d_daily, inputs.lead_time_days, ss)

    return InventoryResults(
        average_demand        = avg_demand,
        demand_std_dev        = std_dev,
        economic_order_qty    = eoq,
        classic_reorder_point = classic_rop,
        safety_stock          = ss,
        safe_reorder_point    = safe_rop,
    )


# ---------------------------------------------------------------------------
# Validazione
# ---------------------------------------------------------------------------

def validate(inputs: InventoryInputs, include_safety_stock: bool) -> None:
    """ValueError con un messaggio user-friendly se qualche input è invalido."""
    demands = [inputs.year1_demand, inputs.year2_demand, inputs.year3_demand]
    if any(d <= 0 for d in demands):
        raise ValueError("I valori di domanda devono essere strettamente positivi.")
    if inputs.holding_cost <= 0:
        raise ValueError("Il costo di mantenimento (H) deve essere maggiore di zero.")
    if any(v < 0 for v in [inputs.setup_cost, inputs.lead_time_days]):
        raise ValueError("Costo setup e lead time non possono essere negativi.")
    if include_safety_stock and inputs.service_level_z <= 0:
        raise ValueError("Il coefficiente Z deve essere positivo (es. 1.645 per 95%).")


# ---------------------------------------------------------------------------
# Presentazione — una funzione per ogni formato di output
# ---------------------------------------------------------------------------

def format_classic_results(r: InventoryResults) -> str:
    """Output per il modello classico EOQ: domanda costante, nessun buffer di sicurezza."""
    sep = "-" * 40
    return "\n".join([
        f"  MODELLO CLASSICO EOQ",
        f"  {sep}",
        f"  Domanda media annua:  {round(r.average_demand, 1)} unita'",
        f"  {sep}",
        f"  Lotto Economico (EOQ)   = {round(r.economic_order_qty)} pezzi",
        f"  Livello di Riordino     = {round(r.classic_reorder_point)} pezzi",
        f"  Scorta di Sicurezza     = 0 pezzi",
    ])


def format_results_with_safety_stock(r: InventoryResults) -> str:
    """Output per il modello con scorta di sicurezza, includendo un confronto laterale con il modello classico."""
    sep = "-" * 40
    rop_delta_pct = (r.safety_stock / r.classic_reorder_point * 100) if r.classic_reorder_point else 0

    return "\n".join([
        f"  MODELLO CON SCORTA DI SICUREZZA",
        f"  {sep}",
        f"  Domanda media annua:  {round(r.average_demand, 1)} unita'",
        f"  Variabilita' (sigma): {round(r.demand_std_dev, 2)} unita'",
        f"  {sep}",
        f"  Lotto Economico (EOQ)     = {round(r.economic_order_qty)} pezzi",
        f"  Scorta di Sicurezza (SS)  = {round(r.safety_stock)} pezzi",
        f"  Livello di Riordino (ROP) = {round(r.safe_reorder_point)} pezzi",
        f"  {sep}",
        f"  CONFRONTO CON MODELLO CLASSICO",
        f"  {sep}",
        f"  {'':30} {'Classic':>7}  {'Con SS':>6}",
        f"  {'Scorta di Sicurezza (pezzi)':<30} {'0':>7}  {round(r.safety_stock):>6}",
        f"  {'Livello di Riordino (pezzi)':<30} {round(r.classic_reorder_point):>7}  {round(r.safe_reorder_point):>6}",
        f"  {sep}",
        f"  Delta ROP: +{round(r.safety_stock)} pezzi (+{round(rop_delta_pct)}%)",
        f"",
        f"  L'EOQ e' identico in entrambi i modelli:",
        f"  la SS non cambia quanto ordinare, ma quando.",
    ])


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

def labeled_entry(parent: tk.Widget, label_text: str) -> tk.Entry:
    """Aggiunge un'etichetta e un campo di inserimento testo al widget genitore."""
    tk.Label(parent, text=label_text, anchor="w").pack(fill="x", padx=8, pady=(4, 0))
    entry = tk.Entry(parent, width=32)
    entry.pack(padx=8, pady=(0, 4))
    return entry


def section(parent: tk.Widget, title: str) -> tk.LabelFrame:
    """Crea una box con un titolo che raggruppa campi correlati."""
    frame = tk.LabelFrame(parent, text=title, font=("Arial", 10, "bold"), padx=5, pady=5)
    frame.pack(fill="x", padx=10, pady=6)
    return frame


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class InventoryApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Gestione Scorte - EOQ e ROP con Safety Stock")
        self.root.geometry("440x740")
        self.root.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        self._build_historical_demand_section()
        self._build_economic_parameters_section()
        self._build_service_level_section()
        self._build_calculate_button()
        self._build_results_area()

    def _build_historical_demand_section(self):
        frame = section(self.root, "ANALISI DOMANDA STORICA (3 anni)")
        self.entry_year1 = labeled_entry(frame, "Domanda Anno 1 (unita')")
        self.entry_year2 = labeled_entry(frame, "Domanda Anno 2 (unita')")
        self.entry_year3 = labeled_entry(frame, "Domanda Anno 3 (unita')")

    def _build_economic_parameters_section(self):
        frame = section(self.root, "PARAMETRI ECONOMICI")
        self.entry_setup_cost   = labeled_entry(frame, "Costo Setup per Ordine (S) [euro]")
        self.entry_holding_cost = labeled_entry(frame, "Costo Mantenimento per unita'/anno (H) [euro]")
        self.entry_lead_time    = labeled_entry(frame, "Lead Time (giorni)")

    def _build_service_level_section(self):
        frame = section(self.root, "SCORTA DI SICUREZZA")

        # Checkbox — controlla se il modello SS è attivo
        self.include_safety_stock = tk.BooleanVar(value=True)
        tk.Checkbutton(
            frame,
            text="Includi Scorta di Sicurezza",
            variable=self.include_safety_stock,
            command=self._on_safety_stock_toggled,
        ).pack(anchor="w", padx=8, pady=(4, 2))

        tk.Label(
            frame,
            text="Valori tipici Z:  1.28 (90%)  |  1.645 (95%)  |  2.33 (99%)",
            font=("Arial", 8), fg="gray",
        ).pack(anchor="w", padx=8)
        self.entry_z = labeled_entry(frame, "Coefficiente Z")

    def _on_safety_stock_toggled(self):
        """Abilita o disabilita il campo Z a seconda dello stato della checkbox."""
        state = tk.NORMAL if self.include_safety_stock.get() else tk.DISABLED
        self.entry_z.config(state=state)

    def _build_calculate_button(self):
        tk.Button(
            self.root,
            text="ESEGUI CALCOLO",
            command=self._on_calculate_clicked,
            bg="#4CAF50", fg="white",
            font=("Arial", 11, "bold"),
            height=2,
        ).pack(fill="x", padx=10, pady=8)

    def _build_results_area(self):
        self.results_label = tk.Label(
            self.root,
            text="I risultati appariranno qui dopo il calcolo.",
            font=("Courier", 10),
            justify="left",
            relief="sunken",
            anchor="nw",
            padx=10, pady=10,
        )
        self.results_label.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _read_inputs(self) -> InventoryInputs:
        """Legge ogni campo di input e li restituisce come un oggetto InventoryInputs.
        Quando SS è disabilitato, Z ha valore predefinito 0 quindi il campo può essere ignorato.
        """
        z = float(self.entry_z.get()) if self.include_safety_stock.get() else 0.0
        return InventoryInputs(
            year1_demand    = float(self.entry_year1.get()),
            year2_demand    = float(self.entry_year2.get()),
            year3_demand    = float(self.entry_year3.get()),
            setup_cost      = float(self.entry_setup_cost.get()),
            holding_cost    = float(self.entry_holding_cost.get()),
            lead_time_days  = float(self.entry_lead_time.get()),
            service_level_z = z,
        )

    def _on_calculate_clicked(self):
        """Legge gli input, li valida, esegue il calcolo e mostra i risultati."""
        try:
            use_ss  = self.include_safety_stock.get()
            inputs  = self._read_inputs()
            validate(inputs, include_safety_stock=use_ss)
            results = compute_results(inputs)
            output  = format_results_with_safety_stock(results) if use_ss else format_classic_results(results)
            self.results_label.config(text=output)
        except ValueError as error:
            messagebox.showerror("Errore", str(error))


# ---------------------------------------------------------------------------
# Entry point root
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    InventoryApp(root)
    root.mainloop()
