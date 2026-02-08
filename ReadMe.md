# Proje Amacı

Bu proje, bir Order Management System (OMS) kapsamında,
sipariş oluşturma ve yönetme süreçlerini ele alan bir arka uç uygulamasıdır.

Sistem; kullanıcıların sipariş oluşturmasını, ürün stoklarının kontrol edilmesini,
ödeme sürecinin simüle edilmesini ve sipariş durumlarının yönetilmesini sağlar.

Proje; Django ve PostgreSQL kullanılarak, modüler monolith mimaride geliştirilmiş,
senkron REST API’ler ile kullanıcıya anında geri dönüş sağlarken,
stok ve ödeme gibi yan etkileri event-driven (asenkron) yaklaşımla yönetmektedir.

Bu yapı sayesinde;

- servis sınırları,
- senkron ve asenkron iletişim trade-off’ları,
- saga ve telafi (compensation) mantığı,
- caching, güvenlik ve veri modeli optimizasyonu

gerçekçi bir iş senaryosu üzerinden pratik olarak gösterilmektedir.

# Servisler

## User / Auth

Kullanıcı kimlik doğrulama ve yetkilendirme işlemlerini JWT tabanlı güvenli bir yapı ile yönetir ve diğer servisler için güvenilir bir kullanıcı bağlamı sağlar.

## Product / Catalog

Ürünlerin okunabilir şekilde listelenmesini ve detaylarının sunulmasını sağlar; sık okunan veriler Redis ile cache’lenerek performans optimizasyonu gösterilir.

## Order

Sipariş oluşturma sürecinin ana iş kurallarını barındırır, REST API üzerinden gelen istekleri doğrular ve sipariş yaşam döngüsünü başlatan merkezi iş kararlarını verir.

## Inventory

Ürün stoklarını yönetir, sipariş sonrası stok düşme işlemlerini asenkron event’ler üzerinden gerçekleştirerek eventual consistency yaklaşımını uygular.

## Payment (Mock)

Ödeme sürecini simüle eder, başarısız senaryolarda sipariş iptali için telafi (compensation) mantığını tetikleyerek saga desenini pratikte gösterir.

## Notification (Opsiyonel / Event Consumer)

Sipariş durum değişikliklerini dinleyerek bildirim üretir ve event-driven mimaride yeni consumer eklemenin sistemi etkilemeden nasıl yapılabildiğini gösterir.

# Event flow (RabbitMQ)

- **Exchange:** `events` (topic)
- **Order oluşturulunca:** Order-service `order.created` yayınlar (order_id, user_id, total_amount, items).
- **Inventory-service:** `order.created` dinler; stok yeterliyse düşer ve `inventory.stock_reserved` yayınlar, yetersizse `inventory.stock_failed` yayınlar.
- **Payment-service:** `order.created` dinler; ödeme simülasyonu (demo: total_amount > 10000 ise fail) yapar, `payment.authorized` veya `payment.failed` yayınlar.
- **Order-service:** `inventory.stock_failed` ve `payment.failed` dinler; ilgili siparişi **CANCELLED** yapar ve cache invalidate eder.

Consumer'lar `docker-compose up` ile ayrı container'larda (order-consumer, inventory-consumer, payment-consumer) otomatik çalışır. Lokal çalıştırıyorsanız her serviste:

- `python manage.py consume_order_events`

# Çalıştırma

1. `docker-compose up --build` (RabbitMQ + tüm servisler + consumer'lar)
2. Migrations: ilk seferde her servis DB'sinde `python manage.py migrate` (veya compose run ile)
3. User: `POST /users/register` → login → JWT ile `POST /orders/create-order/`, `GET /orders/`, `GET /orders/{id}/`

Inventory'de stok kaydı eklemek için admin veya shell ile `Inventory` (product_id, product_sku, quantity) oluşturun; product_id order item'lardaki product_id ile eşleşmeli.

# Servis klasör yapısı (mimari)

Tüm servisler aynı katmanlı yapıyı takip eder:

```
<service>/
  app/                    # Django proje config (settings, urls, wsgi)
  <domain_app>/           # orders | inventory | payments | products | users
    __init__.py
    apps.py
    admin.py
    models.py             # Domain modelleri
    exceptions.py         # Domain exception'ları (varsa)
    selectors.py          # Okuma sorguları (varsa)

    api/                  # HTTP katmanı
      __init__.py
      serializers.py
      urls.py
      views.py

    services/             # İş mantığı (use case'ler)
      __init__.py
      <domain>_service.py # order_service | inventory_service | payment_service | product_service

    common/                # Ortak altyapı (auth, cache, response, exception_handler — sadece ihtiyaç olan servislerde)
      __init__.py
      exception_handler.py
      responses.py
      jwt_auth.py
      request_id.py
      *_cache.py

    messaging/             # Event-driven iletişim (order, inventory, payment)
      __init__.py
      constants.py        # EXCHANGE, ROUTING_*, QUEUE_*
      publisher.py        # Yayınlanan event'ler
      consumer.py         # Dinlenen event'ler ve işleme

    management/
      commands/
        consume_order_events.py   # python manage.py consume_order_events

    migrations/
```

**Order-service:** `orders/messaging/` → OrderCreated yayınlar; StockFailed, PaymentFailed dinler.  
**Inventory-service:** `inventory/messaging/` → OrderCreated dinler; StockReserved, StockFailed yayınlar.  
**Payment-service:** `payments/messaging/` → OrderCreated dinler; PaymentAuthorized, PaymentFailed yayınlar.

# Architecturel Overview
