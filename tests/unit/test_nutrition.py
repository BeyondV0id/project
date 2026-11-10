from src.core.nutrition import scale_nutrients, sum_nutrients, kj_to_kcal


def test_scale_null_stays_null():
    out = scale_nutrients({"kcal": 130.0, "protein_g": None}, 165.0)
    assert out["kcal"] == 130.0 * 1.65
    assert out["protein_g"] is None


def test_sum_null_not_zero():
    parts = [{"kcal": 10.0, "protein_g": None}, {"kcal": None, "protein_g": 5.0}]
    t = sum_nutrients(parts)
    assert t["kcal"] == 10.0
    assert t["protein_g"] == 5.0


def test_kj_conversion():
    assert abs(kj_to_kcal(418.4) - 100.0) < 1e-9
    assert kj_to_kcal(None) is None
