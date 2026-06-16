#criar as rotas do nosso site(os links)

from flask import render_template, url_for, redirect, request, flash, session
from fakepinterest import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from fakepinterest.forms import FormLogin, FormCriarConta, FormFoto
from fakepinterest.models import Usuario, Foto
import os
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt

@app.route("/", methods=['GET','POST'])
def homepage():
    formlogin = FormLogin()
    if formlogin.validate_on_submit():
        usuario = Usuario.query.filter_by(email= formlogin.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, formlogin.senha.data):
            login_user(usuario)
            return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("index.html", form=formlogin)

@app.route('/perfil/<id_usuario>', methods=["GET",'POST'])
@login_required
def perfil(id_usuario):
    if int(id_usuario) == int(current_user.id):
        # o usuário está vendo o perfil dele
        form_foto = FormFoto()
        if form_foto.validate_on_submit():
            arquivo = form_foto.foto.data
            nome_seguro =   secure_filename(arquivo.filename)
            # salvar o arquivo na pasta foto_post
            caminho = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               app.config["UPLOAD_FOLDER"],  nome_seguro)
            arquivo.save(caminho)
            #registrar esse arquivo no banco de dados
               # Verifica se a foto já existe no banco de dados
            foto_existente = Foto.query.filter_by(imagem=nome_seguro, id_usuario=current_user.id).first()
            if not foto_existente:
                foto = Foto(imagem=nome_seguro, id_usuario=current_user.id)
                database.session.add(foto)
                database.session.commit()
                flash('Foto enviada com sucesso!', 'success')
            else:
                flash('Esta foto já foi enviada.', 'info')

            return redirect(url_for('perfil', id_usuario=current_user.id))

        return render_template('perfil.html', usuario=current_user, form=form_foto)
    else:
        usuario = Usuario.query.get(int(id_usuario))
        return render_template('perfil.html', usuario=usuario, form=None)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))


@app.route("/feed")
@login_required
def feed():
    fotos = Foto.query.order_by(Foto.data_criacao).all()
    return render_template("feed.html", fotos = fotos)


@app.route('/buscar_perfis', methods=['GET', 'POST'])
def buscar_perfis():
    if request.method == 'POST':
        termo_busca = request.form.get('busca')  # Obtém o termo de busca do formulário
        perfis_encontrados = Usuario.query.filter(Usuario.username.contains(termo_busca)).all()
        return render_template('resultados_busca.html', perfis=perfis_encontrados, termo_busca=termo_busca)
    return redirect(url_for('homepage'))  # Redireciona se o método não for POST




@app.route('/deletar_foto/<id_foto>', methods=['GET', 'POST'])
@login_required
def deletar_foto(id_foto):
    foto = Foto.query.get(int(id_foto))
    
    # Verifica se o usuário é o dono da foto ou um administrador
    if foto and (foto.id_usuario == current_user.id or current_user.is_admin):
        # Remove o arquivo da foto do sistema de arquivos
        caminho_foto = os.path.join(app.config['UPLOAD_FOLDER'], foto.imagem)
        if os.path.exists(caminho_foto):
            os.remove(caminho_foto)
        
        # Remove o registro da foto do banco de dados
        database.session.delete(foto)
        database.session.commit()
        
        flash('Foto excluída com sucesso!', 'success')
    else:
        flash('Você não tem permissão para excluir esta foto.', 'danger')
    
    return redirect(url_for('perfil', id_usuario=current_user.id))

@app.route('/acesso', methods=['GET', 'POST'])
def acesso():
    if request.method == 'POST':
        chave = request.form.get('chave')  # Obtém a chave do formulário
        if chave == app.config['CHAVE_ACESSO']:
            session['acesso_permitido'] = True  # Armazena na sessão que o acesso foi permitido
            flash('Acesso concedido!', 'success')
            return redirect(url_for('pagina_restrita'))  # Redireciona para a página restrita
        else:
            flash('Chave de acesso incorreta.', 'danger')
    return render_template('acesso.html')  # Renderiza o template de entrada da chave

@app.route('/pagina_restrita')
def pagina_restrita():
    if not session.get('acesso_permitido'):  # Verifica se o acesso foi permitido
         flash('Você precisa fornecer a chave de acesso para acessar esta página.', 'danger')
         return redirect(url_for('acesso'))
    return render_template('homepage')


@app.route("/")
def index():
    return render_template("index.html")