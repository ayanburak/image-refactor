"""
Aşamaları sırayla çalıştıran orkestratör.

Burada birden fazla strateji yok, tek bir mantık yeterli olduğu için
soyut bir sınıf yok. Yeni bir aşama eklemek için `Pipeline`'ın kodu
değişmez, sadece verilen listeye bir aşama daha eklenir.
"""

from .stages import PipelineStage
from .context import PipelineContext

class Pipeline():
    """Verilen aşama listesini, tek bir context üzerinde sırayla çalıştırır."""

    def __init__(self, stages: list[PipelineStage]):
        """
        Args:
            stages: Sırayla çalıştırılacak `PipelineStage` listesi.
        """
        self.stages = stages

    def run(self, context: PipelineContext) -> None:
        """Listedeki her aşama, aynı context üzerinde sırayla çalıştırılır.

        Args:
            context: İşlenen görsele ait veri paketi.
        """
        for stage in self.stages:
            stage.run(context)