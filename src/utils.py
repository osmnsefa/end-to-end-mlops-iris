import functools
import time
import os
import psutil  # Sistem kaynaklarına (CPU, RAM) erişmek için kullanılan kütüphane

def measure_resources(func):
    """
    Fonksiyonların çalışma süresini ve bellek (RAM) kullanımını ölçen decorator.
    
    Bu decorator, sarılan fonksiyonun:
    1. Kaç milisaniye sürdüğünü,
    2. Çalışırken RAM'de ne kadar (MB) artışa sebep olduğunu ölçer.
    
    Args:
        func (callable): Ölçüm yapılacak fonksiyon.
        
    Returns:
        wrapper: Orijinal fonksiyonun ölçüm yeteneği eklenmiş hali.
    """
    
    @functools.wraps(func) # Orijinal fonksiyonun ismini ve dokümantasyonunu korur (Debug için önemlidir)
    def wrapper(*args, **kwargs):
        # Şu an çalışan işlemin (Process) kimliğini (PID) alıyoruz
        process = psutil.Process(os.getpid())
        
        # --- BAŞLANGIÇ ÖLÇÜMÜ ---
        # rss (Resident Set Size): İşlemin RAM'de kapladığı fiziksel alan.
        # Bayt cinsinden gelir, MB'a çevirmek için 1024*1024'e bölüyoruz.
        start_mem = process.memory_info().rss / (1024 * 1024) 
        start_time = time.time()
        
        try:
            # --- ASIL FONKSİYONUN ÇALIŞTIRILMASI ---
            # Fonksiyonu argümanlarıyla çalıştırıp sonucunu result değişkenine alıyoruz.
            result = func(*args, **kwargs)
            return result
            
        finally:
            # --- BİTİŞ ÖLÇÜMÜ ---
            # Fonksiyon hata verse bile (try/finally sayesinde) burası çalışır ve raporu basar.
            end_time = time.time()
            end_mem = process.memory_info().rss / (1024 * 1024)
            
            # Hesaplamalar
            duration = (end_time - start_time) * 1000  # Saniyeyi milisaniyeye çevir
            mem_diff = end_mem - start_mem             # Ne kadar ekstra RAM harcandı?
            
            # --- RAPORLAMA ---
            # Bunu konsola basıyoruz. İleride bunu log dosyasına veya Grafana'ya gönderebiliriz.
            print(f"\n[RESOURCE MONITOR] '{func.__name__}' Raporu:")
            print(f"  ⏱️  Süre: {duration:.2f} ms")
            print(f"  💾 Bellek Değişimi: {mem_diff:+.4f} MB") # (+ artış, - azalış gösterir)
            print(f"  📊 Toplam Bellek: {end_mem:.2f} MB")
            print("-" * 30)

    return wrapper