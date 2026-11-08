# Trattenute a terzi: atto esterno trascritto, trattenuta sul netto, fermo sui concorsi

Pignoramenti, cessioni del quinto e delegazioni sono **atti esterni** trascritti (ADR 0012) sul rapporto o sui rapporti che colpiscono. L'atto porta tipo, creditore, importo totale o quota, data di notifica e decorrenza. Non passa per il fatto in attesa d'atto: lo adotta un terzo, non l'ente.

La **trattenuta a terzi** è un importo che una regola calcola sul netto, dopo le ritenute fiscali e i contributi. Nella composizione del pagamento è un versamento a terzi (ADR 0013). Ogni concorso non ancora modellato **ferma** il calcolo e nomina il caso: più pignoramenti, oppure una cessione insieme a un pignoramento.

Le fonti che Tristo-pignoratore cita sono confermate da Luca:

- art. 545 c. 4 e 5 c.p.c.;
- art. 72-ter DPR 602/1973, che diventa l'art. 171 D.Lgs. 33/2025;
- art. 48-bis DPR 602/1973, che diventa l'art. 144 D.Lgs. 33/2025;
- art. 68 DPR 180/1950.

Tre scelte del tool non poggiano su nessuna norma citata:

- cessioni comprese nella base del netto;
- accessorio e tredicesima allo stesso scaglione;
- riparto proporzionale.

Questi tre punti vanno a un ticket di ricerca prima di diventare regole. Lo stesso ticket controlla la decorrenza dei nuovi articoli.

Scelto da Luca il 06/11/2026 nel grilling del ticket #44, domande 6 e 15.

## Aggiornamento dopo la ricerca #48

Ricerca: `docs/research/trattenute-a-terzi.md`. Scelto da Luca l'08/11/2026 nel grilling del ticket #48, domande 1–5.

Per il dipendente di un ente locale i limiti vengono dal **DPR 180/1950** (art. 1 e art. 2), non dall'art. 545 c.p.c. da solo: l'art. 545 c. 6 fa salve le leggi speciali. Alle fonti si aggiungono gli artt. 2, 5, 69 e 70 DPR 180/1950 e l'art. 13 DPR 895/1950.

- **Netto dei limiti:** lordo del pagamento meno le sole ritenute di legge, cioè fiscali e contributi a carico della persona (art. 13 DPR 895/1950, esteso al pignoramento per lettura della stessa formula «al netto di ritenute»). Trattenute volontarie, cessioni e delegazioni non lo riducono: contano nei tetti complessivi. La scelta di Tristo sulle cessioni è **confermata** (art. 68 c. 2).
- **Misura sul singolo pagamento:** il quinto e le fasce dell'agente della riscossione si misurano sul netto di ogni pagamento, accessorio e tredicesima compresi. Nessun testo letto lo dice: è una **regola datata e rivedibile**, scelta perché la trattenuta si opera quando si paga.
- **Anteriorità tra istituti diversi:** tra cessione o delegazione e pignoramento vale chi è notificato prima, con i tetti degli artt. 68 e 69 (metà del netto meno la quota già vincolata, fermi i limiti dell'art. 2). Il riparto proporzionale di Tristo è **smentito** qui.
- **Più pignoramenti:** il calcolo resta fermo e nomina il caso. Il tetto complessivo è noto (un quinto, la metà con gli alimenti: art. 2 c. 2), il riparto no. Fermo anche a pari data di notifica.
- **Cessione e delegazione insieme:** tetto della metà del netto (art. 70). Oltre la metà solo con un atto esterno di **assenso dell'ente**, datato; senza, fermo. Il 40% della circolare MEF 2/2015, scritta per NoiPA, non si applica d'ufficio.
- **Agente della riscossione:** un decimo fino a 2.500 euro, un settimo fino a 5.000, oltre la misura ordinaria. La frazione si applica a **tutto l'importo**, non a scaglioni. Due testi datati con lo stesso contenuto: art. 72-ter DPR 602/1973 fino al 31/12/2026, art. 171 D.Lgs. 33/2025 dal 01/01/2027 (art. 243 c. 1 come modificato dall'art. 4 c. 4 DL 200/2025).
- **Blocco dei pagamenti** (art. 48-bis DPR 602/1973, poi art. 144 D.Lgs. 33/2025): non è una trattenuta ma una verifica prima di pagare. Va in un ticket a parte.

## Considered Options

- **Trattenuta come importo fisso inserito a mano** (così Tristo tratta la cessione): perde la derivazione e non sa nulla dei limiti.
- **Atto sulla persona invece che sul rapporto:** l'art. 545 riguarda somme del rapporto di lavoro. Dire quali rapporti colpisce è parte della trascrizione.
- **Decidere ora i tre punti senza fonte, come prassi:** una scelta sbagliata trattiene troppo o troppo poco a una persona.
- **Riparto e priorità generici tra concorsi:** senza le regole di concorso dal testo, il fermo è più sicuro.

## Consequences

- Il fatto entra nel registro con un lettore, la regola della trattenuta. La trascrizione resta manuale: canale senza standard, ricerca #7. Il ruolo dell'AI nella trascrizione resta nel punto aperto della mappa.
- Ordine sul netto: prima le ritenute fiscali e i contributi, poi le trattenute a terzi. La capienza dei recuperi fiscali (ADR 0019) si misura prima delle trattenute a terzi.
- Il quadro SY del 770 (somme liquidate a seguito di pignoramento presso terzi, art. 21 c. 15 L. 449/1997) riguarda chi paga in luogo del debitore. Quando il terzo è il datore di lavoro e trattiene sullo stipendio, applica le ritenute ordinarie e non compila SY (istruzioni 770/2026 via vault): **da verificare**.

**Da verificare** (dopo la ricerca #48)

- Testo dei DPR 180/1950 e 895/1950 su Normattiva: letti su una copia universitaria. Art. 545 c.p.c., 72-ter e 48-bis letti su riproduzioni; l'art. 171 è confrontato con la Gazzetta Ufficiale.
- Conversione del DL 200/2025: che non cambi la data del 01/01/2027.
- Riparto tra più pignoramenti e anteriorità del pignoramento (artt. 510-512, 543-547 c.p.c. non letti).
- Base delle fasce dell'agente della riscossione: il testo dice «importi», i commenti «netto».
- Significato di «cessione perfezionata» (art. 68 c. 2).
