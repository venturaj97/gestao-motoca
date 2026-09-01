import os
import subprocess
import time
import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.skipif(os.environ.get("SKIP_E2E") == "1", reason="Pular testes E2E se solicitado")
def test_playwright_e2e_flow():
    """Teste End-to-End com Playwright verificando o frontend e navegabilidade sem erros."""
    env = os.environ.copy()
    env["PATH"] = f"/home/jv/.nvm/versions/node/v22.19.0/bin:{env.get('PATH', '')}"

    # Iniciar backend FastAPI em background
    backend_proc = subprocess.Popen(
        [".venv/bin/uvicorn", "app.main:app", "--port", "8000", "--host", "127.0.0.1"],
        cwd="/home/jv/gm/gestao-motoca",
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Iniciar frontend preview em background
    frontend_proc = subprocess.Popen(
        ["/home/jv/.nvm/versions/node/v22.19.0/bin/npm", "run", "preview", "--", "--port", "5173", "--host", "127.0.0.1"],
        cwd="/home/jv/gm/gestao-motoca/frontend",
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        # Aguardar subida dos servidores
        time.sleep(3)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            # 1. Carregar a aplicação frontend
            response = page.goto("http://127.0.0.1:5173", timeout=15000)
            assert response is not None
            assert response.status == 200

            # 2. Verificar se o conteúdo principal renderizou
            content = page.content()
            assert "Gestão Motoca" in content or "login" in content.lower() or "motoca" in content.lower()

            # 3. Navegar para a página de login / cadastro se necessário
            # Verificar ausência de erros de sintaxe JS fatais
            critical_errors = [err for err in console_errors if "favicon" not in err.lower()]
            assert len(critical_errors) == 0, f"Erros críticos encontrados no console: {critical_errors}"

            browser.close()
    finally:
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
