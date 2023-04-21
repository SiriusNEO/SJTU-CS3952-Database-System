from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.search import SearchAPI

bp_search = Blueprint("search", __name__, url_prefix="/search")

@bp_search.route("/query_book", methods=["POST"])
def query_book():
    restriction = request.json
    code, message , result = SearchAPI().query_book(**restriction)
    return jsonify({"message": message,"books":result}), code 