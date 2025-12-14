# 💰 Bulut Maliyet Simülasyonu (FinOps Raporu)

Bu rapor, Iris MLOps projesinin AWS Lambda (Serverless) üzerinde çalıştırılması durumunda oluşacak tahmini maliyetleri içerir.

## 1. Test Verileri (Baseline)
Load test sonuçlarına (Locust) dayanmaktadır:
* **Ortalama İşlem Süresi (Latency):** 530 ms (0.53 saniye)
* **Kullanılan Bellek (Memory):** ~150 MB (128 MB'lık Lambda yetmeyebilir, 256 MB seçilmeli)
* **Tahmini Trafik:** Ayda 1.000.000 İstek (Orta ölçekli bir start-up)

## 2. AWS Lambda Maliyet Hesabı (x86 Mimarisi)
*AWS us-east-1 bölgesi fiyatları baz alınmıştır.*

* **Birim Fiyat (256 MB RAM için):** $0.0000000042 / milisaniye
* **İstek Başına Maliyet:** 530 ms * $0.0000000042 = **$0.000002226**

## 3. Aylık Toplam Tahmin
Eğer ayda 1 Milyon kişi bu API'yi kullanırsa:

> 1,000,000 * $0.000002226 = **$2.23 (Aylık)**

## 4. Sonuç ve Öneri
Sistem oldukça uygun maliyetlidir. Ancak yük arttıkça (Locust testinde görüldüğü gibi) cevap süresi 2.6 saniyeye kadar çıkabilmektedir. 
Maliyeti düşürmek yerine performansı artırmak için **Auto-Scaling** politikaları veya **Asenkron Mimari** (Celery/RabbitMQ) düşünülmelidir.
