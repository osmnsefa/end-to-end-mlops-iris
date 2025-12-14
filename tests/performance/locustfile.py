import random
from locust import HttpUser, task, between

class IrisUser(HttpUser):
    """
    Bu sınıf, sistemimizi ziyaret eden sanal bir kullanıcıyı (User) temsil eder.
    Locust, testimiz başladığında bu sınıftan belirlediğimiz sayıda (örn: 50 tane)
    örnek (instance) oluşturur ve hepsini aynı anda çalıştırır.
    """

    # --- BEKLEME SÜRESİ (THINK TIME) ---
    # Gerçek kullanıcılar makineli tüfek gibi arka arkaya tıklamaz.
    # Bir işlem yaptıktan sonra sonucu okur, düşünür ve sonraki işlemi yapar.
    # 'between(1, 3)' komutu, her kullanıcının istekler arasında 
    # rastgele 1 ile 3 saniye beklemesini sağlar.
    wait_time = between(1, 3)

    @task
    def predict_flower(self):
        """
        @task decorator'ı, Locust'a bunun tekrarlanacak bir 'görev' olduğunu söyler.
        Kullanıcı her döngüde bu fonksiyonu çalıştırır.
        """
        
        # --- RASTGELE VERİ ÜRETİMİ (DATA VARIANCE) ---
        # Neden sabit veri (Hardcoded) kullanmıyoruz?
        # 1. Sunucu cevabı önbelleğe (Cache) alabilir, test yanıltıcı olur.
        # 2. Modelin farklı sayısal değerlere nasıl tepki verdiğini ölçmek istiyoruz.
        # Iris veri setinin gerçek sınırlarına uygun rastgele float sayılar üretiyoruz.
        payload = {
            "sepal_length": round(random.uniform(4.0, 8.0), 1), # Örn: 5.4
            "sepal_width": round(random.uniform(2.0, 4.5), 1),  # Örn: 3.1
            "petal_length": round(random.uniform(1.0, 7.0), 1), # Örn: 1.5
            "petal_width": round(random.uniform(0.1, 2.5), 1)   # Örn: 0.2
        }
        
        # --- İSTEK GÖNDERME (THE ATTACK) ---
        # self.client, 'requests' kütüphanesi gibi çalışır ama istatistik tutar.
        # json=payload: Veriyi JSON formatında gövdeye (body) ekler.
        # name="/predict": Locust arayüzünde istatistiklerin dağınık görünmemesi için
        # bu isteği "/predict" etiketi altında gruplar.
        self.client.post("/predict", json=payload, name="/predict")