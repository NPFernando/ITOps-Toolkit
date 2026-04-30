from utils.scoring import calculate_risk_score, status_from_score


def test_status_from_score_thresholds():
    assert status_from_score(100) == "Healthy"
    assert status_from_score(80) == "Healthy"
    assert status_from_score(79) == "Warning"
    assert status_from_score(50) == "Warning"
    assert status_from_score(49) == "Critical"


def test_calculate_risk_score_healthy_path():
    result = calculate_risk_score(
        http_ok=True,
        ssl_ok=True,
        ssl_days_remaining=90,
        mx_found=True,
        spf_found=True,
        dmarc_found=True,
    )

    assert result == {"score": 100, "status": "Healthy", "deductions": [], "recommendations": []}


def test_calculate_risk_score_warning_recommendations():
    result = calculate_risk_score(
        http_ok=True,
        ssl_ok=True,
        ssl_days_remaining=10,
        mx_found=True,
        spf_found=False,
        dmarc_found=True,
    )

    assert result["score"] == 70
    assert result["status"] == "Warning"
    assert result["recommendations"] == [
        "SSL certificate expires in less than 30 days.",
        "Missing SPF record.",
    ]


def test_calculate_risk_score_critical_and_nonnegative():
    result = calculate_risk_score(
        http_ok=False,
        ssl_ok=False,
        ssl_days_remaining=None,
        mx_found=False,
        spf_found=False,
        dmarc_found=False,
    )

    assert result["score"] == 5
    assert result["score"] >= 0
    assert result["status"] == "Critical"
    assert len(result["deductions"]) == 5
