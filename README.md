# Projet multilang_site

## Accéder à l'application
L'application est déployée avec Koyeb à l'adresse: https://realistic-katey-lcoutel-a5c970a4.koyeb.app/

### Fonctionnalités
#### Choix de la langue
Pour basculer entre l'anglais et le français, utilisez menu déroulant en haut à droite, dans la barre d'outils.
#### Recherche par similarité
Effectuez une recherche avec un mot-clé, une phrase ou un texte depuis la barre d'outil. L'application vous redirigera vers des articles similaires.
#### Assistant IA
Dans la barre d'outil, cliquez sur le bouton 'Ouvrir l'assistant'. Une fenêtre s'affichera en bas de votre écran, dans laquelle vous pourrez intéragir avec l'assistant, notamment pour effectuer des recherches.

## Dépendances et architecture
### Back-end
Le back-end de l'application est réalisé avec **Django** et utilise l'extension **Channels** pour  la communication via websockets.

Il fait appel à une base de donnée vectorielle PostgreSQL utilisant l'extension  **PgVector**.

L'assistant IA ainsi que les fonctionnalités de recherche par similarité, de suggestions et de recherche augmentée de génération font appel à l'API d'**OpenAI**, permettant notamment de générer les *embeddings* nécessaires.

### Front-end
Le front-end est quasiment intégralement géré grace à **HTMX**, qui permet de créer une interface dynamique semblable à celle d'une SPA moderne sans utiliser de framework Javascript et en déléguant la gestion de l'état de l'application au back-end.

Les évenements relevant purement de l'interface utilisateur (comme le fait d'afficher ou de masquer la fenêtre de chat) sont gérés par un script en Javascript natif.

Les styles sont gérés en CSS natif.

### Déploiement
L'application est déployée sur Koyeb et utilise le serveur web ASGI **Daphne**, qui gère aussi bien les requêtes HTTP classiques que les connections Websocket asynchrones.


## Gestion des langues

Deux langues sont actuellement supportées, l'anglais et le français. La traduction est gérée principalement au niveau des templates, à l'aide du système de dictionnaire (fichiers `.po` et `.mo`), de l'extension Javascript `JavascriptCatalog` ainsi qu'au niveau des URLs, qui sont adapatés selon la langue de navigateur détéctée.

Il est possible de changer la langue à tout moment au niveau de l'interace, grâce à un sélecteur appelant la vue de redirection `set_language` fournie par Django et mise en place aux niveau du fichier de configuration des URLs.

Les articles factices générées pour le projet le sont dans les deux langues, et sont affiché dans la langue de l'utilisateur grâce au package `django-modeltranslation` (https://pypi.org/project/django-modeltranslation/). La génération de données factice est expliquée en détail plus bas.

## Affichage des articles et recherche par similarité

Le module `article_views` définit les vues permettant de consulter les derniers articles, un article individuel ou des résultats de recherches. Les vues sont pensées pour être insérées dynamiquement avec **HTMX** et gèrent le rafraichissement forcé de la page.

### Vues

#### `base(request)`
Retourne la mise en page de base de l'application et déclenche une requête HTMX chargeant la vue `articles` comme vue par défaut.

---

#### `articles(request)`
Retourne une section contenant la liste de tous les articles, par ordre chronologique décroissant. Afin de gérer le défilement à l'infini, cette vue prends en compte un paramètre "page" et peux être rappelée pour renvoyer les articles au fur et à mesure du défilement.

---

#### `article(request)`

Renvoie un article complet ainsi que des suggestions d'articles similaires basées sur une recherche par similarité.

---

#### `search(request)`
Effectue une recherche basée sur la similarité et renvoie la liste des articles trouvées d'une manière similaire à la vue `articles`.

## Assistant IA et Génération Augmentée de Récupération

### Consumer Websocket pour intéragir avec l'assistant IA.

Ce module `AssistantConsumer` utilise Django Channels et permet de gérer les connexions WebSocket et de traiter les messages entrant et sortants.

#### Fonctionnalités

- **Connexion et Initialisation** : Gère la connexion WebSocket, initialise l'assistant et crée un thread de conversation.
- **Réception et Traitement des Messages** : Reçoit les messages de l'utilisateur, les transmet à l'assistant, et renvoie les réponses.
- **Streaming et Gestion des Événements** : Gère le streaming des réponses de l'assistant, incluant les messages et les deltas (message partiel), et traite déclenche des fonctions lorsqu'une action est requise.
- **Formatage des Réponses** : Formate les réponses de l'assistant en HTML pour une présentation optimale.

#### Méthodes

##### `connect()`

- **Description** : Récupère la langue actuelle, initialise l'assistant et crée un thread. Accepte la connexion et commence le streaming pour que l'assistant puisse se présenter.

---

##### `receive(text_data)`

- **Description** : Reçoit les messages de l'utilisateur, crée un rendu HTML grâce à un template, les ajoute au thread et diffuse la réponse.
- **Paramètres** : 
  - `text_data` : Données textuelles JSON entrées par l'utilisateur.

---

##### `stream()`

- **Description** : Crée un flux de messages et de deltas, envoie les messages et traite les événements.

---

##### `handle_events(stream)`

- **Description** : Écoute les événements du flux et réagit en conséquence :
  - Crée un rendu HTML de message vide à la création d'un message.
  - Envoie  au fur et à mesure de leur génération les deltas de texte à insérer dans le corps du message.
  - Déclenche une fonction et traite les valeurs de retour lors d'un événement d'action requise.
  - Formate le contenu du message en HTML lorsque le message est complété.
- **Paramètres** :
  - `stream` : Le flux d'événements.

--- 

##### `wrap_msg(msg_tmp)`

- **Description** : Enveloppe un message dans une section pour que HTMX puisse identifier la section comme cible et insérer le message à l'intérieur.
- **Paramètres** :
  - `msg_tmp` : Le message temporaire à envelopper.
- **Retourne** : Chaîne de caractères enveloppant le message.

---

### assistant_utils.py

Ce module comprend diverses fonctions utilitaires pour utiliser et interagir avec un assistant OpenAI, notamment pour créer des assistants, générer des embeddings, effectuer des recherches par similarité dans la base de données et traiter des événements.

#### Fonction `create_assistant`

Cette fonction crée un assistant OpenAI et initialise un thread de conversation.

##### Arguments :
- `lang` (str) : Code de langue actuel.

##### Retourne :
- `assistant`, `thread` (tuple) : Instances de l'assistant et du thread emballées dans un tuple.

---

#### Fonction `get_embedding`

Cette fonction génère un embedding à partir d'un texte donné en utilisant l'API OpenAI.

##### Arguments :
- `text` (str) : Texte pour lequel générer un embedding.
- `model` (str) : Nom du modèle OpenAI à utiliser (par défaut : "text-embedding-3-small").

##### Retourne :
- `vector embedding`

---

#### Fonction `distance_search`

Cette fonction exécute une recherche de similarité dans la base de données en utilisant une description d'article fournie.

##### Arguments :
- `article_desc` (str) : Description de l'article souhaité par l'utilisateur.

##### Retourne :
- `matching_articles` (QuerySet) : Articles correspondant le mieux à la description fournie.

---

#### Fonction `process_req_action`

Cette fonction déclenche une recherche sur un événement et génère les sorties d'outil correspondantes.

##### Arguments :
- `event` : Objet événement actuel d'OpenAI.

##### Retourne :
- `tool_outputs` (list) : Sorties au format JSON des fonctions appelées.

### Script Javascript pour améliorer l'expérience utilisateur

Le module `collapseAssistant.js` gère l'affichage et le comportement de la fenêtre de chat:

-   **Ouverture de la Fenêtre de Chat** : Lorsque le bouton `open-assistant` est cliqué, la fenêtre de chat est affichée et un gestionnaire d'événements est attaché pour faire défiler automatiquement les nouveaux messages vers le bas.
    
-   **Défilement Automatique de la section messages** : Un `eventListener` sur l'événement `htmx:wsAfterMessage` est utilisé pour faire défiler l'affichage vers le bas au fur et à mesure de leur arrivée en contournant un bug connu d'HTMX. ([Issue HTMX](https://github.com/bigskysoftware/htmx/issues/1882))
    
-   **Affichage/Masquage de la fenêtre** : Un bouton avec l'ID `collapse-assistant` permet de masquer ou d'afficher la fenêtre de chat et de déclencher des transitions CSS. Le texte du bouton change dynamiquement entre "Show" et "Hide" en fonction de l'état de la fenêtre, et est traduit selon la langue.


## Peuplement de la base de donnée

Le module `seed_data` est une commande de gestion personnalisée de Django conçue pour générer et peupler la base de données avec des données factices réalistes générées et traduites par GPT-4o.

### Fonctionnalités

- Génère des articles factices réalistes avec des titres et du contenu en anglais et en français.
- Génère des embedding pour chaque article.
- Insère les articles dans la base de donnée vectorielle.

### Utilisation

Pour utiliser la commande de génération de données factices, exécutez la commande suivante dans le terminal :
```sh
python manage.py seed_data <n_articles>
```
où `<n_articles>` est le nombre d'articles que vous souhaitez créer.

### Détails du code

#### Fonction `generate_data`

La fonction `generate_data` utilise GPT-4 pour générer des données factices à partir d'un mot clé donné. Elle renvoie un tuple contenant le titre et le contenu de l'article en anglais et en français, ainsi qu'une représentation intégrée du texte (embedding).

---

#### Classe `Command`

La classe `Command` définit la commande personnalisée `seed_data` pour Django. Elle gère les arguments de la commande et orchestre le processus de génération et de sauvegarde des articles dans la base de données.

## Tests

Les tests sont gérées par le module `tests.py`. La couverture est faible, mais ils permettent de refactorer plus sereinement, en vérifiant que les vues les plus critiques répondent correctement, du moins au niveau des templates renvoyés.

### Détails du code

#### Fonction `create_dummy_article`

Une fonction utilitaire pour créer rapidement un article factice dans la base de données. Elle génère un embedding pour le titre et le contenu de l'article.

---

#### Classe `AssistantTests`

Cette classe contient les tests pour les utilitaires de l'assistant et les interactions WebSocket.

##### Méthodes :

- `test_ws`: Vérifie la connexion, l'envoi et la réception de messages via WebSocket.
- `test_redirect`: Vérifie si la vue de l'assistant redirige vers une vue localisée.
- `test_create_assistant`: Vérifie la création d'un assistant et d'un thread de conversation.
- `test_create_embedding`: Vérifie les dimensions de l'embedding généré.
- `test_distance_search`: Vérifie la recherche par similarité dans la base de données avec une description d'article fournie.

---

#### Classe `ArticlesTests`

Cette classe contient les tests pour les vues d'articles.

##### Méthodes :

- `setUp`: Initialise un client de test Django.
- `test_get_article`: Vérifie si la vue d'un article utilise le bon template.
- `test_get_articles`: Vérifie si la vue de la liste d'articles utilise le bon template.
- `test_search_articles`: Vérifie si la vue de recherche d'articles utilise le bon template.

