# Malattia del comparto: episodi, decurtazione dei primi 10 giorni, comporto e retribuzione virtuale

Il nucleo calcola la malattia dei dipendenti del comparto Funzioni Locali. L'ufficio registra ogni certificato come fatto categoriale `malattia` per periodo (`ordinaria`, `ricovero`, `salvavita`, `infortunio`); `paghe/malattia.py` ricava lo stato di ogni giorno e il motore riduce gli importi secondo ciò che ciascun istituto dichiara nel corpus.

## Le cinque decisioni (Luca, 12/11/2026, ticket #130)

1. **Un solo ticket.** Trattenuta dei primi 10 giorni (art. 71 DL 112/2008), esclusioni (ricovero e convalescenza, day hospital e simili, terapie salvavita, infortunio), periodi 100% / 90% / 50% / non retribuito con comporto di 18 mesi (art. 48 CCNL 16/11/2022 = art. 36 CCNL 23/02/2026; art. 29 e 30). Tredicesima ridotta nella stessa proporzione per i periodi al 90% e al 50% (art. 75 c. 9 CCNL 2022).
2. **Divisore 26** (art. 74 c. 4 CCNL 16/11/2022). Si usa il divisore giornaliero già nel corpus e il conteggio lunedì-sabato dei tabellari: la trattenuta di un giorno è un ventiseiesimo del mensile della voce, le domeniche non si contano.
3. **Voci tolte nei 10 giorni:** indennità di comparto non conglobata, posizione EQ, vigilanza, specifica e altre fisse e continuative. **Restano:** tabellare (con la quota di comparto conglobata dal 2026), differenziali, differenziale storico, RIA, assegni ad personam, vacanza contrattuale, tredicesima. Nel corpus ogni istituto dichiara `decurtata` o `intera` (`[[malattia_istituto]]`); un istituto senza dichiarazione ferma il calcolo («caso non modellato»), come per il part-time.
4. **Contributi, TFS e TFR sull'intero** (retribuzione virtuale). Le basi CPDEL, Fondo Credito, TFS e TFR ulteriori dichiarano `retribuzione_virtuale = true` e contano l'importo pieno prima della riduzione. IRAP e reddito fiscale seguono il pagato.
5. **Giorni di calendario.** I 10 giorni partono dal primo giorno dell'episodio. Certificati continui senza giorno lavorato in mezzo sono un solo episodio (sabato, domenica e festivi del corpus fra due certificati non lo spezzano). Comporto: giorni di malattia (ordinaria e ricovero) nei tre anni fino a quel giorno compreso, ricalcolato a ogni giorno.

6. **Quota del lavoratore sulla parte non pagata** (Luca, 12/11/2026). La quota CPDEL e TFS del lavoratore si calcola sul pagato; la parte sul non pagato la integra l'ente (cpdel_ente = totale - quota lavoratore). Il Fondo Credito sulla parte non pagata resta a carico del dipendente. Livello: prassi (Conferenza delle Regioni, altro comparto), coerente con le voci del gestionale dell'ente reale (un «fondo credito figurativo» a carico del dipendente, nessuna ritenuta CPDEL figurativa); **da verificare** sulla circ. INPDAP 13/2009. Nel motore: le formule della quota del lavoratore leggono `base.cpdel_pagato` e `base.tfs_pagato` (suffisso `_pagato`: la somma degli importi realmente pagati nella base).
7. **Scelte di realizzazione confermate da Luca:** mesi del comporto da 30 giorni (270/90/180); sabato, domenica e festivi non spezzano l'episodio; 90% e 50% anche sulle indennità fisse e continuative.

## Come funziona

- **Episodio.** Giorni consecutivi `ordinaria` o `ricovero`. La decurtazione tocca solo i giorni `ordinaria` entro il decimo giorno dell'episodio. `salvavita` e `infortunio` non sono decurtati e non contano per il comporto (comporto a parte, art. 29 e 30).
- **Fasce.** Dichiarate nel corpus (`[[malattia]]`): 270 giorni al 100%, 90 al 90%, 180 al 50%, poi 0. I mesi del contratto sono contati a 30 giorni.
- **Importi del mese.** Il mese si divide in frazioni anche quando cambia lo stato della malattia. Per ogni frazione l'importo (dopo la quota e l'eventuale part-time) si moltiplica per la percentuale; se la voce è `decurtata` e il giorno è nei primi 10, vale zero. La derivazione porta `malattia` con l'importo pieno.
- **Tredicesima.** La maturazione sui 365esimi pesa i giorni di malattia con la loro percentuale (90, 50, 0). La decurtazione dei 10 giorni non la tocca (voce fondamentale).
- **Contributi.** `_base_del_periodo` somma, per le basi virtuali, l'importo pieno.

## Considered Options

- **Importo da atto per la riduzione:** scartato, la malattia ha una regola.
- **Trentesimi (parere FP 2/2009):** scartati da Luca per il divisore 26 (ARAN, contratto vigente).
- **Fatto «giorni di malattia» scritto a mano dall'ufficio:** scartato, il comporto si ricalcola dai certificati.

## Consequences

**Norma certa**

- Art. 71 c. 1 DL 112/2008, testo vigente letto su Normattiva il 12/11/2026 (sintesi dello strumento, non verbatim): primi 10 giorni di assenza, trattamento fondamentale, esclusione dei ricoveri in strutture SSN per prestazioni LEA.
- Periodi 100/90/50 e comporto di 18 mesi nei tre anni: art. 48 CCNL 2022 = art. 36 CCNL 2022-24 (stesso testo, una sola famiglia di fonti).
- Tredicesima ridotta con il rapporto dell'importo e non dovuta nei periodi non retribuiti: art. 75 c. 7 e 9.

**Prassi-interpretazione**

- Voci tolte e voci che restano (parere ARAN 795-21C7, orientamenti ARAN, nota RGS 2009).
- Divisore 26 per la trattenuta (ARAN15 punto 3.3), contro i trentesimi del parere FP 2/2009.
- Contributi e TFS/TFR sull'intero: circolare INPDAP 13 del 28/05/2009, **non letta nel testo originale**; la riferiscono solo fonti secondarie (sito di informazione, nota del Ministero della Giustizia, vademecum Difesa). Seconda fonte letta: il documento della Conferenza delle Regioni sul DL 112/2008 (altro comparto, art. 24 RDL 680/1938 non letto). Nessun messaggio INPS trovato: **da verificare**.

**Da verificare**

- Testo originale della circolare INPDAP 13/2009 e una seconda fonte sui contributi.
- Mesi a 30 giorni, fasce 270/90/180 e finestra mobile ricalcolata a ogni giorno (interpretazione, scelta di Luca).
- Percentuale 90% e 50% anche sulle indennità fisse e continuative (scelta di Luca): il testo dice «retribuzione di cui alla lett. a)».
- Giorni non lavorati fra due certificati: sabato, domenica e festivi (scelta di Luca; la settimana corta di cinque giorni è un'ipotesi).
- La quota del lavoratore sul pagato e l'integrazione dell'ente (punto 6).
- IVC ed EQ (interpretazione); convalescenza dopo il ricovero senza certificato (la regola per la Sanità richiede un certificato).

**Limiti nominati**

- Posizione EQ, vigilanza, specifica e gli altri accessori fissi non sono ancora istituti del corpus: quando arriveranno dichiareranno `decurtata`.
- Dirigenti e segretari non dichiarano il trattamento: la malattia li ferma.
- Il TFS oggi non mostra la differenza: il comparto non concorre al TFS e il tabellare non si decurta, quindi pagato e intero coincidono; la regola vale per le voci decurtate che concorreranno.
- La riduzione del lordo TFR del mese (`riduzione_tfr`) legge il tabellare pagato, quindi negli episodi al 90% e al 50% è sul ridotto, non sull'intero.
- Denuncia UniEmens e ListaPosPA non portano ancora i codici evento di malattia.
- Il certificato con prognosi più lunga o con ricovero in clinica privata convenzionata non è distinto dal ricovero SSN.

**Conseguenze sul modello**

- Nuovi fatti: `malattia` (categoriale). Nuove sezioni del corpus: `[[malattia]]`, `[[malattia_istituto]]`; nuovo campo `retribuzione_virtuale` della base. L'impronta le contiene solo se presenti.
- `Derivazione.malattia` (`RiduzioneMalattia`), serializzata con l'importo.
