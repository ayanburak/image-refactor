"""
Piksel matrisini hedef boyuta küçülten decimation (seyreltme) stratejileri.

Küçültme, komşu piksellerden ortalama alarak (interpolasyonla) değil,
belirli aralıklarla gerçek orijinal pikselleri örnekleyerek yapılır — bu
yüzden çıktıdaki her piksel, kaynak görselde birebir var olan bir pikseldir.
Hedef boyutun kendisi bu modülün işi değil, `sizing.py`'den gelir.
"""

from abc import abstractmethod, ABC
import numpy as np

# --- Soyut Sınıf ---

class Decimator(ABC):
    """Decimation stratejileri için soyut sınıf."""

    @abstractmethod
    def decimate(self, original_matrix: np.array, target_size: tuple[int, int]) -> np.array:
        """Piksel matrisini hedef boyuta küçültür.

        Args:
            original_matrix: Orijinal görselin piksel matrisi,
                (yükseklik, genişlik, kanal) şeklinde.
            target_size: (hedef_yükseklik, hedef_genişlik) tuple'ı.

        Returns:
            Küçültülmüş piksel matrisi.
        """
        pass

# --- Somut stratejiler ---

# Orijinal boyutu hedef boyuta bölünce, Örn: 100 // 25 = 4
# "kaç pikselde bir seçim yapılacağı" çıkar. Yani her 4 pikselden 1 tanesi
# alınır, diğer 3'üne hiç bakılmaz.
#
# matrix[::row_step, ::col_step] bu seçimi yapar: satırlarda row_step,
# sütunlarda col_step adımıyla ilerler. RGB'ye hiç dokunulmadığı için kalır.
#
# Yani hiçbir piksel yeniden hesaplanmıyor, hepsi orijinalden direkt
# kopyalanıyor. Tek sorun: tam sayı bölme yuvarlama yaptığı için, çıktı
# boyutu bazen istenen hedeften birkaç piksel farklı çıkabilir.
class NearestPixelDecimator(Decimator):
    """`Decimator` soyut sınıfını, en yakın pikseli seçerek dolduran sınıf.

    Ortalama almadan, sabit bir adımla (step) satır ve sütunları atlayarak
    örnekleme yapar; bu yüzden hedef boyut tam olarak değil, yaklaşık olarak
    tutturulur (tam sayı bölmedeki yuvarlama nedeniyle).
    """

    def decimate(self, original_matrix: np.array, target_size: tuple[int, int]) -> np.array:

        original_height =  original_matrix.shape[0]   # Satır Sayısı / Orijinal Yükseklik
        original_width = original_matrix.shape[1]     # Kolon Sayısı / Orijinal Genişlik

        target_height = target_size[0]                # Gelen tuple'ın birinci elemanı / Hedef Yükseklik
        target_width = target_size[1]                 # Gelen tuple'ın ikinci elemanı / Hedef Genişlik

        row_step = original_height // target_height
        col_step = original_width // target_width

        # [::row_step, ::col_step] satırları ve sütunları bu adımlarla
        # atlayarak örnekler; renk kanalı ekseni hiç dilimlenmediği için
        # tamamen korunur.
        return original_matrix[::row_step, ::col_step]

