from run import db


class Previsao(db.Model):
    cidade = db.Column(db.Integer, db.ForeignKey('cidade.id'), primary_key=True)
    data = db.Column(db.Date, nullable=False, primary_key=True)
    probabilidade = db.Column(db.Float, nullable=False)
    precipitacao = db.Column(db.Float, nullable=False)
    min = db.Column(db.Float, nullable=False)
    max = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('data', 'cidade', name="uma_data_por_cidade"),
    )


class Cidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    estado = db.Column(db.String(30), nullable=False)
    pais = db.Column(db.String(20), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('nome', 'estado', name="um_nome_por_estado"),
    )

    def cidade_mais_quente(data_inicial, data_final):
        maior_temperatura = db.session.query(
            Previsao.cidade, db.func.max(Previsao.max).label('mt')
        ).filter(
            (Previsao.data >= data_inicial) & (Previsao.data <= data_final)
        ).subquery()
        cidade_mais_quente = db.session.query(
            Cidade.nome
        ).join(
            maior_temperatura, maior_temperatura.c.cidade == Cidade.id
        ).first()
        return cidade_mais_quente

    def precipitacao_media(data_inicial, data_final):
        cidades = db.session.query(Cidade.id, Cidade.nome).subquery()
        precipitacao_media = db.session.query(
            cidades.c.nome, db.func.avg(Previsao.precipitacao).label('avg')
        ).filter(
            (Previsao.data >= data_inicial) & (Previsao.data <= data_final)
        ).join( 
            cidades, cidades.c.id == Previsao.cidade
        ).group_by(
            cidades.c.nome
        ).all()
        return [
            {
                'cidade': resposta[0],
                'media': resposta[1]
            } for resposta in precipitacao_media
        ]


db.create_all()
db.session.commit()
