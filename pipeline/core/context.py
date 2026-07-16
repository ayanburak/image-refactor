"""
Aşamalar arası taşınan ortak veri paketi.

İki aşama birbirini doğrudan çağırmaz; ikisi de bu paketi okuyup üstüne
yazarak haberleşir. `source_path` ve `sidecar_path` baştan bellidir,
`original_hash` ve `pixel_matrix` ise Aşama 1 tamamlanınca doldurulur.
"""

class PipelineContext():
    """Aşamalar arasında taşınan, işlenen görsele ait veri paketi."""

    def __init__(self, source_path: str, sidecar_path: str, output_base_path: str):
        """
        Args:
            source_path: Orijinal görsel dosyasının yolu.
            sidecar_path: Bu görsele ait sidecar json dosyasının yolu.
            output_base_path: Çıktıların .npy ve.png yazılacağı, uzantısız temel dosya yolu.
        """
        self.output_base_path = output_base_path
        self.source_path = source_path
        self.sidecar_path = sidecar_path

        # Aşama 1 tamamlanana kadar boş; hashing.py ve loading.py
        # tarafından doldurulur.
        self.original_hash = None
        self.pixel_matrix = None

        # Aşama 2 tamamlanana kadar boş; decimator.py, writers.py ve
        # hashing.py'nin tekrar çağrılmasıyla doldurulur.
        self.npy_output_path = None
        self.png_output_path = None
        self.integrity_ok = None