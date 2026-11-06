# Confine del registro: fatti giuridici, canali di input e atti

Il fatto giuridico nasce nel registro. La sua fonte è l'atto dell'ente o l'evento della persona, e lo registra l'Ufficio personale. Non esiste un secondo sistema giuridico con una propria verità: presenze, attestati di malattia e 730-4 sono **canali di input**, che portano fatti con provenienza. I fatti riguardano una **persona** (codice fiscale, nascita, genere, titolo di studio) o un **rapporto** (inquadramento, orario, ufficio, cessazione). La **scheda della persona** è una vista.

Un **tipo di fatto** entra nel registro solo se almeno un lettore dichiarato lo legge: una regola, un output obbligatorio o un adempimento non stipendiale. Le **assenze** sono fatti giornalieri o orari con una **causale del modello**, tradotta dall'adattatore del fornitore delle presenze. Un solo fatto, per esempio una malattia con attestato INPS, ha più lettori: la riduzione stipendiale, il comporto, SICO e la ListaPosPA. Per gli atti dell'ente l'atto nasce dal dato: si registra un **fatto in attesa d'atto**, che diventa efficace con numero e data dell'atto. Gli atti esterni (pignoramenti, cessioni, notifiche) si trascrivono.

Scelto da Luca il 06/11/2026 nel grilling del ticket #13, domande 1, 2, 3, 11 e 12. Il pain point della mappa è «giuridico e finanziaria scollegati», e due verità per lo stesso fatto lo riprodurrebbero. Gli adempimenti non stipendiali (ricerca #10) chiedono consistenze a qualunque data e una sola registrazione con più mappature, cosa che il registro bitemporale già offre.

## Considered Options

- **Giuridico esterno come fonte di verità, copia nel modello:** due verità da riconciliare. È lo scollegamento che la mappa vuole togliere.
- **Fonte divisa per dato:** il confine tra «giuridico» e «solo calcolo» si sposterebbe a ogni nuovo adempimento.
- **Scheda della persona come entità con stato corrente:** è l'anagrafica dei gestionali (regola metodologica 1). Una correzione retroattiva cancellerebbe ciò che si sapeva prima.
- **Registro aperto a ogni fatto della persona:** la specifica non saprebbe più dire che cosa serve a cosa. Questo ricostruirebbe un gestionale delle risorse umane completo.
- **Presenze come riepilogo mensile:** non serve a trasparenza, Conto Annuale, Perla PA e GEDAP, e lascia la trattenuta senza provenienza.
- **Dato ricavato sempre dall'atto:** il dato si scrive due volte, nella determina e nella paga.

## Consequences

- La gestione della formazione (catalogo, iscrizioni, esami) resta fuori. Le ore di formazione entrano solo se un adempimento le chiede: il contenuto di PIAO 3.3 è **da verificare**.
- Le causali di assenza sono un elenco del modello con lettori dichiarati. La prima mappatura per fornitore resta manuale (ricerca #7).
- Un fatto in attesa d'atto si calcola come simulazione e alimenta il prospetto allegato all'atto. Non entra in un esito né in una proposta.
- Il codice: oggi il corpus reale registra il codice fiscale come fatto del rapporto (`[denuncia]`, ADR 0007), mentre il registro conosce solo rapporti. Il prototipo dovrà introdurre la persona come soggetto dei fatti e spostarvi il codice fiscale.
- Il ruolo dell'AI nella trascrizione degli atti esterni resta nel ticket sul ruolo dell'AI.
