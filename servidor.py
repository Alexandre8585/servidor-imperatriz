from flask import Flask, send_from_directory, abort, render_template_string, request
import subprocess
import re
import os
from flask import render_template, redirect, url_for


app = Flask(__name__)
BASE_DIR = r"D:\Gravações"
BASE_URL = "https://imperatriz.comuniqueclipping.app"  # domínio fixo


@app.route('/raw/<path:subpath>')
def servir_arquivo(subpath):
    caminho_absoluto = os.path.join(BASE_DIR, subpath)
    if not os.path.isfile(caminho_absoluto):
        return abort(404, description="Arquivo não encontrado")

    pasta, nome_arquivo = os.path.split(caminho_absoluto)
    return send_from_directory(pasta, nome_arquivo)


@app.route('/view/<path:subpath>')
def visualizar(subpath):
    caminho_absoluto = os.path.join(BASE_DIR, subpath)
    if not os.path.isfile(caminho_absoluto):
        return abort(404, description="Arquivo não encontrado")

    pasta, nome_arquivo = os.path.split(caminho_absoluto)
    arquivos = sorted(f for f in os.listdir(
        pasta) if f.lower().endswith('.mp4'))

    idx = arquivos.index(nome_arquivo)
    prev_file = next_file = None

    if idx > 0:
        prev_file = os.path.relpath(os.path.join(
            pasta, arquivos[idx - 1]), BASE_DIR).replace("\\", "/")
    if idx < len(arquivos) - 1:
        next_file = os.path.relpath(os.path.join(
            pasta, arquivos[idx + 1]), BASE_DIR).replace("\\", "/")

    # Tenta ler o arquivo .txt com mesmo nome
    nome_txt = os.path.splitext(nome_arquivo)[0] + ".txt"
    caminho_txt = os.path.join(pasta, nome_txt)

    conteudo_txt = ""
    palavra_destaque = request.args.get("palavra", "").lower()
    tempo_inicio = request.args.get("tempo", "0")

    if os.path.exists(caminho_txt):
        with open(caminho_txt, "r", encoding="utf-8", errors="ignore") as f:
            linhas = f.readlines()
            palavras = []
            for linha in linhas:
                linha = linha.strip()
                if "<UNK>" in linha:
                    continue
                if "]" in linha:
                    partes = linha.split("] ")
                    if len(partes) == 2:
                        palavra = partes[1].strip()
                        if palavra_destaque and palavra_destaque in palavra.lower():
                            palavra = re.sub(
                                re.escape(palavra_destaque),
                                f'<span style="color:red">{palavra_destaque}</span>',
                                palavra,
                                flags=re.IGNORECASE
                            )
                        palavras.append(palavra)

            texto = " ".join(palavras)
            conteudo_txt = texto[0].upper() + texto[1:] if texto else ""

    print("🔎 HTML FINAL:", conteudo_txt)

    return render_template("visualizacao.html",
                           filename=os.path.splitext(nome_arquivo)[0],
                           subpath=subpath,
                           prev_file=prev_file,
                           next_file=next_file,
                           conteudo_txt=conteudo_txt,
                           tempo_inicio=tempo_inicio)


@app.route("/meta/<path:subpath>")
def meta_preview(subpath):
    url_completa = f"{BASE_URL}/view/{subpath}"
    image_url = f"{BASE_URL}/static/logo-preview.jpg"
    filename = subpath.split("/")[-1]
    return render_template("meta_preview.html",
                           url=url_completa,
                           image_url=image_url,
                           filename=filename)


if __name__ == '__main__':
    print("[INFO] Iniciando servidor Flask...")
    app.run(host='0.0.0.0', port=8000)
