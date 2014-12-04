Server for serving images
=========================

This is an expermental server for serving images with `SocketIO`. It intends to
be a replacement of existing map loading mechanism(directly issue multiple
HTTP calls to retrieve images) with a single connection, which should speed up
the user experience.

node.js must be installed on the server.
