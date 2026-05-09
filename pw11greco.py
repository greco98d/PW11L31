import math
import tkinter as tk
from tkinter import messagebox

def calcola():
    try:
        #1. Recupero Dati Storici
        d1 = float(entry_anno1.get())
        d2 = float(entry_anno2.get())
        d3 = float(entry_anno3.get())
        d_media = (d1 + d2 + d3) / 3

        #2. Recupero Parametri Economici
        s = float(entry_s.get())
        h = float(entry_h.get())
        lead_time = float(entry_lt.get())

        #3. Recupero Parametri Sicurezza (Richiesti dal PDF)
        #sigma è la variabilità della domanda
        sigma = float(entry_sigma.get())
        #z è il coefficiente basato sul livello di servizio (es. 1.645 per 95%)
        z = float(entry_z.get())

        #CALCOLI
        #Formula Lotto Economico (EOQ)
        eoq = math.sqrt((2 * d_media * s) / h)
        
        #Calcolo Scorta di Sicurezza (SS)
        ss = z * sigma * math.sqrt(lead_time)
        
        #Calcolo Punto di Riordino (ROP)
        d_giornaliera = d_media / 365
        rop = (d_giornaliera * lead_time) + ss

        #MOSTRA RISULTATI (Esattamente come chiede il punto 2 del PDF) 
        testo_risultato = (
            "RISULTATI ELABORAZIONE\n" +
            "----------------------------\n" +
            "Lotto Economico (EOQ): " + str(round(eoq)) + " pezzi\n" +
            "Scorta di Sicurezza (SS): " + str(round(ss)) + " pezzi\n" +
            "Livello di Riordino (ROP): " + str(round(rop)) + " pezzi"
        )
        label_risultato.config(text=testo_risultato)

    except:
        messagebox.showerror("Errore", "Per favore, inserisci numeri validi in tutti i campi.")

#INTERFACCIA
root = tk.Tk()
root.title("Gestione Scorte Avanzata - PW11")
root.geometry("400x650")

#Funzione veloce per la creazione di etichette/entry 
def aggiungi_campo(testo):
    tk.Label(root, text=testo).pack()
    entry = tk.Entry(root)
    entry.pack(pady=2)
    return entry

tk.Label(root, text="ANALISI DOMANDA STORICA", font=("Arial", 10, "bold")).pack(pady=5)
entry_anno1 = aggiungi_campo("Domanda Anno 1")
entry_anno2 = aggiungi_campo("Domanda Anno 2")
entry_anno3 = aggiungi_campo("Domanda Anno 3")

tk.Label(root, text="PARAMETRI OPERATIVI", font=("Arial", 10, "bold")).pack(pady=5)
entry_s = aggiungi_campo("Costo Setup Ordine (S)")
entry_h = aggiungi_campo("Costo Mantenimento (H)")
entry_lt = aggiungi_campo("Lead Time (Giorni)")

tk.Label(root, text="PARAMETRI SICUREZZA", font=("Arial", 10, "bold")).pack(pady=5)
entry_sigma = aggiungi_campo("Variabilità Domanda (Sigma)")
entry_z = aggiungi_campo("Livello Servizio (es. 1.645)")

tk.Button(root, text="ESEGUI CALCOLO", command=calcola, bg="#4CAF50", fg="white").pack(pady=20)

label_risultato = tk.Label(root, text="", font=("Arial", 10), justify="left")
label_risultato.pack()

root.mainloop()