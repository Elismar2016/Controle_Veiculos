# Controle_Veiculos
 Versao atual do CerberusTrack

 
---------------------------------------------------------------------------------------------------------- 
 o login apresentou erro csrf    apos login pemanecia os dados do usuario mas sem token de segurança, 
 obriguei a voltar ao estagio inicial do login , 

 necessario o codigo abaixo no view.py :
 
 def csrf_failure(request, reason=""):
    return redirect(request.META.get('HTTP_REFERER', '/'))

 e no settings.py :
     
 CSRF_FAILURE_VIEW = 'seu_app.views.csrf_failure'
 -------------------------------------------------------------------------------------------------

 

