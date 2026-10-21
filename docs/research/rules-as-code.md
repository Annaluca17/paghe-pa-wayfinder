# Rules as Code: esperienze nelle amministrazioni e applicabilità alle paghe degli Enti Locali

Ticket: #5 (mappa #1). Branch: `research/rules-as-code`. Data ricerca: 21/10/2026.

## Domanda

Quali esperienze pubbliche di "Rules as Code" (RaC) esistono (OpenFisca, Catala e il suo uso nell'amministrazione francese, DMN/FEEL, Blawx, iniziative di Nuova Zelanda, Canada, Australia, OCSE-OPSI, UE, eventuali esperienze italiane) e cosa insegnano su:

- chi scrive e valida le regole;
- testabilità;
- rapporto tra testo normativo e codice;
- governance degli aggiornamenti;
- uso specifico in payroll/retribuzioni pubbliche o calcolo di imposte e contributi.

Applicabilità al CCNL Funzioni Locali e alla normativa previdenziale/fiscale italiana; costi e rischi.

## Legenda delle marcature e limiti di accesso alle fonti

- **norma certa**: per i riferimenti normativi, norma con riferimento verificato; per i fatti su progetti e software, fatto documentato in una fonte primaria che ho letto direttamente (README, codice sorgente, file di test/parametri nei repository ufficiali).
- **prassi-interpretazione**: esperienza riportata da fonti ufficiali o semi-ufficiali, oppure mia inferenza/valutazione (indicata come tale).
- **da verificare**: affermazione ricavata solo da estratti di motore di ricerca (pagina non leggibile integralmente) o non trovata.

Limite importante: dall'ambiente di ricerca erano raggiungibili solo `raw.githubusercontent.com`, il registro npm e PyPI. I siti `catala-lang.org`, `openfisca.org`, `oecd-opsi.org`, `inria.fr`, `hal.science`, `arxiv.org`, `digital.govt.nz`, `interoperable-europe.ec.europa.eu`, `agid.gov.it` restituivano errore di rete/proxy. Per questi le informazioni provengono da estratti di ricerca web e sono marcate di conseguenza; gli URL sono comunque quelli delle fonti primarie da riscontrare.

## Sintesi

1. Il RaC maturo in produzione esiste soprattutto in Francia e quasi sempre sul **calcolo di prestazioni e prelievi** (imposta sul reddito, prestazioni familiari e abitative, contributi sociali), non sulla gestione end-to-end della busta paga di un datore di lavoro pubblico.
2. Le tre famiglie di strumenti hanno filosofie diverse: **OpenFisca** (Python + parametri YAML datati, orientato alla microsimulazione e alle API), **Catala** (linguaggio "literate" che annota articolo per articolo il testo di legge, con logica a default per regola generale/eccezioni), **Publicodes** (YAML dichiarativo con spiegazione del calcolo, usato da URSSAF per simulare una busta paga completa del settore privato). **DMN/FEEL** è uno standard OMG generalista per tabelle decisionali; **Blawx** è un ambiente visuale sperimentale (non production-ready per dichiarazione dell'autore).
3. Lezione ricorrente su chi scrive: funziona il **team misto** (giurista/policy + sviluppatore, a volte redattore normativo), non il giurista da solo né lo sviluppatore da solo; Catala è progettato perché il giurista possa *rileggere e validare* il codice, non necessariamente scriverlo.
4. Testabilità: tutti gli strumenti seri hanno **casi di test dichiarativi** (input -> output atteso per periodo) eseguiti in regressione; la DGFiP valida il proprio calcolo dell'imposta su una base di test interna non pubblicata.
5. Testo-codice: la codifica fa **emergere ambiguità e lacune** del testo (Canada, Catala sulle prestazioni familiari francesi, aides logement); il legame articolo->regola è esplicito in Catala, è un metadato (`reference`) in OpenFisca.
6. Governance degli aggiornamenti: i parametri sono **serie temporali per data di vigenza**; le modifiche passano per pull request, changelog funzionale e versionamento semantico (OpenFisca-France). Le esperienze canadesi segnalano che senza integrazione nel processo di redazione la manutenzione diventa "lunga, ardua e insostenibile".
7. Payroll pubblico: unico esempio specifico trovato è il modello OpenFisca-France delle **ritenute per la funzione pubblica** (pensione CNRACL per territoriali/ospedalieri, RAFP, Ircantec, ATI). Il fallimento di **Louvois** (paghe militari francesi) è citato dagli autori di Catala come motivazione. Nessuna esperienza RaC trovata su contrattazione collettiva del pubblico impiego.
8. Italia: **nessuna esperienza RaC pubblica trovata**. Esistono solo prerequisiti parziali (Normattiva in Akoma Ntoso, codice unico CNEL dei CCNL usato in UniEmens).
9. Implicazione per il progetto: il RaC è adatto come **paradigma per lo strato "regole e parametri"** (aliquote, massimali, tabelle stipendiali, regole di imponibilità) con tracciabilità norma->parametro->importo e test di regressione; non risolve da solo discrezionalità, atti dell'ente, contrattazione integrativa e ciclo contabile.

## Findings per esperienza

### OpenFisca (Francia, poi internazionale)

- OpenFisca è un software libero di microsimulazione; il core è usato da "country package" come OpenFisca-France. **norma certa** - https://github.com/openfisca/openfisca-core (README)
- OpenFisca-France modella il sistema socio-fiscale francese ed espone un'API web pubblica con endpoint per parametri (es. SMIC orario) e formule (es. allocations familiales). **norma certa** - https://github.com/openfisca/openfisca-france (README)
- Parametri: file YAML con `description`, `metadata.unit` e `values` indicizzati per **data di inizio vigenza**; è previsto il segnaposto `expected` per una variazione attesa ma non ancora nota. **norma certa** - https://raw.githubusercontent.com/openfisca/country-template/main/openfisca_country_template/parameters/taxes/income_tax_rate.yaml
- Test: file YAML con `name`, `period`, `input`, `output` eseguiti con `openfisca-run-test`. **norma certa** - https://raw.githubusercontent.com/openfisca/country-template/main/openfisca_country_template/tests/income_tax.yaml
- Payroll pubblico: OpenFisca-France contiene variabili mensili per la funzione pubblica: `pension_salarie` (retenue pour pension; per i titolari territoriali e ospedalieri applica i parametri `cnracl_s_ti` sul trattamento indiciario e `cnracl_s_nbi` sulla NBI), `pension_employeur` (CNRACL datore), `rafp_salarie`/`rafp_employeur`, `ircantec_salarie`/`ircantec_employeur`, `ati_atiacl`, `fonds_emploi_hospitalier`. La variabile `pension_employeur` ha come `reference` una pagina di un'accademia scolastica, non un testo normativo. **norma certa** - https://raw.githubusercontent.com/openfisca/openfisca-france/master/openfisca_france/model/prelevements_obligatoires/prelevements_sociaux/cotisations_sociales/travail_fonction_publique.py
- Governance degli aggiornamenti: ogni modifica ha changelog in francese comprensibile a chi non legge il codice, tipo di cambiamento (es. "Évolution du système socio-fiscal"), **periodi interessati al giorno** ("au 01/01/2017") e zone del modello impattate; controlli automatici (flake8, yamllint) a ogni commit. **norma certa** - https://raw.githubusercontent.com/openfisca/openfisca-france/master/CONTRIBUTING.md
- Il riferimento normativo per variabile è un campo facoltativo (`reference`) e la sua qualità è disomogenea (vedi esempio sopra). **prassi-interpretazione** (mia osservazione sul file citato)
- Esiste una OpenFisca Association (Francia) come custode dei beni comuni del progetto; statuti non letti. **da verificare** - https://openfisca.org/en/association/statutes/
- Usi governativi riportati: Nuova Zelanda (Rates Rebate Act), NSW Australia (Community Gaming Regulation 2020), Canada CSPS (primi esperimenti), Barcellona (prestazioni), LexImpact con l'Assemblée nationale (simulazione emendamenti). **da verificare** - https://digital.govt.nz/blog/turning-the-rules-of-government-into-code-using-openfisca ; https://www.digital.nsw.gov.au/article/an-australian-first-nsw-translating-rules-as-code-to-make-compliance-easy ; https://oecd-opsi.org/wp-content/uploads/2024/04/Rules-as-Code-in-Canada.pdf ; https://interoperable-europe.ec.europa.eu/collection/joinup/solution/openfisca

### Publicodes / modele-social (URSSAF, Francia)

- Publicodes è un linguaggio dichiarativo per "algoritmi di interesse pubblico" che produce il calcolo **insieme a una spiegazione navigabile**; mon-entreprise.urssaf.fr lo usa per tutta la legislazione socio-fiscale e permette tra l'altro di simulare una busta paga completa. **norma certa** - https://raw.githubusercontent.com/publicodes/publicodes/master/README.md
- Le regole del sistema sociale francese sono pubblicate come pacchetto npm `modele-social` (versione 11.1.0 al momento della ricerca); esempio d'uso: da `salarié . contrat . salaire brut` a `salarié . rémunération . net . à payer avant impôt`. **norma certa** - https://registry.npmjs.org/modele-social ; https://github.com/betagouv/mon-entreprise/tree/master/modele-social
- Publicodes nasce (2017) da un simulatore che prima usava OpenFisca, per la complessità di scrittura delle regole in OpenFisca. **da verificare** - https://hackmd.io/@laem/genese-publicodes
- I simulatori URSSAF sono dichiaratamente indicativi. **da verificare** (estratto di ricerca)

### Catala (Inria; CNAF; legame con DGFiP)

- Catala è un DSL per derivare algoritmi "fedeli per costruzione" dai testi legislativi: si annota il testo **articolo per articolo** con il codice ("literate programming"); il compilatore produce una versione PDF leggibile dal giurista; il linguaggio è progettato con professionisti del diritto perché il codice sia **rivisto e certificato dagli esperti di dominio (giuristi)**; incorpora la logica a default (regola generale + eccezioni, da S. Lawsky). **norma certa** - https://github.com/CatalaLang/catala (README)
- Il README dichiara: "Catala is a research project from Inria [...] The compiler is yet unstable and lacks some of its features". **norma certa** - stessa fonte. Risultano pubblicate versioni opam 1.0.0 e 1.1.0 con lo stesso avviso. **da verificare** - https://ocaml.org/p/catala/1.1.0/README.html
- Esempi ufficiali: allocations familiales (Code de la sécurité sociale), aides au logement ("il caso più grande e ambizioso"), sezioni dello US Tax Code. Test di regressione dichiarativi eseguiti con `clerk test`. **norma certa** - https://github.com/CatalaLang/catala-examples (README)
- Il codice compilato si distribuisce come libreria OCaml/JS/Python da inserire in applicazioni esistenti. **norma certa** - https://github.com/CatalaLang/french-law (README)
- Paper ICFP 2021: compilatore con passi centrali dimostrati in F*; caso di studio sulle prestazioni familiari francesi che ha **scoperto un bug nell'implementazione ufficiale**; motivazione citata: le paghe militari francesi (174 tra indennità e supplementi, tre tentativi di riscrittura falliti). **da verificare** - https://arxiv.org/abs/2103.03198
- Rapporto Inria RR-9485 (2022) sulle aides au logement: reverse engineering parziale del sistema CRISTAL della CNAF. **da verificare** - https://inria.hal.science/hal-03781578
- CNAF e Inria hanno firmato una convenzione di partenariato per sviluppare Catala (annuncio 2026); la CNAF lo ha scelto dopo una valutazione come tecnologia strutturante; motivazioni: manutenibilità di CRISTAL (motore storico COBOL poi Oracle), sovranità; risorse annunciate: 2 persone nell'anno e altre 2 nel 2027. **da verificare** - https://www.inria.fr/fr/cnaf-inria-convention-partenariat-catala-2026 ; https://acteurspublics.fr/articles/la-cnaf-fait-le-pari-de-l-open-source-pour-reprendre-la-main-sur-le-calcul-des-allocations/
- DGFiP: l'imposta sul reddito è calcolata in **linguaggio M**, sorgenti pubblicati su Adullact (`dgfip/ir-calcul`); Mlang (Inria) ricompila M e "passa tutti i test privati DGFiP" per i redditi 2018-2021 (settembre 2022); la DGFiP **non pubblica** la propria base di test; parte della logica (liquidazioni multiple) non è pubblicata ed è stata ricostruita in M++. Il README avverte che superare i test significa riprodurre il calcolo DGFiP, **non** che sia fedele alla legge. **norma certa** - https://github.com/MLanguage/mlang (README)
- Non ho trovato evidenza che la DGFiP usi Catala in produzione. **da verificare**

### DMN / FEEL (standard OMG)

- DMN è uno standard OMG per modelli decisionali e tabelle decisionali; FEEL è il suo linguaggio di espressioni con semantica formale; esistono livelli di conformità (S-FEEL vs FEEL completo) e motori open source (es. Camunda, Red Hat/Kogito). **da verificare** - https://www.omg.org/dmn/ ; https://docs.camunda.io/docs/components/modeler/feel/what-is-feel/
- Caso di studio governativo trovato: tassazione degli artisti stranieri in Belgio (Hasić, Vanthienen, KAIS 2020), che lamenta l'assenza di linee guida di modellazione. **da verificare** - https://lirias.kuleuven.be/bitstream/123456789/642718/2/KAIS_2020.pdf
- Nessun caso DMN di payroll pubblico trovato. **da verificare** (non trovato)
- Paesi Bassi (affine, non DMN): la Belastingdienst usa **RegelSpraak**, linguaggio naturale controllato leggibile da esperti fiscali non tecnici, con **TestSpraak** per i casi di test e la catena ALEF che genera codice per il motore FICO Blaze. **da verificare** - https://research.vu.nl/en/publications/regelspraak-a-cnl-for-executable-tax-rules-specification/ ; https://brcommunity.com/articles.php?id=b622

### Blawx (Canada)

- Strumento web open source per RaC (Blockly + SWI-Prolog/s(CASP)), con API REST, spiegazioni delle risposte e ragionamento ipotetico; l'autore dichiara che **non è production-ready** ("intended for educational and experimental purposes"). **norma certa** - https://github.com/Lexpedite/blawx (README)
- Usato da CSPS/CDS in prototipi (Old Age Security, strumento per domande minerarie); le prime codifiche sono state scritte da un giurista-sviluppatore CSPS, con formazione di esperti TBS per scriverle direttamente; difficoltà: interpretazione e comunicazione tra redattori, esperti e programmatori. **da verificare** - https://oecd-opsi.org/innovations/new-techniques-for-building-and-using-legal-encodings-in-the-drafting-room/ ; https://digital.canada.ca/2023/10/12/mining-for-ideas-to-simplify-a-complex-process

### Iniziative di governo e organismi internazionali

- **Nuova Zelanda (Better Rules, 2018)**: discovery sprint di 3 settimane con Inland Revenue, MBIE, Parliamentary Counsel Office e un'azienda privata; conclusione: i team multidisciplinari (policy, redattori, service designer, sviluppatori) sono efficaci per regole "digital ready"; modello OpenFisca Aotearoa open source. **da verificare** - https://www.brcommunity.com/articles.php?id=b962 ; https://digital.govt.nz/blog/turning-the-rules-of-government-into-code-using-openfisca
- **Canada (CSPS, dal 2019)**: la codifica ha rivelato "gaps, loopholes, and ambiguities", ma il processo di conversione di regolamenti esistenti è risultato "long, arduous, and unsustainable". **da verificare** - https://oecd-opsi.org/wp-content/uploads/2024/04/Rules-as-Code-in-Canada.pdf
- **Australia (NSW, 2020)**: versione machine-readable della Community Gaming Regulation 2020 pubblicata insieme al testo e via API, su OpenFisca, con questionario per gli utenti. Non trovati progetti RaC del governo federale su imposte/superannuation. **da verificare** - https://www.digital.nsw.gov.au/article/an-australian-first-nsw-translating-rules-as-code-to-make-compliance-easy
- **OCSE-OPSI**: primer "Cracking the Code" (ottobre 2020) con sei principi: trasparenza, accountability, tracciabilità, appropriatezza e appellabilità, disponibilità e interoperabilità, sicurezza. **da verificare** - https://oecd-opsi.org/publications/cracking-the-code/
- **UE**: corso "Understanding Law as Code" dell'Interoperable Europe Academy; congresso "Rules as Code Europe" (Parigi 2025, DINUM con Digicampus e GRNET); piano d'azione pluriennale presentato a marzo 2026 e consegnato all'Interoperable Europe Board. Non ho letto il testo del piano. **da verificare** - https://www.nldigitalgovernment.nl/news/presentation-of-rules-as-code-action-plan/ ; https://interoperable-europe.ec.europa.eu/collection/govtechconnect/news/rules-code-europe
- **Critiche**: discrezionalità e concetti indeterminati ("ragionevole") non codificabili senza scegliere un'interpretazione; rischio di "legalismo computazionale"; richiamo al caso Robodebt (Australia). **da verificare** - https://cohubicol.com/blog/computational-legalism ; https://www.theconversation.com/csiro-wants-our-laws-turned-into-computer-code-heres-why-thats-a-bad-idea-130131

### Payroll pubblico: casi negativi

- **Louvois** (paghe militari francesi): sostituito dal 2013 in poi con Source Solde (completato per tutte le forze armate dal 1/1/2021); referé della Cour des comptes del 27/12/2013 che attribuisce parte dell'insuccesso a fattori umani e organizzativi; una interrogazione parlamentare riporta 358 M EUR pagati in eccesso e 47 M EUR in difetto dal 2011. **da verificare** - https://acteurspublics.fr/articles/le-ministere-des-armees-tire-un-trait-definitif-sur-lechec-louvois/ ; https://questions.assemblee-nationale.fr/dyn/14/questions/QANR5L14QE93784.pdf
- Il fallimento di Louvois non era un progetto RaC; è citato dalla comunità Catala come esempio del distacco tra team di implementazione e testo normativo. **prassi-interpretazione**

### Italia

- Nessuna esperienza RaC di una PA italiana trovata (ricerche su INPS, Agenzia delle Entrate, Funzione Pubblica, AgID). **da verificare** (non trovato)
- OpenFisca Core risulta catalogato nel catalogo UE del software open source con riferimento alle linee guida AgID sul riuso; non è un progetto italiano. **da verificare** - https://interoperable-europe.ec.europa.eu/eu-oss-catalogue/solutions/openfisca-core
- Normattiva esporta atti in XML Akoma Ntoso (standard OASIS): rappresenta la **struttura** del testo (articoli, commi), non la logica di calcolo. **da verificare** - https://docs.oasis-open.org/legaldocml/akn-core/v1.0/cs01/part2-specs/akn-core-v1.0-cs01-part2-specs-3.html
- Il CCNL applicato si indica in UniEmens e nelle comunicazioni obbligatorie con il **codice alfanumerico unico CNEL** (art. 16-quater DL 76/2020, conv. L. 120/2020; INPS circ. 170/2021, elemento `CodiceContratto`). Il codice identifica il contratto, non ne codifica le regole. **da verificare** (testo della norma e della circolare non letti direttamente) - https://ance.it/wp-content/uploads/allegati/Codice_unico_dei_Ccnl_%E2%80%93_Inps_circolare_n_170_All01161121152533.pdf

## Lezioni trasversali (sulle quattro dimensioni del ticket)

| Dimensione | Cosa insegnano le esperienze | Marcatura |
|---|---|---|
| Chi scrive e valida | Team misto giurista/esperto + sviluppatore; Catala separa chi scrive (programmatore con giurista) da chi valida (giurista sulla vista "literate"); RegelSpraak punta a far leggere le regole agli esperti fiscali | prassi-interpretazione (fonti: README Catala; voci "da verificare" sopra) |
| Testabilità | Casi dichiarativi input/periodo/output (OpenFisca YAML, `clerk test` Catala, FIP DGFiP, TestSpraak); base di test indipendente dal codice come oracolo; la DGFiP mantiene il proprio oracolo privato | norma certa per OpenFisca/Catala/Mlang; da verificare per TestSpraak |
| Testo-codice | Granularità articolo->regola (Catala) o metadato di riferimento per variabile (OpenFisca); la codifica fa emergere ambiguità; superare i test non prova la fedeltà alla legge (Mlang) | norma certa (README Catala, Mlang); prassi-interpretazione per il resto |
| Governance aggiornamenti | Parametri come serie storiche per data di vigenza; pull request + changelog funzionale con periodi al giorno; versionamento semantico; manutenzione insostenibile se il codice è una traduzione a posteriori fatta da pochi | norma certa (OpenFisca-France CONTRIBUTING, template); da verificare (Canada) |

## Trade-off tra paradigmi

- **OpenFisca**: pro: maturo, API, parametri datati, test YAML, modello già esistente per ritenute della funzione pubblica francese. Contro: formule in Python (non leggibili dal giurista), riferimenti normativi facoltativi, orientato al calcolo per periodo di una "situazione", non alla tracciabilità del singolo importo verso un atto. **prassi-interpretazione**
- **Catala**: pro: massima aderenza testo-codice, logica a eccezioni nativa, validabile dal giurista, adottato dalla CNAF. Contro: progetto di ricerca dichiarato instabile, curva di apprendimento, ecosistema piccolo, nessun esempio di payroll. **prassi-interpretazione**
- **Publicodes**: pro: calcolo sempre accompagnato da spiegazione navigabile (vicino al requisito "ogni importo tracciabile fino alla fonte"), busta paga privata completa già modellata da URSSAF. Contro: orientato a simulatori, non a elaborazione massiva con obblighi di rendicontazione. **prassi-interpretazione**
- **DMN/FEEL**: pro: standard, motori commerciali e open source, tabelle leggibili da analisti. Contro: nessun legame nativo con il testo normativo, poche esperienze pubbliche documentate. **prassi-interpretazione**
- **Blawx**: utile per esplorare/interpretare norme con spiegazioni; escluso per produzione per dichiarazione dell'autore. **norma certa** (README) / **prassi-interpretazione** (giudizio d'uso)

## Implicazioni per il modello paghe Enti Locali

- Lo strato di **parametri normativi** (aliquote contributive delle gestioni ex INPDAP come CPDEL e TFS/TFR, massimali, addizionali, scaglioni IRPEF, detrazioni, tabelle stipendiali del CCNL Funzioni Locali per decorrenza) si presta bene alla forma "serie storica per data di vigenza + riferimento all'atto", come nei parametri OpenFisca. **prassi-interpretazione**
- Ogni regola/parametro dovrebbe portare un **riferimento obbligatorio** (non facoltativo come in OpenFisca) a norma, articolo del CCNL o atto dell'ente: è la catena norma -> atto -> input -> importo richiesta dalla mappa. **prassi-interpretazione**
- La spiegazione del calcolo per importo (stile Publicodes) è il meccanismo più vicino al requisito di tracciabilità e alla verifica assistita da AI (l'AI può leggere la spiegazione, non indovinarla). **prassi-interpretazione**
- Serve una **base di test indipendente** (casi certificati dall'ufficio personale o dal consulente, con importi attesi) come oracolo, distinta dal codice: lezione Mlang/DGFiP. I tool esistenti dell'utente possono fornire casi attesi. **prassi-interpretazione**
- Elementi **non codificabili deterministicamente**: contrattazione integrativa e fondo risorse decentrate (dipendono da atti dell'ente), valutazioni della performance, scelte discrezionali; vanno modellati come **input da atto**, non come regola. **prassi-interpretazione**
- La normativa INPS ex INPDAP e fiscale italiana si esprime anche per circolari e messaggi (prassi amministrativa): la regola codificata deve distinguere fonte normativa e fonte di prassi, coerentemente con la marcatura del progetto. **prassi-interpretazione**
- Governance minima: chi propone la modifica (ufficio personale/esperto), chi la valida (revisione da parte di un esperto diverso, con test aggiornati), decorrenza esplicita, changelog funzionale leggibile da non programmatori. **prassi-interpretazione**

## Costi e rischi

- **Costi**: nessuna fonte trovata quantifica il costo di un progetto RaC di payroll. Unico dato di risorse: CNAF 2 + 2 persone dedicate a Catala (da verificare). Il costo principale riportato è il tempo di interpretazione congiunta giurista-sviluppatore (Canada, OPSI). **da verificare**
- **Rischio di falsa certezza**: codice che passa i test ma non è fedele alla norma (avvertenza esplicita di Mlang). **norma certa** (README Mlang)
- **Rischio di interpretazione cristallizzata**: il codice fissa una lettura della norma; senza tracciare l'interpretazione scelta, gli errori diventano sistematici (critiche accademiche; Robodebt; Louvois per il payroll). **da verificare**
- **Rischio di sostenibilità**: manutenzione insostenibile se la codifica è fatta a posteriori da pochi specialisti (Canada). **da verificare**
- **Rischio di dipendenza tecnologica**: Catala e Blawx dichiarati non stabili/non production-ready; OpenFisca e Publicodes più maturi ma con comunità prevalentemente francesi. **norma certa** (README) / **prassi-interpretazione**
- **Rischio specifico italiano**: assenza di un modello pubblico di riferimento per IRPEF/contributi ex INPDAP/CCNL; tutto il corpus andrebbe codificato da zero (o ricavato dai tool esistenti dell'utente). **prassi-interpretazione**

## Domande aperte

1. Adottare un motore esistente (OpenFisca, Catala, Publicodes) o un formato proprio ispirato ai loro principi (parametri datati + riferimento + spiegazione + test)? Da decidere nel grilling sul paradigma.
2. Granularità del riferimento normativo: articolo/comma del CCNL e della norma, oppure anche paragrafo di circolare INPS/AdE?
3. Chi certifica i casi di test nel contesto dell'ente (ufficio personale, ragioneria, consulente esterno, revisore)?
4. Come rappresentare atti dell'ente (determinazioni, contratto integrativo, costituzione del fondo) come input versionati con decorrenza?
5. Esiste un'iniziativa italiana (AgID, Dipartimento per la trasformazione digitale, INPS) non indicizzata o in corso? Non trovata in questa ricerca.
6. Verificare sui testi originali (non accessibili da questo ambiente) le affermazioni marcate "da verificare", in particolare OCSE-OPSI Canada, convenzione CNAF-Inria, art. 16-quater DL 76/2020 e circolare INPS 170/2021.
