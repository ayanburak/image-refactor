"""
Görsel dosyalarını EXIF yönüne göre doğru döndürerek piksel matrisine
çeviren yükleyiciler.

Telefonlar bir fotoğrafı çekerken sensörü fiziksel olarak döndürmez;
bunun yerine dosyanın EXIF (metadata) bilgisine "bunu şu yönde göster" diye
bir etiket ekler. Bu etiket uygulanmazsa, elde edilen piksel matrisi
kullanıcının telefonda gördüğü görüntüyle aynı yönde olmayabilir.
"""

from abc import abstractmethod, ABC
import numpy as np

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()          #Pillow'un HEIC dosyalarını da açabilmesi için bir kere çağrılması yeterli.

# --- Soyut Sınıf ---

class ImageLoader(ABC):
    """Görsel yükleme stratejileri için soyut sınıf."""

    @abstractmethod
    def load(self, path: str) -> np.array:
        """Görsel dosyasını okuyup piksel matrisine çevirir.

        Args:
            path: Okunacak görsel dosyasının yolu.

        Returns:
            Yükseklik, Genişlik, Renk şeklinde RGB piksel matrisi.
        """
        pass

# --- Somut stratejiler ---

# EXIF, bir görsel dosyasının içine gömülü metadata standardı
# çekim tarihi, kamera modeli gibi bilgilerin yanında, bizim için 
# önemli olan orientation etiketini de taşır. 
# Telefon, fotoğrafı sensörün baktığı hâliyle kaydeder ve 
# bunu göstermeden önce şu kadar döndür bilgisini bu etikete yazar.
#
#
class LoadByExif(ImageLoader):
    """`ImageLoader` soyut sınıfını, EXIF yönünü düzelterek dolduran sınıf.

    `load` çağrıldığında sırasıyla: dosyayı Pillow ile açar, EXIF
    etiketine göre gerekiyorsa döndürür, renk modunu RGB'ye sabitler,
    ve sonucu numpy piksel matrisine çevirir. HEIC dosyaları da aynı 
    şekilde açılabilir.
    """

    def load(self, path: str) -> np.array:
        image = Image.open(path)

        # EXIF etiketine göre gerekiyorsa döndürür; etiket normal ya da
        # yoksa hiçbir şey yapmadan görseli olduğu gibi bırakır.
        image = ImageOps.exif_transpose(image)

        # Bazı görseller gri tonlamalı ya da farklı bir modda olabilir;
        # bu, matrisin her zaman 3 kanallı (R, G, B) olmasını garantiler.
        image = image.convert("RGB")
        matrix = np.array(image)

        return matrix