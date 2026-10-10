from flask import Blueprint
from controllers.auth import register, login, logout
from controllers.errors import handle_401, handle_404, favicon
from controllers.index import index
from controllers.mensajes import obtener_mensajes
from controllers.post import feed, reaction
from controllers.users import lista_usuarios, editar_usuario, eliminar_usuario, profile, api_usuarios

routes = Blueprint("routes", __name__)

# auth
routes.route("/register", methods=["GET", "POST"])(register)
routes.route("/login", methods=["GET", "POST"])(login)
routes.route("/logout")(logout)

# errors
routes.app_errorhandler(401)(handle_401)
routes.app_errorhandler(404)(handle_404)
routes.route("/favicon.ico")(favicon)

routes.route('/api/mensajes/<int:otro_usuario_id>', methods=['GET'])(obtener_mensajes)

# index
routes.route("/", methods=["GET"])(index)
routes.route("/feed", methods=["GET", "POST"])(feed)
routes.route('/reaction/<int:post_id>', methods=['POST'])(reaction)

# Users
routes.route("/api/usuarios", methods=["GET"])(api_usuarios)
routes.route("/usuarios", methods=["GET"])(lista_usuarios)
routes.route("/usuarios/editar/<int:id>", methods=["POST"])(editar_usuario)
routes.route("/usuarios/eliminar/<int:id>", methods=["POST"])(eliminar_usuario)
routes.route("/profile", methods=["GET", "POST"])(profile)