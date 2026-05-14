"""
tools/prio_inv_plot.py — Priority Inversion Karşılaştırma Grafiği
=================================================================
prio_inh_demo.c çıktısını görselleştirir.
"PRIO_INHERIT olmadan" vs "PRIO_INHERIT ile" IMU bekleme sürelerini karşılaştırır.

ÇALIŞTIĞI YER: PC (matplotlib GUI) veya Pi
"""

from typing import List


def load_measurement_log(filepath: str) -> dict:
    """
    prio_inh_demo çıktısını parse eder.

    Beklenen format (CSV veya JSON):
    run_id, use_inherit, high_prio_wait_ns

    Yapması gerekenler:
    - Dosyayı oku
    - without_inherit ve with_inherit listelerini ayır
    - Nanosaniyeden milisaniyeye çevir
    - Döndür: {"without": List[float], "with": List[float]}
    """
    pass


def plot_priority_inversion_comparison(
    without_inherit_ms: List[float],
    with_inherit_ms: List[float],
    output_file: str = "docs/figures/prio_inheritance_comparison.png"
):
    """
    İki konfigürasyonun bekleme süresi dağılımını yan yana box plot ile gösterir.

    ÇALIŞTIĞI YER: PC

    Yapması gerekenler:
    - matplotlib ile yan yana box plot çiz
    - Sol kutu: "PRIO_INHERIT Yok" (kırmızı)
    - Sağ kutu: "PRIO_INHERIT Var" (yeşil)
    - Bütçe çizgisi: 50ms'de yatay kırmızı noktalı çizgi
    - Başlık: "Priority Inheritance Etkisi: HIGH Prio Thread Bekleme Süresi"
    - Y ekseni: "Bekleme Süresi (ms)"
    - İyileşme yüzdesini (median farkı) grafik üzerine yaz
    - output_file'a kaydet
    """
    pass


if __name__ == "__main__":
    # Varsayılan: prio_inv_results.csv yükle ve grafiği çiz
    pass
