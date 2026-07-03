import path from 'path';
import react from '@vitejs/plugin-react';
import { defineConfig, loadEnv, type Plugin } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';

function renderFirebaseMessagingWorker(env: Record<string, string>): string {
  const firebaseConfig = {
    apiKey: env.VITE_FIREBASE_API_KEY ?? '',
    authDomain: env.VITE_FIREBASE_AUTH_DOMAIN ?? '',
    projectId: env.VITE_FIREBASE_PROJECT_ID ?? '',
    storageBucket: env.VITE_FIREBASE_STORAGE_BUCKET ?? '',
    messagingSenderId: env.VITE_FIREBASE_MESSAGING_SENDER_ID ?? '',
    appId: env.VITE_FIREBASE_APP_ID ?? ''
  };

  return `importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-messaging-compat.js');

const firebaseConfig = ${JSON.stringify(firebaseConfig, null, 2)};

if (Object.values(firebaseConfig).every(Boolean)) {
  firebase.initializeApp(firebaseConfig);
  const messaging = firebase.messaging();

  messaging.onBackgroundMessage((payload) => {
    const data = payload.data || {};
    const title = payload.notification?.title || 'CrowdIQ notification';
    const body = payload.notification?.body || '';
    const isEmergency = data.type === 'EMERGENCY';

    self.registration.showNotification(title, {
      body,
      icon: '/favicon.svg',
      data: {
        url: isEmergency ? '/emergency' : '/',
        type: data.type || 'GENERIC'
      },
      requireInteraction: isEmergency
    });
  });
} else {
  console.warn('Firebase messaging service worker is not configured.');
}

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = event.notification.data?.url || '/';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if ('focus' in client) {
          client.navigate(url);
          return client.focus();
        }
      }
      return clients.openWindow(url);
    })
  );
});
`;
}

function firebaseMessagingWorkerPlugin(env: Record<string, string>): Plugin {
  const fileName = 'firebase-messaging-sw.js';
  const source = () => renderFirebaseMessagingWorker(env);

  return {
    name: 'firebase-messaging-worker',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (req.url?.split('?')[0] !== `/${fileName}`) {
          next();
          return;
        }

        res.statusCode = 200;
        res.setHeader('Content-Type', 'application/javascript');
        res.end(source());
      });
    },
    generateBundle() {
      this.emitFile({
        type: 'asset',
        fileName,
        source: source()
      });
    }
  };
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_');

  return {
    base: '/',
    plugins: [
      firebaseMessagingWorkerPlugin(env),
      react(),
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['favicon.svg', 'offline.html'],
        manifest: {
          name: 'CrowdIQ Smart Stadium Experience',
          short_name: 'CrowdIQ',
          description: 'Real-time crowd intelligence for large-scale sporting events',
          theme_color: '#0F172A',
          background_color: '#0F172A',
          display: 'standalone',
          scope: '/',
          start_url: '/?source=pwa',
          orientation: 'portrait-primary',
          categories: ['sports', 'navigation', 'utilities'],
          icons: [
            { src: '/favicon.svg', sizes: '192x192', type: 'image/svg+xml', purpose: 'any' },
            { src: '/favicon.svg', sizes: '512x512', type: 'image/svg+xml', purpose: 'any maskable' }
          ]
        },
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,svg}'],
          navigateFallback: '/index.html',
          navigateFallbackDenylist: [/^\/api\//],
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/maps\.googleapis\.com\/.*/i,
              handler: 'CacheFirst',
              options: {
                cacheName: 'google-maps-cache',
                expiration: { maxEntries: 10, maxAgeSeconds: 60 * 60 * 24 * 7 }
              }
            },
            {
              urlPattern: /^https:\/\/maps\.gstatic\.com\/.*/i,
              handler: 'CacheFirst',
              options: {
                cacheName: 'maps-static-cache',
                expiration: { maxEntries: 50, maxAgeSeconds: 60 * 60 * 24 * 30 }
              }
            },
            {
              urlPattern: /^https:\/\/firebasestorage\.googleapis\.com\/.*/i,
              handler: 'NetworkFirst',
              options: {
                cacheName: 'firebase-storage-cache',
                networkTimeoutSeconds: 5,
                expiration: { maxEntries: 50, maxAgeSeconds: 60 * 60 * 24 }
              }
            },
            {
              urlPattern: /\/locales\/.*\.json$/i,
              handler: 'StaleWhileRevalidate',
              options: { cacheName: 'i18n-cache' }
            }
          ]
        }
      })
    ],
    resolve: {
      alias: { '@': path.resolve(__dirname, './src') }
    },
    build: {
      target: 'es2020',
      sourcemap: false,
      chunkSizeWarningLimit: 600,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom', 'react-router-dom'],
            firebase: ['firebase/app', 'firebase/auth', 'firebase/firestore', 'firebase/messaging', 'firebase/storage'],
            maps: ['@react-google-maps/api']
          }
        }
      }
    },
    server: {
      port: 5173,
      host: true
    }
  };
});
