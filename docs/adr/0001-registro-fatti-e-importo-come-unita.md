# Registro di fatti bitemporale e importo come unità del modello

Il modello non adotta anagrafica, tabella voci e ciclo mensile batch. La verità sta in un registro di fatti immutabile e bitemporale; gli esiti verso terzi (pagato, dichiarato, versato) sono istantanee immutabili; ogni altro importo è una proiezione ricalcolabile, calcolata in continuo. L'unità è l'importo (rapporto, istituto, periodo di competenza, derivazione); cedolino, ListaPosPA, F24EP e proposte contabili sono viste. Le regole sono in un formato dichiarativo proprio, separate da parametri datati con fonte e da input da atto dell'ente.

Scelto perché la norma impone cadenze di output, non di calcolo, e perché solo questa combinazione rende ogni importo ricostruibile fino a norma, atto e dato "come risultava" a una data, con rettifiche per differenza rispetto agli esiti.

## Considered Options

- Stato corrente più storico (schema dei gestionali): conserva il risultato, non la derivazione.
- Event sourcing puro: il replay con regole cambiate non riproduce il pagato; servono comunque le istantanee.
- Motore esistente (OpenFisca, Catala, Publicodes): nessuno unisce riferimento obbligatorio, quattro assi temporali e corpus italiano; il formato proprio resta traducibile verso Publicodes/OpenFisca.

## Consequences

- Costo alto di modellazione del tempo e di codifica delle regole; basso di infrastruttura.
- La correzione di una regola è distinta dalla nuova vigenza e produce differenze sugli esiti.
- Ogni esito registra versione del corpus regole, versione di ogni regola applicata e tempo di registrazione dei fatti letti.
