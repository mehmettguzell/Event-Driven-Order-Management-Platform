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

# Architecturel Overview
