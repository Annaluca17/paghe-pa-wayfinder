# CU e 770 sono viste del modello; Verifica 770 diventa il controllo

La CU e il 770 nascono dal modello come **viste**, e ogni invio produce un **esito dichiarato**. Il collegamento tra istituto e punto CU è una **mappatura datata**, come la voce SICO e il codice tributo (ADR 0015): quando la numerazione cambia, cambia la mappatura e non l'istituto. I dati che le estrazioni del gestionale non danno sono fatti del registro con un lettore:

- nascita e domicilio;
- date e giorni;
- gestioni previdenziali;
- eredi;
- dati del conguaglio.

I file telematici seguono le **specifiche tecniche ufficiali dell'AdE** di ogni anno e si validano con il programma di controllo dell'AdE.

Verifica 770 non è più il generatore. Legge il file prodotto dal modello e ne controlla le quadrature (770 con CU e F24EP), come controllo indipendente. Cede al modello ciò che sa del tracciato e degli agganci, da riscontrare sulle specifiche.

Scelto da Luca il 06/11/2026 nel grilling del ticket #44, domande 5 e 16.

## Considered Options

- **Il modello produce un insieme di dati neutro, Verifica 770 genera il file al posto del txt Halley:** il modello dipenderebbe da un tracciato ricostruito dal programma di controllo e fermo al 2026.
- **Verifica 770 resta com'è:** parte dalla CU di Halley e senza di essa non scrive il file. La CU non la genera nessun tool, quindi andrebbe costruita comunque.
- **Il tracciato di Verifica 770 come riferimento del modello:** è ricostruito, non ufficiale, e i suoi agganci voce-punto e voce-tributo sono empirici, senza una norma citata.

## Consequences

- Dal 01/01/2027 la numerazione di articoli e lettere del Testo Unico cambia le tipologie e le causali della CU (ricerca `regimi-titolo-compenso.md`, sezione 13). La mappatura datata lo assorbe. La CU 2027 non è ancora pubblicata.
- Il **controllo di completezza degli output** (ADR 0015) vale anche per CU e 770: un importo pagato senza punto CU ferma l'invio, non il calcolo.
- Una correzione dopo l'invio è una nuova vista confrontata con l'ultimo esito: CU sostitutiva o annullamento, nei termini del provvedimento dell'anno.
- Fuori da questo ADR, e dal ticket #44: SY (pignoramenti presso terzi liquidati dal sostituto), SF e DI restano da decidere quando avranno un lettore. Il 770 in forma semplificata (art. 16 D.Lgs. 1/2024) va verificato per il target.
- Gli ID di Verifica 770 (v3.77) da riscontrare: righi SX 1, 2, 4, 32-34, 49 e 50; punti 361, 374, 375, 449, 718 e 719.
- Il README e i commenti del repo di Verifica 770 contengono dati reali: non si copiano.

**Norma certa**

- Termini: CU entro il 16 marzo e 770 entro il 31 ottobre (art. 4 c. 4-bis DPR 322/1998), riportati dal vault dal Provvedimento CU 2026 e dalle istruzioni 770/2026. Prima di fissarli come parametri va riscontrato il testo.

**Da verificare**

- Le specifiche tecniche CU 2027 e 770/2027, quando escono.
