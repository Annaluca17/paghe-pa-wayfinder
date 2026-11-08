# Addizionali regionale e comunale: saldo, rate dai mesi rimasti, acconto comunale

Le **addizionali** regionale e comunale all'IRPEF si calcolano sull'imponibile fiscale della persona dell'anno, lo stesso del conguaglio (ADR 0019), e sono dovute solo se l'IRPEF dell'anno, al netto delle detrazioni, è dovuta (art. 1 c. 4 D.Lgs. 360/1998; art. 50 c. 2 D.Lgs. 446/1997, **norma certa**). Dal 01/01/2027 i due decreti restano in vigore: cambiano solo i rinvii al TUIR (ricerca `parametri-fiscali-2026-2027.md`, tema 4).

**Aliquote.** Per comune (codice catastale) e per regione, un parametro datato per anno con le **fasce** (fino a, aliquota) e la **soglia di esenzione**: sotto la soglia l'addizionale è zero, sopra si applica a tutto il reddito. Il parametro sta in un file nostro, importato nel corpus con il riferimento alla delibera o alla legge regionale, mai scritto a mano nel codice. Il lettore del file pubblicato dal MEF è fuori da questa decisione.

**Domicilio fiscale.** Fatto datato della persona con codice catastale del comune e codice della regione. Conta quello al 1° gennaio dell'anno d'imposta; per la regionale l'art. 50 dice anche «residenza», **da verificare**. Se manca, il calcolo delle addizionali si ferma: è un dato mancante.

**Saldo.** Al conguaglio dell'anno N la regola calcola l'addizionale regionale e quella comunale dell'anno; il saldo comunale è l'addizionale meno l'acconto trattenuto. Le due si trattengono nell'anno N+1 dal mese dopo il conguaglio, al massimo in undici rate, l'ultima sul periodo di paga di novembre, le cui ritenute si versano a dicembre (art. 1 c. 5 D.Lgs. 360/1998; art. 50 c. 4 D.Lgs. 446/1997, **norma certa**).

**Acconto comunale.** Il 30% dell'addizionale comunale calcolata sul reddito dell'anno prima, con aliquota e soglia dell'anno prima (art. 1 c. 4, **norma certa**, verificato sul testo vigente il 08/11/2026). La base viene dal conguaglio dell'anno prima nel modello, altrimenti dal fatto **reddito dell'anno precedente**; se manca anche quello, niente acconto con avviso, e tutto passa al saldo. Si trattiene da marzo a novembre, al massimo in nove rate. Se il reddito dell'anno prima è sotto la soglia, l'acconto è zero (circolare AdE 23/E/2007, **prassi**).

**Rata del mese.** Nessun piano salvato. A ogni pagamento la rata è il **residuo da trattenere diviso i mesi rimasti** fino a novembre, questo compreso. Le rate restano uguali, i centesimi finiscono nell'ultima e un mese senza pagamento si spalma da solo sui successivi. Una sola rata per persona e per mese, sul primo pagamento del mese con reddito. Chi entra dopo novembre non ha acconto: passa al saldo.

**Cessazione.** Sul pagamento finale (ADR 0019) il residuo delle rate dell'anno prima e le addizionali dell'anno della cessazione, meno l'acconto trattenuto, si trattengono in un'unica soluzione (**norma certa**, stessi commi).

**Addizionale a credito.** Se l'acconto trattenuto supera l'addizionale comunale dell'anno, o un nuovo conguaglio dà meno, la differenza si restituisce in unica soluzione nel pagamento del conguaglio. Nella delega diventa una riga a credito, 161E (160E per la regionale), con riferimento B uguale all'anno d'imposta (ADR 0023, precisazione del 08/11/2026).

**Delega F24EP.** Si versano con 381E (regionale, codice regione), 384E (comunale saldo) e 385E (acconto), con il codice catastale, e riferimento B uguale all'anno d'imposta.

Scelto da Luca l'08/11/2026 nel grilling del ticket #85, sulle decisioni 6 e 6b del #47.

## Considered Options

- **Aliquota unica:** più semplice, ma ferma i comuni e le regioni a fasce, che sono molti.
- **Leggere subito il file del MEF:** più lavoro in questo ticket. Il formato nostro intanto si prova con dati fittizi.
- **Rate fisse a 11 e 9:** con un conguaglio a febbraio si sforerebbe dicembre.
- **Piano di rate salvato al conguaglio:** un mese saltato avrebbe bisogno di una regola a parte. Il residuo diviso i mesi rimasti si corregge da solo.
- **Regione da una tabella comuni → regioni:** un altro dato da mantenere, senza vantaggio.
- **Fermo sull'addizionale a credito:** la regola del credito c'è già (ADR 0023).
