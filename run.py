import requests
from json import dumps
from datetime import datetime

from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import sqlite3

import config
import models

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

parser = reqparse.RequestParser()
parser.add_argument('id')

CLIMATEMPO_TOKEN = config.token


class Analise(Resource):
    def get(self):
        data_inicial = datetime.strptime(
            request.args['data_inicial'], '%Y-%m-%d')
        data_final = datetime.strptime(request.args['data_final'], '%Y-%m-%d')

        cidade_mais_quente = models.Cidade.get_cidade_mais_quente(
            data_inicial, data_final)
        precipitacao_media = models.Cidade.get_precipitacao_media(
            data_inicial, data_final)

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
        db.session.merge(cidade)
        db.session.commit()

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
            db.session.merge(previsao)
            db.session.commit()

        return "ok"


api.add_resource(Analise, '/analise')
api.add_resource(Cidade, '/cidade')


if __name__ == '__main__':
    app.run(port=5000)
