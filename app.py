from flask import Flask, render_template, request, redirect, url_for
import csv
import os
from datetime import datetime

app = Flask(__name__)

# Dados fixos
IMPRESSORAS = [
    {"nome": "IMPADM01", "modelo": "Lexmark MX711"},
    {"nome": "IMP_HALL01", "modelo": "Brother MFC-L6902"},
    {"nome": "IMP_HALL02", "modelo": "Brother MFC-L6902"},
    {"nome": "IMP_CS510", "modelo": "Lexmark CS510de"},
    {"nome": "HP Color", "modelo": "HP M750"},
]

INSUMOS = ["Toner", "Fotocondutor", "Fusor"]
USUARIOS = ["Kelcey", "Bruno", "Andrei", "Paulo"]

CSV_PATH = 'data/registros.csv'
CSV_HEADER = [
    "id", "impressora", "modelo", "insumo", "data", "hora", "usuario",
    "contador_atual", "contador_anterior", "paginas_pelo_insumo"
]

ESTOQUE_CSV_PATH = 'data/estoque.csv'
ESTOQUE_HEADER = ["modelo", "insumo", "quantidade"]

# Limites para alerta de estoque baixo
LIMITE = {'Toner': 3, 'Fotocondutor': 2, 'Fusor': 1}

REGS_POR_PAGINA = 5  # Quantos registros na tabela de cada vez

def criar_csv_se_necessario():
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.isfile(CSV_PATH):
        with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)

def criar_estoque_se_necessario():
    if not os.path.isfile(ESTOQUE_CSV_PATH):
        with open(ESTOQUE_CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(ESTOQUE_HEADER)
            modelos = set(i['modelo'] for i in IMPRESSORAS)
            for modelo in modelos:
                for insumo in INSUMOS:
                    writer.writerow([modelo, insumo, '0'])

criar_csv_se_necessario()
criar_estoque_se_necessario()

@app.template_filter('data_br')
def data_br(data_iso):
    # Converte 'YYYY-MM-DD' para 'DD-MM-AAAA'
    try:
        dt = datetime.strptime(data_iso, "%Y-%m-%d")
        return dt.strftime("%d-%m-%Y")
    except Exception:
        return data_iso

@app.route('/', methods=['GET', 'POST'])
def index():
    ordem = request.args.get('ordem', 'data')
    direcao = request.args.get('direcao', 'desc')  # padrão: mais recentes
    # Paginação: página atual começa em 0
    try:
        pagina = int(request.args.get('pagina', 0))
        if pagina < 0:
            pagina = 0
    except Exception:
        pagina = 0

    # Lê registros do histórico
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        registros = list(csv.DictReader(f))

    # Lê estoque para alerta dinâmico
    with open(ESTOQUE_CSV_PATH, newline='', encoding='utf-8') as f:
        estoque_regs = list(csv.DictReader(f))
    estoque_dict = {
        f"{reg['modelo']}|{reg['insumo']}": int(reg['quantidade'])
        for reg in estoque_regs
    }

    if request.method == 'POST':
        impressora = request.form['impressora']
        usuario = request.form['usuario']
        insumo = request.form['insumo']
        contador_atual = int(request.form['contador_atual'])
        data = request.form['data']
        hora = request.form['hora']
        modelo = next((i['modelo'] for i in IMPRESSORAS if i['nome'] == impressora), '')

        contador_anterior = 0
        for rec in registros:
            if rec['impressora'] == impressora and rec['insumo'] == insumo:
                contador_anterior = int(rec['contador_atual'])
                break

        paginas_pelo_insumo = contador_atual - contador_anterior
        novo_id = str(1 + max([int(r['id']) for r in registros] or [0]))

        novo_registro = [
            novo_id,
            impressora,
            modelo,
            insumo,
            data,
            hora,
            usuario,
            str(contador_atual),
            str(contador_anterior),
            str(paginas_pelo_insumo)
        ]

        with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(novo_registro)

        # Decremento automático do estoque
        for reg in estoque_regs:
            if reg['modelo'] == modelo and reg['insumo'] == insumo:
                reg['quantidade'] = str(max(0, int(reg['quantidade']) - 1))
        with open(ESTOQUE_CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=ESTOQUE_HEADER)
            writer.writeheader()
            writer.writerows(estoque_regs)

        return redirect(url_for('index', ordem=ordem, direcao=direcao, pagina=pagina))

    def ordenar_registros(lista, criterio, direcao):
        reverse = (direcao == 'desc')
        if criterio == 'impressora':
            return sorted(lista, key=lambda x: x['impressora'], reverse=reverse)
        elif criterio == 'data':
            return sorted(lista, key=lambda x: (x['data'], x['hora']), reverse=reverse)
        elif criterio == 'insumo':
            return sorted(lista, key=lambda x: x['insumo'], reverse=reverse)
        else:
            return lista

    registros_ord = ordenar_registros(registros, ordem, direcao)

    # Paginação
    reg_total = len(registros_ord)
    inicio = pagina * REGS_POR_PAGINA
    fim = inicio + REGS_POR_PAGINA
    registros_pagina = registros_ord[inicio:fim]

    return render_template(
        'index.html',
        impressoras=IMPRESSORAS,
        usuarios=USUARIOS,
        insumos=INSUMOS,
        registros=registros_pagina,
        ordem=ordem,
        direcao=direcao,
        estoque=estoque_dict,
        limite=LIMITE,
        pagina=pagina,
        reg_total=reg_total,
        reg_por_pagina=REGS_POR_PAGINA
    )

@app.route('/estoque', methods=['GET', 'POST'])
def estoque():
    modelos = sorted(set(i['modelo'] for i in IMPRESSORAS))
    if request.method == 'POST':
        modelo = request.form['modelo']
        insumo = request.form['insumo']
        acao = request.form['acao']  # 'entrada' ou 'saida'
        qtd = int(request.form['quantidade'])
        estoque_rows = []
        with open(ESTOQUE_CSV_PATH, newline='', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
            for row in reader:
                if row['modelo'] == modelo and row['insumo'] == insumo:
                    if acao == 'entrada':
                        row['quantidade'] = str(int(row['quantidade']) + qtd)
                    elif acao == 'saida':
                        row['quantidade'] = str(max(0, int(row['quantidade']) - qtd))
                estoque_rows.append(row)
        with open(ESTOQUE_CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=ESTOQUE_HEADER)
            writer.writeheader()
            writer.writerows(estoque_rows)
        return redirect(url_for('estoque'))

    with open(ESTOQUE_CSV_PATH, newline='', encoding='utf-8') as f:
        estoque_regs = list(csv.DictReader(f))
    estoque_dict = {
        f"{reg['modelo']}|{reg['insumo']}": int(reg['quantidade'])
        for reg in estoque_regs
    }

    return render_template(
        'estoque.html',
        modelos=modelos,
        insumos=INSUMOS,
        estoque=estoque_dict,
        limite=LIMITE
    )

if __name__ == '__main__':
    app.run(debug=True)