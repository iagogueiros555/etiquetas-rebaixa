// Service worker mínimo. Existe só para o navegador considerar o site
// instalável. NÃO guarda cache de propósito: assim o app sempre abre a
// versão mais recente, sem você precisar limpar nada depois de publicar.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', () => {});
