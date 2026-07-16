"""
Her görsel için üretilen sidecar `.json` dosyasını okuyan, güncelleyen modül.

Sidecar dosyası; orijinal dosyanın hash'i, hedef boyut, çıktı yolları ve
bütünlük kontrolü sonucu gibi bilgileri taşır.
"""
import os, json

class SidecarStore():
    """Sidecar json dosyasını okuyup güncelleyen sınıf.

    Burada birden fazla strateji yok, tek bir mantık yeterli olduğu için
    soyut bir sınıf yok.
    """

    def update(self, path: str, fields: dict) -> None:
        """Sidecar dosyasına yeni alanlar ekler, var olanları korur.

        Dosya yoksa `fields` ile sıfırdan oluşturulur. Dosya varsa önce
        okunur, `fields` üstüne eklenir, sonra tekrar yazılır.
        Böylece önceki çağrıdan kalan alanlar silinmez.

        Args:
            path: Sidecar json dosyasının yolu.
            fields: Eklenecek anahtar değer çiftleri.
        """
        if os.path.exists(path):
            # Dosya daha önce yazılmış üstüne eklemeden önce mevcut
            # içeriği kaybetmemek için önce okunur
            with open(path, "r") as file:
                data = json.load(file)
        else:
            # İlk defa yazılıyor, boş bir sözlükten başlanır.
            data = {}

        # Yeni gelen alanları mevcut veriyle birleştirir. Ortak anahtarlar
        # güncellenir, eskiden kalanlar silinmez.
        data.update(fields)

        # "w" modu dosyanın tamamını yeniden yazar, bu yüzden birleştirilmiş
        # eski + yeni veri yazılır, sadece fields değil.
        with open(path, "w") as file:
            json.dump(data, file)