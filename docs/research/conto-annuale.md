# Conto Annuale: kit e tabelle sulla circolare RGS dell'anno

Ticket: #53 (alimenta l'ADR 0024; parte da `adempimenti-non-stipendiali.md`, ticket #10). Data ricerca: 06/11/2026.

## Domanda

Che cosa chiede il Conto Annuale a un Ente Locale, tabella per tabella, e in quale formato si carica? Serve all'ADR 0024, che fa di ogni tabella una vista dell'anno di rilevazione nel formato del kit RGS, con importi per cassa attraverso la voce SICO come mappatura datata.

## Metodo e fonti

- Fonte primaria letta per intero nelle parti citate: **Circolare RGS 26/06/2026 n. 12** e il suo **Allegato** (istruzioni per il Conto annuale 2025), pubblicati sul sito della Ragioneria generale dello Stato:
  - Circolare n. 12 (testo letto dal vault-pa, che ne riporta il contenuto; l'URL del PDF sul sito RGS non è stato verificato). Il rinvio «Circolare p. N» nel seguito è quindi **da riscontrare** sul PDF ufficiale.
  - Allegato: <https://www.rgs.mef.gov.it/_Documenti/VERSIONE-I/CIRCOLARI/2026/12/Allegato-alla-Circolare-del-26-giugno-2026-n-12.pdf>. Il testo è stato estratto dal PDF scaricato. Nel seguito «All.» + pagina stampata del PDF (es. «All. p. 139»).
- A differenza del ticket #10 (proxy bloccato), qui il sito RGS era raggiungibile: i fatti sotto sono quindi su fonte primaria, salvo dove segnato.
- Il vault-pa (`wiki/1-Projects/ContoAnnuale-2026/`) è stato usato solo come pista per orientarsi nei capitoli, in sola lettura. Nessuna affermazione poggia solo sul vault.
- Legenda: **norma certa** = obbligo di legge richiamato dalla circolare; **istruzione RGS** = istruzione operativa della circolare/allegato dell'anno (fonte primaria, ma può cambiare ogni anno); **prassi-interpretazione** = lettura mia o di fonti non primarie; **da verificare** = non confermato.
- Repo pubblico: nessun dato reale né nome di ente.

## Sintesi

1. Il modello ha **tabelle di consistenza al 31/12** (1, 1E, 2A, 3, 7, 8, 9, 10) e **tabelle di flusso** sull'anno (2, 4, 5, 6, 11, 12, 13, 14) (All. p. 106). Con 15, SICI, Schede 1/1A, A33 e riconciliazione, ognuna è un aggregato per qualifica e genere derivabile dai fatti: l'ipotesi dell'ADR 0024 regge.
2. Il **kit Excel è specifico per contratto e per anno**: i kit degli anni precedenti non si possono usare (All. p. 31). Non esiste un formato stabile: la «vista nel formato del kit dell'anno» va dichiarata per anno.
3. **Importi per cassa**, lordi dipendente, in euro interi; il Servizio sanitario rileva per competenza economica (All. pp. 139-140). Gli oneri a carico dell'ente (contributi, IRAP) vanno in Tab. 14.
4. **Le unità di misura cambiano da tabella a tabella**: teste (Tab. 1, 2A, 7-10), unità-anno con due decimali (Tab. 2), giorni interi su base 5 giorni (Tab. 11), mensilità con due decimali (Tab. 12), euro (Tab. 12-14, 15), FTE solo come domanda della Scheda informativa 1 (SI1).
5. **Riconciliazione**: per quasi tutti gli enti il confronto è con **SIOPE**, caricato da RGS in SICO; solo dove manca si usa il **bilancio consuntivo** (pagamenti di cassa competenza + residui) (All. pp. 159-162).
6. **Correzioni**: dopo la certificazione l'ente non modifica più; serve la riapertura chiesta alla Ragioneria territoriale / Ufficio centrale di bilancio. Eccezione: Tab. 15 e SICI, aggiornabili dall'ente fino alla «consuntivazione» (All. pp. 61, 187-189).

## 1. Elenco e contenuto delle tabelle (rilevazione 2025)

Rilevazione 2025: circolare RGS 26/06/2026 n. 12, termine **25/07/2026**, invio in SICO con modalità web o con kit Excel (FTP per enti con più istituzioni in un solo sistema, su richiesta all'assistenza) (Circolare p. 4). Rilevazione 2026: **non risulta uscita** a oggi (06/11/2026); la ricerca web non ha trovato circolare né kit. **Da verificare** a ridosso della prossima campagna.

Tabelle e schede del comparto Funzioni Locali. Fonte per tutte: Allegato, capitolo 3 (pp. 106-162) e capitolo 6 (pp. 226 ss.), salvo diversa indicazione. Le colonne «unità» sono la sintesi della fonte; «derivabile da» è prassi-interpretazione mia.

| Tabella | Contenuto (istruzione RGS) | Unità | Derivabile da (prassi-interpretazione) |
|---|---|---|---|
| Scheda informativa 1 (SI1) | Domande generali dell'ente, responsabile del procedimento, revisori; domande su permessi L. 104, art. 42 c. 5 d.lgs. 151/2001, FTE accessorio (All. pp. 84-85) | numeri e testo | fatti dell'ente e della persona |
| Scheda informativa 1A / 1A Convenzioni | Unioni, comunità montane e convenzioni: codici SICO dei comuni partecipanti (All. p. 32) | codici | anagrafica enti |
| Tab. 1 | Consistenza al 31/12 del personale a tempo indeterminato (e di alcune qualifiche a termine) per qualifica/profilo, genere, tempo pieno / part-time fino al 50% / oltre il 50%; include comandati, aspettativa (All. p. 107) | persone | rapporti in vigore al 31/12 |
| Tab. 1E | Distribuzione per numero di differenziali stipendiali/economici (obbligo esteso alla Sicilia, All. p. 4) | persone | posizioni economiche |
| Tab. 2 | Lavoro flessibile (tempo determinato, formazione e lavoro, somministrazione, LSU/LPU/ASU) e modalità flessibili (lavoro agile, telelavoro, coworking) (All. pp. 110-116) | unità-anno (flessibile); persone (modalità) | periodi di rapporto e % part-time |
| Tab. 2A | Tempo determinato in servizio al 31/12 per anzianità di rapporto; dal 2025 solo tempo determinato, senza co.co.co. (All. pp. 6, 117) | persone | storia dei rapporti |
| Tab. 3 | Comandi, distacchi, fuori ruolo, convenzioni (in entrata e uscita) al 31/12 | persone | posizioni di stato |
| Tab. 4 | Passaggi di qualifica/posizione economica/differenziale nell'anno | persone | eventi di inquadramento |
| Tab. 5 / Tab. 6 | Cessati / assunti nell'anno per causale | persone | eventi di rapporto |
| Tab. 7 / 8 / 9 | Tempo indeterminato al 31/12 per classi di anzianità di servizio / età / titolo di studio | persone | anagrafica e carriera |
| Tab. 10 | Personale al 31/12 per regione e estero (richiesta solo ad alcune istituzioni, All. p. 38) | persone | sede di servizio |
| Tab. 11 | Giorni di assenza per qualifica, genere, causale; comprende anche formazione e «lavoro a distanza» (All. pp. 134-139) | giorni interi | presenze |
| Tab. 12 | Voci stipendiali: numero mensilità, stipendio, RIA, differenziali, tredicesima, arretrati, recuperi (All. pp. 140-142) | euro; mensilità (2 decimali) | cedolini |
| Tab. 13 | Indennità e compensi accessori per voce SICO, arretrati anni precedenti, straordinario (All. pp. 146-147, 263) | euro | cedolini + fondo |
| Tab. 14 | Altri oneri del costo del lavoro: assegni nucleo familiare (L005), mense (L010), buoni pasto (L011), contributi (P055), IRAP (P061), rimborsi (P071, P074, P090, P098, P099), flessibili (P015, P065), collaborazioni (L111, L112), altre spese (L110) (capitolo 3, sezione Tab. 14; codici riscontrati anche nei quadri di riconciliazione, All. pp. 161-164) | euro | paghe e contabilità |
| Tab. 15 | Fondi per il trattamento accessorio per macrocategoria: costituzione (risorse fisse, variabili, decurtazioni, poste esterne al fondo, straordinario a bilancio) e destinazione (impieghi erogati) (All. cap. 4, pp. 179-189); importi al netto degli oneri riflessi | euro | fondo come soggetto (ADR 0014) |
| SICI | Specifiche Informazioni sulla Contrattazione Integrativa: sezioni GEN, LEG, ORG, A14 (All. cap. 4 e p. 5) | risposte e importi | atti della contrattazione |
| Scheda A33 (nuova 2025) | Solo Regioni, Città metropolitane, Province, Comuni con contratto nazionale: spesa di personale netta, entrate (media triennale), FCDE, parametro ex art. 33 d.l. 34/2019 e soglia del DM 17/03/2020 (All. pp. 245-247) | euro, % | impegni BDAP + 2 dati dell'ente |
| Riconciliazione | Raffronto spesa Conto annuale / SIOPE o bilancio (All. pp. 159-162) | euro | contabilità |

**Correzione al ticket #10.** La nota «Tab. 3 usata per le correzioni per comandi e distacchi nel calcolo dei presenti» è corretta ma riduttiva; la numerazione 3-10 ora è confermata: 3 comandi/distacchi, 4 passaggi, 5 cessati, 6 assunti, 7 anzianità, 8 età, 9 titolo di studio, 10 regione/estero. L'ipotesi «Tab. 7-9 = classi di età, anzianità, titolo di studio» del #10 è giusta. **Norma certa** (richiamata dalla circolare): rilevazione ex titolo V d.lgs. 165/2001, art. 60; sanzione ex artt. 7 e 11 d.lgs. 322/1989 da 516 a 5.164 euro (Circolare pp. 6-7).

**Nuovo nel 2025 (istruzione RGS, All. pp. 1-7):** SI1 con le FTE di dirigenti e non dirigenti che hanno percepito accessorio (Tab. 13); Scheda A33; sezione SICI A14 e voci Tab. 15 per l'art. 14 c. 1-bis d.l. 25/2025; Tab. 2A solo tempo determinato.

## 2. Formato di caricamento: kit Excel

Tutto istruzione RGS (All. pp. 31-32, 37-38, 29).

- Il kit si scarica da SICO (area RGS «Pubblico impiego»), uno **per contratto**; i kit dell'anno precedente non valgono. Per le Funzioni Locali la cartella contiene anche un file «Lista istituzioni» con i codici SICO dei comuni (per Unioni, Comunità montane e convenzioni); quel file **non** va inviato.
- Un **foglio di lavoro per ciascuna scheda informativa e tabella**; in coda i fogli delle squadrature e incongruenze e un foglio «Valori medi» (All. cap. 1, «Acquisizione con il kit excel»; pagina da verificare). Nella SI1 due sezioni si compilano da sole: «Tabelle compilate» e «Anomalie riscontrate».
- Si compila in locale, senza connessione. Non si devono alterare formato o numero di celle e fogli; incollare solo valori. Campi con asterisco obbligatori; un errore in SI1/SI1A può far scartare il kit in acquisizione.
- Con il kit nella Tab. 1 va inserita a mano la colonna «Totale dipendenti al 31 dicembre dell'anno precedente» (dati SICO della rilevazione precedente) solo per far funzionare la squadratura 1 (All. p. 107).
- Massimo **50 istituzioni** che compongono l'ente con il kit; nessun limite con il web.
- Dati SIOPE e BDAP **non** sono nel kit: SICO li carica da sé. Eventuali valori digitati nella colonna «Importo SIOPE» non vengono trasferiti.
- Dopo il caricamento (kit → SICO) si controllano a video i totali delle tabelle; poi «Concludi rilevazione» e certificazione notturna.

**Squadrature e incongruenze** (All. pp. 37-38 e seguenti): 
- **Squadrature** (SQ1-SQ10): errori da rimuovere sempre. Esempio SQ1: presenti dell'anno prima − cessati + assunti ± passaggi = presenti al 31/12 (per qualifica); SQ2: Tab. 1 coincide con Tab. 7, 8, 9 per qualifica e genere; SQ3: Tab. 10 coerente con Tab. 1 e Tab. 3. 
- **Incongruenze** (IN1-IN17): anomalie che si possono **giustificare** con testo, valutato da RTS/UCB. Esempio IN11: unità LSU senza spesa, giustificabile con testo predefinito.
- Senza squadrature e con incongruenze sanate o giustificate e accettate, il modello è **certificato** (Circolare p. 4). L'elenco completo con gli algoritmi è nelle pp. 37-60 dell'Allegato: non trascritto qui, va ripreso nel ticket di codice.

**Prassi-interpretazione:** gli stessi controlli sono calcolabili sui fatti prima dell'invio: la «vista» può quindi produrre un esito dichiarato (ADR 0024) con elenco anticipato di squadrature. Struttura interna celle/colonne del foglio Excel (coordinate): **da verificare** sul kit scaricato, non sull'Allegato.

## 3. Unità di misura

- **Unità-anno (Tab. 2)**: periodi inferiori all'anno ricondotti ad unità annue, **due decimali**; calcolo manuale con mese convenzionale di 30 giorni e somma mesi/12; part-time pesato sulla percentuale (esempio ufficiale: 4 unità × 6 mesi × 60% / 12 = 1,2). RGS fornisce anche un file di ausilio con mese di 31, 30, 28/29 giorni (All. pp. 113-115). Due metodi quindi: il modello deve dichiarare quale usa e il risultato può differire.
- **Persone (Tab. 1, 2A, 3, 7-10)** distinte per genere; part-time diviso in fino al 50% e oltre il 50% in base alle ore effettive.
- **Giorni di assenza (Tab. 11)** (All. pp. 134-139): giorni **lavorativi** su articolazione convenzionale di **5 giorni**, massimo 250 per dipendente nel 2025; le assenze con orario su 6 giorni si trasformano moltiplicando per le ore del giorno e dividendo per **7,2**; valori **interi**, arrotondati per difetto sotto 0,50 e per eccesso da 0,50, minimo 1. Esclusi i riposi compensativi; ore (scioperi, L. 104, allattamento) riportate a giorni. Causali: ferie; malattia retribuita non soggetta a trattenuta; malattia soggetta a trattenuta (art. 71 d.l. 112/2008); art. 42 c. 5 d.lgs. 151/2001; L. 104/1992; maternità, congedo parentale, malattia figli; altri permessi retribuiti; scioperi; altre assenze non retribuite; formazione; lavoro a distanza. **Formazione e lavoro a distanza non sono assenze** (restano nei totali di riga). Non si rilevano le assenze del tempo determinato, formazione e lavoro, somministrati, LSU.
- **Mensilità (Tab. 12)** (All. pp. 141-142): 12 per un anno intero a tempo pieno, due decimali, rapportate a part-time e a frazioni di mese e di retribuzione (es. 30% → 0,30).
- **FTE degli accessori (Tab. 13 e SI1)** (All. pp. 84-85): è una **domanda** della SI1, non una tabella: «unità espresse in full time equivalent» di dirigenti e di non dirigenti che hanno percepito il salario accessorio di Tab. 13, in termini di «uomo anno». Per alcune amministrazioni vale solo per certe categorie e voci, elencate in un file «Elenco delle amministrazioni, con categorie e voci per gli FTE della tabella 13» sul sito RGS (non letto: **da verificare**). Scopo dichiarato: calcolare l'accessorio medio unitario. **Da verificare**: formula esatta delle FTE (la fonte letta dice «uomo anno», non precisa se pesa i mesi di percezione o il part-time).
- **Euro (Tab. 12-14)**: interi, arrotondati 0-49 per difetto e 50-99 per eccesso; lordo dipendente (All. p. 140).

## 4. Criterio di cassa e voci SICO

**Istruzione RGS (All. pp. 139, 146):** le tabelle di spesa registrano la spesa **effettivamente sostenuta nell'anno secondo il principio di cassa** (escluso il SSN, per competenza economica). Gli accessori vanno nell'anno in cui sono **corrisposti**, qualunque sia l'esercizio di competenza; la colonna «Arretrati anni precedenti» (Tab. 13) è solo per quanto di competenza di anni precedenti dovuto a rinnovi contrattuali, progressioni concluse l'anno prima, ricostruzioni di carriera, sentenze. Importi netti dei recuperi (es. art. 71 d.l. 112/2008). Spese per il personale cessato prima dell'anno: Tab. 14, voce L110. I rimborsi da altre amministrazioni si rilevano per cassa in Tab. 14 (P099, P098, P090); l'ente che paga rileva la spesa in Tab. 12-13.

**Tab. 15 non è per cassa allo stesso modo** (prassi-interpretazione dal testo): è fondo per macrocategoria, con impieghi «effettivamente erogati» riferiti all'anno di competenza del fondo; si aggiorna e si «consuntiva» negli anni (vedi punto 6). Il modello deve quindi tenere due viste di calendario diverse: **cassa dell'anno** (Tab. 12-14) e **competenza del fondo erogata** (Tab. 15).

**Voci SICO.** Sono codici alfanumerici per tabella (A… stipendiali, I… e S… accessorie, L… e P… Tab. 14, F… e voci di fondo in Tab. 15). Fatti verificati sull'Allegato:
- I codici **cambiano da un anno all'altro**: nel 2025 sono nate A033/A034 (differenziali, Sicilia), I231 e I507 (Sardegna), S308 (Forze armate); I837 e I524 rinominate (All. pp. 4-5).
- Alcuni codici sono definiti per tipo di personale e contratto (es. nel contratto Funzioni Locali: I207 retribuzione di posizione, I212 risultato, I222 indennità di comparto, I125 vigilanza, I418 assegno ad personam, All. p. 263; nel Tab. 15 non dirigenti: F00B, F10Y, F20K, F33X) e rinviano ad articoli di CCNL.
- La stessa voce SICO ha **descrizione e riferimento contrattuale** che dipendono dal CCNL vigente nell'anno.

Questo conferma la scelta dell'ADR: la voce SICO è una **mappatura datata** da una voce di cedolino/atto a un codice dell'anno. **Da verificare:** l'elenco completo delle voci Funzioni Locali per tabelle 12, 13 e 14 e la loro numerazione anno per anno (qui letti solo i codici citati; il confronto 2024 contro 2025 richiede la circolare 18/2025 e il suo Allegato, non scaricati). Il vault ha un file «Associazioni Voci» come pista, non verificato.

**Importo accessorio, perimetro:** la Tab. 13 comprende «tutti gli emolumenti accessori corrisposti», a prescindere da fondo o bilancio; la quota a fondo si legge in Tab. 15, quella a bilancio (straordinario, EQ a bilancio) è un blocco a parte (All. p. 180 e ss.).

## 5. Riconciliazione: SIOPE o rendiconto

Istruzione RGS (All. pp. 159-162, 31):
- Scopo: raffrontare i dati di spesa del Conto annuale con il bilancio «che non dovrebbero presentare eccessive differenze»; alcune voci sono escluse dal confronto (equo indennizzo, missioni, assicurazioni…).
- Per gli enti tenuti a **SIOPE**, l'Ufficio III IGOP elabora centralmente e carica in SICO le voci SIOPE riconducibili (estrazione collegando il codice fiscale ente; dati al 9 aprile 2026 per la rilevazione 2025). Le colonne «Importo SICO» e «Importo SIOPE» non sono modificabili; l'ente motiva gli scostamenti rilevanti nel campo **Note**. Sono esclusi gli enti con contratto Sanità.
- **Solo se i dati SIOPE mancano**, l'ente inserisce «Importo bilancio» dal consuntivo: valori di **cassa** dei capitoli di spesa, **pagamenti dell'anno (competenza + residui)**, anche se il bilancio è per competenza. Se il consuntivo non è approvato, la nota indica «preconsuntivo».
- La tabella diventa obbligatoria al salvataggio di almeno una tra Tab. 12, 13, 14. «Importo SICO» si compila da solo con i totali delle tabelle di spesa. Voce SICO ↔ codici SIOPE: quadri sinottici dell'Allegato (es. Tab. 12 + Tab. 13 + assegni familiari ↔ competenze fisse e accessorie e arretrati; P055 contributi; P061 IRAP; L011 buoni pasto).
- Esaminata dagli organi di controllo (revisori).
- **Scheda A33**: usa invece **impegni di spesa BDAP** (voci U.1.01.00.00.000, U1.03.02.12.001/002/003/999, meno arretrati U.1.01.01.01.001 e 005) e **accertamenti** dei titoli 1-3 degli ultimi tre rendiconti: è la sola parte del Conto annuale per **competenza di bilancio**, non per cassa (All. p. 246-247).

**Implicazione (prassi-interpretazione):** i dati contabili non sono input del modello paghe ma un confronto esterno: il modello deve poter produrre l'«Importo SICO» per voce e lasciare la nota di spiegazione come testo dell'ente.

## 6. Correzioni dopo l'invio e certificazione

Istruzione RGS (All. pp. 29, 61-62, 187-189; Circolare p. 4):
- **Concludi rilevazione** → certificazione notturna: ok solo se non ci sono squadrature e le incongruenze sono sanate o giustificate e accettate da RTS/UCB. Il responsabile del procedimento (indicato in SI1) e il presidente del collegio dei revisori firmano la stampa del modello certificato, preferibilmente in digitale; l'organo di controllo vigila sulla pubblicazione di Tab. 15 e SICI (art. 40-bis d.lgs. 165/2001).
- Dopo la certificazione **l'ente non modifica**. Per rettificare dati già inviati, aggiungere o cancellare una tabella, chiede la **riapertura (rettifica attiva)** a RTS/UCB, con relazione su importi e ragioni; a rettifica chiusa il modello è ricontrollato e ricertificato. Per le Sanità in piano di rientro la procedura è diversa (non rilevante per gli Enti Locali).
- **Eccezione Tab. 15 e SICI** (All. pp. 187-189): l'ente le aggiorna da solo («Aggiorna T15/SICI») anche dopo la certificazione, perché la contrattazione può concludersi dopo l'anno. Quando il fondo è certificato e gli impieghi tutti erogati, spunta «T15/SICI consuntivate». Non si può consuntivare se, per una macrocategoria con GEN195 valorizzata, manca la data di certificazione (GEN353, GEN355 o GEN196) o gli utilizzi sono inferiori all'80% delle risorse. Le **risorse** già indicate in Tab. 15 non si rettificano da soli: serve RTS/UCB. Inoltre all'avvio della rilevazione 2025 il sistema richiede di aggiornare o consuntivare la Tab. 15/SICI **2024** prima di procedere.
- **Pubblicazione** del modello certificato in «Amministrazione trasparente» ex art. 16 commi 1 e 2 e art. 17 d.lgs. 33/2013 (Circolare p. 5; **norma certa**, richiamata dalla circolare).
- Inadempimento: dichiarazione, diffida del Prefetto con 15 giorni, sanzione (Circolare pp. 6-7).

**Esito dichiarato (ADR 0014/0024):** gli stati reali sono acquisizione, modello completato, con anomalie, certificato, rettificato, in rettifica (All. cap. 1, schema degli stati del modello; **pagina da verificare**). Quindi l'«esito dichiarato» deve avere una data e uno stato per anno e tipo di rettifica, e Tab. 15/SICI hanno un ciclo proprio (aggiornabile / consuntivata).

## Conseguenze per l'ADR 0024 e gli altri ADR

1. **«Ogni tabella è una vista nel formato del kit dell'anno»**: confermato, con questi punti da fissare: (a) il kit cambia per contratto e anno; (b) le tabelle 12-14 sono viste per **cassa** con codice voce SICO datato; (c) Tab. 2 e 11 hanno regole di calcolo (unità-anno, giorni su base 5 giorni, arrotondamenti) che sono parte della vista; (d) Tab. 15 e SICI non seguono la cassa e hanno ciclo di aggiornamento proprio (ADR 0014); (e) A33 usa dati di bilancio, non di paga.
2. **FTE (SI1)**: non è una tabella ma un'unica domanda; la formula esatta resta da verificare.
3. **Riconciliazione**: confronto con SIOPE, non input.
4. **Il ticket #10** va corretto: SIOPE (non rendiconto) è la fonte normale; la numerazione 3-10 è ora confermata; Scheda A33 usa BDAP.

## Da verificare (aperti)

- Circolare e kit della rilevazione **2026**: non usciti a oggi.
- Elenco completo e numerazione anno per anno delle voci SICO per Tab. 12-14 del comparto Funzioni Locali (serve la circolare 2024, n. 18/2025: <https://www.rgs.mef.gov.it/_Documenti/VERSIONE-I/CIRCOLARI/2025/18/Circolare-del-19-giugno-2025-n-18.pdf>, già citata nel #10).
- Struttura delle celle del kit Excel (fogli, colonne): vedere un kit scaricato.
- Formula esatta delle FTE della SI1 e file «Elenco delle amministrazioni, con categorie e voci per gli FTE».
- Elenco completo delle squadrature/incongruenze (pp. 37-60 dell'Allegato), da trasformare in regole nel ticket di codice.
- Pagine esatte di alcune citazioni segnate «pagina da verificare» (stati del modello, fogli del kit).

## Fonti

- Circolare RGS 26/06/2026 n. 12, «Il Conto annuale 2025» (testo letto dal vault-pa; PDF ufficiale da riscontrare sul sito RGS)
- Allegato alla Circolare 26/06/2026 n. 12: <https://www.rgs.mef.gov.it/_Documenti/VERSIONE-I/CIRCOLARI/2026/12/Allegato-alla-Circolare-del-26-giugno-2026-n-12.pdf>
- Ricerca #10: `docs/research/adempimenti-non-stipendiali.md`, sezione A.
