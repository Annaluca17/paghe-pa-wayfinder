# Riferimenti logici e regole sulla normativa vigente

Il campo riferimento è una stringa logica senza URL: URN NIR per le norme; `ccnl:`, `prassi:` ed `ente:` per contratti, prassi e atti dell'ente; `fittizio:` solo per test e dimostrazioni. La sintassi è in `docs/research/riferimenti-normativi.md`; il corpus e i fatti rifiutano un riferimento che non la rispetta.

Ogni regola e ogni parametro devono seguire la normativa vigente per il periodo di competenza. Prima di codificarli si consulta il vault `vault-pa` e si controlla la vigenza. La scelta è dell'utente: una regola scritta su un testo superato produce importi sbagliati anche se il calcolo è corretto.

## Considered Options

- URL: Normattiva, INPS, AdE e ARAN non offrono link stabili per tutti gli atti, e il portale Normattiva può aprire un atto diverso da quello chiesto.
- ELI: in Italia arriva solo all'atto, non all'articolo.
- Testo libero: non si può controllare e non permette di verificare la fonte in automatico.

## Consequences

- Il vault è una pista, non una fonte citabile: la regola cita l'atto. Sul vault si lavora in sola lettura, e per aliquote e importi serve una seconda fonte indipendente, come richiedono le sue stesse regole.
- La versione della norma è ricavata da `dal` della regola o del parametro. Un link generato dal sistema deve sempre indicare la data, perché senza data Normattiva può mostrare un testo futuro.
- Una regola fondata su una norma con fine vigenza nota deve avere `al` e un successore. È già il caso di TUIR e art. 23 D.P.R. 600/1973, abrogati dal 01/01/2027, mentre per il comparto il CCNL 2025-2027 è firmato dal 28/10/2026.
- Il controllo è solo sintattico: l'esistenza dell'atto e la vigenza dell'articolo non sono ancora verificate in automatico. Quando esisterà, la verifica userà l'API di Normattiva, non il portale, e non bloccherà il calcolo.
- Il comma è una notazione del progetto: Normattiva la usa nei propri link ma non la risolve.
- Il caricamento di un corpus reale (`reale=True`) rifiuta i riferimenti `fittizio:` (ADR 0007).
