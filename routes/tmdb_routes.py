from flask import request, jsonify, Blueprint
from dotenv import load_dotenv
import requests
import os

load_dotenv()
api_key = os.getenv('TMDB_KEY')
tmdb_bp = Blueprint("tmdb_bp", __name__)

@tmdb_bp.route("/tmdb/logo", methods=["GET"])
def get_logo():
    tipo = request.args.get('tipo')
    id = request.args.get('id')
    height = request.args.get('height')

    if not (api_key and tipo and id and height):
        return jsonify({"error": "Parâmetros ausentes"}), 400
    url = f"https://api.themoviedb.org/3/{tipo}/{id}/images"
    parametros = {'api_key': api_key}
    response = requests.get(url, params=parametros)

    if response.status_code == 200:
        data = response.json()
        pt_item = next((item for item in data.get('logos', []) if item.get('iso_639_1') == 'pt'), None)
        selected_item = pt_item or next((item for item in data.get('logos', []) if item.get('iso_639_1') == 'en'), None)
        
        if selected_item:
            url = f"https://image.tmdb.org/t/p/{height}{selected_item.get('file_path')}"
            return jsonify({"logo": url})
        else:
            return jsonify({"error": "Não foi possível obter o logo do TMDB"}), 404
    else:
        return jsonify({"error": "Não foi possível obter o logo do TMDB"}), response.status_code

@tmdb_bp.route("/tmdb/popular", methods=["GET"])
def get_popular_media():
    tipo = request.args.get('tipo')
    
    if not tipo:
        return jsonify({"error": "Parâmetros ausentes"}), 400
    url = f"https://api.themoviedb.org/3/trending/{tipo}/week?api_key={api_key}&append_to_response=images%2Caggregate_credits%2Cwatch_providers%2Csimilar%2Cexternal_ids%2Ccontent_ratings%2Creleases&language=pt-BR"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        
        if data.get('results'):
            media = data['results'][0]
            media_id = media['id']
            
            media_logo = None
            url_logo = f"https://api.themoviedb.org/3/{tipo}/{media_id}/images"
            parametros = {'api_key': api_key}
            response_logo = requests.get(url_logo, params=parametros)
            
            if response_logo.status_code == 200:
                data_logo = response_logo.json()
                pt_item = next((item for item in data_logo.get('logos', []) if item.get('iso_639_1') == 'pt'), None)
                selected_item = pt_item or next((item for item in data_logo.get('logos', []) if item.get('iso_639_1') == 'en'), None)
                if selected_item:
                    media_logo = f"https://image.tmdb.org/t/p/w300{selected_item.get('file_path')}"
            
            media_details = None
            url_details = f"https://api.themoviedb.org/3/{tipo}/{media_id}?api_key={api_key}&append_to_response=images%2Caggregate_credits%2Cwatch_providers%2Csimilar%2Cexternal_ids%2Ccontent_ratings%2Creleases&language=pt-BR"
            response_details = requests.get(url_details)
            
            if response_details.status_code == 200:
                media_details = response_details.json()
            
            return jsonify({"trend": media_details, "trend_logo": media_logo})
        else:
            return jsonify({"error": "Não foi possível obter o filme ou série mais assistido(a)"}), 404
    else:
        return jsonify({"error": "Não foi possível obter o filme ou série mais assistido(a)"}), response.status_code
    
@tmdb_bp.route("/tmdb/details", methods=["GET"])
def get_details():
    tipo = request.args.get('tipo')
    media_id = request.args.get('id')
    url = f"https://api.themoviedb.org/3/{tipo}/{media_id}?api_key={api_key}&append_to_response=images%2Caggregate_credits%2Cwatch_providers%2Csimilar%2Cexternal_ids%2Ccontent_ratings%2Creleases%2Ccredits&language=pt-BR"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        media_logo = None
        url_logo = f"https://api.themoviedb.org/3/{tipo}/{media_id}/images"
        parametros = {'api_key': api_key}
        response_logo = requests.get(url_logo, params=parametros)
        
        if response_logo.status_code == 200:
            data_logo = response_logo.json()
            pt_item = next((item for item in data_logo.get('logos', []) if item.get('iso_639_1') == 'pt'), None)
            selected_item = pt_item or next((item for item in data_logo.get('logos', []) if item.get('iso_639_1') == 'en'), None)
            if selected_item:
                media_logo = f"https://image.tmdb.org/t/p/w300{selected_item.get('file_path')}"
        
        return jsonify({"trend": data, "trend_logo": media_logo})
    else:
        return None

@tmdb_bp.route("/tmdb/trailer", methods=["GET"])
def get_media_trailer():
    tipo = request.args.get('tipo')
    id = request.args.get('id')
    url = f"https://api.themoviedb.org/3/{tipo}/{id}/videos"
    parametros = {'api_key': api_key}
    response = requests.get(url, params=parametros)

    if response.status_code == 200:
        data = response.json()
        trailer = next((item for item in data.get('results', []) if item.get('type') == 'Trailer'), None)
        if trailer:
            return jsonify({"trailer_key": trailer.get('key')})
    return None

@tmdb_bp.route("/tmdb/genres", methods=["GET"])
def get_genre_content():
    tipo = request.args.get('tipo')
    
    if not tipo:
        return jsonify({"error": "Parâmetros ausentes"}), 400
    url = f"https://api.themoviedb.org/3/genre/{tipo}/list?api_key={api_key}&language=pt-BR"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return jsonify({"genres": data})
    else:
        return jsonify({"error": "Não foi possível obter o conteúdo do gênero"}), response.status_code
    
@tmdb_bp.route("/tmdb/trending", methods=["GET"])
def fetch_genre_content():
    tipo = request.args.get('tipo')
    
    if not tipo:
        return jsonify({"error": "Parâmetros ausentes"}), 400
    url = f"https://api.themoviedb.org/3/trending/{tipo}/week?api_key={api_key}&language=pt-BR"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return jsonify({"trending": data})
    else:
        return jsonify({"error": "Não foi possível obter o conteúdo do gênero"}), response.status_code
    
@tmdb_bp.route("/tmdb/discover", methods=["GET"])
def fetch_bygenre_content():
    tipo = request.args.get('tipo')
    genre_id = request.args.get('genreId')
    if not (tipo and genre_id):
        return jsonify({"error": "Parâmetros ausentes"}), 400
    url = f"https://api.themoviedb.org/3/discover/{tipo}?api_key={api_key}&language=pt-BR&with_genres={genre_id}&certification_country=BR&certification.lte=14&page=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return jsonify({"genre_content": data})
    else:
        return jsonify({"error": "Não foi possível obter o conteúdo do gênero"}), response.status_code
    
@tmdb_bp.route("/tmdb/now_playing", methods=["GET"])
def fetch_now_playing():
    url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={api_key}&language=pt-BR&page=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return jsonify({"now_playing": data})
    else:
        return jsonify({"error": "Não foi possível obter os filmes em exibição"}), response.status_code

@tmdb_bp.route("/tmdb/search", methods=["GET"])
def search_tmdb():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Parâmetros ausentes"}), 400
    url = f"https://api.themoviedb.org/3/search/multi?api_key={api_key}&language=pt-BR&query={query}&page=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return jsonify({"search_results": data})
    else:
        return jsonify({"error": "Não foi possível realizar a pesquisa"}), response.status_code
    
@tmdb_bp.route("/tmdb/watch_providers", methods=["GET"])
def fetch_watch_providers():
    tipo = request.args.get('tipo')
    id = request.args.get('id')
    url = f"https://api.themoviedb.org/3/{tipo}/{id}/watch/providers?api_key={api_key}&language=pt-BR"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return jsonify({"providers": data})
    else:
        return jsonify({"error": "Não foi possível obter os providers."}), response.status_code

@tmdb_bp.route("/tmdb/season", methods=["GET"])
def fetch_season():
    id = request.args.get('id')
    season = request.args.get('season')
    url = f"https://api.themoviedb.org/3/tv/{id}/season/{season}?api_key={api_key}&language=pt-BR"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return jsonify({"season": data})
    else:
        return jsonify({"error": "Não foi possível obter os dados da temporada"}), response.status_code

@tmdb_bp.route("/tmdb/person", methods=["GET"])
def fetch_person():
    id = request.args.get('id')
    url = f"https://api.themoviedb.org/3/person/{id}?api_key={api_key}&language=pt-BR&append_to_response=external_ids%2Ccombined_credits"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return jsonify({"person": data})
    else:
        return jsonify({"error": "Não foi possível obter os dados da pessoa"}), response.status_code

@tmdb_bp.route("/tmdb/credits", methods=["GET"])
def fetch_episode_actors():
    tv_id = request.args.get('id')
    season_number = request.args.get('season_number')
    episode_number = request.args.get('episode_number')
    url = f"https://api.themoviedb.org/3/tv/{tv_id}/season/{season_number}/episode/{episode_number}/credits?api_key={api_key}&language=pt-BR"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({"error": "Não foi possível obter os atores do episódio"}), response.status_code
    
@tmdb_bp.route("/tmdb/release_date", methods=["GET"])
def get_release_date():
    movie_id = request.args.get('id')
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/release_dates"
    parametros = {'api_key': api_key}
    response = requests.get(url, params=parametros)

    if response.status_code == 200:
        data = response.json()
        data.get('results', []).sort(key=lambda x: x.get('iso_3166_1'))
        brasil_release = next((result for result in data.get('results', []) if result.get('iso_3166_1') == 'BR'), None)
        
        if brasil_release:
            release_dates = brasil_release.get('release_dates', [])[0].get('release_date')
            return jsonify({"release_dates": release_dates})
        else:
            return jsonify({"error": "Não foi possível obter a data de lançamento"}), 404