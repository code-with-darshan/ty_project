from src.safety.incident_response import get_incident_guide


def test_abstract_legal_question_does_not_show_personal_incident_guidance():
    assert get_incident_guide("What is the punishment for cyber fraud?") is None


def test_personal_cyber_fraud_question_shows_cyber_reporting_steps():
    guide = get_incident_guide("My UPI account was hacked and money was sent.")

    assert guide is not None
    assert "cyber" in guide.title.lower()
    assert any("1930" in step for step in guide.steps)


def test_personal_threat_question_shows_emergency_guidance():
    guide = get_incident_guide("Someone threatened me and I am unsafe right now.")

    assert guide is not None
    assert guide.urgency_notice is not None
    assert any("112" in step for step in guide.steps)
