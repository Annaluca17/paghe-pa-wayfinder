# IRAP degli enti locali: scadenza, riparto per regione, base per titolo

Ticket: #81 · Branch: `ticket-81-irap` · Data: 2026-11-07 · Serve a: ADR 0023 (paragrafo IRAP e «fermo dichiarato»), ADR 0016 (amministratori), ricerche `versamenti-f24ep.md` e `regimi-titolo-cifre-2026.md`

## Domanda

L'ADR 0023 tratta l'IRAP come un istituto a carico dell'ente: 8,5% sulla base retributiva, acconto mensile, codice 380E, con due fermi (scadenza e riparto per regione). La ricerca #51 ha lasciato aperti il decreto ministeriale della scadenza, il riparto per regione e alcune voci della base. Questo file prova a chiuderli sul testo vigente e dice che cosa resta aperto. Cinque temi: testo degli artt. 4, 10-bis, 16 e 30 D.Lgs. 446/1997; decreto della scadenza; riparto per regione; base per titolo; effetto dal 01/01/2027.

## Legenda e metodo

- **norma certa**: testo di legge o decreto letto per intero su Normattiva o in Gazzetta in questa sessione.
- **prassi**: circolare, risoluzione o istruzioni ufficiali dell'Agenzia delle Entrate o del MEF, lette sul documento.
- **da verificare**: non riscontrato su fonte primaria; è scritto che cosa è stato cercato.

Come sono state lette le fonti. Questa volta gli artt. 3, 4, 10-bis, 16 e 30 del D.Lgs. 446/1997 sono stati letti **parola per parola** scaricando la pagina del singolo articolo da Normattiva. Nella ricerca #51 lo strumento restituiva solo un riassunto: qui il testo è completo. Il **D.M. 2 novembre 1998, n. 421** è letto per intero su Normattiva (art. 1, 2, 3). Sono stati letti i PDF dell'Agenzia delle Entrate: risoluzioni 29/E del 2010, 367/E del 2007, 75/E del 2019, 378/E del 2008, tabella codici F24EP, istruzioni IRAP per le amministrazioni pubbliche (edizione 2006 e bozza 2026). Il **vault `vault-pa` non è stato consultato**: nessuna affermazione dipende da esso.

Limite da sapere: le istruzioni IRAP 2026 lette sono la **bozza** pubblicata a gennaio 2026 (copia di un editore), non il testo definitivo del provvedimento di approvazione. Dove contano, è scritto.

## Sintesi

1. **Testo vigente.** Aliquota 8,5% (art. 16 c. 2) e acconto mensile (art. 30 c. 5) sono confermati sul testo letterale. L'art. 30 c. 5 rinvia a un decreto: è il **D.M. 2 novembre 1998, n. 421** (GU n. 286 del 07/12/1998, in vigore dal 22/12/1998). **norma certa**
2. **Scadenza: c'è un conflitto da decidere.** Il D.M. 421/1998 dice **il 15** del mese successivo a quello di erogazione delle retribuzioni. La legge sull'F24EP (art. 4 c. 1-2 D.Lgs. 33/2025, dal 01/01/2027) dice **il 16** per le somme dell'F24EP, IRAP compresa. Un decreto non batte una legge: il 16 è la lettura più solida, ma nessun testo letto concilia i due. **norma certa** per i due testi, **da verificare** per la loro convivenza.
3. **Mese dell'acconto: mese di pagamento (cassa).** L'acconto è calcolato sulle retribuzioni **corrisposte** nel mese e versato il mese dopo (art. 30 c. 5; D.M. art. 2). **norma certa**. Quale mese scrivere nel campo «mese di riferimento» dell'F24EP non è detto dalle fonti lette: **da verificare**.
4. **Riparto per regione.** Si conta il personale **addetto con continuità a uffici o basi fisse in quella regione per almeno tre mesi** (art. 4 c. 2), non il domicilio del dipendente. **norma certa** e **prassi** (istruzioni). Il D.M. non dice come dividere ogni acconto mensile tra le regioni: **da verificare**.
5. **F24EP.** Codice 380E, sezione Regioni, codice regione dalla tabella T0 (2 cifre), mese `00MM`, anno `AAAA`, solo a debito. **prassi** (risoluzione 367/E del 2007 e tabella AdE).
6. **Aliquota.** L'8,5% **non può essere aumentato** dalle Regioni (art. 16 c. 3 rinvia solo ai commi 1 e 1-bis). Le Regioni a statuto ordinario possono però **ridurre le aliquote fino ad azzerarle** (art. 5 c. 1 D.Lgs. 68/2011), e le istruzioni IRAP citano una «minore aliquota» regionale. Quindi 8,5% è un massimo e un default, non una costante. **norma certa** + **prassi**.
7. **Base per titolo.** Stipendi: l'importo imponibile previdenziale. Assimilati (amministratori, LSU, co.co.co.): l'importo come determinato per l'IRPEF. **prassi**. Resta **da verificare** se i co.co.co. entrano al netto dei contributi a carico del collaboratore.
8. **Dal 01/01/2027.** Il D.Lgs. 33/2025 cambia i riferimenti del versamento (art. 4 al posto dell'art. 32-ter DL 185/2008). Il nuovo TUIR (D.Lgs. 117/2026) rinumera gli articoli che l'art. 10-bis richiama. Il D.Lgs. 147/2026 (tributi regionali e locali) tocca l'IRAP solo nel D.Lgs. 68/2011. Non esiste un testo unico che sostituisca il D.Lgs. 446/1997. **norma certa** per i testi letti; l'ultima frase è **da verificare** (vedi tema 5).

---

## Tema 1. Testo vigente degli artt. 4, 10-bis, 16 e 30 D.Lgs. 446/1997

Letti su Normattiva il 07/11/2026. Dove Normattiva ha tolto parole, il testo porta «((. . .))»: non sono omissioni nostre.

| Articolo e comma | Che cosa dice (riassunto, con citazione breve) | Marcatura |
|---|---|---|
| Art. 3 c. 1 lett. e-bis | Soggetti passivi sono le amministrazioni pubbliche dell'art. 1 c. 2 D.Lgs. 29/1993 (oggi D.Lgs. 165/2001, come scrivono le istruzioni AdE), e gli organi di Camera, Senato, Corte costituzionale, Presidenza della Repubblica | **norma certa** |
| Art. 4 c. 1 | L'imposta si applica sul valore della produzione «derivante dall'attività esercitata nel territorio della regione» | **norma certa** |
| Art. 4 c. 2 | Se l'attività è in più regioni, il valore è ripartito in proporzione alle retribuzioni del personale «a qualunque titolo utilizzato», compresi gli assimilati e i co.co.co., «addetto, con continuità, a stabilimenti, cantieri, uffici o basi fisse» operanti «per un periodo di tempo non inferiore a tre mesi» in ciascuna regione. Ultimo periodo: l'attività in altre regioni senza personale per almeno tre mesi si considera prodotta nella regione dove il soggetto è domiciliato | **norma certa** |
| Art. 4 c. 3 | Gli atti generali sul riparto li adotta il Ministero delle finanze, sentita la Conferenza Stato-Regioni | **norma certa**. Un atto generale sul riparto dei soli enti pubblici **non è stato trovato**: **da verificare** |
| Art. 10-bis c. 1 | Per i soggetti dell'art. 3 c. 1 lett. e-bis la base imponibile è l'ammontare delle «retribuzioni erogate al personale dipendente», dei redditi assimilati a quelli di lavoro dipendente, dei compensi di collaborazione coordinata e continuativa e di quelli di lavoro autonomo non abituale. Sono escluse le somme esenti da IRPEF per borse di studio (rinvio all'art. 47 c. 1 lett. c TUIR, testo di allora). Sempre escluse le borse di studio e gli interventi per il diritto allo studio universitario (L. 390/1991) | **norma certa** |
| Art. 10-bis c. 2 | Se l'ente ha anche attività commerciali può optare per la base dell'art. 5 su quelle; gli emolumenti si riducono della parte riferibile alle attività commerciali | **norma certa**. Fuori dal modello per ora (ente senza attività commerciale) |
| Art. 16 c. 2 | Per i soggetti della lett. e-bis, sul valore dell'attività non commerciale, determinato ai sensi dell'art. 10-bis, «si applica l'aliquota dell'8,5 per cento» | **norma certa** |
| Art. 16 c. 3 | Le Regioni possono variare «l'aliquota di cui al comma 1 e 1-bis» fino a 0,92 punti. Il comma 2 non è richiamato | **norma certa** |
| Art. 30 c. 5 | In deroga al c. 2, chi determina la base ai sensi dell'art. 10-bis c. 1 «versano l'acconto mensilmente» con modalità e termini stabiliti con decreto del Ministro delle finanze, in un importo pari all'aliquota del c. 2 applicata agli emolumenti «corrisposti nel mese precedente» | **norma certa**. Il comma 5 è nel testo vigente tra doppie parentesi (inserimento successivo): data e fonte dell'inserimento non lette |

Due note sul testo.

- L'art. 10-bis c. 1 richiama ancora gli articoli **47, 49 c. 2 lett. a e 81 c. 1 lett. l** del vecchio TUIR. Normattiva non li ha aggiornati. La corrispondenza con gli articoli attuali è di prassi (risoluzione 29/E del 2010: art. 50, art. 50 c. 1 lett. c-bis, art. 67 c. 1 lett. l). Dal 01/01/2027 cambia ancora: vedi tema 5.
- La base «retribuzioni erogate» è un criterio di **cassa**: lo dicono le istruzioni AdE («principio di cassa») e il D.M. («mese successivo a quello dell'erogazione»). **prassi** + **norma certa**.

## Tema 2. Scadenza dell'acconto mensile

### Il decreto dell'art. 30 c. 5

- **Atto:** decreto del Ministro delle finanze di concerto con il Ministro del tesoro, regolamento: **D.M. 2 novembre 1998, n. 421**, GU n. 286 del 07/12/1998, in vigore dal 22/12/1998. Sostituisce il primo decreto d'urgenza del 24/03/1998 (GU n. 71 del 26/03/1998). **norma certa** (testo letto su Normattiva).
- **Art. 2 c. 1:** i soggetti versano l'acconto «entro il giorno 15 del mese successivo a quello dell'erogazione delle retribuzioni e dei compensi», nelle misure dell'art. 16 c. 2. **norma certa**. L'art. 2 è in vigore dal 22/12/1998, mai modificato secondo la nota di Normattiva.
- **Art. 3:** il saldo, tenuto conto degli acconti mensili, si versa entro il termine della dichiarazione; le eccedenze possono essere fatte valere sui versamenti mensili successivi. **norma certa**
- **Art. 1:** il versamento è «in favore delle regioni e province autonome». Per gli enti che non sono tra quelli dei commi 2-5, c. 6: versamento unitario (F24 ordinario), solo se non si può usare l'«F24 Enti pubblici» (modifica dell'art. 4-quater c. 3 DL 34/2019). **norma certa**. Per queste ipotesi il codice è il 3858 (risoluzione 75/E del 2019), sezione Regioni, codice regione e mese `00MM`. **prassi**
- **Cosa non dice:** nessun criterio di divisione tra regioni, nessun arrotondamento, nessun codice. **norma certa** (assenza nel testo letto).

### Il 15 del decreto e il 16 della legge

| Fonte | Termine | Marcatura |
|---|---|---|
| D.M. 421/1998, art. 2 c. 1 | 15 del mese successivo | **norma certa** (regolamento, 1998) |
| Art. 4 c. 1-2 D.Lgs. 33/2025, dal 01/01/2027 | Per ritenute e **IRAP** versate con F24EP: «entro il giorno 16 del mese di scadenza»; se sabato o festivo, primo giorno lavorativo dopo | **norma certa** (testo letto, vigente dal 07/08/2026 nel testo del TU, efficacia dal 2027) |
| Art. 32-ter c. 2 DL 185/2008, fino al 31/12/2026 | Origine dell'art. 4 D.Lgs. 33/2025. Normattiva oggi mostra solo «articolo abrogato», con testo in vigore dal 01/01/2027 | **da verificare**: testo del 2026 non leggibile. Cercato su Normattiva, versione vigente |
| Istruzioni IRAP 2006 e bozza 2026 (AdE) | Le istruzioni 2006 ripetono «entro il giorno 15 del mese successivo»; la bozza 2026 non riporta la scadenza | **prassi** |
| Il Sole 24 Ore, Studio Sigaudo (già citati nella ricerca #51) | 16 | letture di terzi, **prassi** non confermata |

Lettura proposta: per gli enti dell'F24EP vale la **legge**, quindi il **16** con lo slittamento dei festivi. Il D.M. è un regolamento e la legge posteriore e speciale lo supera sul termine. Questa è un'**interpretazione**: nessuna circolare letta lo dice in modo espresso. Se il termine fosse davvero il 15 per l'IRAP, il versamento del 16 sarebbe tardivo di un giorno.

Perché è utile cercare ancora: la circolare AdE sull'art. 32-ter DL 185/2008 (anno 2009) e le istruzioni definitive IRAP. Non trovate in questa sessione.

### Mese a cui si riferisce l'acconto

- **Cassa.** L'importo è l'aliquota applicata agli emolumenti «corrisposti nel mese precedente» (art. 30 c. 5) rispetto al mese del versamento; il D.M. lo ripete con «mese successivo a quello dell'erogazione». Un emolumento pagato a marzo si versa entro il 16 aprile, qualunque sia il mese di competenza. **norma certa**
- **Mese scritto nell'F24EP.** La tabella AdE e la risoluzione 367/E dicono solo «mese di riferimento (00MM)». La risoluzione 75/E del 2019 per il codice 3858 dice solo «il mese di riferimento». Nessuno scrive se è il mese di pagamento delle retribuzioni o il mese del versamento. **da verificare**. La lettura più coerente con il testo è il **mese di pagamento** (quello dell'«erogazione»), ma è una lettura.

## Tema 3. Riparto per regione

### Dove si conta il personale

- Conta l'ufficio o la base fissa dove il dipendente è «addetto con continuità» per almeno tre mesi, non la residenza né il domicilio fiscale. **norma certa** (art. 4 c. 2). Le istruzioni AdE aggiungono che versare alla regione del domicilio fiscale del dipendente è un **errore tipico**, da correggere con comunicazione alla regione e girofondi della Ragioneria generale. **prassi** (istruzioni 2006 e bozza 2026).
- Il riparto è **proporzionale alle retribuzioni**: dipendenti nell'importo ai fini previdenziali (art. 12 L. 153/1969), assimilati compresi; co.co.co. nell'importo «contrattualmente spettante». **prassi** (bozza 2026).
- La parte di attività in regioni diverse dalla propria **senza personale per almeno tre mesi** va alla regione dove l'ente è domiciliato (art. 4 c. 2, ultimo periodo; istruzioni: «non si verifica la condizione per procedere al riparto»). **norma certa** + **prassi**.
- Personale in uffici **fuori dal territorio nazionale** per almeno tre mesi: non entra nella base (istruzioni, righi IK1-IK3). **prassi**. Per un comune è un caso raro.

### In quale regione si versa l'acconto mensile

- Le istruzioni, sezione di riparto, prevedono per **ogni regione** il totale degli «acconti mensili dovuti» e di quelli «effettuati». Quindi l'acconto mensile **si divide tra le regioni** secondo gli stessi pesi del riparto. **prassi** (bozza 2026, sezione III del quadro IR).
- Come si calcolano i pesi **ogni mese** (retribuzioni del mese, o quota dell'anno precedente, o dell'anno in corso) non è detto da nessuna fonte letta. **da verificare**. Cercato: D.M. 421/1998 (nessun criterio), istruzioni IRAP (solo il riparto annuale), risoluzione 367/E (solo compilazione).
- Un ente tutto in una regione, il caso comune, non ha problema: una riga, un codice regione.

### Come si scrive la regione nell'F24EP

- Codice **380E**, sezione **Regioni**. Colonna «Codice»: **codice regione, 2 byte, dalla tabella T0** (esempio ufficiale: `08` per il Lazio). «Estremi identificativi»: **non compilare**. Riferimento A: mese in formato `00MM`. Riferimento B: anno `AAAA`. Solo **a debito (D)**. In vigore dal 01/01/2008 (risoluzione 367/E del 12/12/2007). **prassi** (tabella AdE aggiornata al 01/04/2020, letta; la ricerca #51 la ha riscontrata anche nelle versioni 2025 e 2026). Il codice regione indica una **regione o provincia autonoma**; più regioni vogliono più righe.
- L'estremo «codice regione» sbagliato non invalida l'acconto, ma la somma finisce alla regione sbagliata: si corregge con la procedura delle istruzioni (comunicazione alla regione, girofondi). **prassi**

### Comando, convenzione, segretario su più enti

- **Distacco e comando.** Le istruzioni AdE dicono: in caso di distacco i relativi oneri concorrono alla base IRAP del soggetto **che impiega** il personale, e conta il **momento in cui questo rimborsa** gli oneri al distaccante; il distaccante non li tratta come retribuzione. Nel riparto, si escludono le retribuzioni del distaccato presso terzi e si includono quelle del personale di terzi impiegato in distacco. **prassi**. Che il **comando** della pubblica amministrazione valga come il distacco non è scritto nel testo letto: **da verificare**.
- **Segretario comunale in convenzione, segretario su più enti.** Nessuna fonte primaria trovata. Le fonti secondarie già raccolte in `regimi-titolo-cifre-2026.md` dicono: contributi e quota TFR divisi tra gli enti, IRAP all'ente che paga. **da verificare**. Come regola prudente, l'IRAP segue **chi eroga** la retribuzione (e chi rimborsa), come per il distacco.
- La regione del riparto è quella della **sede dove presta servizio**. Per un segretario che lavora in due sedi di regioni diverse, il riparto andrebbe fatto per sedi: nessuna fonte lo disciplina. **da verificare**.

### L'aliquota può essere diversa dall'8,5%?

| Punto | Esito | Marcatura |
|---|---|---|
| Le Regioni possono **aumentare** l'8,5% | No. L'art. 16 c. 3 rinvia ai commi 1 e 1-bis, non al comma 2 | **norma certa** (testo letto) |
| Seconda fonte indipendente per «non aumentabile» | MEF, Dipartimento delle Finanze, risoluzione DF 1/2021 (non aumentabile; riduzione non trattata), riportata da [Enti Locali Online](https://www.entilocali-online.it/irap-le-regioni-non-possono-modificare-laliquota-dell85-prevista-per-il-metodo-retributivo-adottato-dalle-amministrazioni-pubbliche/) | **prassi** da fonte secondaria. Il testo della risoluzione non è stato letto |
| Le Regioni a statuto ordinario possono **ridurre** le aliquote «fino ad azzerarle» e disporre detrazioni e deduzioni | Sì, in generale. Resta fermo il potere dell'art. 16 c. 3 | **norma certa**: art. 5 c. 1 D.Lgs. 68/2011 (testo letto su Normattiva, con la parola «detrazioni e» aggiunta dal D.Lgs. 147/2026). Se la riduzione vale anche per l'8,5% delle PA è letto solo nelle istruzioni |
| Le istruzioni ammettono una minore aliquota regionale per le PA | Sì: imposta = base × «8,5 per cento ovvero l'eventuale minore aliquota deliberata con legge regionale», e zero se la legge ha disposto «l'esenzione dal versamento» (art. 1 c. 299 L. 266/2005) | **prassi** (bozza 2026). L'art. 1 c. 299 non è stato riletto: **da verificare** |
| Dove sono le aliquote per regione | Il MEF le pubblica ogni anno da dati inviati dalle Regioni (art. 16 c. 3-bis; D.M. 30/03/2021, art. 1) sul sito `finanze.gov.it`, area «Fiscalità regionale e locale - IRAP» | **norma certa** per l'obbligo di pubblicazione; elenco regione per regione **non letto** |

**Seconda fonte per l'8,5%.** Il valore è su due fonti indipendenti: art. 16 c. 2 D.Lgs. 446/1997 (testo letto) e istruzioni IRAP AdE (bozza 2026: «aliquota d'imposta dell'8,5 per cento»). La seconda è una bozza di un editore: conferma limitata, ma coerente con la risoluzione DF 1/2021 di terzi.

## Tema 4. Base imponibile per titolo

Regola generale. Le istruzioni AdE e la risoluzione 29/E del 2010 dicono due cose distinte.

- **Dipendenti:** la retribuzione concorre per l'importo imponibile ai fini **previdenziali** (art. 12 L. 153/1969). Ciò che non è soggetto a contribuzione, come il TFR, non concorre. **prassi** (istruzioni, risoluzione 29/E del 2010, circolare 97/E del 1998 da essa citata).
- **Assimilati:** concorrono per l'importo determinato con le regole **dell'IRPEF**, a prescindere dalla rilevanza previdenziale (risoluzione 24/E del 2001, riportata dalla 29/E del 2010). **prassi**

| Titolo | Concorre alla base? Con quale importo? | Marcatura e fonte |
|---|---|---|
| **Stipendi dei dipendenti** | Sì, per l'imponibile previdenziale; il TFR no | **norma certa** per «retribuzioni erogate» (art. 10-bis); **prassi** per l'importo (istruzioni; risoluzione 29/E del 2010) |
| **Co.co.co.** | Sì. L'art. 10-bis li nomina espressamente. Le istruzioni li collocano tra gli assimilati: importo, per regola, quello dell'IRPEF; per il riparto, quello «contrattualmente spettante» | **norma certa** (concorrono); **prassi** (importo). **Al netto dei contributi a carico del collaboratore o no: da verificare.** Nessun documento letto lo scrive. Cercato: istruzioni 2006 e 2026, risoluzione 29/E del 2010, risoluzione 132/E del 2008 (solo il titolo, non letta). Gli artt. 51 e 52 del vecchio TUIR, che regolano l'importo IRPEF, non sono più leggibili su Normattiva: art. 52 «abrogato dal D.Lgs. 117/2026» |
| **Amministratori locali: indennità di funzione e gettoni** | Sì, come assimilati (art. 50 c. 1 lett. f e g TUIR; le istruzioni rinviano alla risoluzione 274/E del 2007) | **prassi**. La risoluzione 274/E non è stata letta: **da verificare** |
| **Indennità di fine mandato** | Sì. Concorre per l'importo imponibile IRPEF: indennità ridotta di **309,87 euro per ogni anno di mandato**. Il paragone col TFR non conta | **prassi**: risoluzione AdE 29/E del 15/04/2010, **letta sul PDF dell'Agenzia** (chiude il «da verificare» della ricerca #51). Il motivo: gli assimilati si assumono nell'importo IRPEF, e per la tassazione separata vale l'art. 19 c. 2-bis TUIR di allora |
| **Oneri a carico dell'ente (art. 86 TUEL, quota forfettaria, oneri in aspettativa)** | Non sono retribuzioni erogate al lavoratore | Nessuna fonte letta li colloca nella base. **da verificare** |
| **LSU (lavori socialmente utili)** | I compensi dei soggetti in LSU sono redditi **assimilati** al lavoro dipendente (art. 50 c. 1 lett. l TUIR; risoluzione 378/E del 2008, letta). Per l'art. 10-bis, quindi, concorrono **se li paga l'ente**. L'assegno pagato direttamente dall'INPS non è erogato dall'ente | **prassi** per l'assimilazione. Che l'IRAP sia dovuta sulla sola integrazione a carico dell'ente è una **deduzione**: nessuna risoluzione IRAP sulle LSU trovata. **da verificare** |
| **Borse di studio** | Escluse: le somme esenti IRPEF di borse di studio o assegni, e le borse del diritto allo studio universitario (L. 390/1991) | **norma certa** (art. 10-bis c. 1). Una borsa tassata IRPEF (non esente) va nella base per lettura dell'art. 10-bis: **prassi** (istruzioni IK2) |
| **Lavoro autonomo occasionale** | Sì (art. 67 c. 1 lett. l TUIR); la bozza 2026 include i redditi per obblighi di fare, non fare, permettere | **norma certa** + **prassi** |
| **Interinali** | Gli oneri concorrono alla base | **prassi** (istruzioni) |
| **Premi e rimborsi INAIL, contributi a carico ente** | Non sono retribuzione erogata; non concorrono | Lettura del testo, nessuna fonte esplicita. **da verificare** |

**Effetto utile per il modello.** I co.co.co. sono materia di scelta: la quota di contributo a carico del collaboratore vale circa un terzo dell'aliquota (circa 11% del compenso con l'aliquota piena della circolare INPS 8/2026, calcolo nostro), cioè circa un punto di IRAP sul compenso. Differenza piccola ma sistematica.

## Tema 5. Effetto dal 01/01/2027

- **D.Lgs. 33/2025** (testo unico versamenti e riscossione). L'IRAP degli enti dell'F24EP è nell'**art. 4 c. 1**, la scadenza nell'art. 4 c. 2 (letto, vigente dal 07/08/2026 per l'ultima modifica), il versamento unitario dell'IRAP nell'**art. 3 c. 5 lett. d** (letto). **norma certa**. Non cambia il contenuto: cambia il riferimento, come già nella tabella della ricerca #51 (art. 32-ter DL 185/2008 diventa art. 4).
- **Art. 4 c. 2 D.Lgs. 33/2025** dice «giorno 16 del mese di scadenza»: per l'IRAP resta il conflitto col 15 del D.M. 421/1998 (tema 2). L'art. 240 del D.Lgs. 33/2025 elenca le abrogazioni che restano: non cita né il D.Lgs. 446/1997 né il D.M. 421/1998 (letto). **norma certa** per quella lista. Che nessun altro articolo del TU incida sul D.M. è **da verificare**: letti solo gli artt. 3, 4, 8, 11, 239, 240 e 241.
- **D.Lgs. 147/2026** (7 agosto 2026, GU n. 185 dell'11/08/2026, vigente dal 12/08/2026), «tributi regionali e locali e federalismo fiscale regionale». L'art. 23 modifica l'art. 5 del D.Lgs. 68/2011 (aggiunge «detrazioni e» al c. 1 e abroga il c. 3). Non modifica gli artt. 4, 10-bis, 16 e 30 del D.Lgs. 446/1997. Chiama l'IRAP fonte di finanziamento delle regioni «fino alla data della sua sostituzione con altri tributi». **norma certa** (testo letto in PDF; Normattiva, ELI 2026/08/11/26G00168). Il testo è lungo: letti i passi con «IRAP» e «446».
- **D.Lgs. 117/2026** (nuovo TUIR, dal 01/01/2027). Normattiva mostra già l'art. 52 del vecchio TUIR come abrogato dal D.Lgs. 117/2026. Gli articoli richiamati dall'art. 10-bis (47, 49, 81) cambiano numero. Se esiste una norma di rinvio che aggiorna d'ufficio l'art. 10-bis non è stato verificato. **da verificare**. Il D.Lgs. 33/2025 usa già la numerazione nuova («articolo 51, comma 2, lettera a», art. 3 c. 5 lett. g).
- **Testo unico dell'IRAP.** Non trovato né sul sito delle norme né nei decreti letti. Il D.Lgs. 446/1997 risulta ancora il testo vigente su Normattiva. **da verificare** (cercato: Normattiva, D.Lgs. 147/2026, D.Lgs. 33/2025).

## Esito per il grilling

1. **Termine dell'acconto mensile: 15 o 16.** Opzioni: (a) 16 con slittamento dei festivi, come le altre righe dell'F24EP; (b) 15 del D.M. 421/1998; (c) regola datata con due fonti, 15 e 16, e il modello avvisa se la data cade tra le due. Raccomandazione: **(a)**, perché la legge sull'F24EP prevale sul regolamento e così il modello sbaglia solo in anticipo; la nota sul 15 resta **da verificare** nell'ADR.
2. **Mese scritto nel riferimento dell'F24EP.** Opzioni: (a) mese di pagamento delle retribuzioni; (b) mese del versamento; (c) mese di competenza. Raccomandazione: **(a)**, perché l'acconto segue la cassa dell'«erogazione» (art. 30 c. 5 e D.M. art. 2); da riscontrare su un F24EP storico dell'ente prima di scrivere la regola.
3. **Dove si conta il personale.** Opzioni: (a) fatto datato di **sede di lavoro** sul rapporto, con la regione ricavata dalla sede; (b) regione dell'ente per tutti; (c) domicilio del dipendente. Raccomandazione: **(a)**, perché è il criterio dell'art. 4 c. 2, il domicilio è un errore noto; la sede ferma la delega se manca.
4. **Soglia dei tre mesi.** Opzioni: (a) il modello usa la regione della sede al mese di pagamento e segnala il cambio di sede; (b) applica la soglia come regola mese per mese; (c) la lascia alla dichiarazione annuale. Raccomandazione: **(a)**, perché la soglia è un concetto annuale e il saldo è fuori ambito; il cambio di sede sotto i tre mesi diventa un avviso.
5. **Divisione dell'acconto tra più regioni.** Opzioni: (a) pesi del mese (retribuzioni pagate per sede); (b) pesi dell'anno precedente; (c) ente in più regioni fuori ambito per ora, con fermo. Raccomandazione: **(c)** finché non c'è una fonte sul calcolo mensile (**da verificare**); il caso di una sola regione, quasi tutti i comuni, resta senza fermo.
6. **Aliquota.** Opzioni: (a) 8,5% fisso; (b) 8,5% come massimo e default, con regola datata per regione e fonte la tabella MEF; (c) 8,5% con fermo se la tabella MEF della regione non lo conferma. Raccomandazione: **(b)**, perché le Regioni possono ridurre e azzerare ma non aumentare; (c) solo se Luca vuole zero rischio sulle regioni a statuto speciale.
7. **Fermo dichiarato: da due a uno.** Opzioni: (a) togliere il fermo «scadenza» (c'è il decreto) e tenere solo «riparto per regione» quando manca la sede o le sedi sono in più regioni; (b) tenere entrambi; (c) togliere entrambi. Raccomandazione: **(a)**, perché il decreto è stato individuato e l'unica incertezza di scadenza è il 15 contro il 16, che è un avviso, non un fermo.
8. **Co.co.co.: importo che entra nella base.** Opzioni: (a) compenso lordo; (b) compenso al netto dei contributi a carico del collaboratore, come per il reddito IRPEF dei dipendenti. Raccomandazione: **(a)** finché la fonte non c'è, perché è il valore «contrattualmente spettante» delle istruzioni; è una scelta prudente, da rivedere (circa un punto di IRAP in più sul compenso). Segnare il punto **da verificare**.
9. **Titoli senza fonte esplicita: LSU, oneri art. 86 e rimborsi, segretario in convenzione, comando.** Opzioni: (a) tutti nella base con marcatura «prassi da verificare»; (b) fermo del calcolo finché non c'è fonte; (c) chi eroga o rimborsa paga l'IRAP (distacco). Raccomandazione: **(c)** per comando e convenzione, **(a)** per le LSU integrate dall'ente, e **fuori base** gli oneri dell'art. 86; ogni caso con la sua nota nell'ADR 0016.
10. **Enti fuori dall'F24EP (codice 3858, D.M. art. 1 c. 6).** Opzioni: (a) fuori ambito, con dato dell'ente che dice quale modello usa; (b) il modello emette anche il 3858. Raccomandazione: **(a)**, perché l'ADR 0013 limita l'F24EP al target e la differenza è solo di codice.
11. **Riferimenti normativi dal 01/01/2027.** Opzioni: (a) regola datata con due fonti: art. 32-ter DL 185/2008 e art. 4 D.Lgs. 33/2025; (b) solo la fonte nuova da subito. Raccomandazione: **(a)**, come già deciso con l'ADR 0022; l'art. 10-bis resta citato col vecchio TUIR e col nuovo da 2027, una riga di tabella.

## Personale e somme escluse dalla base IRAP (metodo retributivo)

Domanda: per un ente col metodo dell'art. 10-bis, quali persone o somme restano fuori dalla base, o si deducono? Fonti lette in questa sessione: art. 11 D.Lgs. 446/1997 su Normattiva (letto **in sintesi**, non parola per parola: lo strumento non restituisce il testo intero) e istruzioni IRAP 2026 **bozza** (PDF, sezione «amministrazioni pubbliche», righi IK1-IK4 e IS7), già citate sopra. Non lette: risoluzioni AdE 142/E del 2004, 64/E e 139/E del 2006 (disabili), 327/E del 2007 (avvocatura), 274/E del 2007. Il vault non è stato usato.

Regola di base. L'art. 10-bis c. 1 costruisce una base di **cassa** fatta di somme erogate: righi IK1 (dipendenti), IK2 (assimilati), IK3 (lavoro autonomo occasionale). Le **deduzioni** non sono nella base: stanno nel rigo IK4 e si sottraggono dopo. Quindi «escluso» e «dedotto» sono due cose diverse nel modello: la prima non entra nel calcolo, la seconda entra e poi esce.

| Categoria | Trattamento | Fonte e marcatura |
|---|---|---|
| **Disabili** (L. 68/1999 o L. 482/1968) | **Deducibili** le spese per il personale disabile impiegato nel periodo, per intero. Vale per le PA: l'art. 11 c. 1 lett. a n. 5 richiama espressamente chi determina la base con l'art. 10-bis c. 1, e le istruzioni lo mettono nel rigo IK4 colonna 2. La somma sta prima nella base (IK1) e poi si deduce (IK4) | Rinvio dell'art. 11 a 10-bis c. 1: **norma certa** nel contenuto, ma testo letto in sintesi. Rigo IK4: **prassi** (istruzioni 2026, bozza). Dettaglio dei limiti (risoluzioni 64/E e 139/E del 2006): **da verificare**, non lette |
| **Apprendisti** | Deducibili per intero come i disabili, stesso rigo IK4 colonna 2 | **norma certa** (art. 11, in sintesi) + **prassi** (IK4) |
| **Contratti di formazione e lavoro** | Deducibili, rigo IK4 colonna 3. Per una PA oggi è un caso raro | **norma certa** (in sintesi) + **prassi** (IK4) |
| **Personale addetto a ricerca e sviluppo** | Il n. 5 prevede una deduzione per questo personale, ma il rigo IK4 delle PA **non** ha una colonna per esso (ha solo ricercatori e docenti rientrati dall'estero, art. 44 DL 78/2010, col. 1, con limiti de minimis). Non risulta applicabile alle PA | **da verificare**: letto solo il riassunto del n. 5, che lo lega ai soggetti delle lett. a-e dell'art. 3. Il testo parola per parola va riletto. Nessuna prassi favorevole alle PA trovata |
| **Deduzione costo del lavoro a tempo indeterminato (art. 11 c. 4-octies)** | **Non vale** per il metodo retributivo. Le istruzioni (rigo IS7) la riconoscono ai soggetti degli artt. 5-9. Nel quadro IK compare solo in IK20 col. 5 e IK24 col. 4, cioè per la sezione delle attività commerciali con opzione e per l'agricoltura. Nessun cambio nel 2025-2026 trovato nel testo letto (ultima modifica: DL 73/2022) | **prassi** (IS7 e IK20) + **norma certa** (rinvio agli artt. 5-9, in sintesi). Altre deduzioni generali (c. 4-bis, 4-bis.1): per le lett. a-e dell'art. 3 e per chi ha ricavi bassi, non per la lett. e-bis: **da verificare** sul testo |
| **Contributi INAIL** | Per la sezione IK delle PA non c'è un rigo di deduzione in IK4. Gli oneri a carico dell'ente non sono retribuzione erogata e restano fuori dalla base | Lettura del testo: **da verificare**. Il n. 1 INAIL compare solo nelle sezioni commerciali (IK20 col. 2) |
| **Borse di studio esenti IRPEF** | **Escluse** dalla base (somme art. 50 c. 1 lett. c TUIR esenti) | **norma certa** (art. 10-bis c. 1) + **prassi** (IK2) |
| **Borse e interventi per il diritto allo studio universitario (L. 390/1991)** | **Escluse** sempre, se erogate da regioni, province autonome, organismi regionali o università | **norma certa** + **prassi** (IK2). Per un comune è un caso raro |
| **TFR** | **Escluso**: non è soggetto a contribuzione, e per i dipendenti conta solo l'imponibile previdenziale | **prassi** (IK1: «ad esempio T.f.r.»). L'art. 10-bis non lo dice in modo espresso |
| **TFS, indennità premio di servizio, buonuscita** | Stessa logica del TFR (non imponibile previdenziale), quindi fuori dalla base. Nessun documento letto li nomina | **da verificare** (deduzione per analogia con la riga sul TFR) |
| **Indennità di fine mandato (amministratori)** | **Dentro**, come assimilato, ridotta di 309,87 euro per anno di mandato (vedi tema 4) | **prassi** (risoluzione 29/E del 2010, già letta) |
| **Indennità di trasferta e rimborsi spese** | Concorrono solo per la parte che è imponibile previdenziale. Se il rimborso è fuori dall'imponibile previdenziale (limiti di legge), resta fuori. Le istruzioni non li nominano per le PA | **da verificare**. Lettura dalla regola «imponibile ai fini previdenziali» (IK1). Per gli assimilati vale l'importo IRPEF: **da verificare** nel caso dei rimborsi |
| **Somme non erogate** (es. giorni di sciopero, pur assoggettati a contributi) | **Fuori** dalla base: conta l'erogazione | **prassi** (IK1) |
| **Arretrati di anni precedenti** | Il criterio è di **cassa**: conta quando sono pagati, non l'anno di competenza. Quindi un arretrato pagato nel 2026 entra nella base del 2026, per l'importo imponibile previdenziale. Nessun testo letto fa eccezioni | **prassi** (IK1: «principio di cassa») + **norma certa** («retribuzioni erogate»). Applicazione agli arretrati: **da verificare** |
| **Personale in comando** | L'IRAP la paga chi eroga la retribuzione e chi rimborsa nel momento del rimborso: resta come regola prudente. Un testo che dica «comando = distacco» non è stato letto | **da verificare** |
| **Personale in distacco** | Gli oneri concorrono alla base **dell'ente che impiega** il distaccato, e conta il momento in cui rimborsa il distaccante. Nel riparto, le retribuzioni del distaccato presso terzi si escludono | **prassi** (IK1; riparto già in tema 3) |
| **Rimborsi tra enti (quota stipendio al comune ospite)** | Segue il distacco: concorre all'ente che rimborsa, nell'anno del rimborso. Il distaccante non lo conta due volte | **prassi** per il distacco; applicazione ai rimborsi di convenzione: **da verificare** |
| **Personale interinale** | Gli oneri concorrono alla base (rigo IK1) | **prassi** |
| **Avvocatura interna** | I compensi professionali concorrono come retribuzioni (risoluzione 327/E del 2007, citata nelle istruzioni, non letta) | **prassi** (istruzioni) |
| **Uffici all'estero per almeno tre mesi** | Le somme **non** vanno in IK1, IK2, IK3 | **prassi** (istruzioni, già in tema 3). Qui «fuori del territorio nazionale»; per un comune è caso raro |
| **Attività commerciale con opzione (art. 10-bis c. 2)** | Gli emolumenti si riducono della parte riferibile all'attività commerciale (importo specifico oppure quota ricavi / entrate correnti). Chi opta passa all'art. 5 per quelle attività (opzione nel quadro IS, rigo IS34). Stessa quota per le spese di IK4 | **norma certa** (art. 10-bis c. 2) + **prassi** (istruzioni). Fuori dal modello per ora |

Cose da non confondere.

- **Escluso non vuol dire dedotto.** Le borse di studio e il TFR non entrano nel conto. Disabili e apprendisti entrano (sono stipendi) e poi si deducono in IK4. Per il programma sono due regole diverse: un filtro sul titolo e una deduzione sul lavoratore.
- **Il disabile conta due volte** nel flusso dati: la retribuzione va in IK1 per intero, la deduzione in IK4 per le spese relative a lui. Se la spesa deducibile supera la retribuzione, lo scoperto non è indicato dalle istruzioni PA: **da verificare**.
- **Le istruzioni sono una bozza.** Le citazioni dei righi vengono dal file di gennaio 2026; la versione definitiva può cambiare i numeri dei righi, difficilmente la regola.

### Esito per il grilling

1. **Disabili, apprendisti, CFL: dedurre o no.** Opzioni: (a) il modello calcola la base lorda IK1+IK2+IK3 e mostra la deduzione IK4 se il dato del lavoratore dice «disabile» o «apprendista»; (b) ignora la deduzione; (c) segnala solo un avviso. Raccomandazione: **(a)**, perché la fonte è chiara (art. 11 c. 1 lett. a n. 5, rigo IK4) e il dato è un fatto datato sul rapporto; limiti fini (risoluzioni 64/E e 139/E) **da verificare** prima di fissare la regola.
2. **R&D e art. 11 c. 4-octies.** Opzioni: (a) non applicarli al metodo retributivo; (b) applicarli; (c) fermo. Raccomandazione: **(a)**, perché il 4-octies è escluso dalle istruzioni (IS7) e il R&D non ha rigo nel quadro PA; segnare la rilettura del testo parola per parola dell'art. 11 come **da verificare**.
3. **Titoli fuori base e arretrati.** Opzioni: (a) filtro sul titolo (borse esenti, TFR, TFS, somme non erogate fuori) e cassa per gli arretrati; (b) filtro e arretrati per competenza; (c) tutto in base con avviso. Raccomandazione: **(a)**, perché il principio di cassa e l'esclusione del TFR sono nelle istruzioni; TFS, trasferte e arretrati restano «prassi da verificare» nell'ADR.
4. **Comando e rimborsi tra enti.** Opzioni: (a) IRAP a chi eroga e a chi rimborsa, come il distacco; (b) sempre all'ente di appartenenza; (c) fermo. Raccomandazione: **(a)** per coerenza con la regola scritta sul distacco, con nota «comando non letto» nell'ADR 0016.

## Fonti

Fonti primarie lette.

- D.Lgs. 446/1997, artt. 3, 4, 10-bis, 16, 30: [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:1997-12-15;446). Testo letto articolo per articolo il 07/11/2026.
- D.M. 2 novembre 1998, n. 421 (GU n. 286 del 07/12/1998): [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:ministero.economia.finanze:decreto:1998-11-02;421).
- DL 34/2019, art. 4-quater c. 3 (modifica del D.M. 421/1998): [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legge:2019-04-30;34~art4quater).
- D.Lgs. 33/2025, artt. 3, 4, 8, 240: [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2025-03-24;33:1~art4). DL 185/2008 art. 32-ter e D.Lgs. 241/1997 art. 18: stato «abrogato dal 01/01/2027» su Normattiva.
- D.Lgs. 68/2011, art. 5: [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2011-05-06;68~art5).
- D.Lgs. 147/2026 (GU n. 185 dell'11/08/2026), art. 23: [Normattiva ELI](https://www.normattiva.it/eli/id/2026/08/11/26G00168/ORIGINAL), PDF letto da [ANCE](https://ance.it/wp-content/uploads/allegati/decreto_legislativo_147-2026.pdf).
- D.Lgs. 117/2026 (nuovo TUIR): stato dell'art. 52 del vecchio TUIR su Normattiva.
- Decreto MEF-DF 30/03/2021 (pubblicazione dati IRAP regionali): [finanze.gov.it](https://www.finanze.gov.it/export/sites/finanze/.galleries/Documenti/Fiscalita-locale/DECRETO-IRAP-30-marzo-2021.pdf).

Prassi letta.

- Risoluzione AdE 29/E del 15/04/2010: [PDF AdE](https://www.agenziaentrate.gov.it/portale/documents/20143/305373/Ris+29+del+15+04+10_ris.+n.+29+del+15+aprile+2010.pdf/6fa617db-b56b-01ad-9080-0a0ecb5c4061).
- Risoluzione AdE 367/E del 12/12/2007 (codici F24EP): [PDF AdE](https://www.agenziaentrate.gov.it/portale/documents/20143/306263/Risoluzione+n+367+del+12+dicembre+2007_risoluzione_367_12_dic_2007.pdf/7887e35f-3960-3fd6-cca6-35cd1a8b6b89).
- Risoluzione AdE 75/E del 09/08/2019 (codice 3858): [copia](https://www.misterfisco.it/wp-content/uploads/2014/04/risoluzione-n.-75.pdf).
- Risoluzione AdE 378/E del 10/10/2008 (LSU): [PDF AdE](https://agenziaentrate.gov.it/portale/documents/20143/305947/Risoluzione+n+378+2008_risoluzione378Edel10ott2008.pdf/327a3a8c-ac87-d5a6-e182-92da0a428679).
- Tabella codici F24EP (aggiornata al 01/04/2020): [PDF AdE](https://www.agenziaentrate.gov.it/portale/documents/20143/448330/Tabella+codici+tributo+F24EP+aggiornata+01-04-2020.pdf/eab36abb-0da5-765e-a305-bb4d6c35d7cb).
- Istruzioni IRAP, amministrazioni pubbliche, periodo 2005: [PDF AdE](https://www.agenziaentrate.gov.it/portale/documents/20143/329373/Istruzioni_Irap_AP_istr.pdf/ea603605-4e5c-99a8-cf67-899b72c5242d).
- Istruzioni IRAP 2026, **bozza** (copia di editore): [Ipsoa](https://www.ipsoa.it/~/media/Quotidiano/2026/01/31/dichiarazioni-fiscali-2026-aggiornati-i-modelli-in-bozza/N_FIS_30012026_IRAP_2026_istruzioni%20pdf.ashx).

Letture di terzi, non primarie.

- [Enti Locali Online](https://www.entilocali-online.it/irap-le-regioni-non-possono-modificare-laliquota-dell85-prevista-per-il-metodo-retributivo-adottato-dalle-amministrazioni-pubbliche/) sulla risoluzione DF 1/2021 (non letta).
- [Fisco e Tasse](https://www.fiscoetasse.com/rassegna-stampa/27244-versamento-acconto-mensile-dell-irap-enti-e-pa.html) sulla risoluzione 75/E del 2019.

## Punti ancora da verificare (elenco)

- Testo del 2026 dell'art. 32-ter c. 2 DL 185/2008 e prassi AdE che concili il 15 del D.M. 421/1998 col 16.
- Mese da scrivere nel riferimento A dell'F24EP per il 380E.
- Pesi mensili di divisione tra più regioni; atti generali dell'art. 4 c. 3.
- Co.co.co. al netto dei contributi a carico del collaboratore.
- Risoluzione 274/E del 2007 (amministratori); risoluzione DF 1/2021 sul testo; art. 1 c. 299 L. 266/2005; elenco aliquote regionali MEF.
- Comando e convenzione (segretario): nessuna fonte primaria.
- LSU: nessuna risoluzione IRAP specifica.
- Istruzioni IRAP 2026 definitive; rinvio del nuovo TUIR sull'art. 10-bis; altri articoli del D.Lgs. 33/2025 che toccano il D.M. 421/1998.
