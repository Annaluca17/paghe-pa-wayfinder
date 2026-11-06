# Ciclo proposta–conferma–esito con la Ragioneria

Il modello paghe propone **liquidazioni**, con allegata la **composizione del pagamento**: beneficiari e netti, ritenute collegate al mandato, versamenti a terzi. Propone **impegni** solo quando l'obbligazione nasce da un fatto del registro (fondo, integrativo, arretrati da rinnovo) e non è già coperta dall'impegno automatico del bilancio. Mandati e reversali non si propongono: sono atti della Ragioneria. *Precisato dall'ADR 0017: si propone anche l'accertamento, per un credito che nasce da un fatto del registro. Precisato dall'ADR 0015: ogni istituto dichiara l'origine del proprio impegno.*

Una **riga di proposta** ha come chiave classificazione ufficiale (missione, programma, piano dei conti di V livello) e impegno, ed elenca gli importi che la sommano. Il capitolo lo aggiunge la **mappatura contabile dell'ente**, fuori dal modello. Gli impegni arrivano come **fatti contabili**. Il modello li **abbina** con una regola dichiarata: se nessun impegno è capiente si ferma, se l'impegno non è noto lo segnala come dato mancante.

Ogni invio è una **versione di proposta** immutabile. Se un fatto cambia gli importi, la versione diventa superata e ne nasce una nuova. La Ragioneria conferma o respinge con motivo, e può cambiare solo l'abbinamento all'impegno, lasciando traccia. L'esito **pagato** nasce dall'evento di ritorno del pagamento eseguito, con le righe della versione confermata, e la valuta letta dall'evento diventa il fatto data di pagamento. La **valuta prevista** della proposta serve solo a calcolare ritenute e netti. I versamenti F24EP sono liquidazioni verso terzi: l'esito **versato** nasce dall'evento di versamento eseguito, che sia mandato `F24EP` o regolarizzazione di un provvisorio.

Il **contratto neutro** è uno schema di messaggi versionato e indifferente al trasporto: versioni di proposta in uscita, fatti contabili ed eventi di ritorno in ingresso. Ogni messaggio ha un identificativo stabile, e un evento ripetuto non produce due fatti. Gli **adattatori** dell'ente lo alimentano da contabilità, Giornale di cassa SIOPE+ o inserimento manuale. Il modello non si collega a SIOPE+.

Scelto da Luca il 06/11/2026 nel grilling del ticket #13, domande 4–10 e 13. Chiude il punto lasciato aperto dall'ADR 0006 («il flusso con la ragioneria resta da definire»).

Fonti (ricerca #8):
- impegno automatico del tabellare e degli oneri: art. 183 c. 2 lett. a) TUEL e allegato 4/2 punto 5.2, **norma certa**;
- controllo e numerazione del mandato al servizio finanziario: art. 185 c. 3 TUEL, **norma certa**;
- pagamento dei tributi senza mandato e regolarizzazione: art. 185 c. 4 TUEL, **norma certa**, con il termine di 30 giorni **da verificare**;
- struttura `ritenute` e `tipo_pagamento` OPI: regole tecniche AgID, **norma certa** come standard tecnico. Usarle come vocabolario delle proposte è una **scelta di progetto**.

## Considered Options

- **Ciclo completo, con impegno del fisso e mandati proposti dal modello:** duplica il registro contabile e invade un atto della Ragioneria.
- **Solo liquidazione, senza composizione:** la Ragioneria ricostruisce a mano il legame netto–ritenute, che conosce solo la paga.
- **Proposta fino al capitolo:** il modello paghe dovrebbe conoscere il bilancio di ogni ente, e il contratto non sarebbe più neutro.
- **Riga per persona e istituto:** volumi fuori scala per la Ragioneria. La provenienza consultabile dà la stessa tracciabilità.
- **Impegno lasciato vuoto, o tenuto dal modello:** nel primo caso nessun controllo di capienza, nel secondo un doppio registro.
- **Proposta viva, con importi correggibili dalla Ragioneria:** non si conferma ciò che cambia, e un importo corretto a mano perde la derivazione.
- **Esito pagato alla conferma:** un mandato annullato lascerebbe un esito falso e incancellabile.
- **Lettura diretta di SIOPE+ o solo inserimento manuale:** nel primo caso il modello entra nel canale ente–tesoriere, nel secondo il ciclo non si chiude mai da solo.
- **Proposta di regolarizzazione dedicata:** è un tipo in più, e porta nella proposta dati che solo il tesoriere conosce.
- **API del modello:** lega il contratto a una tecnologia e a chi lo ospita.

## Consequences

- Una valuta effettiva diversa da quella prevista sposta gli importi nella denuncia del mese giusto (ADR 0006). La differenza sui netti si regola per differenza sull'esito.
- Un fatto in attesa d'atto (ADR 0012) non entra in una proposta.
- I fermi già esistenti si estendono alle proposte, per esempio l'impegno incapiente. Una proposta con dati mancanti si invia solo con l'avvertenza.
- Restano **da verificare**:
  - il campo OPI che porta la valuta di accredito al beneficiario;
  - se gli enti del target siano in Tesoreria Unica, condizione per `tipo_pagamento = F24EP`;
  - i codici di V livello di IRAP e Titolo 9;
  - gli elementi obbligatori della transazione elementare.
- Il formato concreto dello schema (JSON Schema o altro) e l'adattatore di riferimento, inserimento manuale più file, spettano al prototipo.
- Le regole di abbinamento per accessorio, FPV e residui dipendono dal ticket sul fondo risorse decentrate. *Definite dall'ADR 0014: impegno proposto alla sottoscrizione dell'integrativo per destinazione ed esercizio di esigibilità, FPV per la quota esigibile dopo l'anno, abbinamento all'impegno della sottoscrizione del fondo dell'anno di competenza.*
