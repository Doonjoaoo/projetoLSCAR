from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, hashlib

app = Flask(__name__)
app.secret_key = "segredo_megatron"  # chave para sessão

# Função para conectar ao banco
def get_db():
    conn = sqlite3.connect("agenda.db")
    conn.row_factory = sqlite3.Row
    return conn

# Inicializa tabelas
def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    senha_hash TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS enderecos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empresa TEXT,
                    nome TEXT,
                    rua TEXT,
                    cidade TEXT)""")

    # cria usuário admin padrão (senha: 1234)
    c.execute("SELECT * FROM usuarios WHERE username=?", ("admin",))
    if not c.fetchone():
        senha_hash = hashlib.sha256("1234".encode()).hexdigest()
        c.execute("INSERT INTO usuarios (username, senha_hash) VALUES (?,?)", ("admin", senha_hash))

    conn.commit()
    conn.close()

# 🔐 Tela de login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        senha = request.form["senha"]
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE username=? AND senha_hash=?", (username, senha_hash))
        user = c.fetchone()
        conn.close()

        if user:
            session["usuario"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", erro="Usuário ou senha incorretos")

    return render_template("login.html")

# 🔓 Logout
@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

# 📋 Dashboard - lista com filtros
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    filtro_nome = request.args.get("nome", "")
    filtro_empresa = request.args.get("empresa", "")
    filtro_cidade = request.args.get("cidade", "")

    conn = get_db()
    c = conn.cursor()
    query = "SELECT * FROM enderecos WHERE 1=1"
    params = []

    if filtro_nome:
        query += " AND nome LIKE ?"
        params.append(f"%{filtro_nome}%")
    if filtro_empresa:
        query += " AND empresa LIKE ?"
        params.append(f"%{filtro_empresa}%")
    if filtro_cidade:
        query += " AND cidade LIKE ?"
        params.append(f"%{filtro_cidade}%")

    c.execute(query, params)
    enderecos = c.fetchall()

    # conta total
    c.execute("SELECT COUNT(*) FROM enderecos")
    total = c.fetchone()[0]

    conn.close()
    return render_template("dashboard.html", enderecos=enderecos, total=total,
                           filtro_nome=filtro_nome, filtro_empresa=filtro_empresa, filtro_cidade=filtro_cidade)

# ➕ Adicionar endereço
@app.route("/novo", methods=["POST"])
def novo():
    if "usuario" not in session:
        return redirect(url_for("login"))

    empresa = request.form["empresa"]
    nome = request.form["nome"]
    rua = request.form["rua"]
    cidade = request.form["cidade"]

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO enderecos (empresa, nome, rua, cidade) VALUES (?,?,?,?)",
              (empresa, nome, rua, cidade))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

# ✏️ Editar endereço
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    c = conn.cursor()
    if request.method == "POST":
        empresa = request.form["empresa"]
        nome = request.form["nome"]
        rua = request.form["rua"]
        cidade = request.form["cidade"]
        c.execute("UPDATE enderecos SET empresa=?, nome=?, rua=?, cidade=? WHERE id=?",
                  (empresa, nome, rua, cidade, id))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))

    c.execute("SELECT * FROM enderecos WHERE id=?", (id,))
    endereco = c.fetchone()
    conn.close()
    return render_template("editar.html", endereco=endereco)

# ❌ Excluir endereço
@app.route("/excluir/<int:id>")
def excluir(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM enderecos WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
