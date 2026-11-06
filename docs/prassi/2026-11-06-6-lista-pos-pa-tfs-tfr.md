# Nota di prassi 6: TFS e TFR nella ListaPosPA

Riferimento: `prassi:immedia:nota:2026-11-06;6`. Fonte: decisioni dell'operatore del 06/11/2026 sulle domande 1, 5, 7 e 8 del ticket #33, che accettano i default proposti.

## Gestione previdenziale

**Decisione dell'operatore.** TFS e TFR dei Comuni vanno nella gestione 6, ex INADEL; li distingue il regime. **Norma certa** (istruzione INPS): Allegato tecnico 4.33.1, p. 245; DT 4.33, p. 191-192; Circ. INPS 185/2021.

## Retribuzione teorica tabellare TFR

**Decisione dell'operatore.** È il mensile intero delle voci fisse utili al TFR: oggi il solo tabellare dell'area. È intera anche nel mese parziale e non comprende la tredicesima. Si espone anche nel V1 causale 5 solo giuridico.

**Limiti.** La Circ. INPS 185/2021 § 2.2.1 parla di «retribuzione tabellare mensile»: non dice se comprenda altre voci fisse, né come trattare il mese parziale. Il DT 4.33 la rende obbligatoria solo con `GestPrevidenziale`: nel V1 causale 5 l'esposizione segue la circolare, che la vuole «sempre valorizzata». **Prassi-interpretazione.**

## Arretrati a cessati e sospesi

**Decisione dell'operatore.** Nel V1 causale 1 le terne Ente Versante usano TipoContributo 7 per il TFS e 8 per il TFR (Allegato tecnico, p. 252). Gli ulteriori elementi fermano la vista. **Da verificare**: la tabella dell'Allegato è la sola fonte.

## Cambio di regime nell'anno

**Decisione dell'operatore.** Ferma la vista: la tredicesima con il codice 2 di `IdentAtto` non è modellata.

## Quando rivedere

Quando il Software di controllo INPS segnala qualcosa sull'esempio, quando INPS chiarisce il contenuto della teorica o la terna degli ulteriori elementi, o quando la tredicesima entra nel corpus.
