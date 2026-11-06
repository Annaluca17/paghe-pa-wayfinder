# PASSWEB, INAIL, Conto Annuale, PIAO e trasparenza come viste

Applica l'ADR 0022 agli output che non sono la delega F24EP.

**PASSWEB.** La posizione assicurativa non si corregge più direttamente in PASSWEB, ma con denunce ListaPosPA a variazione, anche tramite SCAD (circolare INPS 118/2025, da riscontrare sul testo). Ne restano due cose:

- la **sistemazione della posizione** è la ListaPosPA con quadri V1 che il modello già produce (ADR 0008 e 0011): nessun output nuovo;
- l'**ultimo miglio** (pensione, TFS/TFR, DMA previste, miglioramento contrattuale) è una vista di **valori da digitare** nelle maschere, perché un flusso non esiste. Legge gli esiti pagati e i fatti del rapporto; i mesi prima dell'avvio del modello vengono da un fatto con fonte sulle **retribuzioni pregresse**, altrimenti sono un dato mancante. L'esito dichiarato nasce quando l'Ufficio personale registra l'inserimento, con data e pratica.

Le regole e le tabelle CCNL di Pensione-2.0, che portano la fonte valore per valore, entrano nel corpus; il suo calcolo serve da controllo indipendente sugli stessi dati.

**Autoliquidazione INAIL.** Una **base imponibile INAIL** propria, con il concorso dichiarato dall'istituto; la **voce di tariffa** come fatto datato sul rapporto; la **dichiarazione delle retribuzioni** come vista annuale (regolazione dell'anno precedente e rata dell'anno), con esito dichiarato; il **premio** con righe nella sezione INAIL della delega F24EP, senza compensare crediti e debiti INAIL; le rate come scelta dell'ente. Finché il ticket #52 non chiude, l'output INAIL è fermo.

**Conto Annuale.** Ogni tabella è una vista dell'anno di rilevazione nel formato del **kit** RGS dell'anno, dove esiste. Gli importi passano dalla voce SICO (mappatura datata) e si rilevano per cassa; le tabelle su consistenze e assenze sono viste sui fatti. L'invio produce un esito dichiarato. Il contenuto delle tabelle e il kit vanno verificati nel ticket #53.

**PIAO.** Il prospetto della sottosezione 3.3 (consistenza al 31/12, cessazioni previste, capacità assunzionale) è una vista; diventa esito dichiarato quando è registrata la delibera che adotta il PIAO. Le **cessazioni previste** non le calcola il modello: sono fatti in attesa d'atto o previsioni dell'Ufficio personale, perché la data di pensione richiede la posizione assicurativa intera. Capacità assunzionale e limiti di spesa restano viste che non fermano nulla (ADR 0015).

**Trasparenza.** Ogni pubblicazione (tassi di assenza trimestrali per ufficio, costo del personale, personale non a tempo indeterminato, premi, compensi) è una vista nel formato degli schemi standard ANAC dove esistono, altrimenti un prospetto tabellare. L'esito dichiarato nasce quando l'ente registra la data di pubblicazione; il caricamento sul sito resta fuori dal modello.

Scelto da Luca il 06/11/2026 nel grilling del ticket #45, domande 6, 7, 8, 14, 15 e 16.

## Considered Options

- **Pensione-2.0 come generatore dell'ultimo miglio:** ricostruisce le voci dai cedolini Halley, mentre il modello ha gli esiti pagati.
- **Ultimo miglio stimato quando mancano i mesi pregressi:** una vista non stima.
- **Cessazioni previste calcolate dal modello:** servirebbe tutta la posizione assicurativa, che il modello non ha.
- **INAIL deciso subito su regime e tariffe:** il vault ha solo la guida INAIL e nessuna fonte sul regime degli enti locali.
- **Trasparenza come solo prospetto:** lascerebbe all'ente la conversione negli schemi ANAC.
- **Conto Annuale come prospetto da digitare in SICO:** dove il kit esiste, è un passaggio manuale inutile.

## Consequences

- Nuovi tipi di fatto con un lettore: retribuzioni pregresse, voce di tariffa INAIL, inserimento dell'ultimo miglio, pubblicazione, delibera del PIAO.
- Gli output Conto Annuale, INAIL e ultimo miglio avranno ciascuno un ticket di codice quando le ricerche #52 e #53 avranno chiuso.

**Da verificare**

- Circolare INPS 118/2025 sull'inibizione di PASSWEB e sulle eccezioni (CTPS, CPUG, ENPAS); il vault segnala una contraddizione con il manuale SCAD.
- Termine TFS/TFR di 9 mesi dal 01/01/2027 (L. 199/2025 c. 198, circolare INPS 30/2026, riportati dal vault).
- Regime INAIL, soggetti coperti, base e tariffe: ticket #52.
- Tabelle, kit e unità di misura del Conto Annuale: ticket #53.
- Schemi standard ANAC per gli obblighi del personale (artt. 16, 17, 20, 21 D.Lgs. 33/2013) e legge di conversione del DL 80/2021 (il vault si contraddice tra L. 113/2021 e L. 131/2021).
