# Event-Driven Order Management Platform

- Sipariş oluşturma, stok yönetimi ve ödeme süreçlerini kapsayan mikroservis tabanlı bir backend geliştirdim.
- Bu projede;
  - REST API’ler senkron çalışırken, stok ve ödeme akışları RabbitMQ üzerinden event-driven olarak asenkron yürütüldü.
  - Tutarlılığı sağlayabilmek için Saga ve compensation (telafi) mekanizmaları uygulandı.

---

## Teknoloji ve Mimari

| Alan                 | Kullanılan teknoloji / yaklaşım                                    |
| -------------------- | ------------------------------------------------------------------ |
| **Backend**          | Python, Django, Django REST Framework                              |
| **Veritabanı**       | PostgreSQL (her servis için ayrı DB)                               |
| **Mesaj kuyruğu**    | RabbitMQ (topic exchange, event isimlerine göre queue yönlendirme) |
| **Kimlik doğrulama** | JWT (SimpleJWT), stateless auth                                    |
| **Cache**            | In-memory (geliştirme); production için Redis’e geçilebilir        |
| **Container Yönetimi**     | Docker Compose (servisler + consumer’lar + RabbitMQ)               |

**Servisler:** user-service, product-service, order-service, inventory-service, payment-service. Her servis kendi veritabanına sahip; iletişim REST (senkron) ve event (asenkron) ile yapılır.

---

## API Gateway ve URL yapısı

**Gateway** (Nginx) tek giriş noktasıdır; istekleri path’e göre ilgili servise iletir.

| Kullanım              | Base URL                  | Açıklama                                                                                                 |
| --------------------- | ------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Gateway üzerinden** | `http://localhost:8080`   | Tüm API’lere tek adres. Gateway container’ı `docker-compose` ile ayağa kalkar (port **8080**).           |
| **Servise doğrudan**  | `http://localhost:<port>` | Geliştirme/debug: user **8001**, product **8002**, order **8003**, inventory **8004**, payment **8005**. |

**Gateway routing (path → servis):**

Tüm path’lerde **rate limit** uygulanır: **10 istek/saniye**, burst **20** (Nginx `limit_req_zone`).

| Path prefix   | Servis            | Rate limit         |
| ------------- | ----------------- | ------------------ |
| `/users/`     | user-service      | 10 req/s, burst 20 |
| `/products/`  | product-service   | 10 req/s, burst 20 |
| `/orders/`    | order-service     | 10 req/s, burst 20 |
| `/inventory/` | inventory-service | 10 req/s, burst 20 |
| `/payments/`  | payment-service   | 10 req/s, burst 20 |

Gateway kullanırken tüm endpoint’ler **`http://localhost:8080`** ile başlar (örn. `http://localhost:8080/users/register/`). Doğrudan servise giderken base **`http://localhost:<port>`** olur (örn. `http://localhost:8001/users/register/`).

---

## API Endpoint’leri

Tüm endpoint’ler JSON alır/verir. `<id>`, `<product_id>`, `<order_id>` UUID’dir.

### User Service

**Base path:** `/users/`  
**Tam URL (gateway):** `http://localhost:8080/users/...`  
**Tam URL (direkt):** `http://localhost:8001/users/...`

| Method | Endpoint                | Query / body              | Açıklama                                    |
| ------ | ----------------------- | ------------------------- | ------------------------------------------- |
| POST   | `/users/register/`      | Body: `email`, `password` | Kayıt; şifre hash’lenir, JWT döner.         |
| POST   | `/users/login/`         | Body: `email`, `password` | Giriş; access + refresh token.              |
| POST   | `/users/refresh-token/` | Body: `refresh`           | Access token yenileme.                      |
| POST   | `/users/logout/`        | Body: `refresh`           | Çıkış (refresh blacklist). **JWT gerekli.** |
| GET    | `/users/user-profile/`  | —                         | Mevcut kullanıcı bilgisi. **JWT gerekli.**  |
| POST   | `/users/verify-token/`  | Body: `token`             | Token doğrulama (diğer servisler için).     |

### Product Service

**Base path:** `/products/`  
**Tam URL (gateway):** `http://localhost:8080/products/...`  
**Tam URL (direkt):** `http://localhost:8002/products/...`

| Method | Endpoint                 | Query / body                                                                           | Açıklama                                                     |
| ------ | ------------------------ | -------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| GET    | `/products/all/`         | `page`, `page_size`, `only_active`, `min_price`, `max_price`, `search`, `sku`, `order` | Ürün listesi (pagination + cache). Aşağıda query açıklaması. |
| GET    | `/products/<id>/`        | —                                                                                      | Ürün detay (cache).                                          |
| POST   | `/products/create/`      | Body: ürün alanları                                                                    | Ürün oluştur. **JWT gerekli.**                               |
| PUT    | `/products/<id>/update/` | Body: güncellenecek alanlar                                                            | Ürün güncelle; cache invalidate. **JWT gerekli.**            |

**GET /products/all/ query parametreleri:**

| Parametre     | Tip    | Varsayılan    | Açıklama                                                                                  |
| ------------- | ------ | ------------- | ----------------------------------------------------------------------------------------- |
| `page`        | int    | 1             | Sayfa numarası.                                                                           |
| `page_size`   | int    | 20, max 100   | Sayfa başına kayıt.                                                                       |
| `only_active` | bool   | true          | Sadece aktif ürünler.                                                                     |
| `min_price`   | float  | —             | Min fiyat.                                                                                |
| `max_price`   | float  | —             | Max fiyat.                                                                                |
| `search`      | string | —             | İsim/benzeri arama.                                                                       |
| `sku`         | string | —             | SKU ile filtre.                                                                           |
| `order`       | string | `-created_at` | Sıralama: `created_at`, `-created_at`, `price`, `-price`, `name`, `-name`, `sku`, `-sku`. |

### Order Service

**Base path:** `/orders/`  
**Tam URL (gateway):** `http://localhost:8080/orders/...`  
**Tam URL (direkt):** `http://localhost:8003/orders/...`

| Method | Endpoint                | Query / body                    | Açıklama                                                              |
| ------ | ----------------------- | ------------------------------- | --------------------------------------------------------------------- |
| POST   | `/orders/create-order/` | Body: `total_amount`, `items[]` | Sipariş oluştur; **order.created** event yayınlanır. **JWT gerekli.** |
| GET    | `/orders/all/`          | `page`, `page_size`             | Kullanıcının siparişleri (pagination). **JWT gerekli.**               |
| GET    | `/orders/<id>/`         | —                               | Sipariş detayı (cache). **JWT gerekli.**                              |

**GET /orders/all/ query parametreleri:**

| Parametre   | Tip | Varsayılan  | Açıklama            |
| ----------- | --- | ----------- | ------------------- |
| `page`      | int | 1           | Sayfa numarası.     |
| `page_size` | int | 20, max 100 | Sayfa başına kayıt. |

### Inventory Service

**Base path:** `/inventory/`  
**Tam URL (gateway):** `http://localhost:8080/inventory/...`  
**Tam URL (direkt):** `http://localhost:8004/inventory/...`

| Method | Endpoint                   | Query / body                                  | Açıklama                                         |
| ------ | -------------------------- | --------------------------------------------- | ------------------------------------------------ |
| GET    | `/inventory/all`           | —                                             | Tüm stok kayıtları.                              |
| POST   | `/inventory/create`        | Body: `product_id`, `product_sku`, `quantity` | Stok ekle veya güncelle (product_id ile upsert). |
| GET    | `/inventory/<product_id>/` | —                                             | Ürüne göre stok.                                 |
| PUT    | `/inventory/<product_id>/` | Body: `quantity`                              | Stok miktarı güncelle.                           |

### Payment Service

**Base path:** `/payments/`  
**Tam URL (gateway):** `http://localhost:8080/payments/...`  
**Tam URL (direkt):** `http://localhost:8005/payments/...`

| Method | Endpoint                      | Query / body           | Açıklama                             |
| ------ | ----------------------------- | ---------------------- | ------------------------------------ |
| GET    | `/payments/all/`              | `order_id` (opsiyonel) | Son ödemeler; `order_id` ile filtre. |
| GET    | `/payments/order/<order_id>/` | —                      | Siparişe ait ödeme kaydı.            |

**GET /payments/all/ query parametreleri:**

| Parametre  | Tip  | Açıklama                                |
| ---------- | ---- | --------------------------------------- |
| `order_id` | UUID | Sadece bu siparişe ait ödemeleri döner. |

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

Bu proje kapsamında:

- Mikroservis mimarisi ve servisler arası iletişim
- REST API tasarımı ve HTTP tabanlı senkron akışlar
- RabbitMQ ile event-driven ve asenkron sistemler
- Saga pattern ve compensation yaklaşımı ile distributed sistemlerde tutarlılık
- API Gateway, rate limiting ve temel güvenlik önlemleri
- Veritabanı modelleme ve servis bazlı veri izolasyonu

konularında pratik yaparak, kendimi geliştirdim.
