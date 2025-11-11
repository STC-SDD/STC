# Attribution des fragments

Il s’agit de concevoir comment le serveur va déterminer et attribuer dynamiquement les morceaux de vidéo à chaque sous-titreur connecté.

Voici quelques axes importants pour cette tâche :

Fragmentation efficace : Décider la taille et la durée des fragments à distribuer (ex : par phrases, segments temporels, ou phrases détectées automatiquement).

Répartition dynamique : L’algorithme doit prendre en compte l’arrivée, le départ ou même la performance des sous-titreurs en cours de session.

Équilibrage et redondance : Éviter de surcharger un utilisateur et permettre éventuellement, pour certains fragments, une relecture par un autre sous-titreur pour la qualité.

Gestion des cas particuliers : Absence inattendue, sous-titreur trop lent, correction de dernière minute, etc.

Communication serveur/clients : Concevoir la structure des messages ou API entre serveur et front-end pour l’attribution, la récupération et le suivi en temps réel.
