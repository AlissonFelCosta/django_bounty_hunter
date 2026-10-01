from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.shortcuts import render

from .models import Bando, Cartaz, Procurado


def dashboard(request):
    """
    Painel do xerife. De propósito NÃO é uma ListView: cada bloco aqui
    vem de uma consulta agregada diferente (soma, contagem agrupada,
    ordenação por outro model, junção com outro model) — não existe uma
    generic view pronta pra "misturar 4 agregações diferentes na mesma
    página", então uma função simples é o jeito mais direto de montar
    esse contexto.
    """
    cartazes_ativos = Cartaz.objects.filter(status=Cartaz.Status.ATIVO)

    # --- 1) Indicador financeiro -----------------------------------
    # aggregate() devolve um dicionário ({'total': ...}), não um
    # queryset — é a forma certa de pedir "me dê só o número", sem
    # precisar trazer os cartazes e somar em Python.
    #
    # Pegadinha do SQLite: SUM() sobre um DecimalField(decimal_places=2)
    # pode devolver Decimal('6800') em vez de Decimal('6800.00') — o
    # SQLite não tem tipo decimal nativo, então a soma perde a escala
    # fixa que os valores individuais têm quando lidos direto da coluna.
    # Isso é específico de SQLite; em Postgres/MySQL o SUM já preserva
    # as casas decimais. quantize() garante o formato certo de qualquer
    # jeito, nos dois cenários.
    total_recompensas_ativas = (
        cartazes_ativos.aggregate(total=Sum('valor_recompensa'))['total']
        or Decimal('0.00')
    ).quantize(Decimal('0.01'))

    # --- 2) Ranking de ameaças --------------------------------------
    # annotate() adiciona uma coluna calculada a cada Bando do resultado.
    # O Count aqui não conta todos os procurados do bando, só os que têm
    # ALGUM cartaz ativo — por isso o filter=Q(...) dentro do Count em
    # vez de um .filter() solto na queryset (que filtraria os BANDOS,
    # não a contagem). distinct=True evita contar o mesmo procurado
    # duas vezes caso ele tenha mais de um cartaz ativo.
    ranking_bandos = (
        Bando.objects
        .annotate(
            total_procurados_ativos=Count(
                'procurados',
                filter=Q(procurados__cartazes__status=Cartaz.Status.ATIVO),
                distinct=True,
            )
        )
        .order_by('-total_procurados_ativos', 'nome')
    )

    # --- 3) Alvos prioritários ---------------------------------------
    # Procurados que têm pelo menos um cartaz ativo, do mais perigoso
    # pro menos perigoso. distinct() evita duplicar o procurado na
    # lista se ele tiver mais de um cartaz ativo ao mesmo tempo.
    alvos_prioritarios = (
        Procurado.objects
        .filter(cartazes__status=Cartaz.Status.ATIVO)
        .distinct()
        .order_by('-nivel_periculosidade', 'nome')[:5]
    )

    # --- 4) Últimas baixas --------------------------------------------
    # exclude(status=ATIVO) pega Capturado + Abatido de uma vez.
    # select_related evita 1 query extra por linha pra buscar o nome do
    # procurado e do caçador (JOIN único em vez de N+1 consultas).
    ultimas_baixas = (
        Cartaz.objects
        .exclude(status=Cartaz.Status.ATIVO)
        .select_related('procurado', 'cacador')
        .order_by('-atualizado_em')[:3]
    )

    contexto = {
        'total_recompensas_ativas': total_recompensas_ativas,
        'total_cartazes_ativos': cartazes_ativos.count(),
        'ranking_bandos': ranking_bandos,
        'alvos_prioritarios': alvos_prioritarios,
        'ultimas_baixas': ultimas_baixas,
    }
    return render(request, 'recompensas/dashboard.html', contexto)
