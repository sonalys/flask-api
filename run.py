from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from json import dumps
import requests
from datetime import datetime

import models

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

parser = reqparse.RequestParser()
parser.add_argument('id')

CLIMATEMPO_TOKEN = "b22460a8b91ac5f1d48f5b7029891b53"


class Analise(Resource):
    def get(self):
        cidade_mais_quente = models.Cidade.get_cidade_mais_quente()
        precipitacao_media = models.Cidade.get_precipitacao_media()

        data = {
                'cidade_mais_quente': cidade_mais_quente,
                'precipitacao_media': precipitacao_media
        }
        return app.response_class(
            response=dumps(data),
            mimetype='application/json'
        )


class Cidade(Resource):
    def get(self):
        id = request.args['id']
        return self._pegar_dados_climatempo(id)

    def _pegar_dados_climatempo(self, id):
        url = f'http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/{id}/days/15?token={CLIMATEMPO_TOKEN}'
        response = requests.get(url).json()
        cidade = models.Cidade(
                nome=response["name"],
                estado=response["state"],
                pais=response["country"]
        )
        try:
            db.session.add(cidade)
            db.session.commit()
        except Exception:
            pass

        lista_previsoes = response["data"]

        for previsao in lista_previsoes:
            previsao = models.Previsao(
                cidade=cidade.id,
                data=datetime.strptime(previsao["date"], '%Y-%m-%d'),
                probabilidade=previsao["rain"]["probability"],
                precipitacao=previsao["rain"]["precipitation"],
                min=previsao["thermal_sensation"]["min"],
                max=previsao["thermal_sensation"]["max"]
            )
            try:
                db.session.add(previsao)
                db.session.commit()
            except Exception:
                pass

        return "ok"


api.add_resource(Analise, '/analise')
api.add_resource(Cidade, '/cidade')


if __name__ == '__main__':
    app.run(port=5000)
