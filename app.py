from flask import Flask, render_template, request, redirect, url_for, session
import os, hashlib
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = "segredo_megatron"  # chave para sessão

# Configuração do banco: Render usa DATABASE_URL. Local usa SQLite.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///agenda.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Para desenvolvimento local, você pode usar esta URL do PostgreSQL do Render:
# DATABASE_URL = "postgresql://bancodeenderecos_user:GWLa4Qo4t4gFaPElKZaJWu9YK0nwmiz8@dpg-d3097rnfte5s73f3qj50-a.oregon-postgres.render.com/bancodeenderecos"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    senha_hash = Column(String(255))


class Endereco(Base):
    __tablename__ = "enderecos"
    id = Column(Integer, primary_key=True)
    empresa = Column(Text)
    nome = Column(Text)
    rua = Column(Text)
    cidade = Column(Text)


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(Usuario).filter(Usuario.username == "admin").first()
        if not admin:
            senha_hash = hashlib.sha256("1234".encode()).hexdigest()
            db.add(Usuario(username="admin", senha_hash=senha_hash))
            db.commit()
    finally:
        db.close()

# 🔐 Tela de login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        senha = request.form["senha"]
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()

        db = SessionLocal()
        try:
            user = db.query(Usuario).filter(Usuario.username == username, Usuario.senha_hash == senha_hash).first()
        finally:
            db.close()

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

    db = SessionLocal()
    try:
        consulta = db.query(Endereco)
        if filtro_nome:
            consulta = consulta.filter(Endereco.nome.ilike(f"%{filtro_nome}%"))
        if filtro_empresa:
            consulta = consulta.filter(Endereco.empresa.ilike(f"%{filtro_empresa}%"))
        if filtro_cidade:
            consulta = consulta.filter(Endereco.cidade.ilike(f"%{filtro_cidade}%"))
        enderecos = consulta.all()
        total = db.query(Endereco).count()
        enderecos_ctx = [{"id": e.id, "empresa": e.empresa, "nome": e.nome, "rua": e.rua, "cidade": e.cidade} for e in enderecos]
    finally:
        db.close()
    return render_template("dashboard.html", enderecos=enderecos_ctx, total=total,
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

    db = SessionLocal()
    try:
        db.add(Endereco(empresa=empresa, nome=nome, rua=rua, cidade=cidade))
        db.commit()
    finally:
        db.close()
    return redirect(url_for("dashboard"))

# ✏️ Editar endereço
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        if request.method == "POST":
            empresa = request.form["empresa"]
            nome = request.form["nome"]
            rua = request.form["rua"]
            cidade = request.form["cidade"]
            e = db.get(Endereco, id)
            if e:
                e.empresa, e.nome, e.rua, e.cidade = empresa, nome, rua, cidade
                db.commit()
            return redirect(url_for("dashboard"))

        e = db.get(Endereco, id)
        endereco = {"id": e.id, "empresa": e.empresa, "nome": e.nome, "rua": e.rua, "cidade": e.cidade}
    finally:
        db.close()
    return render_template("editar.html", endereco=endereco)

# ❌ Excluir endereço
@app.route("/excluir/<int:id>")
def excluir(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        e = db.get(Endereco, id)
        if e:
            db.delete(e)
            db.commit()
    finally:
        db.close()
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
