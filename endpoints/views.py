from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from endpoints.serializers import EmpresaSerializer
from endpoints.models import Empresa
import joblib
import pandas as pd
import numpy as np
import shap
import matplotlib
import base64
import io

matplotlib.use("Agg")
import matplotlib.pyplot as plt

columns = ['CODIGO', 'Scope 1 Estimated Totals To Revenues USD in Million\n(FY0)',
           'Water Use To Revenues USD in million\n(FY0)',
           'Total Energy Use To Revenues USD in million\n(FY0)',
           'Health & Safety Policy\n(FY0)',
           'Policy Supply Chain Health & Safety\n(FY0)',
           'Policy Diversity and Opportunity\n(FY0)', 'Salary Gap\n(FY0)',
           'Net Employment Creation\n(FY0)', 'Policy Board Independence\n(FY0)',
           'Policy Board Diversity\n(FY0)', 'Policy Board Experience\n(FY0)',
           'Total Renewable Energy\n(FY0)', 'Market Cap', 'Green Capex\n(FY0)']


@api_view(['GET'])
def get_all_data(request):
    if request.method == 'GET':
        res = EmpresaSerializer(Empresa.objects.all(), many=True)
        return JsonResponse(res.data, status=200, safe=False)


@api_view(['POST'])
def create_data(request):
    if request.method == 'POST':
        empresa_data = JSONParser().parse(request)
        empresa_serialized = EmpresaSerializer(data=empresa_data)
        print(empresa_data)
        if empresa_serialized.is_valid():
            data = pd.DataFrame(np.array([[
                empresa_serialized.validated_data['sector_code'],
                empresa_serialized.validated_data['co2_revenues'],
                empresa_serialized.validated_data['water_revenues'],
                empresa_serialized.validated_data['energy_revenues'],
                empresa_serialized.validated_data['health_policy'],
                empresa_serialized.validated_data['supply_chain_policy'],
                empresa_serialized.validated_data['diversity_policy'],
                empresa_serialized.validated_data['salary_gap'],
                empresa_serialized.validated_data['net_employment_creation'],
                empresa_serialized.validated_data['board_independency_policy'],
                empresa_serialized.validated_data['board_diversity_policy'],
                empresa_serialized.validated_data['board_experience_policy'],
                empresa_serialized.validated_data['renewable_energy'],
                empresa_serialized.validated_data['market_gap'],
                empresa_serialized.validated_data['green_capex'],
            ]]))
            data.columns = columns
            scaler = joblib.load(
                'C:\\Users\\jrtta\\OneDrive\\Escritorio\\proyectos '
                'personales\\python\\hackatonBCPBackend\\model\\scaler.model')
            scaled_data = scaler.transform(data)
            random_forest = joblib.load(
                'C:\\Users\\jrtta\\OneDrive\\Escritorio\\proyectos '
                'personales\\python\\hackatonBCPBackend\\model\\random_forest.model')
            predicted = random_forest.predict(scaled_data)
            empresa_serialized.save(esg_score=predicted[0])
            res = EmpresaSerializer(Empresa.objects.all().filter(name=empresa_serialized.data['name']), many=True)
            return JsonResponse(res.data, status=200, safe=False)
        return JsonResponse(empresa_serialized.errors, status=400)


@api_view(['GET'])
def get_data(request):
    if request.method == 'GET':
        company_name = request.GET.get('name', "No se encontro el parametro 'params' en la URL")
        print(company_name)
        res = EmpresaSerializer(Empresa.objects.all().filter(name=company_name), many=True)
        return JsonResponse(res.data, status=200, safe=False)


def save_shap_plot_as_base64(plot):
    # Save the plot as HTML and then read it as a string
    buf = io.StringIO()
    shap.save_html(buf, plot)
    html_str = buf.getvalue()

    # Encode the HTML string as a base64 string
    plot_base64 = base64.b64encode(html_str.encode()).decode('utf-8')
    return plot_base64


def save_summary_plot_as_base64(shap_values, x_test_scaled, feature_names):
    # Create the summary plot and save to a bytes buffer
    buf = io.BytesIO()
    shap.summary_plot(shap_values, x_test_scaled, feature_names=feature_names, show=False)
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Encode the plot as a base64 string
    plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return plot_base64


@api_view(['GET'])
def generate_image(request):
    if request.method == 'GET':
        company_name = request.GET.get('name', "No se encontro el parametro 'params' en la URL")
        data = Empresa.objects.all().filter(name=company_name).order_by('-date')[0]
        data_df = pd.DataFrame(np.array([[
            data.sector_code,
            data.co2_revenues,
            data.water_revenues,
            data.energy_revenues,
            data.health_policy,
            data.supply_chain_policy,
            data.diversity_policy,
            data.salary_gap,
            data.net_employment_creation,
            data.board_independency_policy,
            data.board_diversity_policy,
            data.board_experience_policy,
            data.renewable_energy,
            data.market_gap,
            data.green_capex,
        ]]))
        scaler = joblib.load(
            'C:\\Users\\jrtta\\OneDrive\\Escritorio\\proyectos '
            'personales\\python\\hackatonBCPBackend\\model\\scaler.model')
        new_data_scaled = scaler.transform(data_df)
        best_rf = joblib.load('C:\\Users\\jrtta\\OneDrive\\Escritorio\\proyectos '
                              'personales\\python\\hackatonBCPBackend\\model\\features_importance.model')
        explainer = shap.TreeExplainer(best_rf)
        x_test_scaled = pd.read_excel('C:\\Users\\jrtta\\OneDrive\\Escritorio\\proyectos '
                                      'personales\\python\\hackatonBCPBackend\\endpoints\\test_data.xlsx')
        shap_values = explainer.shap_values(x_test_scaled)
        summary_plot_img = save_summary_plot_as_base64(shap_values, x_test_scaled, columns)

        new_shap_values = explainer.shap_values(new_data_scaled)
        shap.initjs()
        force_plot = shap.force_plot(explainer.expected_value, new_shap_values[0], new_data_scaled[0],
                                     feature_names=columns)
        force_plot_img = save_shap_plot_as_base64(force_plot)
        return JsonResponse({'force_plot': force_plot_img, 'summary_plot': summary_plot_img})
