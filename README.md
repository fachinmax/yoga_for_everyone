# Yoga per tutti
Piattaforma per poter creare delle aste per la vendita di vari prodotti a sceltra dell'amministratore.
Essa permette di creare una nuova asta in pochi semplici passi per poi permettere agli utenti di partecipare.

## Funzionamento
Nel momento che un utente accede alla pagina principale, gli vengono proposte tutte le aste attive, e puo avere maggiori informazinoi cliccando sull'asta desiderata.
Qualora volesse partecipare all'asta basta semplicemente cliccare sul pulsante "partecipa" per poter, nel caso si abbia installato Metamask, fare delle offerte in ether o una sua sotto valuta.
Nel momento che l'utente partecipa all'asta gli vengono fornite tutte le informazioni necessarie per poter fare le varie offerte: descrizione del prodotto e tutte le offerte svolte dagli altri partecipanti.
Inoltre ogni utente, ha una propria area personale, visibile esclusivamente se si ha installato Metamask, dove può visualizzare lo storico di tutte le offerte svolte, divise per ogni asta che ha partecipato, e inviare le propria offerta al proprietario, qualora risulta essere vincitore di un asta conclusa.
Ogni volta che viene svolta un offerta viene controllato che l'utente abbia l'importo indicato nel proprio wallet e qualora c'è lo abbia verra salvata su Redis e successivamente viene aggiornato su SQlite l'offerta più alta, l'offerente migliore e il partecipante. In questo modo l'amministratore del sito ha in tempo reale tutte le informazioni dell'asta ancora aperta.
L'amministratore ha una pagina dedicata dove può visualizzare tutte le aste e tutte le loro offerte, una pagina per creare nuove aste indicando un titolo, la descrizione del prodotto, la data di inizio e di fine asta e una pagina per aggiungere varie immagini per ogni asta. Alla chiusura dell'asta potrà visualizzare l'hash del file json pubblicato sulla blockchain di Ganache, e nel momento che il vincitore di un asta invia l'ether anche l'hash della transazione svolta sempre sulla blockchain di Ganache.

### Metamask
Come Descritto nella sezione precedente l'unico modo per poter partecipare all'asta e di aver installato Metamask. Questo perchè da all'utente la possibilita di partecipare all'asta in maniera molto più veloce e semplice senza doversi registrare ed autenticarsi sul sito.
Inoltre è stato utilizzato Metamask per un aspetto fondamentale: permettere all'utente di partecipare all'asta senza che salvi da nessuna parte la sua chiave privata del proprio wallet. Garantendo una certa sicurezza nell'utilizzo del sito.

## Caratteristiche
Questa piattaforma viene realizzata basandosi sulla blockchain per poter rendere trasparente tutte le varie aste e le relative attività. Infatti alla chiusura di ogni asta viene generato un file json con all'interno tutte le informazioni riguardo lo svolgimento dell'asta (data di inizio, data di fine, offerte, partecipanti, vincitore, offerta vincente) che viene salvato sulla blockchain di Ganache, una volta conclusa l'asta.
Le inoformazioni oltre a essere salvate sulla blockchain di Ganache vengono salvate anche sul database SQLite e Redis, piú precisamente nel database SQLite vengono salvate tutte le informazioni inerenti l'asta: vincitore, offerta piú alta, data di inizio e fine, partecipanti, ... e sul database Redis vengono salvate tutte le offerte fatte dai partecipanti garantendo una velocità di scrittura e di lettura elevate.
Inoltre per garantire un esperienza utente ottimale le pagine sono state realizzate in maniera responsive con una grafica pulita ed esenziale.

### API
Lista di tutte le API per poter richiedere i dati delle varie aste:
* ```/<int:pk>/```: ritorna tutte le aste ancora aperte
* ```<int:pk>/register/<int:bid>/<str:address>```: salva una puntata
* ```<int:pk>/allBids```: ritorna un file json con tutte le offerte di una specifica asta
* ```history/<str:address>```: ritorna tutte le aste e le relative offerte fatte di un partecipante
* ```send-ether/<str:address>```: ritorna tutte le aste che l'utente deve pagare
* ```<int:pk>/price```: ritorna il prezzo in wei del offerta migliore di un'asta
* ```hash/<str:hash>/<int:pk>```: riceve l'hash della transazione con la quale è stato inviato l'ether al venditore
* ```images/<str:address>```: ritorna tutte le aste per le quali si possono aggiungere nuove immagini per mostrare il prodotto dell'asta stessa
* ```images/<str:address>/<int:pk>```: riceve tutte le immagini da caricare sull'asta indicata

## Strumenti utilizzati
Per la realizzazione sono stati utilizzati i seguenti strumenti:
* Ganache,
* Database SQLite,
* Database Redis,
* Django.

## Linguaggi di programmazione utilizzati
Per la realizzazione sono stati utilizzati i seguenti linguaggi:
* Python,
* Javascript,
* HTML,
* CSS.

## Blockchain come database
Come scritto nella sezione precedente, i dati sono salvati in maniera centralizzata e in maniera decentralizzata in modo da rendere i piú possibile trasparente e sicuro le operazioni e le vincite dei vari utenti. Garantendo una certa sicurezza da parte dell'utente nel momento che invia l'ether dell'offerta al venditore del prodotto, in quanto ha una prova dell'invio dell'ether.

## Installazione
Per poter eseguire il programma bisogna installare Redis e avviare il server:
```python
pip install django-redis
redis-server
```
Attivare l'ambiente virtuale:
```python
pip3 -r requirements.txt
source venv/bin/activate
```
Eseguire il server:
```python
python3 manage.py runserver
```
infine aggiungere il file .env nel quale indicare la chiave privata e l'indirizzo dell'amministratore del sito:
```python
ADDRESS = '0xb16761...'
PRIVATE_KEY = '0x6e2....'
```