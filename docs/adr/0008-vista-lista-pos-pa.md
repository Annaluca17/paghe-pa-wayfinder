# Vista ListaPosPA: quadri della prima fetta, dati chiesti, bozza e serializzazione separata

La vista `lista_pos_pa` legge la denuncia calcolata e la dispone in quadri:

- **E0** per i periodi in servizio con importi pagati;
- **V1 causale 5 solo giuridico** per un mese di servizio pagato per la prima volta nel mese della denuncia, con l'inquadramento e senza gestioni (nota di prassi 2);
- **V1 causale 1** per un arretrato pagato a un cessato o a un sospeso, sull'ultimo periodo di servizio prima del mese, con le terne Ente Versante sul mese di pagamento.

Le altre variazioni non producono un quadro. La vista indica quello necessario e conserva gli importi calcolati: è un `QuadroFermo`. Un dato obbligatorio del tracciato che manca nel registro diventa un `DatoMancante` e viene chiesto. Un fermo del corpus con ambito `vista` rende la lista una **bozza non trasmissibile**. La serializzazione (`paghe.uniemens.in_xml`) scrive l'XML solo se non ci sono fermi né dati mancanti. Una bozza esce solo se chiesta, con un commento in testa.

Scelto perché le decisioni di Luca del 06/11/2026 (ticket #29) chiedono di produrre un primo XML da mostrare senza nascondere ciò che manca. Codici di inquadramento e anagrafica sono fatti registrati dall'ufficio personale. Ente e mittente sono argomenti. Il fermo TFS/TFR passa dalla denuncia alla vista.

## Considered Options

- **Lasciare il fermo TFS/TFR nella denuncia:** nessun XML uscirebbe per un dipendente reale, perché il regime è obbligatorio nel tracciato.
- **Derivare contratto e qualifica dall'area:** meno dati da registrare, ma la tabella sarebbe nostra. L'Appendice G resta un controllo nei test.
- **Fermare la vista con un'eccezione al primo problema:** l'ufficio vedrebbe una mancanza per volta. La vista invece le raccoglie tutte, e la serializzazione si rifiuta.
- **Arrotondare nella serializzazione:** nasconderebbe un errore del calcolo. Un importo con più di 2 decimali è rifiutato.

## Consequences

- Fatti categoriali nuovi: `tipo_servizio`, `contratto`, `qualifica`, `regime_fine_servizio` (codice INPS 1, 2 o 3), `codice_cessazione`, `cognome`, `nome`, `comune_sede_lavoro`, `cap_sede_lavoro`. `tipo_impiego` resta il fatto di servizio.
- Il codice di cessazione si chiede quando il servizio finisce con il periodo dichiarato. Vale anche per una sospensione: il tracciato usa lo stesso elemento.
- **Norma certa** (istruzione INPS): codici del tracciato dall'Allegato tecnico 4.33.1, appendice B. CodGestione 2 è la CPDEL, 9 il credito (p. 245). TipoContributo 1 vale per il tipo impiego 1, e 9 è il credito (p. 251). Aliquota 2 è «di cassa» (p. 256). Il codice motivo 7 è «Recupero competenze dipendente cessato» (p. 254). Il codice motivo si compila solo con la causale 7 (documento tecnico 4.33, p. 204). Importi con virgola e al massimo 2 decimali (DT p. 31, XSD `ImportoConDecConSegno`).
- **Prassi-interpretazione:** il V1 causale 5 solo giuridico senza gestioni. Il V1 causale 1 sull'ultimo periodo di servizio. Cessato e sospeso riconosciuti allo stesso modo, perché il modello non ha un fatto di sospensione. L'1% esposto solo se diverso da zero. L'1% del V1 causale 1 come terna con TipoContributo 5.
- **Da verificare:** il TipoContributo 5 per l'1% (la tabella dell'Allegato è impaginata male). Il periodo e il codice cessazione 32 del V1 causale 7, codice motivo 7. `StipendioTabellare` e `RetribIndivAnzianita` non esposti. Il significato dell'attributo `Tipo` di `DatiMittente`.
- La bozza contiene il regime ma non `GestPrevidenziale`. Il documento tecnico lega il regime alla gestione previdenziale, e il controllo INPS lo segnalerebbe: per questo la bozza non è trasmissibile.
- Schema XSD 4.33.1 e Appendice G v15 sono «tutti i diritti riservati» INPS e non stanno nel repo. I test li cercano in `PAGHE_XSD_UNIEMENS` e `PAGHE_APPENDICE_G` e vengono saltati se mancano. Lo schema verifica il formato, non i controlli INPS (00xxxI).
