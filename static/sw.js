// Service Worker for Vanity PWA
const CACHE_NAME = 'vanity-v1.0.0';
const urlsToCache = [
    '/',
    '/content/tasks/',
    '/static/css/mobile.css',
    '/static/manifest.json',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
];

// 安装事件
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                return cache.addAll(urlsToCache);
            })
    );
});

// 激活事件
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// 拦截网络请求
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // 如果有缓存则返回缓存
                if (response) {
                    return response;
                }
                
                // 否则发起网络请求
                return fetch(event.request).then(function(response) {
                    // 检查是否收到有效响应
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }
                    
                    // 克隆响应
                    var responseToCache = response.clone();
                    
                    caches.open(CACHE_NAME)
                        .then(function(cache) {
                            cache.put(event.request, responseToCache);
                        });
                    
                    return response;
                });
            })
            .catch(function() {
                // 网络失败时的离线页面
                if (event.request.destination === 'document') {
                    return caches.match('/content/tasks/');
                }
            })
    );
});

// 后台同步
self.addEventListener('sync', function(event) {
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

function doBackgroundSync() {
    // 这里可以实现后台数据同步
    return Promise.resolve();
}

// 推送通知
self.addEventListener('push', function(event) {
    const options = {
        body: event.data ? event.data.text() : '你有新的任务提醒',
        icon: '/static/icons/icon-192.png',
        badge: '/static/icons/badge.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: '查看任务',
                icon: '/static/icons/checkmark.png'
            },
            {
                action: 'close',
                title: '关闭',
                icon: '/static/icons/xmark.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('Vanity 任务提醒', options)
    );
});

// 通知点击事件
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/content/tasks/')
        );
    }
});