self.addEventListener('install', function(e){ self.skipWaiting(); });
self.addEventListener('activate', function(e){ self.clients.claim(); });
self.addEventListener('push', function(e){
  try{
    var data = {};
    try{ data = e.data ? e.data.json() : {}; }catch(err){ data = {}; }
    var title = data.title || 'Synapsis';
    var opts = {
      body: data.body || '',
      icon: '/static/image/synapsis%20logo.png',
      tag: data.tag || 'synapsis',
      data: data.data || {}
    };
    e.waitUntil(self.registration.showNotification(title, opts));
  }catch(err){ }
});
self.addEventListener('notificationclick', function(e){
  e.notification.close();
  var url = (e.notification && e.notification.data && e.notification.data.url) || '/operativo/cierre-ciclo';
  e.waitUntil(clients.openWindow(url));
});
