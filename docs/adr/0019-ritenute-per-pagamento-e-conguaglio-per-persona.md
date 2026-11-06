# Ritenuta per pagamento, imponibile fiscale per persona, conguaglio per differenza

Il modello calcola le ritenute IRPEF come dice la norma, non con un metodo progressivo. Ogni pagamento ha la propria **ritenuta**: si calcola sulle somme pagate nel periodo di paga, con gli scaglioni annui ragguagliati al periodo. Le detrazioni sono rapportate allo stesso periodo. Il **conguaglio fiscale** è un calcolo distinto. Una proiezione del conguaglio è sempre visibile come avviso e non cambia le ritenute.

L'imposta riguarda la persona. Una base nuova, l'**imponibile fiscale**, somma per persona e **anno d'imposta** gli esiti pagati di tutti i suoi rapporti con l'ente, ciascuno con la sua categoria di reddito. La ritenuta è un importo sul rapporto del pagamento in cui è operata, e la sua derivazione risale al cumulo. L'anno d'imposta si ricava dalla data di pagamento. Ogni **categoria di reddito** dichiara, con date e riferimento, se per lei vale la cassa allargata (somme pagate entro il 12 gennaio attribuite all'anno prima). L'anno si calcola sulla valuta prevista e si congela nell'esito pagato.

Le detrazioni, l'aliquota più alta chiesta dalla persona e i redditi di altri sostituti da conguagliare vengono dalla **dichiarazione del sostituito**. È un fatto della persona, con validità e documento di origine. Se manca, il modello calcola senza detrazioni e lo segnala, senza fermarsi. Se la persona ha redditi da lavoro dipendente e da carica elettiva, le due detrazioni non si sommano. Il modello applica la più favorevole sul reddito complessivo, salvo una scelta diversa scritta nella dichiarazione.

Il conguaglio di fine anno si calcola in automatico sull'ultimo pagamento attribuito all'anno. Se poi un fatto cambia il dovuto (CU di un altro sostituto, comunicazione di un ente secondario, un arretrato), il modello fa un nuovo conguaglio per differenza entro il 28 febbraio. Quel conguaglio è attribuito all'anno precedente, e gli esiti già fissati non cambiano. Alla cessazione il conguaglio si fa sul pagamento finale. Ogni pagamento successivo nello stesso anno porta un nuovo conguaglio per differenza.

Scelto da Luca il 06/11/2026 nel grilling del ticket #44, domande 1-4 e 7-14.

## Considered Options

- **Ritenuta progressiva** (a ogni pagamento l'imposta dell'anno fino a quel giorno, meno le ritenute già operate): conguaglio quasi nullo, ma è una prassi senza testo. Inoltre cambia la ritenuta di un mese per fatti che riguardano mesi diversi.
- **Imponibile per rapporto:** l'imposta e il conguaglio sono della persona, e due rapporti con lo stesso ente darebbero due scaglioni.
- **Cassa allargata per istituto:** la regola dipende dal tipo di reddito, non dall'elemento retributivo.
- **Fermo senza dichiarazione del sostituito:** bloccherebbe ogni nuovo assunto prima della consegna del modulo. Senza dichiarazione la norma non dà le detrazioni, non sospende la ritenuta.
- **Sempre la detrazione dell'art. 13 c. 1, oppure solo la scelta della persona:** la prima può danneggiare la persona, la seconda lascia il caso senza risposta finché la persona non sceglie.
- **Pagamento di conguaglio indicato ogni volta dall'ufficio:** un passaggio manuale ogni anno per ogni persona, senza una scelta reale da fare.
- **Aliquota provvisoria per la tassazione separata, se manca il reddito del biennio:** una ritenuta su un numero inventato, lasciata alla riliquidazione dell'AdE.

## Consequences

**Norma certa**

- Ritenuta del periodo di paga, scaglioni ragguagliati, detrazioni a richiesta: art. 23 c. 2 lett. a) DPR 600/1973. Per gli assimilati: art. 24 c. 1, che rinvia all'art. 23 in quanto compatibile.
- Conguaglio entro il 28 febbraio o alla cessazione. Incapienza con dichiarazione scritta e interesse dello 0,50% mensile: art. 23 c. 3 (ricerca `differenze-errore-ente.md`, finding 7).
- Detrazione dell'art. 13 c. 5 TUIR «non cumulabile con quelle previste ai commi 1, 2, 3 e 4», letta su Normattiva al 06/11/2026.
- Cassa allargata: art. 51 c. 1 TUIR, dal 01/01/2027 art. 53 c. 1 TU D.Lgs. 117/2026.
- Dal 01/01/2027 l'art. 23 diventa l'art. 33 D.Lgs. 33/2025 e l'art. 24 l'art. 34 (ricerca `regimi-titolo-compenso.md`, sezione 13). Il testo si sceglie in base all'anno d'imposta del pagamento (ADR 0015): un conguaglio del 2026 fatto a febbraio 2027 usa il TUIR e l'art. 23.

**Prassi-interpretazione**

- La scelta automatica della detrazione più favorevole, con una nota di prassi.
- La proiezione del conguaglio come avviso.
- Il limite di quanto si può trattenere, misurato sul netto dopo le ritenute fiscali e i contributi e prima delle trattenute a terzi (ADR 0021).

**Conseguenze sul modello**

- **Incapienza.** Un fatto **richiesta di differimento** della persona porta il resto nei mesi successivi, con l'interesse. Senza la richiesta, la trattenuta si ferma a capienza e il non trattenuto va in CU.
- **Recuperi a rate.** I recuperi a rate oltre i 60 euro (trattamento integrativo, ulteriore detrazione) sono regole con fonte.
- **Addizionali.** Il **domicilio fiscale** è un fatto datato della persona. Le aliquote regionali e comunali sono parametri per regione o comune, con la delibera come riferimento. Il saldo nasce dal conguaglio. Acconto, rate e cessazione sono regole ancora da scrivere.
- **730-4.** È un fatto della persona dal canale (ADR 0012), con la sua provenienza; un rettificativo o un integrativo lo sostituisce con un nuovo fatto. Rimborsi e trattenute sono importi dal primo pagamento utile da luglio, con le rate e gli interessi del 730-4. Se il conguaglio non si può fare, il fatto **conguaglio non effettuato** porta il codice del punto 51 della CU (cessazione, aspettativa, decesso, retribuzione insufficiente, incapienza, passaggio). Il recupero in F24EP dei rimborsi anticipati spetta al ticket #45.
- **Tassazione separata (ADR 0018).** L'importo va all'anno d'imposta del pagamento, conserva l'anno di competenza come anno di riferimento e non entra nell'imponibile ordinario. L'aliquota media legge il reddito del biennio precedente. Se il biennio è anteriore al modello, serve il fatto **reddito del biennio**, preso dalle CU già consegnate: se manca, il calcolo fiscale si ferma.
- **Sostitutiva del 15% sull'accessorio (L. 199/2025 c. 237).** È un terzo regime di tassazione. L'istituto dichiara se rientra, con date e riferimento; una regola applica il tetto annuo per persona. La rinuncia del dirigente e la condizione di reddito sono fatti della persona.
- **Motori esistenti.** Nessun motore IRPEF dei tool esistenti si riusa. Le regole si scrivono dal testo vigente con fonte.

**Da verificare** (ticket di ricerca #47; codice nel ticket #49)

- Scaglioni, aliquote, detrazioni, ulteriore detrazione, somma esente e trattamento integrativo per il 2026 e il 2027, con le modifiche della L. 199/2025: il vault non ha nessuna di queste fonti primarie.
- Addizionali: percentuale e rate dell'acconto, rate del saldo, cessazione (D.Lgs. 360/1998, D.Lgs. 446/1997, e i successori dal 2027).
- Rate dei recuperi oltre i 60 euro, oggi lette solo nelle istruzioni CU 2026 riportate dal vault.
- 730-4: termini, interessi delle rate e dell'incapienza, rifiuto per i cessati (D.M. 164/1999 e istruzioni dell'anno).
- Sostitutiva del 15%: limite di reddito, anno su cui si misura, scadenza, sul testo della legge e della Ris. 4/E/2026.
- Aliquota media: art. 19 TUIR e successore, oggi senza riscontro.
