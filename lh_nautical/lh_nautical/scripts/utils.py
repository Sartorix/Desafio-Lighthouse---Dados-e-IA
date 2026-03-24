import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent


def load_dataset(filename):
    """
    Carrega dataset da pasta datasets.

    Parâmetros:
        filename (str): Nome do arquivo (ex: 'vendas_2023_2024.csv')

    Retorna:
        pd.DataFrame: Dataset carregado
    """
    filepath = BASE_PATH / 'datasets' / filename

    if filename.endswith('.csv'):
        return pd.read_csv(filepath)
    elif filename.endswith('.json'):
        return pd.read_json(filepath)
    else:
        raise ValueError(f"Formato não suportado: {filename}")


def save_output(df, filename, output_type='dados_processados'):
    """
    Salva output na pasta outputs.

    Parâmetros:
        df (pd.DataFrame): DataFrame a ser salvo
        filename (str): Nome do arquivo
        output_type (str): Tipo de output ('dados_processados', 'relatorios', 'graficos')
    """
    output_path = BASE_PATH / 'outputs' / output_type
    output_path.mkdir(parents=True, exist_ok=True)

    filepath = output_path / filename

    if filename.endswith('.csv'):
        df.to_csv(filepath, index=False, encoding='utf-8')
    elif filename.endswith('.json'):
        df.to_json(filepath, orient='records', indent=2)

    print(f"✓ Arquivo salvo: {filepath}")


def detect_outliers_iqr(series, multiplier=1.5):
    """
    Detecta outliers usando método IQR.

    Parâmetros:
        series (pd.Series): Série para análise
        multiplier (float): Multiplicador IQR (default: 1.5)

    Retorna:
        tuple: (índices_outliers, limite_inferior, limite_superior)
    """
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1

    limite_inferior = Q1 - multiplier * IQR
    limite_superior = Q3 + multiplier * IQR

    outliers = (series < limite_inferior) | (series > limite_superior)

    return outliers, limite_inferior, limite_superior


def format_currency(value):
    """Formata valor como moeda BRL."""
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def create_date_dimension(start_date, end_date):
    """
    Cria dimensão de calendário.

    Parâmetros:
        start_date (str ou datetime): Data de início (YYYY-MM-DD)
        end_date (str ou datetime): Data de fim (YYYY-MM-DD)

    Retorna:
        pd.DataFrame: Dimensão de datas com coluna 'dia_semana'
    """
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)

    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    df_datas = pd.DataFrame({
        'data': date_range,
        'dia_semana': date_range.day_name(),
        'dia_semana_pt': date_range.strftime('%A').map({
            'Monday': 'Segunda-feira',
            'Tuesday': 'Terça-feira',
            'Wednesday': 'Quarta-feira',
            'Thursday': 'Quinta-feira',
            'Friday': 'Sexta-feira',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }),
        'mes': date_range.month,
        'ano': date_range.year,
        'semana': date_range.isocalendar().week
    })

    return df_datas


def plot_with_style(figsize=(12, 6), title="", xlabel="", ylabel=""):
    """
    Cria figura com estilo padrão.

    Retorna:
        tuple: (fig, ax)
    """
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=figsize)

    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=11)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=11)

    return fig, ax


def validate_data_quality(df, required_columns=None):
    """
    Valida qualidade básica do dataset.

    Parâmetros:
        df (pd.DataFrame): DataFrame a validar
        required_columns (list): Colunas obrigatórias

    Retorna:
        dict: Relatório de qualidade
    """
    report = {
        'total_linhas': len(df),
        'total_colunas': len(df.columns),
        'valores_nulos': df.isnull().sum().to_dict(),
        'duplicatas': df.duplicated().sum(),
        'colunas_presentes': list(df.columns),
        'tipos_dados': df.dtypes.to_dict()
    }

    if required_columns:
        report['colunas_faltantes'] = [col for col in required_columns if col not in df.columns]

    return report


def print_quality_report(report):
    """Imprime relatório de qualidade de forma formatada."""
    print("=" * 60)
    print("RELATÓRIO DE QUALIDADE DOS DADOS")
    print("=" * 60)
    print(f"\nTotal de linhas: {report['total_linhas']:,}")
    print(f"Total de colunas: {report['total_colunas']}")
    print(f"Duplicatas: {report['duplicatas']}")

    nulos = {k: v for k, v in report['valores_nulos'].items() if v > 0}
    if nulos:
        print(f"\nValores nulos:")
        for col, count in nulos.items():
            print(f"  {col}: {count}")
    else:
        print("\nValores nulos: Nenhum encontrado ✓")

    if 'colunas_faltantes' in report and report['colunas_faltantes']:
        print(f"\nColunas faltantes: {report['colunas_faltantes']}")
