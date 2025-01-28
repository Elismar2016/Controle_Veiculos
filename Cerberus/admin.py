
# Register your models here.
#admin.site.register(User)
import os
from django.contrib import admin
from django.utils.timezone import now
import datetime
from datetime import timedelta
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.templatetags.static import static
from django.utils.html import escape
from django.contrib.auth.admin import UserAdmin
from django.conf import settings  
from django.contrib.auth.models import User, Group
from .models import User, Supervisor, Motorista,Veiculo,Viagem

#admin.site.register(User)
#@admin.register(User)
class UserAdmin(UserAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser

        if not is_superuser:
            form.base_fields['username'].disabled = True
            form.base_fields['is_superuser'].disabled = True
            form.base_fields['user_permissions'].disabled = True
            form.base_fields['groups'].disabled = True
        return form
    
admin.site.register(Supervisor)
admin.site.register(Motorista)

@admin.register(Viagem)
class ViagemAdmin(admin.ModelAdmin):
    list_display = ("motorista", "veiculo", "destino", "status", "data_partida", "data_chegada")
    list_filter = ("status", "motorista__setor", "veiculo__setor")
    search_fields = ("destino", "motorista__user__username", "veiculo__placa")
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "veiculo" and hasattr(request.user, "motorista"):
            # Filtra os veículos disponíveis e do setor do motorista
            kwargs["queryset"] = Veiculo.objects.filter(
                setor=request.user.motorista.setor,
                status="disponível"
            )
        elif db_field.name == "motorista":
            # Filtra os motoristas ativos
            kwargs["queryset"] = Motorista.objects.filter(ativo=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(User)

def exportar_relatorio_para_desktop(modeladmin, request, queryset):
    """
    Exporta o relatório mensal diretamente para a área de trabalho do usuário.
    """
    hoje = now().date()
    inicio_mes = hoje.replace(day=1)
    fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    # Caminho para a área de trabalho
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
   

def generate_pdf(template_src, context_dict):
    """
    Helper function to generate PDF from a template and context.
    """
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_mensal.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse(f"Erro ao gerar PDF: {pisa_status.err}", status=400)
    return response

@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "modelo","odometro", "status")
    actions = [exportar_relatorio_para_desktop]
    
    actions = ["exportar_relatorio_mensal"]

    def exportar_relatorio_mensal(self, request, queryset):
        """
        Action to export monthly report for selected vehicles.
        """
        veiculo = queryset.first()  # Supondo apenas um veículo por vez
        if not veiculo:
            self.message_user(request, "Nenhum veículo selecionado.", level="error")
            return

        # Filtrando viagens do mês atual
        hoje = datetime.date.today()
        inicio_mes = hoje.replace(day=1)
        fim_mes = (inicio_mes + datetime.timedelta(days=31)).replace(day=1) - datetime.timedelta(days=1)
        
        viagens = Viagem.objects.filter(
            veiculo=veiculo,
            data_partida__gte=inicio_mes,
            data_partida__lte=fim_mes,
        )
        
        # Contexto para o template
        context = {
            "veiculo": veiculo,
            "viagens": viagens,
            "inicio_mes": inicio_mes.strftime("%d/%m/%Y"),
            "fim_mes": fim_mes.strftime("%d/%m/%Y"),
            "data_emissao": hoje,
        }
        # Gerar PDF
        return generate_pdf("relatorios/relatorio_mensal.html", context)

    exportar_relatorio_mensal.short_description = "Exportar relatório mensal (PDF)"
    #pip install xhtml2pdf  para exportar relatorio em pdf.