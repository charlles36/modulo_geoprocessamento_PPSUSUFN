# Instruções para o Projeto de Geoprocessamento PPSUS UFN
 
Módulo de processamento e geoprocessamento de dados obtidos atráves do sistema de saúde da Prefeitura de Santa Maria



# Instalar virtualenv

pip install virtualenv

python -m venv venv

.\venv\Scripts\activate

pip install -r requirements.txt --use-pep517

# Instruções

Ao acessar o projeto, você será direcionado para a página de geração de mapas. Siga os passos abaixo para gerar mapas e relatórios:

1.	Selecione um CID disponível.

2.	Escolha uma data inicial e uma data final.

3.	Clique no botão "Gerar Mapa".

Para fazer o upload de um relatório:
1.	Selecione uma data.
    - Datas com marcação indicam que um arquivo já foi carregado nesse dia.
    - Se tentar carregar um arquivo em uma data já marcada, o sistema emitirá um aviso de que já existe um relatório para essa data.

2.	Escolha o arquivo referente à data selecionada. Os arquivos estão na pasta “Relatórios para upload no módulo de Geoprocessamento PPSUS UFN”.
    -	Relatórios disponíveis: de 12/02/2024 até 20/06/2024.

3.	Ao upar, se todos os bairros do relatório já estiverem identificados, você verá a mensagem de confirmação.

Caso existam bairros para corrigir, você será direcionado para a página de correção. Nesta página:

Utilize os links fornecidos para auxiliar na identificação:

- [Lei Complementar Nº 42/2006](https://leismunicipais.com.br/a/rs/s/santa-maria/lei-complementar/2006/4/42/lei-complementar-n-42-2006-cria-unidades-urbanas-altera-a-divisao-urbana-de-santa-maria-da-nova-denominacao-aos-bairros-e-revoga-a-lei-municipal-n-2770-86-de-02-071986-artigos-2-a-25-e-da-outras-providencias)
- [OpenStreetMap](https://www.openstreetmap.org/#map=12/-29.6885/-53.7997)

      

Na página de relatórios, você pode:

-	Visualizar todos os arquivos upados.
-	Realizar o download dos arquivos.
 -	Deletar arquivos.
    -	Ao deletar um arquivo, todos os casos vinculados a ele serão removidos do banco de dados.
