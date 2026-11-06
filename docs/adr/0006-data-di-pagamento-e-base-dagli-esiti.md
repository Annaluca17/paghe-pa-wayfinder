# La base imponibile legge gli esiti pagati e la loro data di pagamento

La base del periodo dichiarato somma le righe degli esiti `pagato` la cui data di pagamento cade nel mese. La data è un fatto legato all'esito, registrato con `registra_pagamento`. Regole di cassa, parametri e dichiarazioni di concorso si scelgono alla data di pagamento. Sono regole di cassa quelle che leggono una base o un'altra regola di cassa: non compaiono nel calcolo per competenza.

Scelto perché la denuncia dichiara ciò che è stato corrisposto (Circ. INPS 105/2012 § 2.1, § 6.1, § 6.4.1). Un ricalcolo della competenza sposterebbe nel mese originario anche un arretrato pagato dopo. Con gli esiti l'arretrato entra nel mese in cui è pagato e il mese originario non cambia.

## Considered Options

- Data di pagamento come fatto su rapporto, istituto e competenza: un aumento retroattivo cambierebbe la base di un mese già pagato.
- Data di pagamento solo come campo dell'esito: un esito è immutabile, quindi una valuta sbagliata non si potrebbe correggere con la sua storia.
- Una regola che dichiara in quale data leggere i parametri: inutile, perché ogni regola che legge una base segue il pagamento.

## Consequences

- Senza data di pagamento un esito non entra in una base: la denuncia lo elenca in `esiti_senza_data`.
- Un nuovo fatto corregge la valuta: l'importo cambia mese e `noto_al` mostra ancora il mese precedente.
- Il concorso si sceglie alla data di pagamento, come l'aliquota. L'ADR 0005 chiede solo che abbia date: è una **scelta di progetto**.
- Se due pagamenti dello stesso periodo cadono a cavallo di un cambio di aliquota, il calcolo si ferma. Una sola base non può avere due aliquote.
- Un pagamento prima dell'inizio del servizio, o tra due periodi dello stesso mese, ferma il calcolo: la nota di prassi 2 non copre questi casi.
- In un mese senza servizio la denuncia ha un solo periodo con `in_servizio` falso, pari al mese. Il quadro da esporre lo sceglie la vista.
- I codici come contratto e qualifica sono fatti categoriali (`registra_codice`): restano testo e una formula non li legge. Un periodo dichiarato si apre quando il valore cambia, non quando lo stesso valore viene registrato di nuovo. Le frazioni continuano a seguire ogni fatto.
- Le regole sul periodo che leggono importi per competenza restano ammesse per i corpus fittizi. Il corpus reale userà solo le basi.
- Il contributo si calcola dopo la registrazione della data. Per conoscere il netto prima del mandato si registra la valuta prevista e poi, se cambia, la si corregge. Il flusso con la ragioneria resta da definire nella mappa. *Definito dall'ADR 0013: la valuta prevista sta nella proposta, l'esito pagato e la data di pagamento nascono dall'evento di ritorno del pagamento eseguito.*
- `differenze` non confronta ancora le denunce già fissate con le basi ricalcolate: è il V1 di variazione, fuori da questa fetta.
