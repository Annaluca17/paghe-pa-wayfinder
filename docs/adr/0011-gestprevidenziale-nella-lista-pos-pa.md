# GestPrevidenziale nella ListaPosPA: fine della bozza

La vista espone TFS e TFR in `GestPrevidenziale`, con CodGestione 6 (I.N.A.D.E.L., Allegato tecnico UniEmens 4.33.1, p. 245):

- **Regime 3:** `ImponibileTFS` e `ContributoTFS`.
- **Regime 1:** `ImponibileTFR` e `ContributoTFR`. Gli ulteriori elementi vanno in `ImponibileTFRUlterioriElem` e `ContributoTFRUlterioriElem`, quando ci sono.
- **Retribuzioni TFR:** `RetribTeoricaTabellareTFR` e `RetribValutabileTFR` stanno nei quadri con il regime 1 o 2. Il fermo con ambito `vista` sul regime è tolto dal corpus reale: la lista è trasmissibile.

La vista legge solo importi già calcolati dalla denuncia (parti 1 e 2 del ticket #33). L'unica eccezione è la retribuzione teorica tabellare TFR, che non dipende dai pagamenti: la vista la ricava dal calcolo per competenza del periodo.

Scelto per le decisioni di Luca del 06/11/2026 sulle domande 1, 5, 7 e 8 del ticket #33, che accettano i default proposti.

## Considered Options

- **Teorica come regola del corpus:** una regola per competenza entrerebbe nel cedolino come importo; una regola di cassa non ci sarebbe nei mesi senza pagamenti, come il V1 causale 5.
- **Teorica dai parametri del tabellare, letti dalla vista:** la vista conoscerebbe i nomi dei parametri del corpus. Con il mensile della formula restano dato le dichiarazioni di concorso.
- **CodGestione 6 per il TFS e 7 per il TFR:** è la richiesta iniziale, smentita dall'Allegato tecnico. 7 è l'ex ENPAS.

## Consequences

- **Teorica:** somma dei mensili delle voci a giorni che concorrono per intero a `tfs` o `tfr_ulteriori`, cioè il valore della formula prima della quota del mese parziale. È intera anche nel mese parziale e senza tredicesima. Esce anche nel V1 causale 5 solo giuridico (Circ. INPS 185/2021 § 2.2.1: «sempre valorizzata»). Se manca, la vista la chiede.
- **V1 causale 1:** terne con TipoContributo 7 per il TFS e 8 per il TFR (Allegato tecnico, p. 252), con imponibile e contributo come nel quadro. Un arretrato con ulteriori elementi TFR è un `QuadroFermo`, perché non esiste un tipo contributo.
- **Cambio di regime nell'anno:** un regime diverso tra gennaio e il mese ferma la vista. La tredicesima andrebbe dichiarata con il codice 2 di `IdentAtto` (msg INPS 1974/2018 e 2918/2018). Il fermo scatta anche se la tredicesima non è nel corpus: è prudente.
- **Bozza:** il meccanismo resta per i fermi futuri con ambito `vista` e un test lo copre.
- **Esempio:** `docs/esempi/lista-pos-pa-2026-09.xml` sostituisce la bozza. È un funzionario fittizio in regime TFR, assunto il 24/08 e pagato a settembre. Un test lo rigenera e lo confronta.
- **Controlli INPS:** lo schema verifica il formato, non i controlli INPS. Il Software di controllo UniEmens non è stato eseguito sull'esempio.
