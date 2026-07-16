"""
Görsel için hedef boyutu piksel cinsinden genişlik ve yükseklik hesaplayan
stratejiler.

Bu modül küçültmenin kendisini yapmaz, sadece hedef boyut ne
olmalı hesabını üretir. Gerçek piksel atlama işlemi ayrı bir
modülde yapılır. Hedef boyut iki farklı şekilde belirlenebilir:

- Orjinal boyutun bir oranı olarak, 
- Doğrudan sabit bir genişlik x yükseklik (WxH) olarak.
"""

from abc import abstractmethod, ABC
import re

# --- Soyut Sınıf ---

class TargetSize(ABC):
    """Hedef boyut hesaplama stratejileri için soyut sınıf.

    Bu sınıfın kendisi örneklenemez. Alt sınıflar , orijinal yükseklik 
    genişlik bilgisini alıp hedef yükseklik genişlik döndürür. 
    """

    @abstractmethod
    def get_size(self, original_height: int, original_width: int) -> tuple[int, int]:
        """Orijinal boyuta göre hedef yükseklik ve genişliği hesaplar.

        Args:
            original_height: Orijinal görselin yüksekliği (piksel).
            original_width: Orijinal görselin genişliği (piksel).

        Returns:
            [hedef_yükseklik, hedef_genişlik] şeklinde bir tuple, 
            piksel cinsinden.
        """
        pass

# --- Somut stratejiler ---

class RatioTargetSize(TargetSize):
    """`TargetSize` soyut sınıfını, orijinal boyutun bir oranını alarak dolduran sınıf.

    Genişlik ve yükseklik aynı oranla çarpılır, bu yüzden en-boy oranı
    (aspect ratio) korunur.
    """

    def __init__(self, ratio: float):
        """
        Args:
            ratio: Hedef boyutu belirleyen çarpan. 0.25 değeri, orijinalin
                %25'i demektir.
        """
        self.ratio = ratio

    def get_size(self, original_height: int, original_width: int) -> tuple[int, int]:
        # int() ile tam sayıya yuvarlanır çünkü piksel sayısı ondalıklı olamaz.
        height = int(original_height * self.ratio)
        widht = int(original_width * self.ratio)
        return (height, widht)


class FixedTargetSize(TargetSize):
    """`TargetSize` soyut sınıfını sabit bir hedef çözünürlükle dolduran sınıf.

    Orijinal boyut ne olursa olsun her zaman aynı, önceden belirlenmiş
    hedefi döndürür.
    """

    def __init__(self, resolution: tuple = None):
        """
        Args:
            resolution: Her zaman döndürülecek sabit (yükseklik, genişlik) çifti.
        """
        self.resolution = resolution

    def get_size(self, original_height: int, original_width: int) -> tuple[int, int]:
        # original_height/original_width kullanılmıyor; sadece TargetSize
        # soyut sınıfına uymak (her stratejinin aynı imzayla çağrılabilmesi)
        # için burada duruyorlar. Hedef, orijinalden tamamen bağımsız.
        return self.resolution
           

# --- Ayrıştırma / Factory ---

_RATIO_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*%\s*$")
_FIXED_RE = re.compile(r"^\s*(\d+)\s*[xX]\s*(\d+)\s*$")


def parse_target_size(parameter: str) -> TargetSize:
    """String bir parametreyi uygun TargetSize alt sınıfına çevirir.

    Args:
        parameter: "25%" gibi bir oran ya da "512x384" gibi
            genişlik x yükseklik formatında sabit bir boyut.

    Returns:
        Girdiye göre bir RatioTargetSize ya da FixedTargetSize örneği.

    Raises:
        ValueError: parameter ne oran ne de WxH formatına uyuyorsa.
    """
    if (m := _RATIO_RE.match(parameter)):
        # ratio 0-1 aralığında bekleniyor
        percent = float(m.group(1))
        return RatioTargetSize(ratio=percent / 100)

    if (m := _FIXED_RE.match(parameter)):
        # parameter "WxH" formatında geliyor,
        # ancak FixedTargetSize.resolution sırasını bekliyor 
        width = int(m.group(1))
        height = int(m.group(2))
        return FixedTargetSize(resolution=(height, width))

    raise ValueError(f"Geçersiz hedef boyut formatı: {parameter!r}")
