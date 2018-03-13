Web Client Mechanics
====================

The ClientManager handles web clients in cooperation with the WebSocket.
All client and user requests run through the ClientManager.

Legitimate requests are fired off to their according request managers.

It delegates authentication requests separately to the Auth Component.