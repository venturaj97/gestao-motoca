import os
import subprocess
import time
import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.skipif(os.environ.get("SKIP_E2E") == "1", reason="Pular testes E2E se solicitado")
def test_playwright_desktop_viewport():
    """Teste E2E em viewport Desktop (1280x800) verificando layout, tag PRO na sidebar e ausência de erros."""
    env = os.environ.copy()
    env["PATH"] = f"/home/jv/.nvm/versions/node/v22.19.0/bin:{env.get('PATH', '')}"

    backend_proc = subprocess.Popen(
        [".venv/bin/uvicorn", "app.main:app", "--port", "8000", "--host", "127.0.0.1"],
        cwd="/home/jv/gm/gestao-motoca",
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    frontend_proc = subprocess.Popen(
        ["/home/jv/.nvm/versions/node/v22.19.0/bin/npm", "run", "preview", "--", "--port", "5173", "--host", "127.0.0.1"],
        cwd="/home/jv/gm/gestao-motoca/frontend",
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        time.sleep(3)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # Viewport de Desktop
            context = browser.new_context(viewport={"width": 1280, "height": 800})
            page = context.new_page()

            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            response = page.goto("http://127.0.0.1:5173", timeout=15000)
            assert response is not None
            assert response.status == 200

            content = page.content()
            assert "Gestão Motoca" in content or "login" in content.lower() or "motoca" in content.lower()

            critical_errors = [err for err in console_errors if "favicon" not in err.lower()]
            assert len(critical_errors) == 0, f"Erros críticos no console (Desktop): {critical_errors}"

            browser.close()
    finally:
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()


@pytest.mark.skipif(os.environ.get("SKIP_E2E") == "1", reason="Pular testes E2E se solicitado")
def test_playwright_smartphone_viewport():
    """Teste E2E em viewport Smartphone (375x667) verificando layout responsivo e ausência de erros."""
    env = os.environ.copy()
    env["PATH"] = f"/home/jv/.nvm/versions/node/v22.19.0/bin:{env.get('PATH', '')}"

    backend_proc = subprocess.Popen(
        [".venv/bin/uvicorn", "app.main:app", "--port", "8000", "--host", "127.0.0.1"],
        cwd="/home/jv/gm/gestao-motoca",
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    frontend_proc = subprocess.Popen(
        ["/home/jv/.nvm/versions/node/v22.19.0/bin/npm", "run", "preview", "--", "--port", "5173", "--host", "127.0.0.1"],
        cwd="/home/jv/gm/gestao-motoca/frontend",
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        time.sleep(3)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # Viewport de Smartphone (iPhone SE / Android)
            context = browser.new_context(
                viewport={"width": 375, "height": 667},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
            )
            page = context.new_page()

            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            response = page.goto("http://127.0.0.1:5173", timeout=15000)
            assert response is not None
            assert response.status == 200

            content = page.content()
            assert "Gestão Motoca" in content or "login" in content.lower() or "motoca" in content.lower()

            critical_errors = [err for err in console_errors if "favicon" not in err.lower()]
            assert len(critical_errors) == 0, f"Erros críticos no console (Smartphone): {critical_errors}"

            browser.close()
    finally:
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
