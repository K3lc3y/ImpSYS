# Sistema de Controle de Insumos para Impressoras

Este projeto é um sistema web para registrar, visualizar e administrar as trocas de insumos das impressoras (toner, fotocondutor e fusor) dividido por modelo, com controle de estoque dinâmico.

## Funcionalidades

- Registro de troca de insumos em impressoras, com histórico e cálculo automático de páginas por insumo.
- Controle de estoque de insumos por modelo de impressora (com entradas, saídas e exclusões).
- Alerta visual para estoque baixo para cada insumo (toner, fotocondutor e fusor, com limites personalizáveis).
- Visualização moderna nas tabelas, com ordenação por coluna (Impressora, Insumo, Data) e paginação dos registros.
- Alternância entre modo claro e escuro.
- Interface intuitiva e responsiva.

## Estrutura de Pastas


```
├── app.py
├── data/
│ ├── registros.csv
│ └── estoque.csv
├── static/
│ └── style.css
├── templates/
│ ├── index.html
│ └── estoque.html
├── README.md

```

## Como Executar

1. Certifique-se de ter o [Python](https://www.python.org/) instalado (>= 3.8 recomendado).
2. Instale o Flask em um terminal:
    ```
    pip install flask
    ```
3. Execute o projeto pela linha de comando:
    ```
    python app.py
    ```
4. Acesse `http://localhost:5000` no seu navegador preferido.

## Sobre os arquivos de dados

- **data/registros.csv:** Histórico das trocas realizadas e contadores de páginas por insumo.
- **data/estoque.csv:** Quantidade de insumos disponíveis por modelo de impressora.

## Segurança e Usuários

- O sistema não possui autenticação (login/senha).
- Qualquer usuário pode acessar e alterar cadastros de estoque.

## Recomendações

- Para evitar perda de dados, mantenha backup dos arquivos `.csv` periodicamente.
- Imagens, logos ou complementos visuais podem ser adicionados na pasta `static` para personalizar a interface.
- Alertas e temas podem ser facilmente ajustados no arquivo `static/style.css`.

---

Desenvolvido para gestão eficiente e transparente de insumos de impressoras em ambientes empresariais, educacionais ou residenciais.
