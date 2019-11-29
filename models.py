from run import db


class Previsao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cidade = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Date, nullable=False)
    probabilidade = db.Column(db.Float, nullable=False)
    precipitacao = db.Column(db.Float, nullable=False)
    min = db.Column(db.Float, nullable=False)
    max = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('data', 'cidade', name="_prevision_per_city"),
    )


class Cidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    estado = db.Column(db.String(30), nullable=False)
    pais = db.Column(db.String(20), nullable=False)

    def get_cidade_mais_quente(data_inicial, data_final):
        maior_temperatura = db.session.query(
            Previsao.cidade, db.func.max(Previsao.max).label('mt')
        ).filter(
            (Previsao.data >= data_inicial) & (Previsao.data < data_final)
        ).subquery()
        cidade_mais_quente = db.session.query(
            Cidade.nome
        ).join(
            maior_temperatura, maior_temperatura.c.cidade == Cidade.id
        ).first()
        return cidade_mais_quente

    def get_precipitacao_media(data_inicial, data_final):
        precipitacao_media = db.session.query(
            Previsao.cidade, db.func.avg(Previsao.precipitacao).label('avg')
        ).filter(
            (Previsao.data >= data_inicial) & (Previsao.data < data_final)
        ).subquery()
        precipitacao_media_por_cidade = db.session.query(
            Cidade.nome, precipitacao_media.c.avg
        ).join(
            precipitacao_media, precipitacao_media.c.cidade == Cidade.id
        ).all()

        return [
            {
                'cidade': resposta[0],
                'media': resposta[1]
            } for resposta in precipitacao_media_por_cidade
        ]


db.create_all()
db.session.commit()
