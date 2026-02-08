# Event-Driven Order Management Platform

# TODO

Sipariş oluşturma, stok yönetimi ve ödeme akışını kapsayan **mikroservis tabanlı** bir backend. REST API’ler senkron çalışır; stok ve ödeme işlemleri **event-driven** (RabbitMQ) ile asenkron yürütülür. Saga ve telafi (compensation) mantığı ile tutarlılık sağlanır.

---

## Teknoloji ve Mimari

| Alan                 | Kullanılan teknoloji / yaklaşım                                    |
| -------------------- | ------------------------------------------------------------------ |
| **Backend**          | Python, Django, Django REST Framework                              |
| **Veritabanı**       | PostgreSQL (her servis için ayrı DB)                               |
| **Mesaj kuyruğu**    | RabbitMQ (topic exchange, event isimlerine göre queue yönlendirme) |
| **Kimlik doğrulama** | JWT (SimpleJWT), stateless auth                                    |
| **Cache**            | In-memory (geliştirme); production için Redis’e geçilebilir        |
| **Orkestrasyon**     | Docker Compose (servisler + consumer’lar + RabbitMQ)               |

**Servisler:** user-service, product-service, order-service, inventory-service, payment-service. Her servis kendi veritabanına sahip; iletişim REST (senkron) ve event (asenkron) ile yapılır.

---

## API Endpoint’leri

Tüm endpoint’ler JSON alır/verir. Portlar: user **8001**, product **8002**, order **8003**, inventory **8004**, payment **8005**.

### User Service — `/users/`

| Method | Endpoint                | Açıklama                                             |
| ------ | ----------------------- | ---------------------------------------------------- |
| POST   | `/users/register/`      | Kayıt (email, password); şifre hash’lenir, JWT döner |
| POST   | `/users/login/`         | Giriş; access + refresh token                        |
| POST   | `/users/refresh-token/` | Access token yenileme                                |
| POST   | `/users/logout/`        | Çıkış (refresh token blacklist) — **JWT gerekli**    |
| GET    | `/users/user-profile/`  | Mevcut kullanıcı bilgisi — **JWT gerekli**           |
| POST   | `/users/verify-token/`  | Token doğrulama (diğer servisler için)               |

### Product Service — `/products/`

| Method | Endpoint                 | Açıklama                                           |
| ------ | ------------------------ | -------------------------------------------------- |
| GET    | `/products/all/`         | Ürün listesi (pagination, cache)                   |
| GET    | `/products/<id>/`        | Ürün detay (cache)                                 |
| POST   | `/products/create/`      | Ürün oluştur — **JWT gerekli**                     |
| PUT    | `/products/<id>/update/` | Ürün güncelle (cache invalidate) — **JWT gerekli** |

### Order Service — `/orders/`

| Method | Endpoint                | Açıklama                                                              |
| ------ | ----------------------- | --------------------------------------------------------------------- |
| POST   | `/orders/create-order/` | Sipariş oluştur; **order.created** event yayınlanır — **JWT gerekli** |
| GET    | `/orders/`              | Kullanıcının siparişleri (pagination) — **JWT gerekli**               |
| GET    | `/orders/<id>/`         | Sipariş detayı (cache) — **JWT gerekli**                              |

### Inventory Service — `/inventory/`

| Method | Endpoint                   | Açıklama                                        |
| ------ | -------------------------- | ----------------------------------------------- |
| GET    | `/inventory/`              | Tüm stok kayıtları                              |
| POST   | `/inventory/`              | Stok ekle veya güncelle (product_id ile upsert) |
| GET    | `/inventory/<product_id>/` | Ürüne göre stok                                 |
| PUT    | `/inventory/<product_id>/` | Stok miktarı güncelle                           |

### Payment Service — `/payments/`

| Method | Endpoint                      | Açıklama                                         |
| ------ | ----------------------------- | ------------------------------------------------ |
| GET    | `/payments/`                  | Son ödemeler (opsiyonel `?order_id=` ile filtre) |
| GET    | `/payments/order/<order_id>/` | Siparişe ait ödeme kaydı                         |

---

## Event Akışı (RabbitMQ)

- **Exchange:** `events` (topic).
- **Order oluşturulunca:** Order-service **order.created** yayınlar (order_id, user_id, total_amount, items).
- **Inventory:** **order.created** dinler; stok yeterliyse düşer ve **inventory.stock_reserved**, yetersizse **inventory.stock_failed** yayınlar.
- **Payment:** **order.created** dinler; ödeme simülasyonu (demo: total_amount > 10000 ise fail) yapar; **payment.authorized** veya **payment.failed** yayınlar.
- **Order:** **inventory.stock_failed** ve **payment.failed** dinler; ilgili siparişi **CANCELLED** yapar ve cache invalidate eder.

Consumer’lar ayrı process/container’da çalışır: `python manage.py consume_order_events` (order, inventory, payment servislerinde).

---

## Çalıştırma

```bash
docker-compose up -d --build
```

İlk seferde migration:

```bash
docker-compose run user-service python manage.py migrate
docker-compose run product-service python manage.py migrate
docker-compose run order-service python manage.py migrate
docker-compose run inventory-service python manage.py migrate
docker-compose run payment-service python manage.py migrate
```

Stok eklemek için: `POST /inventory/` ile `product_id`, `product_sku`, `quantity` gönderin (product_id, product-service’teki ürün UUID’si olmalı).

---

## Proje Yapısı (Klasör Mimarisı)

Her serviste katmanlı yapı kullanıldı:

- **api/** — HTTP katmanı (views, serializers, urls)
- **services/** — İş mantığı (use case’ler)
- **messaging/** — Event yayınlama (publisher) ve dinleme (consumer), routing/queue sabitleri
- **common/** — Exception handler, response formatı, JWT auth, cache, request_id (ihtiyaç olan servislerde)
- **models.py, selectors.py, exceptions.py** — Domain ve okuma katmanı

Kod; test edilebilir, okunabilir ve sürdürülebilir olacak şekilde API / servis / messaging ayrımına uygun yazıldı.

---

## Teknik Özellikler ve Uygulanan Konular

- **Servis mimarisi ve API tasarımı:** Mikroservis sınırları, RESTful endpoint’ler, tutarlı response formatı (success/error, kod ve mesaj).
- **Veri modeli:** Servis başına ayrı veritabanı, UUID primary key, ilişkiler ve index’ler (sorgu performansı).
- **Mesaj kuyruğu:** RabbitMQ topic exchange, event publish/consume, queue ve routing key kullanımı.
- **Caching:** Ürün listesi/detay ve sipariş detayı için cache; create/update’te invalidate.
- **Güvenlik:** JWT (access/refresh), şifre hash’leme, token blacklist; product/order servislerinde stateless JWT doğrulama.
- **Veritabanı:** PostgreSQL, migration’lar, index’ler, transaction (stok rezervasyonu), select_for_update ile race condition önleme.
- **Saga / telafi:** Stok veya ödeme başarısız olunca siparişin CANCELLED yapılması ve cache invalidate.
- **Kod kalitesi:** Katmanlı yapı (api, services, messaging, common), domain exception’lar, ortak exception handler, sürdürülebilir klasör düzeni.
- **Dağıtım:** Docker Compose ile tüm servislerin ve consumer’ların tek komutla ayağa kalkması; Git ile versiyon kontrolüne uygun yapı.

# Kazanımlar

Bu proje; servis mimarisi, REST API, event-driven sistemler, cache, güvenlik ve veritabanı tasarımı konularında pratik deneyim göstermek için uygundur.
