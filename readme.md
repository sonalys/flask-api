# Requerimentos
## Bibliotecas
```
Python              3.7.0
Flask               1.1.1
Flask-RESTful       0.3.7
Flask-SQLAlchemy    2.4.1
SQLAlchemy          1.3.11
requests            2.22.0
```
## Arquivos de configuração
***Token de Acesso da API do ClimaTempo(config.py)***
```
token = "TOKEN_DE_ACESSO"
```

# Instalação
```
python3 -m venv env
. env/bin/activate
pip install -r requirements.txt
```

# Execução
```
python run.py
```
Roda em 
```
localhost:5000
```

# Rotas
### ***/analise?data_inicial=yyyy-mm-dd&data_final=yyyy-mm-dd***
* Pesquisa a cidade com maior temperatura
* Devolve a média de precipitação por cidade
### ***/cidade?id=\<ID>***
* Cadastra a temperatura dos últimos 15 dias da cidade selecionada