# Blocco dei pagamenti (art. 48-bis / 144): verifica prima di pagare e accantonamento

Prima di pagare, l'ente verifica presso l'agente della riscossione (AdER) se il beneficiario ha cartelle non pagate per almeno 5.000 euro. Non è una trattenuta a terzi (ADR 0021): è una **verifica** che può sospendere una parte del pagamento.

**Soglia.** Si misura sul **netto del singolo pagamento** del rapporto, nella versione di proposta: lordo meno ritenute fiscali e contributi, prima di cessioni, delegazioni e pignoramenti. I pagamenti dello stesso mese non si sommano. Rimborsi 730 e trasferte documentate non entrano nel netto per la soglia. La soglia è nel corpus, per titolo e periodo:

- dipendenti, TFR/TFS e arretrati compresi: oltre 2.500 euro, dal 01/01/2026 (art. 48-bis c. 1-bis DPR 602/1973, L. 207/2024 art. 1 c. 84-85); dal 01/01/2027 art. 144 c. 2-3 D.Lgs. 33/2025, stesso contenuto;
- co.co.co., amministratori e altri titoli: oltre 5.000 euro (art. 48-bis c. 1, poi art. 144 c. 1);
- prima del 2026 gli stipendi non si verificano.

**Verifica.** Due fatti datati della persona, trascritti come eventi di ritorno (ADR 0025): la **richiesta di verifica** (data e importo) e l'**esito** (non inadempiente, oppure inadempiente con il debito comunicato). Un rapporto sopra soglia senza esito è un **rapporto fermo**: il motivo nomina la verifica mancante e il netto da comunicare. Si sblocca con l'esito, o con una richiesta più vecchia di 5 giorni feriali senza risposta, che vale come esito non inadempiente (DM 40/2008 art. 3 c. 1). Gli altri rapporti proseguono.

**Somma sospesa.** Con esito inadempiente la versione porta una riga di composizione **somma sospesa 48-bis**, effetto meno sul netto, accantonata dall'ente. Importo: il minore tra

1. il debito comunicato da AdER;
2. la fascia sul netto di questo pagamento: 1/10 fino a 2.500 euro, 1/7 fino a 5.000, 1/5 oltre, applicata a tutto il netto (art. 72-ter, poi art. 171);
3. quanto resta sotto la **metà del netto** dopo le trattenute a terzi dello stesso pagamento (artt. 2 e 68 DPR 180/1950): la somma sospesa cede alle trattenute notificate prima.

Il resto del netto si paga. La somma sospesa resta reddito del pagamento in cui matura: ritenute e contributi non cambiano.

**Chiusura dell'accantonamento.** Tre fatti, ognuno chiude con un esito:

- **ordine di versamento** di AdER (art. 72-bis): la somma diventa trattenuta a terzi verso AdER, canale bonifico, esito versato (ADR 0025);
- **debito pagato o ridotto** comunicato da AdER (DM 40/2008 art. 3 c. 5): si paga al dipendente quanto indicato;
- **60 giorni** dalla comunicazione dell'esito senza ordine (DM 40/2008 art. 3 c. 4 e 6): la data la calcola il modello, poi la somma torna pagabile al dipendente.

Negli ultimi due casi la somma entra nel primo pagamento utile come riga verso il beneficiario, senza nuova tassazione.

Scelto da Luca il 09/11/2026 nel grilling del ticket #89, domande 1-7. Ricerca: `docs/research/blocco-pagamenti-48bis.md`.

## Considered Options

- **Rapporto fermo per intero con esito inadempiente:** blocca anche la parte non pignorabile.
- **Fuori dal modello, sul mandato:** la Ragioneria non ha il netto né le trattenute già operate.
- **Dato mancante senza esito:** permetterebbe di pagare senza la verifica, che è obbligatoria.
- **Soglia sul lordo o sul netto del mese:** il cumulo obbligherebbe a riaprire versioni pagate.
- **Sospendere tutto il debito o tutto il netto:** si tratterrebbe più di quanto AdER potrà pignorare, e il resto andrebbe comunque pagato a 60 giorni.

## Consequences

**Norma certa:** soglie e decorrenze; risposta entro 5 giorni feriali e silenzio che vale pagamento; sospensione di 60 giorni fino a concorrenza del debito; pagamento senza ordine entro 60 giorni; debito ridotto (DM 40/2008 artt. 2-3).

**Regole datate e rivedibili:** netto del singolo pagamento; fasce e tetto della metà sulla somma sospesa; TFR/TFS e arretrati inclusi; rimborsi 730 e trasferte esclusi.

**Scelte di implementazione:** la richiesta di verifica vale per quel netto e quella valuta; nel tetto contano solo le trattenute a terzi pagate al creditore, non i recuperi fiscali in F24EP; il sabato è feriale, domenica e festivi del calendario del corpus no (senza calendario la regola dei 5 giorni ferma il rapporto); i 60 giorni sono di calendario.

**Non modellato:** il residuo quando AdER indica una somma pagabile minore della sospesa; il rilascio a una persona che non ha più pagamenti; l'ordine di versamento arrivato dopo i 60 giorni (oggi vince sul rilascio non ancora pagato).

**Da verificare:** circolare RGS 2026 sugli stipendi (numero non confermato); FAQ AdER; vigenza del DM 40/2008 con l'art. 144 c. 4 dal 2027; termini dell'ordine di versamento (art. 72-bis).
