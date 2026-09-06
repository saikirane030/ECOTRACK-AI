"""
Automated tests for EcoTrack AI.
Run with:  python _check.py
"""
import sys
import re
import pathlib

PASS = []
FAIL = []

def ok(msg):
    PASS.append(msg)
    print(f"  PASS  {msg}".encode("ascii", "replace").decode("ascii"))

def fail(msg):
    FAIL.append(msg)
    print(f"  FAIL  {msg}".encode("ascii", "replace").decode("ascii"))

# ============================================================
# 1. FILE PRESENCE
# ============================================================
print("\n=== 1. File Presence ===")
required_files = [
    "app.py",
    "pages/waste_classifier.py",
    "pages/csv_analytics.py",
    "pages/ai_assistant.py",
    "pages/impact_calculator.py",
    "pages/responsible_ai.py",
    "utils/watsonx_client.py",
    "utils/waste_categories.py",
    "utils/impact_formulas.py",
    "data/sample_campus_waste.csv",
    ".env.example",
    "requirements.txt",
    "README.md",
]
for f in required_files:
    if pathlib.Path(f).exists():
        ok(f"exists: {f}")
    else:
        fail(f"MISSING: {f}")

# ============================================================
# 2. NO HARDCODED SECRETS
# ============================================================
print("\n=== 2. No Hardcoded Secrets ===")
# Pattern: variable assignment with a long alphanumeric literal (likely a key)
secret_pattern = re.compile(
    r'(WATSONX_API_KEY|WATSONX_PROJECT_ID)\s*=\s*["\'][a-zA-Z0-9\-_]{15,}["\']'
)
py_files = [f for f in pathlib.Path(".").rglob("*.py")
            if "__pycache__" not in str(f) and "_check.py" not in str(f)]
found_secrets = []
for f in py_files:
    src = f.read_text(encoding="utf-8")
    for m in secret_pattern.finditer(src):
        found_secrets.append(f"{f}:{m.group()}")

if found_secrets:
    for s in found_secrets:
        fail(f"Hardcoded secret: {s}")
else:
    ok("No hardcoded API keys or project IDs in any .py file")

# ============================================================
# 3. ENV FILE NOT PRESENT (should only have .env.example)
# ============================================================
print("\n=== 3. .env File Check ===")
if pathlib.Path(".env").exists():
    fail(".env file exists in project root — must not be committed")
else:
    ok(".env file not present (correct — only .env.example should exist)")

if pathlib.Path(".env.example").exists():
    ok(".env.example template present")
else:
    fail(".env.example missing")

# ============================================================
# 4. IMPORTS – all page and util modules load cleanly
# ============================================================
print("\n=== 4. Module Imports ===")
import importlib, traceback

# Add project root to path
sys.path.insert(0, str(pathlib.Path(".").resolve()))

modules = [
    "utils.waste_categories",
    "utils.impact_formulas",
    "utils.watsonx_client",
    "pages.waste_classifier",
    "pages.csv_analytics",
    "pages.ai_assistant",
    "pages.impact_calculator",
    "pages.responsible_ai",
]
for mod in modules:
    try:
        importlib.import_module(mod)
        ok(f"imports OK: {mod}")
    except Exception as e:
        fail(f"import failed: {mod} — {e}")

# ============================================================
# 5. CROSS-FILE SYMBOL CONNECTIONS
# ============================================================
print("\n=== 5. Cross-file Symbol Connections ===")
try:
    from utils.waste_categories import (
        WASTE_CATEGORIES, DEMO_EXAMPLES,
        VISION_CLASSIFICATION_PROMPT, ASSISTANT_SYSTEM_PROMPT
    )
    assert isinstance(WASTE_CATEGORIES, dict) and len(WASTE_CATEGORIES) == 5
    assert isinstance(DEMO_EXAMPLES, list) and len(DEMO_EXAMPLES) == 5
    assert isinstance(VISION_CLASSIFICATION_PROMPT, str) and len(VISION_CLASSIFICATION_PROMPT) > 50
    assert isinstance(ASSISTANT_SYSTEM_PROMPT, str) and len(ASSISTANT_SYSTEM_PROMPT) > 50
    ok("waste_categories exports: WASTE_CATEGORIES(5), DEMO_EXAMPLES(5), both prompts")
except Exception as e:
    fail(f"waste_categories symbol check: {e}")

try:
    from utils.impact_formulas import FACTORS, KG_CO2_PER_TREE_PER_YEAR, calculate_impact
    assert set(FACTORS.keys()) == {"plastic", "paper", "food", "e-waste", "general"}
    assert KG_CO2_PER_TREE_PER_YEAR == 21.0
    ok("impact_formulas exports: FACTORS(5 types), KG_CO2_PER_TREE_PER_YEAR, calculate_impact")
except Exception as e:
    fail(f"impact_formulas symbol check: {e}")

try:
    from utils.watsonx_client import (
        generate_text, classify_image,
        is_text_ai_available, is_vision_ai_available
    )
    ok("watsonx_client exports: generate_text, classify_image, is_text_ai_available, is_vision_ai_available")
except Exception as e:
    fail(f"watsonx_client symbol check: {e}")

try:
    from pages.waste_classifier import render, _parse_vision_response, _show_category_result
    ok("waste_classifier exports: render, _parse_vision_response, _show_category_result")
except Exception as e:
    fail(f"waste_classifier symbol check: {e}")

# ============================================================
# 6. SAMPLE CSV VALIDATION
# ============================================================
print("\n=== 6. Sample CSV ===")
try:
    import pandas as pd
    df = pd.read_csv("data/sample_campus_waste.csv")
    required_cols = {"date", "location", "waste_type", "weight_kg", "disposed_correctly"}
    assert required_cols == set(df.columns), f"Columns: {set(df.columns)}"
    assert len(df) == 100, f"Expected 100 rows, got {len(df)}"
    assert set(df["waste_type"].unique()) == {"plastic", "paper", "food", "e-waste", "general"}
    ok(f"sample CSV: 100 rows, 5 columns, all 5 waste types present")
except Exception as e:
    fail(f"sample CSV: {e}")

# ============================================================
# 7. IMPACT CALCULATOR LOGIC — NORMAL AND EDGE CASES
# ============================================================
print("\n=== 7. Impact Calculator Logic ===")
try:
    from utils.impact_formulas import calculate_impact

    # Normal: plastic, 10 kg, 20% reduction
    r = calculate_impact("plastic", 10.0, 20.0)
    assert r["kg_avoided"] == 2.0, f"Expected 2.0, got {r['kg_avoided']}"
    assert r["co2_saved_kg"] == 3.0, f"Expected 3.0, got {r['co2_saved_kg']}"
    assert r["has_estimate"] is True
    ok("plastic 10kg 20% -> kg_avoided=2.0, co2_saved=3.0")

    # Normal: paper, 8 kg, 25% -> water saved
    r = calculate_impact("paper", 8.0, 25.0)
    assert r["kg_avoided"] == 2.0
    assert r["water_saved_litres"] == round(2.0 * 13.0, 1)
    ok("paper 8kg 25% -> water_saved=26.0 L")

    # Normal: food, 5 kg, 100% reduction
    r = calculate_impact("food", 5.0, 100.0)
    assert r["kg_avoided"] == 5.0
    assert r["co2_saved_kg"] == round(5.0 * 0.5, 2)
    ok("food 5kg 100% -> kg_avoided=5.0, co2_saved=2.5")

    # Edge: 0 kg input
    r = calculate_impact("plastic", 0.0, 50.0)
    assert r["kg_avoided"] == 0.0
    assert r["co2_saved_kg"] == 0.0
    ok("edge: 0 kg -> all zeros, no crash")

    # Edge: 0% reduction
    r = calculate_impact("paper", 100.0, 0.0)
    assert r["kg_avoided"] == 0.0
    ok("edge: 0% reduction -> kg_avoided=0.0")

    # Edge: 100% reduction
    r = calculate_impact("plastic", 100.0, 100.0)
    assert r["kg_avoided"] == 100.0
    ok("edge: 100% reduction -> kg_avoided=100.0")

    # Edge: reduction > 100 (clamped)
    r = calculate_impact("plastic", 10.0, 150.0)
    assert r["kg_avoided"] == 10.0, f"Expected 10.0 (clamped), got {r['kg_avoided']}"
    ok("edge: reduction=150% clamped to 100% -> kg_avoided=10.0")

    # Edge: negative kg (clamped)
    r = calculate_impact("plastic", -5.0, 50.0)
    assert r["kg_avoided"] == 0.0
    ok("edge: negative kg clamped to 0 -> kg_avoided=0.0")

    # e-waste: no CO2 estimate
    r = calculate_impact("e-waste", 10.0, 50.0)
    assert r["has_estimate"] is False
    assert r["co2_saved_kg"] == 0.0
    ok("e-waste: has_estimate=False, co2=0.0")

    # general: no estimate
    r = calculate_impact("general", 10.0, 50.0)
    assert r["has_estimate"] is False
    ok("general: has_estimate=False")

    # Unknown waste type falls back to general
    r = calculate_impact("unknown_type", 10.0, 50.0)
    assert r["has_estimate"] is False
    ok("unknown waste type falls back to general (has_estimate=False)")

    # Disclaimer is always present
    r = calculate_impact("plastic", 1.0, 10.0)
    assert "estimate" in r["disclaimer"].lower()
    ok("disclaimer always present in result")

except Exception as e:
    fail(f"impact calculator logic: {e}")
    import traceback; traceback.print_exc()

# ============================================================
# 8. DEMO MODE LOGIC (no credentials)
# ============================================================
print("\n=== 8. Demo Mode (no credentials) ===")
try:
    from utils.watsonx_client import is_text_ai_available, is_vision_ai_available
    # In a clean environment with no .env, both should be False
    assert is_text_ai_available() is False, "Expected False without credentials"
    assert is_vision_ai_available() is False, "Expected False without credentials"
    ok("is_text_ai_available() -> False (no credentials)")
    ok("is_vision_ai_available() -> False (no credentials)")
except Exception as e:
    fail(f"Demo mode credential check: {e}")

try:
    # Confirm generate_text returns an error (not a fake response) without credentials
    from utils.watsonx_client import generate_text
    result, error = generate_text("test prompt")
    assert result is None, f"Expected None result, got: {result}"
    assert error is not None, "Expected error message"
    assert "not configured" in error.lower() or "api" in error.lower()
    ok(f"generate_text without credentials -> result=None, error='{error[:60]}...'")
except Exception as e:
    fail(f"generate_text no-credentials test: {e}")

try:
    from utils.watsonx_client import classify_image
    result, error = classify_image(b"fake", "image/jpeg", "test prompt")
    assert result is None
    assert error is not None
    assert "not configured" in error.lower() or "vision" in error.lower()
    ok(f"classify_image without credentials -> result=None, error='{error[:60]}'")
except Exception as e:
    fail(f"classify_image no-credentials test: {e}")

# ============================================================
# 9. VISION RESPONSE PARSER
# ============================================================
print("\n=== 9. Vision Response Parser ===")
try:
    from pages.waste_classifier import _parse_vision_response
    from utils.waste_categories import WASTE_CATEGORIES

    # Well-formed response
    raw = "CATEGORY: plastic\nCONFIDENCE: high\nREASONING: It is a bottle.\nDISPOSAL_TIP: Recycle it."
    p = _parse_vision_response(raw)
    assert p["category"] == "plastic"
    assert p["confidence"] == "high"
    assert p["reasoning"] == "It is a bottle."
    assert p["disposal_tip"] == "Recycle it."
    assert p["parse_success"] is True
    ok("well-formed response parses correctly")

    # Unknown category -> falls back to 'general'
    raw2 = "CATEGORY: batteries\nCONFIDENCE: medium\nREASONING: Unclear.\nDISPOSAL_TIP: Check local rules."
    p2 = _parse_vision_response(raw2)
    assert p2["category"] == "general", f"Got: {p2['category']}"
    ok("unknown category -> fallback to 'general'")

    # Completely garbled response -> safe defaults
    p3 = _parse_vision_response("this is not the expected format at all")
    assert p3["category"] == "general"
    assert p3["confidence"] == "low"
    assert p3["parse_success"] is False
    ok("garbled response -> safe defaults (category=general, confidence=low, parse_success=False)")

    # All categories accepted
    for cat in WASTE_CATEGORIES:
        raw_cat = f"CATEGORY: {cat}\nCONFIDENCE: high\nREASONING: test\nDISPOSAL_TIP: test"
        p = _parse_vision_response(raw_cat)
        assert p["category"] == cat, f"Expected {cat}, got {p['category']}"
    ok("all 5 known categories parsed correctly")

except Exception as e:
    fail(f"vision response parser: {e}")
    import traceback; traceback.print_exc()

# ============================================================
# 10. CSV ANALYTICS LOAD + VALIDATE
# ============================================================
print("\n=== 10. CSV Analytics Load & Validate ===")
try:
    from pages.csv_analytics import _load_and_validate, _build_summary_prompt
    import pandas as pd

    # Valid sample CSV
    df, warning = _load_and_validate("data/sample_campus_waste.csv")
    assert df is not None, "DataFrame should not be None for valid CSV"
    assert warning is None, f"Unexpected warning: {warning}"
    assert len(df) == 100
    assert df["disposed_correctly"].dtype == bool
    ok("valid CSV loads cleanly: 100 rows, disposed_correctly is bool")

    # KPI computations don't crash
    total_kg = df["weight_kg"].sum()
    assert total_kg > 0
    top_type = df.groupby("waste_type")["weight_kg"].sum().idxmax()
    assert top_type in {"plastic", "paper", "food", "e-waste", "general"}
    ok(f"KPI: total_kg={total_kg:.1f}, top_type={top_type}")

    # Summary prompt builds without error
    prompt = _build_summary_prompt(df)
    assert len(prompt) > 50
    assert "waste" in prompt.lower()
    ok("summary prompt builds correctly")

    # Missing column triggers error
    bad_df_file = "data/sample_campus_waste.csv"
    import io
    bad_csv = "date,location,weight_kg\n2024-01-01,Cafeteria,5.0\n"
    df_bad, err = _load_and_validate(io.StringIO(bad_csv))
    assert df_bad is None, "Should fail on missing columns"
    assert "missing" in err.lower()
    ok("missing columns -> returns (None, error_message)")

    # Invalid date rows handled gracefully
    partial_bad = "date,location,waste_type,weight_kg,disposed_correctly\nNOTADATE,Cafeteria,food,1.0,True\n2024-01-01,Lib,paper,2.0,False\n"
    df_partial, warn2 = _load_and_validate(io.StringIO(partial_bad))
    assert df_partial is not None
    assert len(df_partial) == 1, f"Expected 1 valid row, got {len(df_partial)}"
    assert warn2 is not None and "invalid" in warn2.lower()
    ok("invalid dates skipped with warning, valid rows kept")

except Exception as e:
    fail(f"CSV analytics: {e}")
    import traceback; traceback.print_exc()

# ============================================================
# 11. REQUIREMENTS FILE CHECK
# ============================================================
print("\n=== 11. Requirements File ===")
try:
    req_text = pathlib.Path("requirements.txt").read_text()
    required_pkgs = ["streamlit", "pandas", "plotly", "Pillow", "ibm-watsonx-ai", "python-dotenv", "requests"]
    for pkg in required_pkgs:
        if pkg.lower() in req_text.lower():
            ok(f"requirements.txt contains: {pkg}")
        else:
            fail(f"requirements.txt MISSING: {pkg}")
except Exception as e:
    fail(f"requirements.txt check: {e}")

# ============================================================
# 12. README ACCURACY CHECKS
# ============================================================
print("\n=== 12. README Accuracy ===")
try:
    readme = pathlib.Path("README.md").read_text(encoding="utf-8")

    checks = [
        ("streamlit run app.py", "launch command"),
        ("granite-3-3-8b-instruct", "correct text model name"),
        ("granite-vision-3-2-2b", "correct vision model name"),
        ("WATSONX_API_KEY", "env var name"),
        ("WATSONX_PROJECT_ID", "env var name"),
        ("WATSONX_REGION", "env var name"),
        ("WATSONX_VISION_DEPLOYMENT_ID", "optional vision env var"),
        ("300,000 tokens", "correct Lite plan token limit"),
        ("deploy-on-demand", "vision model deployment type"),
        ("sample_campus_waste.csv", "sample data reference"),
        ("SDG 12", "SDG alignment"),
        ("1M1B", "internship name"),
        ("WRAP UK", "impact factor source"),
        ("US EPA", "impact factor source"),
        ("IPCC", "impact factor source"),
        (".gitignore", "secret protection guidance"),
    ]
    for term, desc in checks:
        if term in readme:
            ok(f"README contains '{term}' ({desc})")
        else:
            fail(f"README missing '{term}' ({desc})")

except Exception as e:
    fail(f"README check: {e}")

# ============================================================
# 13. APP.PY COMMENT SAYS "FOUR TABS" BUT ROUTES FIVE
# ============================================================
print("\n=== 13. app.py Comment vs. Reality ===")
try:
    app_src = pathlib.Path("app.py").read_text(encoding="utf-8")
    # Check the comment says "four tabs" but the code has five
    if "Creates four tabs" in app_src and "tab1, tab2, tab3, tab4, tab5" in app_src:
        fail("app.py comment says 'four tabs' but code creates five — comment is inaccurate")
    else:
        ok("app.py tab count comment matches actual tab count")
except Exception as e:
    fail(f"app.py comment check: {e}")

# ============================================================
# 14. DEMO EXAMPLES COVER ALL 5 CATEGORIES
# ============================================================
print("\n=== 14. Demo Examples Coverage ===")
try:
    from utils.waste_categories import DEMO_EXAMPLES, WASTE_CATEGORIES
    demo_cats = {ex["category"] for ex in DEMO_EXAMPLES}
    all_cats = set(WASTE_CATEGORIES.keys())
    if demo_cats == all_cats:
        ok(f"Demo examples cover all 5 categories: {sorted(demo_cats)}")
    else:
        missing = all_cats - demo_cats
        fail(f"Demo examples missing categories: {missing}")
except Exception as e:
    fail(f"Demo examples coverage: {e}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*60)
print(f"PASSED: {len(PASS)}")
print(f"FAILED: {len(FAIL)}")
if FAIL:
    print("\nFailed tests:")
    for f in FAIL:
        print(("  FAIL: " + f).encode("ascii", "replace").decode("ascii"))
    sys.exit(1)
else:
    print("\nAll checks passed.")
    sys.exit(0)
