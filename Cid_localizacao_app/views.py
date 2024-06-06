import base64
import geopandas as gp
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import os
import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RelatorioForm
from .models import Relatorio, Casos, CorrecaoBairro


def index(request):
    return render(request, 'index.html')


def lista_relatorios(request):
    relatorios = Relatorio.objects.all().order_by('data')  # Lista relatório ordenado por data
    return render(request, 'lista_relatorios.html', {'relatorios': relatorios})


def delete_relatorio(request, relatorio_id):
    relatorio = get_object_or_404(Relatorio, id=relatorio_id)
    Casos.objects.filter(relatorio=relatorio).delete()  # Deleta os casos relacionados
    relatorio.relatorio.delete()  # Deleta o arquivo do sistema de arquivos
    relatorio.delete()  # Deleta o objeto do banco de dados
    messages.success(request, 'Relatório e dados relacionados deletados com sucesso!')
    return redirect('lista_relatorios')


def transformar_dataframe(df):
    df.rename(  # Alterar nome das colunas
        columns={
            'Localidade': 'NM_BAIRRO',
            'Quant.': 'Quant',
            'Código': 'Codigo',
            'Descrição do CID': 'Descrição_do_CID'
        },
        inplace=True
    )
    df['Descrição_do_CID'] = df['Descrição_do_CID'].astype(str)  # Altera para String
    df['Quant'] = pd.to_numeric(df['Quant'], errors='coerce').fillna(0).astype(int)  # Se tiver campo null altera para 0
    df['NM_BAIRRO'] = df['NM_BAIRRO'].str.upper().str.strip().str.replace(',', '')  # Remove virgula que possa conter na coluna NM_Bairro bairros
    return df


def carregar_bairros_distritos():
    bairros_distritos_path = os.path.join(settings.MEDIA_ROOT, 'BairroseDistrito-sm.json')
    Bairros_distritos = gp.read_file(bairros_distritos_path)
    Bairros_distritos['NM_BAIRRO'] = Bairros_distritos['NM_BAIRRO'].str.upper().str.strip()
    return Bairros_distritos


def carregar_bairros():
    bairros_path = os.path.join(settings.MEDIA_ROOT, 'Bairros-SM.json')
    Bairros = gp.read_file(bairros_path)
    Bairros['NM_BAIRRO'] = Bairros['NM_BAIRRO'].str.upper().str.strip()
    return Bairros


def normalizar_bairros(df, mapeamentos, bairros_corretos):
    mapeamento_dict = {m.bairro_incorreto: m.bairro_correto for m in mapeamentos}
    df['NM_BAIRRO'] = df['NM_BAIRRO'].apply(lambda x: mapeamento_dict.get(x, x))
    bairros_incorretos = df.loc[~df['NM_BAIRRO'].isin(bairros_corretos), 'NM_BAIRRO'].unique()
    return df, bairros_incorretos


def salvar_dados(df, relatorio):
    for index, row in df.iterrows():
        Casos.objects.create(
            relatorio=relatorio,
            cid=row['Codigo'],
            bairro=row['NM_BAIRRO'],
            descricao_cid=row['Descrição_do_CID'].upper(),
            quantidade_casos=row['Quant'],
            data=relatorio.data,
        )

def salvar_grafico(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close(fig)
    return base64.b64encode(image_png).decode('utf-8')


def criar_grafico_bairros(bairros_merged, cid, descricao_cid, data_inicial, data_final):
    fig, ax = plt.subplots(figsize=(10, 12))
    Bairros = carregar_bairros()
    Bairros.plot(ax=ax, alpha=0.4, color='lightgrey')  # Cria uma primeira camada em cinza
    bairros_merged.plot(ax=ax, alpha=0.6, cmap='tab20b')  # Preenche onde tem casos
    for idx, row in bairros_merged.iterrows():
        plt.text(row.geometry.centroid.x, row.geometry.centroid.y, f"{row['NM_BAIRRO']}", fontsize=5,
                 horizontalalignment='center')
        plt.text(row.geometry.centroid.x, row.geometry.centroid.y, f"{row['quantidade_casos']}", fontsize=10,
                 verticalalignment='top')
    plt.title(f"Mapa de Bairros com Casos de CID {cid} - {descricao_cid} - {data_inicial} - {data_final}")
    return salvar_grafico(fig)


def criar_grafico_barras(bairros_merged, cid, descricao_cid):
    fig, ax = plt.subplots(figsize=(10, 6))
    barras = bairros_merged.plot(kind='bar', x='NM_BAIRRO', y='quantidade_casos', ax=ax, legend=False)
    for bar in barras.patches:
        ax.annotate(format(bar.get_height(), '.0f'),
                    (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha='center', va='center',
                    size=10, xytext=(0, 8),
                    textcoords='offset points')
    plt.title(f"Quantidade de Casos por Bairro para CID {cid} - {descricao_cid}")
    plt.xlabel("Bairros")
    plt.ylabel("Quantidade de Casos")
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    return salvar_grafico(fig)


def criar_grafico_casos_por_dia(casos_df, cid, descricao_cid):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(casos_df['data'], casos_df['total_casos'], marker='o', linestyle='-')
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    for i in range(len(casos_df)):
        ax.annotate(format(casos_df['total_casos'][i], '.0f'),
                    (casos_df['data'][i], casos_df['total_casos'][i]),
                    ha='center', va='bottom',
                    size=10, xytext=(0, 8),
                    textcoords='offset points')
    plt.title(f"Quantidade de Casos por Dia para CID {cid} - {descricao_cid}")
    plt.xlabel("Data")
    plt.ylabel("Quantidade de Casos")
    plt.xticks(rotation=45)
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    return salvar_grafico(fig)


def upload_relatorio(request):
    if request.method == 'POST':
        form = RelatorioForm(request.POST, request.FILES)
        if form.is_valid():
            relatorio = form.save(commit=False)
            relatorio.save()

            df = pd.read_excel(relatorio.relatorio)
            cidade_desejada = 'SANTA MARIA'
            df = df[df['Cidade'] == cidade_desejada]
            df = df[['Localidade', 'Quant.', 'Descrição do CID', 'Código']]
            df = transformar_dataframe(df)


            Bairros = carregar_bairros_distritos()
            bairros_corretos = Bairros['NM_BAIRRO'].unique().tolist()
            mapeamentos = CorrecaoBairro.objects.all()
            df, bairros_incorretos = normalizar_bairros(df, mapeamentos, bairros_corretos)

            if bairros_incorretos.any():
                request.session['relatorio_id'] = relatorio.id
                request.session['bairros_incorretos'] = list(bairros_incorretos)
                request.session['df_corrigido'] = df.to_json()
                return redirect('vincular_bairros')

            salvar_dados(df, relatorio)
            messages.success(request, 'Relatório enviado e dados salvos com sucesso!')
            return redirect('upload_relatorio')
        else:
            messages.error(request, 'Erro ao enviar o relatório. Verifique os dados e tente novamente.')
    else:
        form = RelatorioForm()

    return render(request, 'upload_relatorio.html', {'form': form})


def vincular_bairros(request):
    if request.method == 'POST':
        mapeamentos = request.POST.getlist('mapeamento')
        for mapping in mapeamentos:
            bairro_incorreto, bairro_correto = mapping.split(',')
            CorrecaoBairro.objects.create(bairro_incorreto=bairro_incorreto, bairro_correto=bairro_correto)

        relatorio_id = request.session.get('relatorio_id')
        relatorio = Relatorio.objects.get(id=relatorio_id)
        df = pd.read_json(request.session.get('df_corrigido'))
        df = transformar_dataframe(df)

        mapeamentos = CorrecaoBairro.objects.all()
        df, _ = normalizar_bairros(df, mapeamentos, bairros_corretos=[])
        salvar_dados(df, relatorio)

        del request.session['df_corrigido']
        del request.session['relatorio_id']
        del request.session['bairros_incorretos']

        messages.success(request, 'Bairros vinculados e dados salvos com sucesso!')
        return redirect('upload_relatorio')

    bairros_incorretos = request.session.get('bairros_incorretos', [])
    Bairros = carregar_bairros_distritos()
    bairros_corretos = Bairros['NM_BAIRRO'].str.upper().str.strip().unique()
    return render(request, 'corrigir_bairros.html', {'bairros_incorretos': bairros_incorretos, 'bairros_corretos': bairros_corretos})


def get_relatorio_datas(request):
    datas = Relatorio.objects.values_list('data', flat=True).distinct()
    datas = [data.strftime('%Y-%m-%d') for data in datas]
    return JsonResponse({'datas': datas})


def get_cids(request):
    cids = Casos.objects.values('cid', 'descricao_cid').distinct().order_by('cid')
    return JsonResponse({'cids': list(cids)})


def get_datas(request):
    cid = request.GET.get('cid')
    if not cid:
        return JsonResponse({'error': 'CID não fornecido'}, status=400)

    datas = Casos.objects.filter(cid=cid).values_list('data', flat=True).distinct()
    datas = [data.strftime('%Y-%m-%d') for data in datas]
    return JsonResponse({'dates': list(datas)})


def get_bairros(request):
    cid = request.GET.get('cid')
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')

    bairros = Casos.objects.filter(cid=cid)
    if data_inicial:
        bairros = bairros.filter(data__gte=data_inicial)
    if data_final:
        bairros = bairros.filter(data__lte=data_final)
    descricao_cid = bairros.first().descricao_cid if bairros.exists() else "Descrição não disponível"

    bairros_path = os.path.join(settings.MEDIA_ROOT, 'Bairros-SM.json')
    Bairros = gp.read_file(bairros_path)
    Bairros['NM_BAIRRO'] = Bairros['NM_BAIRRO'].str.upper()

    bairros_df = pd.DataFrame.from_records(bairros.values())
    bairros_df.rename(columns={'bairro': 'NM_BAIRRO'}, inplace=True)
    bairros_df = bairros_df.groupby('NM_BAIRRO').agg(
        {'quantidade_casos': 'sum', 'descricao_cid': 'first'}).reset_index()
    bairros_merged = Bairros.merge(bairros_df, on='NM_BAIRRO', how='inner')

    if 'geometry' in bairros_merged and bairros_merged['geometry'].dtype == 'geometry':
        grafico_mapa = criar_grafico_bairros(bairros_merged, cid, descricao_cid, data_inicial, data_final)
        grafico_bairros = criar_grafico_barras(bairros_merged, cid, descricao_cid)

        if data_inicial and data_final:
            date_range = pd.date_range(start=data_inicial, end=data_final)
        else:
            date_range = pd.date_range(start=bairros.earliest('data').data, end=bairros.latest('data').data)

        casos_por_dia = bairros.values('data').annotate(total_casos=Sum('quantidade_casos')).order_by('data')
        casos_df = pd.DataFrame.from_records(casos_por_dia)
        casos_df['data'] = pd.to_datetime(casos_df['data'])
        casos_df.set_index('data', inplace=True)
        casos_df = casos_df.reindex(date_range, fill_value=0).reset_index()
        casos_df.rename(columns={'index': 'data'}, inplace=True)

        grafico_caso_dia = criar_grafico_casos_por_dia(casos_df, cid, descricao_cid)

        html_response = f'''
            <h2>Mapa de Bairros com Casos de CID {cid} - {descricao_cid} - {data_inicial} - {data_final}</h2>
            <img src="data:image/png;base64,{grafico_mapa}" alt="Mapa de Bairros">
            <h2>Quantidade de Casos por Bairro</h2>
            <img src="data:image/png;base64,{grafico_bairros}" alt="Gráfico de Casos por bairros">
            <h2>Quantidade de Casos por Dia</h2>
            <img src="data:image/png;base64,{grafico_caso_dia}" alt="Gráfico de Casos por dia">
        '''
        return HttpResponse(html_response)
    else:
        return HttpResponse('<p>Dados geográficos inválidos ou faltando.</p>')
