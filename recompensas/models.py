from django.db import models
from django.urls import reverse


class Bando(models.Model):
    """Uma gangue. Pode ter vários Procurados (1:N)."""

    nome = models.CharField('nome do bando', max_length=100, unique=True)
    area_atuacao = models.CharField('área de atuação', max_length=100)

    class Meta:
        ordering = ['nome']
        verbose_name = 'bando'
        verbose_name_plural = 'bandos'

    def __str__(self):
        return self.nome


class Cacador(models.Model):
    """
    O caçador de recompensas.

    Não tem um campo próprio apontando para os Cartazes concluídos — essa
    "lista de cartazes concluídos" é o lado reverso da ForeignKey definida
    em Cartaz.cacador (veja related_name='cartazes_concluidos' abaixo).
    Um ForeignKey já modela certinho a regra de negócio "cada cartaz tem
    no máximo um caçador responsável"; um ManyToManyField permitiria vários
    caçadores no mesmo cartaz, o que não faz sentido aqui.
    """

    nome = models.CharField('nome', max_length=120)
    reputacao = models.PositiveIntegerField(
        'reputação',
        default=0,
        help_text='Pontos acumulados por cartazes concluídos.',
    )

    class Meta:
        ordering = ['-reputacao', 'nome']
        verbose_name = 'caçador'
        verbose_name_plural = 'caçadores'

    def __str__(self):
        return self.nome


class Procurado(models.Model):
    """O alvo. Pertence (opcionalmente) a um Bando — relação 1:N."""

    class NivelPericulosidade(models.IntegerChoices):
        """
        IntegerChoices em vez de um CharField com 'Baixo'/'Alto'/'Lenda':
        guarda um número no banco (ordena corretamente em "top 5 mais
        perigosos") mas exibe o rótulo em português via
        get_nivel_periculosidade_display() — o melhor dos dois mundos que
        o enunciado sugeriu.
        """
        BAIXO = 1, 'Baixo'
        MEDIO = 2, 'Médio'
        ALTO = 3, 'Alto'
        MUITO_ALTO = 4, 'Muito Alto'
        LENDA = 5, 'Lenda'

    nome = models.CharField('nome', max_length=120)
    apelido = models.CharField('apelido', max_length=100, blank=True)
    nivel_periculosidade = models.PositiveSmallIntegerField(
        'nível de periculosidade',
        choices=NivelPericulosidade.choices,
        default=NivelPericulosidade.BAIXO,
    )
    bando = models.ForeignKey(
        Bando,
        verbose_name='bando',
        related_name='procurados',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Opcional — nem todo foragido pertence a uma gangue.',
    )
    # Mantido do model antigo (CartazProcurado.foto) — o upload de imagem
    # agora mora aqui, já que a foto é do foragido, não do contrato.
    foto = models.ImageField(
        'foto',
        upload_to='procurados/',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['-nivel_periculosidade', 'nome']
        verbose_name = 'procurado'
        verbose_name_plural = 'procurados'

    def __str__(self):
        return f'{self.nome} ({self.get_nivel_periculosidade_display()})'


class Cartaz(models.Model):
    """
    O contrato de recompensa. Vinculado a um Procurado via ForeignKey
    (1:N) — e não OneToOne — porque um foragido pode ter mais de um
    cartaz ao longo do tempo (ex.: escapou depois de capturado e um novo
    cartaz foi emitido). Se a regra do seu professor exigir 1:1 estrito,
    basta acrescentar unique=True no campo `procurado` abaixo.
    """

    class Status(models.TextChoices):
        ATIVO = 'ATIVO', 'Ativo'
        CAPTURADO = 'CAPTURADO', 'Capturado'
        ABATIDO = 'ABATIDO', 'Abatido'

    procurado = models.ForeignKey(
        Procurado,
        verbose_name='procurado',
        related_name='cartazes',
        on_delete=models.CASCADE,
    )
    valor_recompensa = models.DecimalField(
        'valor da recompensa (US$)',
        max_digits=10,
        decimal_places=2,
    )
    data_emissao = models.DateField('data de emissão', auto_now_add=True)
    status = models.CharField(
        'status',
        max_length=10,
        choices=Status.choices,
        default=Status.ATIVO,
    )
    # Preenchido só quando o cartaz é resolvido (Capturado/Abatido).
    cacador = models.ForeignKey(
        Cacador,
        verbose_name='caçador responsável',
        related_name='cartazes_concluidos',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_emissao']
        verbose_name = 'cartaz'
        verbose_name_plural = 'cartazes'

    def __str__(self):
        return f'Cartaz de {self.procurado.nome} — {self.get_status_display()}'

    def get_absolute_url(self):
        return reverse('recompensas:dashboard')
