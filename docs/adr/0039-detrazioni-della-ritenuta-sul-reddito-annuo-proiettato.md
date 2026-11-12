# Detrazioni della ritenuta sul reddito annuo proiettato

Supera in parte l'ADR 0033: la ritenuta del mese non calcola più le detrazioni sul reddito del mese per dodici, ma sul **reddito annuo proiettato**. Resta dell'ADR 0033 tutto il resto: i carichi sono a mese, un dodicesimo per familiare, e il conguaglio ricalcola sull'imponibile vero dell'anno.

Il confronto con un ente reale mostrava che il nucleo trattiene meno IRPEF del gestionale: il mese per dodici sottostima il reddito di chi riceve la tredicesima o un aumento, e le detrazioni, che calano al crescere del reddito, risultavano troppo alte. Decisioni di Luca del 12/11/2026 (grilling del ticket #119).

## Decisioni

1. **Reddito annuo proiettato.** È la somma di: il pagato dall'inizio dell'anno (imponibile fiscale degli esiti della persona pagati prima del mese), l'imponibile del mese, l'imponibile **ricorrente** del mese per i mesi che restano, la tredicesima non ancora pagata. Il ricorrente è l'imponibile del mese senza arretrati (competenza precedente al mese di paga) né importi non ordinari (maturazione «evento», «annuale», «onere»). I mesi che restano sono 12 meno il mese del pagamento; un pagamento di gennaio per l'anno prima (cassa allargata) non ne ha.
2. **Tredicesima.** Solo il residuo: `calcola_annuale` dell'anno meno quanto già pagato, per istituto. Entra come imponibile fiscale, cioè al netto dei contributi a carico del dipendente: il modello applica alla tredicesima la stessa quota di contributi che il ricorrente del mese ha pagato, perché la tredicesima concorre per intero alla base. A dicembre il residuo è già nel pagamento e il reddito annuo è il reddito vero dell'anno.
3. **Gennaio e assunti.** Nessun caso speciale. A gennaio il pagato prima è zero; per un assunto in corso d'anno contano i mesi dal primo pagamento. I redditi di altri datori restano fuori dalla proiezione (circ. AdE 15/E/2007 § 2.1): la CU del precedente datore andrà nel conguaglio, in un ticket a parte.
4. **Somma esente e trattamento integrativo** restano sul reddito annuo **teorico**: il pagato diviso i giorni di servizio per 365 (circ. AdE 4/E/2025 § 1.2). La differenza con l'ulteriore detrazione, che usa la proiezione, è voluta: i due istituti hanno una base di legge propria. Il modello non la riconcilia.
5. **Detrazione del mese.** La detrazione annua per giorni del mese / giorni dell'anno, come fa il gestionale. Il minimo annuo di 690 euro segue la stessa quota. È **prassi-interpretazione, da verificare**: nessuna fonte letta lo dice in modo esplicito (nota di prassi 13). Si usano i giorni veri dell'anno (366 nel bisestile), come il conguaglio: dodici mesi sommano esattamente la detrazione annua.

Vale per la detrazione di lavoro (art. 13 c. 1 TUIR), l'ulteriore detrazione automatica e i carichi di famiglia (art. 12). Gli **scaglioni dell'imposta lorda** restano ragguagliati al periodo di paga, sull'imponibile del mese. La detrazione della carica elettiva (art. 13 c. 5) **non cambia**: resta un dodicesimo per pagamento sul reddito del mese per dodici.

## Come è fatto

Il corpus legge due valori nuovi del motore: `fisco.reddito_annuo`, il reddito delle fasce delle detrazioni (nel conguaglio l'imponibile dell'anno, quindi nulla cambia lì), e `fisco.quota_minimo`. Le formule di detrazione, detrazione automatica e carichi non dividono più per `fisco.periodi`: la quota del periodo è nei giorni. Il motore proietta solo se una formula della regola legge `fisco.reddito_annuo`; i corpus che non lo leggono si comportano come prima.

## Considered Options

- **Mese per dodici (ADR 0033):** semplice, ma sottostima chi ha tredicesima o aumenti; il conguaglio di dicembre assorbe tutta la differenza.
- **Un dodicesimo della detrazione annua:** più semplice dei giorni, ma differisce dal gestionale nei mesi non da 30 giorni.
- **Proiettare anche gli arretrati e le una tantum sui mesi che restano:** gonfierebbe il reddito annuo per un importo che non si ripete.
- **Servizio del corpus per contare i mesi che restano (cessazione nota):** più preciso per i tempi determinati, ma Luca ha scelto nessun caso speciale; il conguaglio corregge.
- **Tredicesima lorda:** sovrastimerebbe il reddito dei contributi del lavoratore.

## Consequences

- I conguagli di dicembre si avvicinano a zero, perché la ritenuta ha già usato il reddito vero dell'anno.
- Restano **da verificare**: il criterio giorni del mese / giorni dell'anno, la stima dei contributi sulla tredicesima con la quota del ricorrente, la classificazione di ricorrente per maturazione.
- Un importo di competenza di un mese precedente pagato di norma (stipendio pagato il mese dopo) conta come arretrato: oggi gli enti pagano nel mese di competenza.
- Il mese per dodici resta, per scelta, nell'imposta lorda, nella carica elettiva, nella somma esente e nel trattamento integrativo.
- Ticket a parte: i redditi del precedente datore (CU) nel conguaglio; la carica elettiva sulla proiezione, se serve.
